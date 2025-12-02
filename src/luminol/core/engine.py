import logging
from pathlib import Path
import shutil
import time

from ..cli.term_colors import AnsiColors, tty_color_sequence, preview_theme
from ..utils.logging_config import configure_logging
from ..color.color_assign import assign_color
from ..color.extraction import extract_colors
from ..config.parser import Config, load_config
from ..exceptions import InvalidConfigError, WallpaperSetError
from ..utils.file_io import write_file
from ..utils.palette_generator import compile_color_syntax, compile_template
from ..utils.path_utils import (
    clear_directory,
    clear_old_logs,
    get_cache_dir,
    get_log_dir,
    get_luminol_dir,
)
from ..utils.system_actions import apply_wallpaper, run_reload_commands

LUMINOL_CONFIG_DIR = get_luminol_dir()
LUMINOL_CACHE_DIR = get_cache_dir()


def handle_preview_mode(image_path: str | Path, quality: str):
    logging.info("Extracting colors...")
    start = time.perf_counter()

    colors = extract_colors(
        image_path=str(image_path),
        num_colors=8,
        preset=quality,
        sort_by="luma",
    )

    print("Extracted Colors:")
    for col in colors:
        print(col.rgb, end=" ", flush=True)

        logging.debug(
            "Coverage: %5.3f H: %6.2f  S: %4.2f  V: %4.2f",
            col.coverage,
            col.rgb.hsv.h * 360,
            col.rgb.hsv.s,
            col.rgb.hsv.v,
        )

    print("\n")
    end = time.perf_counter()
    logging.info("Color Extraction took %.4f seconds", end - start)


def generate_palette_files(config: Config, color_palette: dict):
    enabled_apps = config.enabled_apps

    for app in enabled_apps:
        app_settings = config.get_app(app)
        output_dir = Path(app_settings.output_file)
        cache_path = LUMINOL_CACHE_DIR / f"{app}" / output_dir.name

        syntax = app_settings.syntax
        fmt = app_settings.color_format
        remap = app_settings.colors if app_settings.remap_colors else None

        template_path = app_settings.template
        if not template_path:
            palette = compile_color_syntax(
                named_colors=color_palette,
                syntax=syntax,
                color_format=fmt,
                remap=remap,
            )
            write_file(cache_path, palette)
            continue

        # template mode
        try:
            text = Path(template_path).read_text(encoding="utf-8")
        except FileNotFoundError:
            logging.error("Template not found: %s", template_path)
            raise SystemExit(1)

        except Exception:
            logging.exception("Template read error")
            raise SystemExit(1)

        rendered = compile_template(
            named_colors=color_palette,
            syntax=syntax,
            template=text,
            remap=remap,
            color_format=fmt,
        )
        write_file(cache_path, rendered)


def export_palettes(config: Config):
    for app in config.enabled_apps:
        app_settings = config.get_app(app)
        destination = Path(app_settings.output_file)
        source = LUMINOL_CACHE_DIR / f"{app}" / destination.name

        try:
            shutil.copy(src=source, dst=destination)
        except FileNotFoundError:
            logging.exception("Destination not found: '%s'. Cannot export '%s'.", destination, app)
        except Exception:
            logging.exception("Failed to copy '%s' to '%s'", source, destination)


def set_wallpaper(config: Config, image_path: str | Path, log_dir: None | str | Path):
    cmd: str = config.global_settings.wallpaper_command
    if cmd:
        try:
            apply_wallpaper(
                wallpaper_set_command=cmd,
                image_path=image_path,
                log_dir=log_dir,
            )
        except WallpaperSetError:
            logging.exception("Wallpaper command: '%s' failed", cmd)
            raise SystemExit(1)

        except Exception:
            logging.exception("Unexpected error occurred while setting wallpaper.")
            raise SystemExit(1)


def reload_commands(config: Config, log_dir: Path | str | None):
    cmd_list: list = config.global_settings.reload_commands
    if cmd_list:
        try:
            run_reload_commands(
                reload_commands=cmd_list,
                use_shell=config.global_settings.use_shell,
                log_dir=log_dir,
            )

        except Exception:
            logging.exception("Unexpected error occurred while reloading.")
            raise SystemExit(1)


def run_luminol(
    image_path: str | Path,
    theme_type: str | None,
    quality: str | None,
    preview_only: bool,
    validate_only: bool,
    dry_run_only: bool,
    verbose: bool = False,
):
    configure_logging(verbose)
    # NOTE: The quality flag is handled manually instead of setting a default in argparse.
    # This ensures that commands unrelated to image processing (like --validate)
    # don’t incorrectly trigger validation errors due to an implicit "balanced" default.
    if quality is None:
        quality = "balanced"

    if preview_only is True:
        handle_preview_mode(image_path=image_path, quality=quality)
        raise SystemExit(0)

    try:
        raw_config = load_config(config_file_path=LUMINOL_CONFIG_DIR / "config.toml")
        config = Config(config_data=raw_config)
    except InvalidConfigError as e:
        print(f"\n{e}")
        raise SystemExit(1) from e

    except Exception as e:
        logging.exception("Failed to load configuration")
        raise SystemExit(1) from e  # exit with exit code 1

    # if validation_flag is true then stop the program just after validation
    if validate_only is True:
        logging.info(
            "%s✓ Configuration validation successful.%s",
            AnsiColors.SUCCESS,
            AnsiColors.RESET,
        )
        raise SystemExit(0)

    if config.global_settings.log_output is True:
        log_dir = get_log_dir()
    else:
        log_dir = None

    if not dry_run_only:
        # if wallpaper-command is not set then skip execution of wallpaper command
        set_wallpaper(config=config, image_path=image_path, log_dir=log_dir)

    logging.info("Extracting colors...")
    extract_start = time.perf_counter()
    color_data = extract_colors(image_path=image_path, num_colors=8, preset=quality, sort_by="luma")
    if verbose:
        for col in color_data:
            logging.debug(
                "%s H: %6.2f S: %4.2f V: %4.2f",
                col,
                col.rgb.hsv.h * 360,
                col.rgb.hsv.s,
                col.rgb.hsv.v,
            )

    extract_end = time.perf_counter()
    logging.debug("Extraction took: %s", extract_end - extract_start)

    assign_start_time = time.perf_counter()

    # clear cache
    clear_directory(dir_path=LUMINOL_CACHE_DIR, preserve_dir=True)
    logging.info("Old cache cleared")

    # if theme is set in cli then override the theme_type in config
    if theme_type is not None:
        color_palette = assign_color(
            color_data=color_data,
            theme_type=theme_type,
            presorted=True,
        )
    else:
        color_palette = assign_color(
            color_data=color_data,
            theme_type=config.global_settings.theme_type,
            presorted=True,
        )

    preview_theme(color_palette)
    assign_end_time = time.perf_counter()
    logging.debug("Color assign took %s", assign_end_time - assign_start_time)

    # generate palette files
    palette_start_time = time.perf_counter()

    generate_palette_files(config=config, color_palette=color_palette)

    if dry_run_only is True:
        # when dry_run is enabled
        # terminate just after palette_files are saved to cache
        palette_end_time = time.perf_counter()
        logging.info("Palette creation took %s", palette_end_time - palette_start_time)
        raise SystemExit(0)

    ## final export to output_dir
    export_palettes(config=config)

    palette_end_time = time.perf_counter()
    logging.info("Palette creation and export took %s", palette_end_time - palette_start_time)

    # TODO: also make a tty reload similar to pywall
    print(tty_color_sequence(color_palette), end="")
    reload_commands(config=config, log_dir=log_dir)

    if log_dir:
        clear_old_logs()
