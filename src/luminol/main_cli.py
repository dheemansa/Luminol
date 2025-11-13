import time
import logging
from .exceptions.exceptions import InvalidConfigError
from .cli.term_colors import AnsiColors
from .utils.logging_config import configure_logging
from .cli.cli_parser import parse_arguments
from .config.parser import Config, load_config
from .color.extraction import get_colors
from .utils.path import get_cache_dir, get_luminol_dir, clear_directory
from .core.system_actions import apply_wallpaper, run_reload_commands
from .color.assign import assign_color


# TODO later use Luminol package to create the cli


def main():
    """Main entry point for the Luminol application."""

    args = parse_arguments()

    # if args.verbvose is true, then enable verbose logging
    configure_logging(verbose=args.verbose)

    # verbose_flag: bool = args.verbose
    image_path: str = args.image
    theme_type_flag: str | None = args.theme
    quality_flag: str | None = args.quality
    preview_flag: bool = args.preview
    validate_flag: bool = args.validate
    dry_run_flag: bool = args.dry_run

    # NOTE: The quality flag is handled manually instead of setting a default in argparse.
    # This ensures that commands unrelated to image processing (like --validate)
    # don’t incorrectly trigger validation errors due to an implicit "balanced" default.

    if quality_flag is None:
        quality_flag = "balanced"

    if preview_flag is True:
        extract_start_time = time.perf_counter()

        raw_colors = get_colors(
            image_path=image_path, num_colors=8, preset=quality_flag
        )

        for col in raw_colors:
            print(col)

        extract_end_time = time.perf_counter()

        logging.info(f"Color Extraction took {extract_end_time - extract_start_time}")

        raise SystemExit(0)

    LUMINOL_CONFIG_DIR = get_luminol_dir()
    LUMINOL_CACHE_DIR = get_cache_dir()

    try:
        raw_config = load_config(config_file_path=LUMINOL_CONFIG_DIR / "config.toml")
        config = Config(config_data=raw_config)
    except InvalidConfigError as e:
        print(f"\n{e}")
        raise SystemExit(1)

    except Exception as e:
        logging.error(f"Failed to load configuration: {e}")
        raise SystemExit(1)  # exit with exit code 1

    # if validation_flag is true then stop the program just after validation
    if validate_flag is True:
        print(
            f"{AnsiColors.SUCCESS}✓ Configuration validation successful.{AnsiColors.RESET}"
        )
        raise SystemExit(0)

    if config.global_settings.log_output is True:
        log_dir = LUMINOL_CACHE_DIR / "logs"
    else:
        log_dir = None

    # if wallpaper-command is not set then skip execution of wallpaper command
    if config.global_settings.wallpaper_command:
        try:
            apply_wallpaper(
                wallpaper_set_command=config.global_settings.wallpaper_command,
                image_path=image_path,
                log_dir=log_dir,
            )
        except Exception as e:
            logging.error(e)
            return

    extract_start_time = time.perf_counter()

    color_data = get_colors(
        image_path=image_path, num_colors=8, preset=quality_flag, sort_by="luma"
    )

    for color in color_data:
        print(color)

    extract_end_time = time.perf_counter()
    print(f"Color Extraction took {extract_end_time - extract_start_time}")

    assign_start_time = time.perf_counter()

    # clear cache
    clear_directory(dir_path=LUMINOL_CACHE_DIR, recreate=True)

    # if theme is set in cli then override the theme_type in config
    if theme_type_flag is not None:
        assign_color(color_data=color_data, theme_type=theme_type_flag)
    else:
        assign_color(
            color_data=color_data, theme_type=config.global_settings.theme_type
        )

    assign_end_time = time.perf_counter()
    logging.warning(f"Color assign took {assign_end_time - assign_start_time}")

    # TODO: create and save palette files to cache and use dry_run_flag and then copy files to specified directory
    # TODO: also make a tty reload similar to pywall and also implement a config setting in config.toml to enable/disable tty-reload=false

    # NOTE: this will be the last step
    # if reload-command is not set then skip execution of reload command
    if config.global_settings.reload_commands:
        try:
            run_reload_commands(
                reload_commands=config.global_settings.reload_commands,
                use_shell=config.global_settings.use_shell,
                log_dir=log_dir,
            )

        except Exception as e:
            logging.error(e)
            return


if __name__ == "__main__":
    main()
