class AnsiColors:
    """
    ANSI color codes and utilities for terminal output formatting.

    Provides RGB color support, predefined semantic colors (INFO, WARNING, ERROR, etc.),
    and utilities for colorizing text in terminal output.

    Attributes:
        RESET: Reset all formatting
        BOLD: Bold text style
        INFO: Soft blue color for informational messages
        WARNING: Golden yellow color for warnings
        ERROR: Light red color for error messages
        SUCCESS: Bright green color for success messages
        DEBUG: Light violet-blue color for debug messages

    Examples:
        Basic color usage:
            >>> print(f"{AnsiColors.INFO}Info message{AnsiColors.RESET}")
            Info message  # (displayed in blue)

        Using colorize method:
            >>> colored_text = AnsiColors.colorize("Warning!", AnsiColors.WARNING)
            >>> print(colored_text)
            Warning!  # (displayed in yellow)

        Bold colored text:
            >>> error = AnsiColors.colorize("Error!", AnsiColors.ERROR, bold=True)
            >>> print(error)
            Error!  # (displayed in bold red)

        Custom RGB colors:
            >>> custom = AnsiColors.rgb_to_ansi(255, 100, 200)
            >>> print(f"{custom}Custom pink text{AnsiColors.RESET}")
            Custom pink text  # (displayed in pink)

        Background colors:
            >>> bg = AnsiColors.bg_rgb(50, 50, 50)
            >>> print(f"{bg}Dark background{AnsiColors.RESET}")
            Dark background  # (displayed with dark gray background)
    """

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

    SUCCESS = rgb_to_ansi(125, 227, 70)  # bright green
    DEBUG = rgb_to_ansi(240, 198, 198)  # light violet-blue

    @classmethod
    def colorize(cls, text: str, color: str, bold: bool = False) -> str:
        """Wrap text with color (and optional bold)."""
        style = cls.BOLD if bold else ""
        return f"{style}{color}{text}{cls.RESET}"
