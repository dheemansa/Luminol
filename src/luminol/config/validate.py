"""
This module provides functions for validating configuration data for the Luminol application.

The main validation functions are:
- validate_global_config: Validates the [global] section of the config.
- validate_application_config: Validates all application sections (e.g., [dunst], [rofi]).

"""

import logging
import os

from ..cli.term_colors import AnsiColors
from ..core.constants import (
    AVAILABLE_COLORS,
    SUPPORTED_COLOR_FORMATS,
    SUPPORTED_COLOR_TRANFORMATION,
)
from ..utils.path import _expand_path, _is_file_name, get_luminol_dir

WARN = AnsiColors.WARNING
INFO = AnsiColors.INFO
ERR = AnsiColors.ERROR
RESET = AnsiColors.RESET

SUPPORTED_THEME_TYPES = ("auto", "light", "dark")

# [global] schema
GLOBAL_SCHEMA = {
    "wallpaper-command": {"type": str},
    "theme-type": {"type": str, "allowed": SUPPORTED_THEME_TYPES},
    "reload-commands": {"type": list},
    "use-shell": {"type": bool},
    "log-output": {"type": bool},
}

# Schema for application
APPLICATION_SCHEMA = {
    "enabled": {"type": bool, "required": True},
    "color-format": {"type": str, "required": True, "allowed": SUPPORTED_COLOR_FORMATS},
    "output-file": {"type": str, "required": True},
    "syntax": {"type": str, "required": True},
    "remap-colors": {"type": bool},
    "template": {"type": str},
    "colors": {"type": dict},
}

TRANSFORMATION_VALIDATORS = {
    "hue": {"min": -360, "max": 360, "type": int},
    "saturation": {"min": 0, "max": float("inf"), "type": (int, float)},
    "opacity": {"min": 0, "max": 1, "type": (int, float)},
    "brightness": {"min": 0, "max": float("inf"), "type": (int, float)},
    "temperature": {"min": -100, "max": 100, "type": int},
    "contrast": {"min": 0, "max": float("inf"), "type": (int, float)},
}


def _validate_datatypes(options: dict, schema: dict, location: str) -> int:
    """Validates the data types of options against the schema."""
    error_count = 0
    for option, value in options.items():
        rule = schema.get(option)
        if rule and not isinstance(value, rule["type"]):
            logging.error(
                "Invalid type for option '%s%s%s' in %s%s%s. "
                "Expected %s%s%s, got %s%s%s.",
                ERR,
                option,
                RESET,
                INFO,
                location,
                RESET,
                INFO,
                rule["type"].__name__,
                RESET,
                ERR,
                type(value).__name__,
                RESET,
            )
            error_count += 1
    return error_count


def _validate_mandatory_options(options: dict, schema: dict, location: str) -> int:
    """Validates that all required options are present."""
    error_count = 0
    missing_options = [
        opt
        for opt, rule in schema.items()
        if rule.get("required") and opt not in options
    ]
    if missing_options:
        logging.error(
            "Missing mandatory option(s) %s%s%s in %s%s%s",
            WARN,
            ", ".join(
                f"'{opt}'" for opt in missing_options
            ),  # TODO: i think this was unnescessary
            RESET,
            INFO,
            location,
            RESET,
        )
        error_count += 1
    return error_count


def _warn_unsupported_options(options: dict, schema: dict, location: str):
    """Warns about unsupported options."""
    # only warn because these will be ignored later
    invalid_options: set = options.keys() - schema.keys()
    if invalid_options:
        supported_options_str = ", ".join(schema.keys())
        for option in invalid_options:
            logging.warning(
                "Unknown option '%s%s%s' in %s%s%s. Supported options are: %s%s%s",
                WARN,
                option,
                RESET,
                INFO,
                location,
                RESET,
                INFO,
                supported_options_str,
                RESET,
            )


def _validate_string_options(options: dict, location: str) -> int:
    """Checks that required string options are not empty."""
    error_count = 0
    required_str_options = [
        opts
        for opts, schema in APPLICATION_SCHEMA.items()
        if schema["type"] is str and schema.get("required")
    ]
    for option in required_str_options:
        if option in options and not options[option].strip():
            logging.error(
                "'%s%s%s' cannot be empty in %s%s%s",
                ERR,
                option,
                RESET,
                INFO,
                location,
                RESET,
            )
            error_count += 1
    return error_count


