import logging
from pathlib import Path
import time

from .cli.cli_parser import parse_arguments
from .cli.term_colors import AnsiColors
from .color.assign import assign_color
from .color.extraction import extract_colors
from .config.parser import Config, load_config
from .core.test_preset import TEST_PRESET
from .exceptions.exceptions import InvalidConfigError, WallpaperSetError
from .utils.file_io import write_file
from .utils.logging_config import configure_logging
from .utils.palette_generator import compile_color_syntax, compile_template
from .utils.path import (
    clear_directory,
    clear_old_logs,
    get_cache_dir,
    get_log_dir,
    get_luminol_dir,
)
from .utils.system_actions import apply_wallpaper, run_reload_commands

LUMINOL_CONFIG_DIR = get_luminol_dir()
LUMINOL_CACHE_DIR = get_cache_dir()


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
        logging.info("Extracting colors...")
        extract_start_time = time.perf_counter()

        colors = extract_colors(
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

    logging.info("Extracting colors...")
    color_data = extract_colors(
        image_path=image_path, num_colors=8, preset=quality_flag, sort_by="luma"
    )
    for col in color_data:
        print(col)

    assign_start_time = time.perf_counter()

    # clear cache
    clear_directory(dir_path=LUMINOL_CACHE_DIR, preserve_dir=True)
    logging.info("Old cache cleared")

    # if theme is set in cli then override the theme_type in config
    if theme_type_flag is not None:
        assign_color(color_data=color_data, theme_type=theme_type_flag)
    else:
        assign_color(
            color_data=color_data, theme_type=config.global_settings.theme_type
        )

    assign_end_time = time.perf_counter()
    logging.debug("Color assign took %s", assign_end_time - assign_start_time)

    # create palette
    enabled_apps: list = config.enabled_apps

    palette_start_time = time.perf_counter()
    for app in enabled_apps:
        app_settings = config.get_app(app)
        output_dir: Path = Path(app_settings.output_file)

        ## first save in cache: <cache_dir>/<app_name>/<file_name>
        cache_save_dir = LUMINOL_CACHE_DIR / f"{app}" / output_dir.name
        template_file_path = app_settings.template

        app_syntax: str = app_settings.syntax
        app_color_format: str = app_settings.color_format
        remap: bool = app_settings.remap_colors
        if remap:
            app_remap = app_settings.colors
        else:
            app_remap = None

        if template_file_path is None:

            palette_list: list = compile_color_syntax(
                named_colors=TEST_PRESET,
                syntax=app_syntax,
                color_format=app_color_format,
                remap=app_remap,
            )
            write_file(file_path=cache_save_dir, content=palette_list)
        else:  # template mode
            try:
                with open(template_file_path, "r", encoding="utf-8") as template_file:
                    template_file_contents = template_file.read()
            except FileNotFoundError as e:
                logging.error("Template file: %s not found", template_file_path)
                raise SystemExit(1) from e

            except Exception as e:
                logging.exception(
                    f"Unexpected error occured wile reading the template file: {template_file_path}"
                )
                raise SystemExit(1) from e

            palette_file_contents: str = compile_template(
                named_colors=TEST_PRESET,
                syntax=app_syntax,
                template=template_file_contents,
                remap=app_remap,
                color_format=app_color_format,
            )

            write_file(file_path=cache_save_dir, content=palette_file_contents)

    palette_end_time = time.perf_counter()
    logging.info("Palette export took %s", palette_end_time - palette_start_time)

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

    clear_old_logs()


if __name__ == "__main__":
    main()
