class AnsiColors:
    RESET = "\033[0m"
    BOLD = "\033[1m"

    @staticmethod
    def rgb_to_ansi(r: int, g: int, b: int) -> str:
        """Return ANSI escape for given RGB color (foreground)."""
        return f"\033[38;2;{r};{g};{b}m"

    @staticmethod
    def bg_rgb(r: int, g: int, b: int) -> str:
        """Return ANSI escape for given RGB color (background)."""
        return f"\033[48;2;{r};{g};{b}m"

    # Named colors
    INFO = rgb_to_ansi(114, 135, 253)  # soft blue
    WARNING = rgb_to_ansi(238, 212, 159)  # golden yellow
    ERROR = rgb_to_ansi(238, 17, 65)  # light red

    SUCCESS = rgb_to_ansi(64, 160, 43)  # bright green
    DEBUG = rgb_to_ansi(240, 198, 198)  # light violet-blue

    @classmethod
    def colorize(cls, text: str, color: str, bold: bool = False) -> str:
        """Wrap text with color (and optional bold)."""
        style = cls.BOLD if bold else ""
        return f"{style}{color}{text}{cls.RESET}"


if __name__ == "__main__":
    print(AnsiColors.colorize("This is info", AnsiColors.INFO))
    print(AnsiColors.colorize("This is a warning!", AnsiColors.WARNING))
    print(AnsiColors.colorize("This is an error message", AnsiColors.ERROR))
    print(AnsiColors.colorize("This is a success message", AnsiColors.SUCCESS))
    print(AnsiColors.colorize("This is a debug message", AnsiColors.DEBUG))
    # example use of f string
    hello = "Hello sir"
    print(AnsiColors.colorize(f"{hello}", AnsiColors.INFO))
