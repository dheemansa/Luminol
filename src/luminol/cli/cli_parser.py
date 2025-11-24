import argparse
from pathlib import Path
import sys

VALID_IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp")


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


def add_base_args(parser: argparse.ArgumentParser, image_required: bool = False):
    """Adds arguments related to running color extraction to the parser."""
    parser.add_argument(
        "-i",
        "--image",
        type=image_path,
        required=image_required,
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
        choices=["fast", "balanced", "high"],
        help="Adjust color extraction quality (higher is slower but more accurate).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Generate and cache palette, but do not write files or set wallpaper.",
    )
    parser.add_argument(
        "--preview",
        action="store_true",
        help="Preview the generated palette in the terminal without writing any files.",
    )


def validate_main_cli_args(parser, args):
    """Validates arguments for the main non-daemon CLI."""
    if not args.image and not args.validate:
        parser.error("--image is required unless you are using --validate.")

    image_dependent_args = {
        "--preview": args.preview,
        "--dry-run": args.dry_run,
        "--quality": args.quality,
        "--theme": args.theme,
    }

    if not args.image:
        for arg_name, arg_value in image_dependent_args.items():
            if arg_value:
                parser.error(f"{arg_name} requires --image to be specified.")


def parse_main_cli_args():
    """Parses command-line arguments for the main luminol application (lumi)."""
    parser = argparse.ArgumentParser(
        prog="lumi",
        description="A tool to generate color palettes from images and apply them to system configs.",
    )
    add_base_args(parser, image_required=False)
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable detailed logging for debugging.",
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate the configuration file and exit. All other flags are ignored, except for --verbose.",
    )

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args()
    validate_main_cli_args(parser, args)
    return args


def parse_daemon_cli_args():
    """Parses command-line arguments for the luminol daemon client (lumid)."""
    parser = argparse.ArgumentParser(
        prog="lumid",
        description="A client to control the Luminol daemon and run color extraction tasks.",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable detailed logging for debugging.",
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate the configuration file and exit. Overrides all other commands.",
    )

    # Subparsers are not required, to allow --validate to be used alone
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # run command
    run_parser = subparsers.add_parser(
        "run", help="Generate and apply a color palette from an image."
    )
    add_base_args(run_parser, image_required=True)

    # daemon control commands
    subparsers.add_parser("start", help="Start the luminol daemon.")
    subparsers.add_parser("stop", help="Stop the luminol daemon.")
    subparsers.add_parser("status", help="Check the status of the luminol daemon.")

    args = parser.parse_args()

    # If no command is given and --validate is not used, print help.
    if not args.command and not args.validate:
        parser.print_help(sys.stderr)
        sys.exit(1)

    return args
