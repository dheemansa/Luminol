import logging
from pathlib import Path
from ..utils.path import _expand_path, get_luminol_dir
import os
from ..cli.term_colors import AnsiColors

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
            location = f"[{table_name}]" if table_name else "configuration"
            logging.error(
                f"Invalid type for option '{WARN}{option}{RESET}' in {INFO}{location}{RESET}. "
                f"Expected {INFO}{expected_type.__name__}{RESET}, got {ERR}{type(value).__name__}{RESET}."
            )
            error_count += 1

    return error_count == 0


def warn_unsupported_option(
    config: dict, supported_options: set, table_name: str = ""
) -> None:
    # Example:
    # config = {
    #     "theme-type": "auto",
    #     "wallpaper-command": "swww img {wallpaper_path}",
    #     "reload-commands": ["notify-send reload1", "notify-send reload2"],
    #     "wallpaper-color": "Black",  # <-- this is an unsupported, warning is given
    # }

    # supported_options = { "wallpaper-command", "theme-type", "reload-commands" }

    location = f"[{table_name}]" if table_name else "configuration"
    options = set(config.keys())
    if not options.issubset(supported_options):
        invalid_options = options - supported_options
        for i in invalid_options:
            logging.warning(
                f"Unknown option '{WARN}{i}{RESET}' in {INFO}{location}{RESET}.\n"
                f"{' ' * 10}Supported: {INFO}{', '.join(supported_options)}{RESET}"
            )


def validate_global_config(global_settings: dict) -> bool:
    error_count = 0
    SUPPORTED_THEME_TYPES = ["auto", "light", "dark"]
    GLOBAL_OPTION_SCHEMA = {
        "wallpaper-command": str,
        "theme-type": str,
        "reload-commands": list,
        "use-shell": bool,
        "log-output": bool,
    }
    global_supported_options = set(GLOBAL_OPTION_SCHEMA.keys())

    if is_datatype_valid(global_settings, GLOBAL_OPTION_SCHEMA, "global") == False:
        error_count += 1

    warn_unsupported_option(global_settings, global_supported_options, "global")

    # Specifically validate the 'theme-type' value if it exists.
    if "theme-type" in global_settings:
        if global_settings.get("theme-type") not in SUPPORTED_THEME_TYPES:
            logging.error("Invalid theme-type in [global]")
            error_count += 1

    if error_count > 0:
        return False
    else:
        return True


