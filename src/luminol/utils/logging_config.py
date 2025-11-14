import logging
from ..cli.term_colors import AnsiColors


def configure_logging(verbose: bool):
    logging_level = logging.DEBUG if verbose else logging.INFO

    logging.addLevelName(logging.DEBUG, f"{AnsiColors.DEBUG}DEBUG{AnsiColors.RESET}")
    logging.addLevelName(logging.INFO, f"{AnsiColors.INFO}INFO{AnsiColors.RESET}")
    logging.addLevelName(
        logging.WARNING, f"{AnsiColors.WARNING}WARNING{AnsiColors.RESET}"
    )
    logging.addLevelName(logging.ERROR, f"{AnsiColors.ERROR}ERROR{AnsiColors.RESET}")
    logging.addLevelName(
        logging.CRITICAL,
        f"{AnsiColors.BOLD}{AnsiColors.ERROR}CRITICAL{AnsiColors.RESET}",
    )
    logging.basicConfig(level=logging_level, format="[%(levelname)s] %(message)s")
