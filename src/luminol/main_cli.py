import time

import_start_time = time.perf_counter()
import logging
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
from .color.assign import decide_theme

import_end_time = time.perf_counter()
print(f"Import Time {import_end_time - import_start_time}")

# TODO later use Luminol package to create the cli


def main():
    """Main entry point for the Luminol application."""

    args = parse_arguments()

    # if args.verbvose is true, then enable verbose logging
    configure_logging(verbose=args.verbose)

    verbose_flag: bool = args.verbose
    image_path: str = args.image
    theme_type_flag: str = args.theme
    quality_flag: str = args.quality
    preview_flag: bool = args.preview
    validate_flag: bool = args.validate
    dry_run_flag: bool = args.dry_run

    if preview_flag is True:
        extract_start_time = time.perf_counter()

        raw_colors = get_colors(
            image_path=image_path, num_colors=8, preset=quality_flag
        )

        for col in raw_colors:
            r, g, b = col
            ansi_color = AnsiColors.bg_rgb(r, g, b)
            print(f"{ansi_color}rgb{col}{AnsiColors.RESET}")

        extract_end_time = time.perf_counter()

        logging.info(f"Color Extraction took {extract_end_time - extract_start_time}")

        return

    config_load_start_time = time.perf_counter()
    default_paths = LuminolPath()

    try:
        raw_config = load_config(config_file_path=default_paths.config_file_path)
        global_config = LuminolConfigGlobal(raw_config)
        app_config = LuminolConfigApplication(raw_config)

    except (FileNotFoundError, SystemExit) as e:
        logging.critical(f"Failed to load configuration: {e}")
        return
    config_load_end_time = time.perf_counter()

    logging.info(f"Config load took {config_load_end_time - config_load_start_time}")

    # Validate Global
    # initialise both as true
    is_global_valid = True
    is_app_config_valid = True

    validation_start_time = time.perf_counter()
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

    validation_end_time = time.perf_counter()

    logging.info(f"Validation took {validation_end_time - validation_start_time}")

    # if any one of these if false(i.e config invalid) then terminate the program
    if not (is_app_config_valid or is_global_valid):
        return

    # if validation_flag is true then stop the program just after validation
    if validate_flag is True:
        logging.warning("Configuration validation successful.")
        return

    if global_config.log_output is True:
        log_dir = default_paths.cache_path / "logs"
    else:
        log_dir = None

    # if wallpaper-command is not set then skip execution of wallpaper command
    if global_config.wallpaper_command:
        try:
            apply_wallpaper(
                wallpaper_set_command=global_config.wallpaper_command,
                image_path=image_path,
                log_dir=log_dir,
            )
        except Exception as e:
            logging.error(e)
            return

    extract_start_time = time.perf_counter()
    raw_colors = get_colors(image_path=image_path, num_colors=8, preset=quality_flag)
    print(decide_theme(raw_colors))
    extract_end_time = time.perf_counter()
    logging.info(f"Color Extraction took {extract_end_time - extract_start_time}")

    sorted_color = sorted(raw_colors.items(), key=lambda item: item[1]["luma"])
    sorted_color = [item[0] for item in sorted_color]
    for col in sorted_color:
        r, g, b = col
        ansi_color = AnsiColors.bg_rgb(r, g, b)
        print(
            f"{ansi_color}rgb{col}{AnsiColors.RESET} Coverage {raw_colors[col]['coverage']} luma {raw_colors[col]['luma']:.2f}"
        )

    # NOTE: this will be the last step
    # if reload-command is not set then skip execution of reload command
    if global_config.reload_commands:
        try:
            run_reload_commands(
                reload_commands=global_config.reload_commands,
                use_shell=global_config.use_shell,
                log_dir=log_dir,
            )

        except Exception as e:
            logging.error(e)
            return

    print("TODO: Main logic - generate colors, write files, run reload commands.")