def _validate_color_format(options: dict, location: str) -> int:
    """Validates the 'color-format' option."""
    color_format = options.get("color-format")
    if color_format and color_format not in SUPPORTED_COLOR_FORMATS:
        logging.error(
            "Invalid value for '%scolor-format%s' in %s%s%s. Got '%s%s%s'.\n"
            "%sSupported formats: %s%s%s",
            WARN,
            RESET,
            INFO,
            location,
            RESET,
            ERR,
            color_format,
            RESET,
            " " * 7,  # indent for new line error logging
            INFO,
            ", ".join(SUPPORTED_COLOR_FORMATS),
            RESET,
        )
        return 1
    return 0


def _validate_output_file(options: dict, location: str) -> int:
    """Validates the 'output-file' path and permissions."""
    output_file = options.get("output-file")
    if not output_file or _is_file_name(output_file):
        return 0  # Skip if empty (handled by string check) or just a filename

    parent_dir = _expand_path(output_file).parent
    if not parent_dir.exists():
        logging.error(
            "No such directory exists: %s%s%s, for %s%s%s",
            WARN,
            parent_dir,
            RESET,
            INFO,
            location,
            RESET,
        )
        return 1
    if not os.access(parent_dir, os.W_OK):
        logging.error(
            "Cannot write to directory: '%s%s%s' for %s%s%s. Check permissions.",
            ERR,
            parent_dir,
            RESET,
            INFO,
            location,
            RESET,
        )
        return 1
    return 0


def _validate_template_and_syntax(options: dict, location: str) -> int:
    """Validates template and syntax options."""
    error_count = 0
    template = options.get("template")
    syntax = options.get("syntax", "")

    if template:
        if _is_file_name(template):
            template_path = get_luminol_dir() / "templates" / template
        else:
            template_path = _expand_path(template)

        if not template_path.is_file():
            logging.error(
                "No such template exists: %s%s%s for %s%s%s",
                ERR,
                template_path,
                RESET,
                INFO,
                location,
                RESET,
            )
            error_count += 1
        if "placeholder" not in syntax:
            logging.error(
                "'%ssyntax%s' in %s%s%s must contain 'placeholder' when using a template.",
                WARN,
                RESET,
                INFO,
                location,
                RESET,
            )
            error_count += 1

    elif syntax:
        # In default mode, warn if tokens are missing
        if "{name}" not in syntax:
            logging.warning(
                "No {name} token found in syntax for %s. Ignore if intentional.",
                location,
            )
        if "{color}" not in syntax:
            logging.warning(
                "No {color} token found in syntax for %s. Ignore if intentional.",
                location,
            )

    return error_count


