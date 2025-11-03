import tomllib
import logging
from typing import Any
from .validate import validate_application_config, validate_global_config
from ..cli.term_colors import AnsiColors
from ..exceptions.exceptions import InvalidConfigError
from pathlib import Path


def load_config(config_file_path: str | Path) -> dict:
    """Load the TOML configuration file as dict"""

    try:
        with open(config_file_path, "rb") as config:
            config_toml_data: dict = tomllib.load(config)
            logging.info("Config File Loaded")

        return config_toml_data

    except tomllib.TOMLDecodeError as e:
        logging.error("Invalid TOML syntax in config: %s", e)
        raise SystemExit(1)  # exit gracefully

    except OSError as e:
        logging.error("Cannot read config file %s: %s", config_file_path, e)
        raise SystemExit(1)

    except Exception as e:
        raise


class LuminolConfigGlobal:
    global_config = {}

    def __init__(self, config: dict[str, Any], validate: bool = True):
        self.global_config: dict = config.get("global", {})

        self.wallpaper_commands: str = self.global_config.get("wallpaper-command", "")
        self.reload_commands: list = self.global_config.get("reload-commands", [])
        self.theme_type: str = self.global_config.get("theme-type", "auto")

    def validate(self):
        valid: bool = validate_global_config(self.global_config)

        if not valid:
            raise InvalidConfigError(
                "Invalid global configuration. Please review the errors above."
            )
            # raise SystemExit(
            #     AnsiColors.colorize(
            #         "Invalid global configuration. Please review the errors above.",
            #         AnsiColors.ERROR,
            #     )
            # )


class LuminolConfigApplication:
    def __init__(self, config: dict[str, Any], validate: bool = True):
        self.app_config: dict = {
            key: value
            for key, value in config.items()
            if key != "global" and value.get("enabled", False)
        }

        self.app_list: list[str] = list(self.app_config)

    def validate(self) -> None:
        valid = validate_application_config(self.app_config)
        if not valid:
            raise InvalidConfigError(
                "Invalid application configuration. Please review the errors above."
            )
            # raise SystemExit(
            #     AnsiColors.colorize(
            #         "Invalid application configuration. Please review the errors above.",
            #         AnsiColors.ERROR,
            #     )
            # )
