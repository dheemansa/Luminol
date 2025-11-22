import argparse
from pathlib import Path
import sys

VALID_IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp")


##TODO validate image using imghdr for corrupt files
def image_path(path: str) -> Path:
    """Custom type for argparse to validate an image path."""

    # .resolve() to handel symlinks.
    absolute_path = Path(path).resolve()
    if not absolute_path.is_file():
        raise argparse.ArgumentTypeError(f"File not found: {absolute_path}")

    if absolute_path.suffix.lower() not in VALID_IMAGE_EXTENSIONS:
        raise argparse.ArgumentTypeError(
            f"\nUnsupported image type: {absolute_path.suffix}\n"
            f"(Supported types: {', '.join(VALID_IMAGE_EXTENSIONS)})"
        )

    return absolute_path


def parse_arguments():
    """Parses command-line arguments for the luminol application."""
    parser = argparse.ArgumentParser(
        prog="luminol",
        description="A tool to generate color palettes \
        from images and apply them to system configs.",
    )

    parser.add_argument(
        "-i",
        "--image",
        type=image_path,
        help="Path to the image file to generate colors from.",
    )
    parser.add_argument(
        "-t",
        "--theme",
        choices=["dark", "auto", "light"],
        help="Force a specific theme type, overriding the value in the config file.",
    )
    parser.add_argument(
        "-q",
        "--quality",
        # default="balanced",
        # NOTE:The quality flag default is not set here to avoid
        # argparse treating it as user-provided.
        # This prevents commands unrelated to image processing (like --validate) from
        # incorrectly triggering dependency errors due to an implicit "balanced" default.
        # Instead, the default is applied later in main() after parsing.
        choices=["fast", "balanced", "high"],
        help="Adjust color extraction quality (higher is slower but more accurate).",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable detailed logging for debugging.",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Generate colors and palettes. \
        The generated palette is saved to cache, but it is not written to its final destination files,\
        wallpaper is not set, and reload commands are not executed.",
    )

    parser.add_argument(
        "--preview",
        action="store_true",
        help="Preview the generated palette in the terminal without writing any files.",
    )

    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate the configuration file and exit.\
        All other flags are ignored, except for --verbose.",
    )

    # show help if no arguments are passed
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args()

    image_dependent_args = {
        "--preview": args.preview,
        "--dry-run": args.dry_run,
        "--quality": args.quality,
        "--theme": args.theme,
    }

    for arg_name, arg_value in image_dependent_args.items():
        if arg_value and not args.image:
            parser.error(f"{arg_name} requires --image to be specified.")

    return args
