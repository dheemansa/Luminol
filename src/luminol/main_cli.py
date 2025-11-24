from .utils.logging_config import configure_logging
from .core.engine import run_luminol
from .cli.cli_parser import parse_main_cli_args


def main():
    """Main entry point for the Luminol application."""

    args = parse_main_cli_args()

    # if args.verbvose is true, then enable verbose logging
    configure_logging(verbose=args.verbose)

    # verbose_flag: bool = args.verbose
    image_path: str = args.image
    theme_type: str | None = args.theme
    quality: str | None = args.quality
    preview_only: bool = args.preview
    validate_only: bool = args.validate
    dry_run_only: bool = args.dry_run

    run_luminol(
        image_path, theme_type, quality, preview_only, validate_only, dry_run_only
    )


if __name__ == "__main__":
    main()
