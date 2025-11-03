import logging
import time
from .utils.logging_config import configure_logging
from .cli.cli_parser import parse_arguments
from .config.parser import (
    LuminolConfigGlobal,
    LuminolConfigApplication,
    load_config,
)
from .cli.term_colors import AnsiColors
from .color.extraction import (
    get_colors,
)
from .utils.path import LuminolPath
from .core.system_actions import apply_wallpaper, run_reload_commands
from .exceptions.exceptions import WallpaperSetError


# TODO later use Luminol package to create the cli


def main():
    """Main entry point for the Luminol application."""

    args = parse_arguments()

    # if args.verbvose is true, then enable verbose logging
    configure_logging(verbose=args.verbose)

    # verbose_flag: bool = args.verbose
    image_path: str = args.image
    theme_type_flag: str = args.theme
    quality_flag: str = args.quality
    preview_flag: bool = args.preview
    validate_flag: bool = args.validate
    dry_run_flag: bool = args.dry_run

    if preview_flag is True:
        extract_start_time = time.time()

        raw_colors = get_colors(
            image_path=image_path, num_colors=8, preset=quality_flag
        )

        for col in raw_colors:
            r, g, b = col
            ansi_color = AnsiColors.bg_rgb(r, g, b)
            print(f"{ansi_color}rgb{col}{AnsiColors.RESET}")

        extract_end_time = time.time()

        logging.info(f"Color Extraction took {extract_end_time - extract_start_time}")

        return

    default_paths = LuminolPath()

    try:
        raw_config = load_config(config_file_path=default_paths.config_file_path)
        global_config = LuminolConfigGlobal(raw_config)
        app_config = LuminolConfigApplication(raw_config)

    except (FileNotFoundError, SystemExit) as e:
        logging.critical(f"Failed to load configuration: {e}")
        return

    # Validate Global
    # initialise both as true
    is_global_valid = True
    is_app_config_valid = True

    try:
        global_config.validate()
    except Exception as e:
        # if any exception is raised then the global config is invalid
        is_global_valid = False
        logging.error(e)
    try:
        app_config.validate()
    except Exception as e:
        # if any exception is raised then the application config is invalid
        is_app_config_valid = False
        logging.error(e)

    # if any one of these if false(i.e config invalid) then terminate the program
    # TODO make sure to uncomment this after testing
    # if is_app_config_valid or is_global_valid:
    #     return

    # if validation_flag is true then stop the program just after validation
    if validate_flag is True:
        logging.warning("Configuration validation successful.")
        return

    try:
        apply_wallpaper(global_config.wallpaper_commands, image_path)
    except Exception as e:
        logging.error(e)
        return

    # NOTE: this will be the last step
    try:
        run_reload_commands(global_config.reload_commands)

    except Exception as e:
        logging.error(e)
        return

    print("TODO: Main logic - generate colors, write files, run reload commands.")


if __name__ == "__main__":
    main()