def _validate_remap_colors(options: dict, location: str) -> int:
    """Validates the [*.colors] table when remap-colors is true."""
    if not options.get("remap-colors"):
        return 0

    error_count = 0
    colors_table = options.get("colors")

    if not colors_table:
        logging.error(
            "%s%s%s has '%sremap-colors%s' enabled, but no '%s%s.colors%s' table was found.",
            INFO,
            location,
            RESET,
            WARN,
            RESET,
            ERR,
            location.strip("[]"),
            RESET,
        )
        return 1

    for color_name, values in colors_table.items():
        if not isinstance(values, dict):
            logging.error(
                "Expected a table for color '%s' in %s%s.colors%s, got %s%s%s.",
                color_name,
                INFO,
                location,
                RESET,
                ERR,
                type(values).__name__,
                RESET,
            )
            error_count += 1
            continue

        source = values.get("source")
        if not source:
            logging.error(
                "No '%ssource%s' defined for color '%s%s%s' in %%s.colors%s.",
                ERR,
                RESET,
                INFO,
                color_name,
                RESET,
                INFO,
                location,
                RESET,
            )
            error_count += 1

        elif source not in AVAILABLE_COLORS:
            logging.error(
                "Invalid source color '%s%s%s' for '%s%s%s' in %s%s.colors%s.",
                ERR,
                source,
                RESET,
                WARN,
                color_name,
                RESET,
                INFO,
                location,
                RESET,
            )
            error_count += 1

        # validation for transformations values
        for transformation, amount in values.items():
            if transformation == "source":
                continue

            if transformation not in SUPPORTED_COLOR_TRANFORMATION:
                logging.warning(
                    "Unsupported transformation '%s%s%s' for color '%s%s%s' in %s%s%s.\n "
                    "%sSupported transformations are: %s%s%s.\n",
                    WARN,
                    transformation,
                    RESET,
                    WARN,
                    color_name,
                    RESET,
                    INFO,
                    location,
                    RESET,
                    " " * 9,  # indent for logging.warning new line
                    INFO,
                    ", ".join(SUPPORTED_COLOR_TRANFORMATION),
                    RESET,
                )
                continue

            validator = TRANSFORMATION_VALIDATORS.get(transformation)
            if not validator:
                continue  # Should be caught by the check above, but good practice.

            # Type check
            expected_type = validator["type"]
            if not isinstance(amount, expected_type):
                type_names = (
                    " or ".join(t.__name__ for t in expected_type)
                    if isinstance(expected_type, tuple)
                    else expected_type.__name__
                )
                logging.error(
                    "Invalid type for '%s%s%s' on color '%s%s%s'. Expected %s%s%s, got %s%s%s.",
                    WARN,
                    transformation,
                    RESET,
                    WARN,
                    color_name,
                    RESET,
                    INFO,
                    type_names,
                    RESET,
                    ERR,
                    type(amount).__name__,
                    RESET,
                )
                error_count += 1
                continue  # Don't range check if type is wrong

            # Range check
            min_val, max_val = validator["min"], validator["max"]
            if not (min_val <= amount <= max_val):
                if max_val == float("inf"):
                    range_str = f"greater than or equal to {min_val}"
                else:
                    range_str = f"between {min_val} and {max_val}"

                logging.error(
                    "Invalid value for '%s%s%s' on color '%s%s%s' in %s%s%s. "
                    "Expected a value %s, but got %s%s%s.",
                    WARN,
                    transformation,
                    RESET,
                    WARN,
                    color_name,
                    RESET,
                    INFO,
                    location,
                    RESET,
                    range_str,
                    ERR,
                    amount,
                    RESET,
                )
                error_count += 1

    return error_count


def validate_global_config(global_settings: dict) -> bool:
    """
    Validates the [global] configuration section.
    Returns True if valid, False otherwise.
    """
    error_count = 0
    location = "[global]"

    error_count += _validate_datatypes(global_settings, GLOBAL_SCHEMA, location)
    _warn_unsupported_options(global_settings, GLOBAL_SCHEMA, location)

    # Specific value check for 'theme-type'
    theme_type = global_settings.get("theme-type")
    if theme_type and theme_type not in SUPPORTED_THEME_TYPES:
        logging.error(
            "Invalid value for '%stheme-type%s' in %s%s%s. Got '%s%s%s', expected one of %s%s%s.",
            ERR,
            RESET,
            INFO,
            location,
            RESET,
            ERR,
            theme_type,
            RESET,
            INFO,
            ", ".join(SUPPORTED_THEME_TYPES),
            RESET,
        )
        error_count += 1

    return error_count == 0


def validate_application_config(application_config: dict) -> bool:
    """
    Validates all application sections in the configuration.
    Returns True if the configuration is valid, False otherwise.
    """
    total_errors = 0
    for app_name, options in application_config.items():
        location = f"[{app_name}]"
        app_errors = 0

        # Layer 1: Schema-driven validation
        app_errors += _validate_datatypes(options, APPLICATION_SCHEMA, location)
        app_errors += _validate_mandatory_options(options, APPLICATION_SCHEMA, location)
        _warn_unsupported_options(options, APPLICATION_SCHEMA, location)

        # Layer 2: Specialized, contextual validation
        app_errors += _validate_string_options(options, location)
        app_errors += _validate_color_format(options, location)
        app_errors += _validate_output_file(options, location)
        app_errors += _validate_template_and_syntax(options, location)
        app_errors += _validate_remap_colors(options, location)

        if app_errors > 0:
            logging.error(
                "Found %s%d error(s)%s in section %s%s%s.",
                ERR,
                app_errors,
                RESET,
                INFO,
                location,
                RESET,
            )
            total_errors += app_errors

    return total_errors == 0
