from .cli.term_colors import AnsiColors

ERR = AnsiColors.ERROR
RESET = AnsiColors.RESET


class InvalidConfigError(Exception):
    """Raised when the config is not valid"""

    def __init__(self, message: str) -> None:
        self.message = f"{ERR}{message}{RESET}"
        super().__init__(self.message)


class WallpaperSetError(Exception):
    """Raised when wallpaper command execution failed"""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)
