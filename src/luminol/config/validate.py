import logging
import os
from pathlib import Path

from ..cli.term_colors import AnsiColors
from ..core.constants import (
    AVAILABLE_COLORS,
    SUPPORTED_COLOR_FORMATS,
    SUPPORTED_COLOR_TRANFORMATION,
)
from ..utils.path import _expand_path, get_luminol_dir

# All supported options for an application section.
# Expected types for application options
APPLICATION_OPTION_SCHEMA = {
    "enabled": bool,
    "color-format": str,
    "output-file": str,
    "syntax": str,
    "remap-colors": bool,
    "template": str,
    "colors": dict,
}

GLOBAL_OPTION_SCHEMA = {
    "wallpaper-command": str,
    "theme-type": str,
    "reload-commands": list,
    "use-shell": bool,
    "log-output": bool,
}

# Mandatory options for each application section.
APPLICATION_MANDATORY_OPTIONS: set = {
    "enabled",
    "output-file",
    "color-format",
    "syntax",
}

SUPPORTED_THEME_TYPES = ("auto", "light", "dark")

WARN = AnsiColors.WARNING
INFO = AnsiColors.INFO
ERR = AnsiColors.ERROR
RESET = AnsiColors.RESET


def is_datatype_valid(options: dict, type_schema: dict, table_name: str = "") -> bool:
    # Example:
    # options = {
    #     'wallpaper-command': 'swww img {wallpaper_path}',
    #     'theme-type': 'auto',
    #     'reload-commands': ['notify-send reload1', 'notify-send reload2'],
    # }

    # type_schema = {
    #     "wallpaper-command": str,
    #     "theme-type": str,
    #     "reload-commands": list,
    # }

    error_count = 0

    for option, value in options.items():
        expected_type = type_schema.get(option)
        if expected_type and not isinstance(value, expected_type):
            location = "[{table_name}]" if table_name else "configuration"
            logging.error(
                "Invalid type for option '%s%s%s' in %s%s%s. \
                Expected %s%s%s, got %s%s%s.",
                WARN,
                option,
                RESET,
                INFO,
                location,
                RESET,
                INFO,
                expected_type.__name__,
                RESET,
                ERR,
                type(value).__name__,
                RESET,
            )
            error_count += 1

    return error_count == 0


def warn_unsupported_option(
    config: dict, supported_options: set, table_name: str = ""
) -> None:
    location = f"[{table_name}]" if table_name else "configuration"
    options = set(config.keys())
    if not options.issubset(supported_options):
        invalid_options = options - supported_options
        for i in invalid_options:
            logging.warning(
                "Unknown option '%s%s%s' in %s%s%s.\n%s \
                Supported options are: %s%s%s\n",
                WARN,
                i,
                RESET,
                INFO,
                location,
                RESET,
                " " * 9,  # indent for logging.warning new line
                INFO,
                ", ".join(supported_options),
                RESET,
            )


def validate_global_config(global_settings: dict) -> bool:
    error_count = 0
    global_supported_options = set(GLOBAL_OPTION_SCHEMA.keys())

    if is_datatype_valid(global_settings, GLOBAL_OPTION_SCHEMA, "global") is False:
        error_count += 1

    warn_unsupported_option(global_settings, global_supported_options, "global")

    # Specifically validate the 'theme-type' value if it exists.
    if "theme-type" in global_settings:
        if global_settings.get("theme-type") not in SUPPORTED_THEME_TYPES:
            logging.error("Invalid theme-type in [global]")
            error_count += 1

    return error_count == 0


