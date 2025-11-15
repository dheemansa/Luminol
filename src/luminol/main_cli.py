import logging
from pathlib import Path
import time

from .cli.cli_parser import parse_arguments
from .cli.term_colors import AnsiColors
from .color.assign import assign_color
from .color.extraction import get_colors
from .config.parser import Config, load_config
from .core.constants import TEST_PRESET  # TODO: remove this after testing
from .utils.system_actions import apply_wallpaper, run_reload_commands
from .exceptions.exceptions import InvalidConfigError, WallpaperSetError
from .utils.logging_config import configure_logging
from .utils.palette_generator import compile_color_syntax
from .utils.file_io import write_file
from .utils.path import (
    clear_directory,
    clear_old_logs,
    get_cache_dir,
    get_log_dir,
    get_luminol_dir,
)

# TODO later use Luminol package to create the cli

LUMINOL_CONFIG_DIR = get_luminol_dir()
LUMINOL_CACHE_DIR = get_cache_dir()


def main():
    """Main entry point for the Luminol application."""

    args = parse_arguments()

    # if args.verbvose is true, then enable verbose logging
    configure_logging(verbose=args.verbose)

    # Clean up old log files before this run
    clear_old_logs()

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
        logging.info("Extracting colors...")
        extract_start_time = time.perf_counter()

        colors = get_colors(
            image_path=str(image_path),
            num_colors=8,
            preset=quality_flag,
            sort_by="luma",
        )

        for color in colors:
            print(color.rgb)

        extract_end_time = time.perf_counter()
        duration = extract_end_time - extract_start_time
        logging.info("Color Extraction took %.4f seconds", duration)
        raise SystemExit(0)

    try:
        raw_config = load_config(config_file_path=LUMINOL_CONFIG_DIR / "config.toml")
        config = Config(config_data=raw_config)
    except InvalidConfigError as e:
        print(f"\n{e}")
        raise SystemExit(1) from e

    except Exception as e:
        logging.error("Failed to load configuration: %s", e)
        raise SystemExit(1) from e  # exit with exit code 1

    # if validation_flag is true then stop the program just after validation
    if validate_flag is True:
        print(
            f"{AnsiColors.SUCCESS}✓ Configuration validation successful.{AnsiColors.RESET}"
        )
        raise SystemExit(0)

    if config.global_settings.log_output is True:
        log_dir = get_log_dir()
    else:
        log_dir = None

    if dry_run_flag is False:
        # if wallpaper-command is not set then skip execution of wallpaper command
        if config.global_settings.wallpaper_command:
            try:
                apply_wallpaper(
                    wallpaper_set_command=config.global_settings.wallpaper_command,
                    image_path=image_path,
                    log_dir=log_dir,
                )
            except WallpaperSetError as e:
                logging.error(e)
                raise SystemExit(1) from e

            except Exception as e:
                logging.error(e)
                raise SystemExit(1) from e

    color_data = get_colors(
        image_path=image_path, num_colors=8, preset=quality_flag, sort_by="luma"
    )
    for col in color_data:
        print(col)

    assign_start_time = time.perf_counter()

    # clear cache
    clear_directory(dir_path=LUMINOL_CACHE_DIR, preserve_dir=True)
    logging.info("Cache Cleared")

    # if theme is set in cli then override the theme_type in config
    if theme_type_flag is not None:
        assign_color(color_data=color_data, theme_type=theme_type_flag)
    else:
        assign_color(
            color_data=color_data, theme_type=config.global_settings.theme_type
        )

    assign_end_time = time.perf_counter()
    logging.info("Color assign took %s", assign_end_time - assign_start_time)

    # create palette
    enabled_apps: list = config.enabled_apps

    for app in enabled_apps:
        app_settings = config.get_app(app)
        output_dir: Path = Path(app_settings.output_file)

        ## first save in cache: <cache_dir>/<app_name>/<file_name>
        cache_save_dir = LUMINOL_CACHE_DIR / f"{app}" / output_dir.name
        if not app_settings.template:
            app_syntax: str = app_settings.syntax
            app_color_format: str = app_settings.color_format
            remap: bool = app_settings.remap_colors
            if remap:
                app_remap = app_settings.colors
            else:
                app_remap = None

            palette_list: list = compile_color_syntax(
                named_colors=TEST_PRESET,
                syntax=app_syntax,
                color_format=app_color_format,
                remap=app_remap,
            )
            write_file(file_path=cache_save_dir, content=palette_list)

    # TODO: also make a tty reload similar to pywall

    if dry_run_flag is False:
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
                logging.exception(e)
                raise SystemExit(1) from e


if __name__ == "__main__":
    main()
