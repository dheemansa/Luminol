import logging
from ..cli.term_colors import AnsiColors

ERR = AnsiColors.ERROR
RESET = AnsiColors.RESET
INFO = AnsiColors.INFO
WARN = AnsiColors.WARNING
DEBUG = AnsiColors.DEBUG
BOLD = AnsiColors.BOLD


def configure_logging(verbose: bool):
    logging_level = logging.DEBUG if verbose else logging.INFO

    logging.addLevelName(logging.DEBUG, f"{DEBUG}DEBUG{RESET}")
    logging.addLevelName(logging.INFO, f"{INFO}INFO{RESET}")
    logging.addLevelName(logging.WARNING, f"{WARN}WARNING{RESET}")
    logging.addLevelName(logging.ERROR, f"{ERR}ERROR{RESET}")
    logging.addLevelName(
        logging.CRITICAL,
        f"{BOLD}{ERR}CRITICAL{RESET}",
    )

    if verbose:
        logging_format = f"[%(levelname)s] [Module: {INFO}%(module)s{RESET} Func: {INFO}%(funcName)s{RESET}]\n%(message)s\n"
    else:
        logging_format = "[%(levelname)s] %(message)s"

    logging.basicConfig(level=logging_level, format=logging_format, force=True)