def validate_application_config(application_config: dict) -> bool:
    error_count = 0
    warning_count = 0

    supported_options_set = set(APPLICATION_OPTION_SCHEMA)

    for application in application_config:
        application_options: dict = application_config.get(application, {})

        # check if non-supported functions are present
        # Warn about any unknown options for the current application.
        # Any unsupported option will be be ignored later,
        # so even if config has unsupported options it is still valid
        warn_unsupported_option(
            config=application_options,
            supported_options=supported_options_set,
            table_name=application,
        )

        # Verify that the option's value has the correct data type.
        # If invalid datatype is found then the config is in invalid
        if not is_datatype_valid(
            application_options, APPLICATION_OPTION_SCHEMA, table_name=application
        ):
            error_count += 1

        application_options_set = set(application_options.keys())
        # check all the mandetory options are present
        # Ensure all mandatory options are present for the application.
        if not APPLICATION_MANDATORY_OPTIONS.issubset(application_options_set):
            missing_mandatory_options = (
                APPLICATION_MANDATORY_OPTIONS - application_options_set
            )
            missing_options: str = ", ".join(
                f"'{option}'" for option in missing_mandatory_options
            )
            logging.error(
                "Missing mandatory option %s%s%s in %s[%s]%s",
                WARN,
                missing_options,
                RESET,
                INFO,
                application,
                RESET,
            )
            error_count += 1

        # Empty checks for required string options
        syntax_val: str = application_options.get("syntax", "")
        if not syntax_val.strip():
            logging.error(
                "'%ssyntax%s' cannot be empty, Error in %s[%s]%s",
                ERR,
                RESET,
                INFO,
                application,
                RESET,
            )
            error_count += 1

        color_format_val: str = application_options.get("color-format", "")
        if not color_format_val.strip():
            logging.error(
                "'%scolor-format%s' cannot be empty, Error in %s[%s]%s",
                ERR,
                RESET,
                INFO,
                application,
                RESET,
            )
            error_count += 1

        # validate the 'color-format' value.
        # Check if color-format exists before validating its value
        if "color-format" in application_options:
            color_format = application_options.get("color-format")
            # Only validate against supported formats if non-empty;
            # emptiness is handled separately
            if color_format and color_format not in SUPPORTED_COLOR_FORMATS:
                logging.error(
                    "Invalid value for option '%scolor-format%s' in %s[%s]%s. \
                    Got '%s%s%s'\n %s Supported formats: %s%s%s\n",
                    WARN,
                    RESET,
                    INFO,
                    application,
                    RESET,
                    ERR,
                    color_format,
                    RESET,
                    " " * 7,  # indent for logging.error new line
                    INFO,
                    ", ".join(SUPPORTED_COLOR_FORMATS),
                    RESET,
                )
                error_count += 1

        output_file = application_options.get("output-file", None)
        # Only validate the parent directory
        # if the output_file contains a path separator,
        # indicating it's a path and not just a filename.
        if output_file is not None and not output_file.strip():
            logging.error(
                "'%soutput-file%s' cannot be empty, Error in %s%s%s",
                ERR,
                RESET,
                INFO,
                application,
                RESET,
            )
            error_count += 1

        # NOTE: os.sep not really needed
        # but in case the future version has compability for windows too

        # validation for path, if the parent folder exists
        # and whether it has write permission
        if output_file is not None and (os.sep in output_file or "/" in output_file):
            parent_file_path: Path = _expand_path(output_file).parent
            if parent_file_path.exists():
                # check for write permission if exists
                if not os.access(parent_file_path, os.W_OK):
                    logging.error(
                        "Cannot write to directory: '%s%s%s' for %s[%s]%s. \
                        Check permissions.",
                        ERR,
                        parent_file_path,
                        RESET,
                        INFO,
                        application,
                        RESET,
                    )
                    error_count += 1
            else:
                logging.error(
                    "No such directory exists: %s%s%s, for %s[%s]%s",
                    WARN,
                    parent_file_path,
                    RESET,
                    INFO,
                    application,
                    RESET,
                )
                error_count += 1

        remap_color_option: bool = application_options.get("remap-colors", False)

        if remap_color_option is True:
            remap_dict: dict | None = application_options.get("colors", None)
            if remap_dict is None:
                logging.error(
                    "%s[%s]%s has remap-colors set to true,%s \
                    but no 'colors' table for was found.%s",
                    INFO,
                    application,
                    RESET,
                    WARN,
                    RESET,
                )
                error_count += 1

            elif len(remap_dict) == 0:
                logging.error(
                    "%s[%s]%s has remap-colors set to true, \
                    but the '%s[%s.colors]%s' table is empty.",
                    INFO,
                    application,
                    RESET,
                    WARN,
                    application,
                    RESET,
                )
                error_count += 1

            else:
                for color_name, values in remap_dict.items():
                    # check if values is a dict,
                    # if it is not then config is invalid
                    if not isinstance(values, dict):
                        error_count += 1
                        logging.error(
                            "Invalid configuration for color '%s%s%s' in \
                            %s[%s.colors]%s. Expected a table/dictionary, \
                            got %s%s%s",
                            WARN,
                            color_name,
                            RESET,
                            INFO,
                            application,
                            RESET,
                            ERR,
                            type(values).__name__,
                            RESET,
                        )
                        continue

                    source = values.get("source", None)
                    if source is None:
                        error_count += 1
                        logging.error(
                            "No source color defined for '%s' in [%s.colors]",
                            color_name,
                            application,
                        )
                    else:
                        if source not in AVAILABLE_COLORS:
                            error_count += 1
                            logging.error(
                                "Invalid source color '%s%s%s' for '%s%s%s' \
                                in %s[%s.colors]%s.\n%sAvailable colors: \
                                %s%s%s\n",
                                ERR,
                                source,
                                RESET,
                                WARN,
                                color_name,
                                RESET,
                                INFO,
                                application,
                                RESET,
                                " " * 7,  # indent for logging.error new line
                                INFO,
                                ", ".join(AVAILABLE_COLORS),
                                RESET,
                            )

                    # check for transformation
                    # warn if an unknown transformation is used

                    for transformation, amount in values.items():
                        if transformation == "source":
                            continue

                        if transformation not in SUPPORTED_COLOR_TRANFORMATION:
                            logging.error(
                                "Unsupported transformation '%s%s%s' \
                                for color '%s%s%s' in %s[%s.colors]%s. \
                                Supported transformations are: %s%s%s.\n",
                                WARN,
                                transformation,
                                RESET,
                                WARN,
                                color_name,
                                RESET,
                                INFO,
                                application,
                                RESET,
                                INFO,
                                " ".join(SUPPORTED_COLOR_TRANFORMATION),
                                RESET,
                            )
                            # no further check needed
                            # as the transformation was not suppoerted
                            continue

                        if transformation == "hue":
                            if not -360 <= amount <= 360:
                                logging.error(
                                    "Invalid value for '%shue%s' \
                                    transformation on color '%s%s%s' \
                                    in %s[%s.colors]%s. Expected a value \
                                    between %s-360 and 360%s, but got %s%s%s.",
                                    WARN,
                                    RESET,
                                    WARN,
                                    color_name,
                                    RESET,
                                    INFO,
                                    application,
                                    RESET,
                                    INFO,
                                    RESET,
                                    ERR,
                                    amount,
                                    RESET,
                                )
                                error_count += 1

                        elif transformation == "saturation":
                            if not 0 <= amount:
                                logging.error(
                                    "Invalid value for '%ssaturation%s' \
                                    transformation on color '%s%s%s' \
                                    in %s[%s.colors]%s. Expected a value \
                                    greater than %s0%s, but got %s%s%s.",
                                    WARN,
                                    RESET,
                                    WARN,
                                    color_name,
                                    RESET,
                                    INFO,
                                    application,
                                    RESET,
                                    INFO,
                                    RESET,
                                    ERR,
                                    amount,
                                    RESET,
                                )
                                error_count += 1

                        elif transformation == "opacity":
                            if not 0 <= amount <= 1:
                                logging.error(
                                    "Invalid value for '%sopacity%s' \
                                    transformation on color '%s%s%s' in \
                                    %s[%s.colors]%s. Expected a value between \
                                    %s0.0 and 1.0%s, but got %s%s%s.",
                                    WARN,
                                    RESET,
                                    WARN,
                                    color_name,
                                    RESET,
                                    INFO,
                                    application,
                                    RESET,
                                    INFO,
                                    RESET,
                                    ERR,
                                    amount,
                                    RESET,
                                )
                                error_count += 1

                        elif transformation == "brightness":
                            if not 0 <= amount:
                                logging.error(
                                    "Invalid value for '%sbrightness%s' \
                                    transformation on color '%s%s%s' in \
                                    %s[%s.colors]%s. Expected a value greater \
                                    than %s0%s, but got %s%s%s.",
                                    WARN,
                                    RESET,
                                    WARN,
                                    color_name,
                                    RESET,
                                    INFO,
                                    application,
                                    RESET,
                                    INFO,
                                    RESET,
                                    ERR,
                                    amount,
                                    RESET,
                                )
                                error_count += 1

                        elif transformation == "temperature":
                            if not -100 <= amount <= 100:
                                logging.error(
                                    "Invalid value for '%stemperature%s' \
                                    transformation on color '%s%s%s' in \
                                    %s[%s.colors]%s. Expected a value between \
                                    %s-100 and 100%s, but got %s%s%s.",
                                    WARN,
                                    RESET,
                                    WARN,
                                    color_name,
                                    RESET,
                                    INFO,
                                    application,
                                    RESET,
                                    INFO,
                                    RESET,
                                    ERR,
                                    amount,
                                    RESET,
                                )
                                error_count += 1

                        elif transformation == "contrast":
                            if not 0 <= amount:
                                logging.error(
                                    "Invalid value for '%scontrast%s' \
                                    transformation on color '%s%s%s' in \
                                    %s[%s.colors]%s. Expected a value greater \
                                    than %s0%s, but got %s%s%s.",
                                    WARN,
                                    RESET,
                                    WARN,
                                    color_name,
                                    RESET,
                                    INFO,
                                    application,
                                    RESET,
                                    INFO,
                                    RESET,
                                    ERR,
                                    amount,
                                    RESET,
                                )
                                error_count += 1

        template = application_options.get("template", None)

        syntax: str = application_options.get("syntax", "")  # type: ignore
        if template is not None:
            # NOTE: os.sep not really needed but
            # in case the future version has compability for windows too
            is_file_name = not (os.sep in template or "/" in template)

            if is_file_name:
                template_path = get_luminol_dir() / "templates" / template
            else:
                template_path = _expand_path(template)

            if not template_path.is_file():
                logging.error(
                    "No such template exists: %s%s%s for %s[%s]%s",
                    ERR,
                    template_path,
                    RESET,
                    INFO,
                    application,
                    RESET,
                )
                error_count += 1

            syntax: str = application_options.get("syntax", "")  # type: ignore
            if syntax and ("placeholder" not in syntax):
                error_count += 1
                logging.error(
                    "'%ssyntax%s' in %s[%s]%s must contain the word \
                    '%splaceholder%s' when using template mode. \
                    Current syntax: '%s%s%s'",
                    WARN,
                    RESET,
                    INFO,
                    application,
                    RESET,
                    WARN,
                    RESET,
                    ERR,
                    syntax,
                    RESET,
                )
        else:
            # for default mode
            if syntax:
                if "{name}" not in syntax:
                    logging.warning(
                        "No {name} token found in syntax for [%s]. \
                        Ignore if intentional",
                        application,
                    )
                    warning_count += 1

                if "{color}" not in syntax:
                    logging.warning(
                        "No {color} token found in syntax for [%s]. \
                        Ignore if intentional",
                        application,
                    )
                    warning_count += 1

    if warning_count != 0:
        print(
            f"{WARN}Warning doesnt mean that \
            there is an issue with the config, \
            it can be safely ignored if it was intentional{RESET}"
        )

    # Return True if no errors were found, False otherwise.
    return error_count == 0