def validate_application_config(application_config: dict) -> bool:
    error_count = 0
    warning_count = 0

    AVAILABLE_COLORS = (
        "bg-primary",
        "bg-secondary",
        "bg-tertiary",
        "text-primary",
        "text-secondary",
        "text-tertiary",
        "accent-primary",
        "accent-secondary",
        "error-color",
        "warning-color",
        "success-color",
        "border-active",
        "border-inactive",
        "ansi-0",  # Black
        "ansi-1",  # Red
        "ansi-2",  # Green
        "ansi-3",  # Yellow
        "ansi-4",  # Blue
        "ansi-5",  # Magenta
        "ansi-6",  # Cyan
        "ansi-7",  # White
        "ansi-8",  # Bright Black
        "ansi-9",  # Bright Red
        "ansi-10",  # Bright Green
        "ansi-11",  # Bright Yellow
        "ansi-12",  # Bright Blue
        "ansi-13",  # Bright Magenta
        "ansi-14",  # Bright Cyan
        "ansi-15",  # Bright White
    )

    SUPPORTED_COLOR_FORMATS = (
        "hex6",
        "hex8",
        "rgb",
        "rgba",
        "rgb_decimal",
        "rgba_decimal",
    )
    # Mandatory options for each application section.
    MANDATORY_OPTIONS: set = {"enabled", "output-file", "color-format", "syntax"}

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

    supported_options_set = set(APPLICATION_OPTION_SCHEMA)

    for application in application_config:
        application_options: dict = application_config.get(application, {})
        # Info:
        # application_options = {
        #     "enabled": True,
        #     "file": "~/test/colors.css",
        #     "syntax": "@define-color {name} {color};",
        #     "color-format": "hex6",
        # }

        # check if non-supported functions are present
        # Warn about any unknown options for the current application.
        # Any unsupported option will be be ignored later, so even if config has unsupported options it is still valid
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
        if not MANDATORY_OPTIONS.issubset(application_options_set):
            missing_mandatory_options = MANDATORY_OPTIONS - application_options_set
            missing_options: str = ", ".join(
                f"'{option}'" for option in missing_mandatory_options
            )
            logging.error(
                f"Missing mandatory option {WARN}{missing_options}{RESET} in {INFO}[{application}]{RESET}"
            )
            error_count += 1

        # validate the 'color-format' value.
        # Check if color-format exists before validating its value
        if "color-format" in application_options:
            color_format = application_options.get("color-format")
            if color_format not in SUPPORTED_COLOR_FORMATS:
                logging.error(
                    f"Invalid value for option '{WARN}color-format{RESET}' in {INFO}[{application}]{RESET}.\n"
                    # using {' '* 8} to match indentation with the previous line
                    f"{' ' * 8}Got '{ERR}{color_format}{RESET}', supported formats are: {INFO}{', '.join(SUPPORTED_COLOR_FORMATS)}{RESET}",
                )
                error_count += 1

        # TODO make changes to the plan, if output-path is just a file name then the palette for that application will be only stored in cache

        output_file = application_options.get("output-file", None)
        # Only validate the parent directory if the output_file contains a path separator,
        # indicating it's a path and not just a filename.
        if output_file is not None and not output_file.strip():
            logging.error(
                f"'{ERR}output-file{RESET}' cannot be empty, Error in {INFO}{application}{RESET}"
            )
            error_count += 1

        # NOTE: os.sep not really needed but in case the future version has compability for windows too

        # validation for path, if the parent folder exists and whether it has write permission
        if output_file is not None and (os.sep in output_file or "/" in output_file):
            parent_file_path: Path = _expand_path(output_file).parent  # fmt: skip
            if parent_file_path.exists():
                # check for write permission if exists
                if not os.access(parent_file_path, os.W_OK):
                    logging.error(
                        f"Cannot write to directory: '{ERR}{parent_file_path}{RESET}' for {INFO}[{application}]{RESET}. Check permissions."
                    )
                    error_count += 1
            else:
                logging.error(
                    f"No such directory exists: {WARN}{parent_file_path}{RESET}, for {INFO}[{application}]{RESET}",
                )
                error_count += 1

        remap_color_option: bool = application_options.get("remap-colors", False)

        if remap_color_option == True:
            remap_dict: dict | None = application_options.get("colors", None)
            if remap_dict is None:
                logging.error(
                    f"'{INFO}{application}{RESET}' has remap-colors set to true,{WARN} but no 'colors' table for was found.{RESET} \n"
                )
                error_count += 1

            elif len(remap_dict) == 0:
                logging.error(
                    f"'{INFO}{application}{RESET}' has remap-colors set to true, "
                    f"but the '{WARN}[{application}.colors]{RESET}' table is empty.\n"
                )
                error_count += 1

            else:
                for color_name, values in remap_dict.items():
                    # check if values is a dict, if it is not then config is invalid
                    if not isinstance(values, dict):
                        error_count += 1
                        logging.error(
                            f"Invalid configuration for color '{WARN}{color_name}{RESET}' in {INFO}[{application}.colors]{RESET}.\n"
                            f"{' ' * 8}Expected a table/dictionary, got {ERR}{type(values).__name__}{RESET}"
                        )
                        continue

                    source = values.get("source", None)
                    if source is None:
                        error_count += 1
                        logging.error(
                            f"No source color defined for '{color_name}' in [{application}.colors]"
                        )
                    else:
                        if source not in AVAILABLE_COLORS:
                            error_count += 1
                            logging.error(
                                f"Invalid source color '{ERR}{source}{RESET}' for '{WARN}{color_name}{RESET}' in {INFO}[{application}.colors]{RESET}.\n"
                                f"{' ' * 8}Available colors: {INFO}{', '.join(AVAILABLE_COLORS)}{RESET}"
                            )

                    # check for transformation
                    # warn if an unknown transformation is used

                    for transformation, amount in values.items():
                        if transformation == "source":
                            continue

                        if transformation not in (
                            "hue",
                            "contrast",
                            "saturation",
                            "opacity",
                            "temperature",
                            "brightness",
                        ):
                            logging.error(
                                f"Unsupported transformation '{WARN}{transformation}{RESET}' for color '{WARN}{color_name}{RESET}' in {INFO}[{application}.colors]{RESET}. "
                                f"Supported transformations are: {INFO}hue, saturation, brightness, contrast, temperature, opacity{RESET}."
                            )
                            continue  # no further check needed as the transformation was not suppoerted

                        if transformation == "hue":
                            if not (-360 <= amount <= 360):
                                logging.error(
                                    f"Invalid value for '{WARN}hue{RESET}' transformation on color '{WARN}{color_name}{RESET}' in {INFO}[{application}.colors]{RESET}. "
                                    f"Expected a value between {INFO}-360 and 360{RESET}, but got {ERR}{amount}{RESET}."
                                )
                                error_count += 1

                        elif transformation == "saturation":
                            if not (0 <= amount):
                                logging.error(
                                    f"Invalid value for '{WARN}saturation{RESET}' transformation on color '{WARN}{color_name}{RESET}' in {INFO}[{application}.colors]{RESET}. "
                                    f"Expected a value greater than {INFO}0{RESET}, but got {ERR}{amount}{RESET}."
                                )
                                error_count += 1

                        elif transformation == "opacity":
                            if not (0 <= amount <= 1):
                                logging.error(
                                    f"Invalid value for '{WARN}opacity{RESET}' transformation on color '{WARN}{color_name}{RESET}' in {INFO}[{application}.colors]{RESET}. "
                                    f"Expected a value between {INFO}0.0 and 1.0{RESET}, but got {ERR}{amount}{RESET}."
                                )
                                error_count += 1

                        elif transformation == "brightness":
                            if not (0 <= amount):
                                logging.error(
                                    f"Invalid value for '{WARN}brightness{RESET}' transformation on color '{WARN}{color_name}{RESET}' in {INFO}[{application}.colors]{RESET}. "
                                    f"Expected a value greater than {INFO}0{RESET}, but got {ERR}{amount}{RESET}."
                                )
                                error_count += 1

                        elif transformation == "temperature":
                            if not (-100 <= amount <= 100):
                                logging.error(
                                    f"Invalid value for '{WARN}temperature{RESET}' transformation on color '{WARN}{color_name}{RESET}' in {INFO}[{application}.colors]{RESET}. "
                                    f"Expected a value between {INFO}-100 and 100{RESET}, but got {ERR}{amount}{RESET}."
                                )
                                error_count += 1

                        elif transformation == "contrast":
                            if not (0 <= amount):
                                logging.error(
                                    f"Invalid value for '{WARN}contrast{RESET}' transformation on color '{WARN}{color_name}{RESET}' in {INFO}[{application}.colors]{RESET}. "
                                    f"Expected a value greater than {INFO}0{RESET}, but got {ERR}{amount}{RESET}."
                                )
                                error_count += 1

        template = application_options.get("template", None)

        if template is not None:
            # NOTE: os.sep not really needed but in case the future version has compability for windows too
            is_file_name = not (os.sep in template or "/" in template)

            if is_file_name:
                template_path = get_luminol_dir() / "templates" / template
            else:
                template_path = _expand_path(template)

            if not template_path.is_file():
                logging.error(f"No such file exists: {template_path}")
                error_count += 1

            syntax: str = application_options.get("syntax", "")  # type: ignore
            if syntax and ("placeholder" not in syntax):
                # TODO: improve the warning message
                error_count += 1
                logging.error(
                    f"'{WARN}syntax{RESET}' in {INFO}[{application}]{RESET} must contain the word '{WARN}placeholder{RESET}' when using template mode.\n"
                    f"{' ' * 8}Current syntax: '{ERR}{syntax}{RESET}'"
                )

    ## TODO: also count warning and, if waring count is >0, then inform that warning doesnt mean that there is an issue with the config,
    ##       user can safely ignore the warning is it was intentional
    if warning_count != 0:
        print(
            f"{WARN}Warning doesnt mean that there is an issue with the config, it can be safely ignored if it was intentional{RESET}"
        )

    # Return True if no errors were found, False otherwise.
    return error_count == 0
