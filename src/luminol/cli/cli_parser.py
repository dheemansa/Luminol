import argparse
from pathlib import Path


##TODO validate image using imghdr for corrupt files
def image_path(path: str) -> Path:
    """Custom type for argparse to validate an image path."""
    VALID_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp"}

    ##  TODO REFACTOR: do we really need resolve
    ##  NOTE: shell automatically converts relative path and pass to the tool
    absolute_path = Path(path).resolve()
    if not absolute_path.is_file():
        raise argparse.ArgumentTypeError(f"File not found: {absolute_path}")

    if absolute_path.suffix.lower() not in VALID_IMAGE_EXTENSIONS:
        raise argparse.ArgumentTypeError(
            f"Unsupported image type: {absolute_path.suffix}\n"
            f"(Supported types: {', '.join(VALID_IMAGE_EXTENSIONS)})"
        )

    return absolute_path


def parse_arguments():
    """Parses command-line arguments for the luminol application."""
    parser = argparse.ArgumentParser(
        prog="luminol",
        description="A tool to generate color palettes from images and apply them to system configs.",
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
        choices=["dark", "light"],
        help="Force a specific theme type, overriding the value in the config file.",
    )
    parser.add_argument(
        "-q",
        "--quality",
        choices=["fast", "balanced", "high"],
        default="balanced",
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
        help="Generate colors but do not write them to their final destination files.",
    )

    parser.add_argument(
        "--preview",
        action="store_true",
        help="Preview the generated palette in the terminal without writing any files.",
    )

    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate the configuration file and exit. All other flags are ignored, except for --verbose.",
    )

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
