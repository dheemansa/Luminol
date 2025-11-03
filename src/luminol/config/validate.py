import logging
from pathlib import Path
from ..utils.path import _expand_path
import os
from ..cli.term_colors import AnsiColors

# TODO use these instead
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

    has_errors = False

    for option, value in options.items():
        expected_type = type_schema.get(option)
        if expected_type and not isinstance(value, expected_type):
            location = f"[{table_name}]" if table_name else "configuration"
            logging.error(
                f"Invalid type for option '{AnsiColors.WARNING}{option}{AnsiColors.RESET}' in {AnsiColors.INFO}{location}{AnsiColors.RESET}. "
                f"Expected {AnsiColors.INFO}{expected_type.__name__}{AnsiColors.RESET}, got {AnsiColors.ERROR}{type(value).__name__}{AnsiColors.RESET}."
            )
            has_errors = True

    return not has_errors


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
                f"Unknown option '{AnsiColors.WARNING}{i}{AnsiColors.RESET}' in {AnsiColors.INFO}{location}{AnsiColors.RESET}.\n"
                f"{' ' * 10}Supported: {AnsiColors.INFO}{', '.join(supported_options)}{AnsiColors.RESET}"
            )


def validate_global_config(global_settings: dict) -> bool:
    error_count = 0
    SUPPORTED_THEME_TYPES = ["auto", "light", "dark"]
    GLOBAL_OPTION_SCHEMA = {
        "wallpaper-command": str,
        "theme-type": str,
        "reload-commands": list,
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

    SUPPORTED_COLOR_FORMATS = [
        "hex6",
        "hex8",
        "rgb",
        "rgba",
        "rgb_decimal",
        "rgba_decimal",
    ]
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
        "placeholders": dict,
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
                f"Missing mandatory option {AnsiColors.WARNING}{missing_options}{AnsiColors.RESET} in {AnsiColors.INFO}[{application}]{AnsiColors.RESET}"
            )
            error_count += 1

        # validate the 'color-format' value.
        # Check if color-format exists before validating its value
        if "color-format" in application_options:
            color_format = application_options.get("color-format")
            if color_format not in SUPPORTED_COLOR_FORMATS:
                logging.error(
                    f"Invalid value for option '{AnsiColors.WARNING}color-format{AnsiColors.RESET}' in {AnsiColors.INFO}[{application}]{AnsiColors.RESET}.\n"
                    # using {' '* 8} to match indentation with the previous line
                    f"{' ' * 8}Got '{AnsiColors.ERROR}{color_format}{AnsiColors.RESET}', supported formats are: {AnsiColors.INFO}{', '.join(SUPPORTED_COLOR_FORMATS)}{AnsiColors.RESET}",
                )
                error_count += 1

        # validation for path, if the parent folder exists and whether it has write permission
        # TODO make changes to the plan, if path is an empty string then the palette for that application will be only stored in cache
        # if it is a empty string then generated file is only stored in the cache

        # only validate if file is not an empty string
        if application_options.get("output-file", ""):
            parent_file_path: Path = _expand_path(application_options.get("output-file", "")).parent  # fmt: skip
            if parent_file_path.exists():
                # check for write permission if exists
                if not os.access(parent_file_path, os.W_OK):
                    logging.error(
                        f"Cannot write to directory: '{AnsiColors.ERROR}{parent_file_path}{AnsiColors.RESET}' for {AnsiColors.INFO}[{application}]{AnsiColors.RESET}. Check permissions."
                    )
                    error_count += 1

            else:
                logging.error(
                    f"No such directory exists: {AnsiColors.WARNING}{parent_file_path}{AnsiColors.RESET}, for {AnsiColors.INFO}[{application}]{AnsiColors.RESET}",
                )
                error_count += 1

        ## TODO implement check for app.color is present if remap-color is set to true
        remap_color_option = application_options.get("remap-color", False)
        # if

    ## TODO check if correct sementic colors names are used in template placeholder and app.colors
    ## TODO check if correct transformation are used in colors and placeholders
    ## TODO if app.placeholders is present then syntax must contain {placeholder}
    ## TODO: Check if [app.colors] is present when remap-colors is true.
    ## TODO: Check if [app.placeholders] is present when a template is specified.
    ## TODO: Validate semantic color names used as sources in [app.colors] and [app.placeholders].
    ## TODO: Validate transformation types and their values.
    ## TODO: Ensure syntax contains {placeholder} when [app.placeholders] is defined.
    ## TODO: check value of transformation

    # Return True if no errors were found, False otherwise.
    if error_count > 0:
        return False
    else:
        return True


def validate_config(config: dict) -> None:
    isGlobalValid = validate_global_config(config.get("global", {}))
    config.pop("global")
    isApplicationValid = validate_application_config(config)
    if not (isGlobalValid and isApplicationValid):
        raise SystemExit(
            AnsiColors.colorize(
                "Luminol configuration is invalid. Please review your settings.",
                AnsiColors.ERROR,
            )
        )

    logging.info("Validation Complete")
