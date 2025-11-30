"""
This module provides utilities for displaying colors and themes in a terminal,
including 24-bit color support and standard ANSI escape codes.
"""

from typing import Any


class AnsiColors:
    """
    A utility class for terminal color and style escape codes.

    Provides standard ANSI codes for semantic colors (e.g., INFO, WARNING),
    allowing them to adapt to the user's terminal theme. Also includes
    methods for full 24-bit RGB color conversion.
    """

    RESET = "\033[0m"
    BOLD = "\033[1m"

    # Standard ANSI escape codes (bright variants for visibility)
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    GRAY = "\033[90m"

    INFO = BLUE
    WARNING = YELLOW
    ERROR = RED
    SUCCESS = GREEN
    DEBUG = GRAY

    @staticmethod
    def rgb_to_ansi(r: int, g: int, b: int) -> str:
        """Returns the escape sequence for a 24-bit RGB foreground color."""
        return f"\033[38;2;{r};{g};{b}m"

    @staticmethod
    def bg_rgb(r: int, g: int, b: int) -> str:
        """Returns the escape sequence for a 24-bit RGB background color."""
        return f"\033[48;2;{r};{g};{b}m"

    @classmethod
    def colorize(cls, text: str, color: str, bold: bool = False) -> str:
        """Wraps text with a color and optional bold style."""
        style = cls.BOLD if bold else ""
        return f"{style}{color}{text}{cls.RESET}"


def tty_color_sequence(theme: dict[str, Any]) -> str:
    """
    Generates a string of OSC escape sequences to theme a terminal.

    Args:
        theme: A dictionary mapping color names to RGB objects.

    Returns:
        A single string containing all necessary OSC escape codes.
    """
    sequence = ""

    def rgb_to_hex_format(rgb: Any) -> str:
        """Convert RGB to terminal hex format (RR/GG/BB)."""
        return f"{rgb.r:02x}/{rgb.g:02x}/{rgb.b:02x}"

    # Set background color (OSC 11)
    if "bg-primary" in theme:
        bg = theme["bg-primary"]
        bg_hex = rgb_to_hex_format(bg)
        sequence += f"\033]11;rgb:{bg_hex}\007"

    # Set foreground/text color (OSC 10)
    if "text-primary" in theme:
        fg = theme["text-primary"]
        fg_hex = rgb_to_hex_format(fg)
        sequence += f"\033]10;rgb:{fg_hex}\007"

    # Set cursor color (OSC 12) - same as foreground
    if "text-primary" in theme:
        fg = theme["text-primary"]
        fg_hex = rgb_to_hex_format(fg)
        sequence += f"\033]12;rgb:{fg_hex}\007"

    # Set ANSI colors 0-15 (OSC 4)
    for i in range(16):
        ansi_key = f"ansi-{i}"
        if ansi_key in theme:
            color = theme[ansi_key]
            color_hex = rgb_to_hex_format(color)
            sequence += f"\033]4;{i};rgb:{color_hex}\007"

    return sequence


def preview_theme(theme: dict[str, Any]) -> None:
    """
    Displays a visual preview of the generated color theme in the terminal.

    Args:
        theme: A dictionary mapping color names to RGB objects.
    """

    def format_pair_line(label: str, bg_rgb: Any, fg_rgb: Any) -> str:
        """Format a background/foreground pair line."""
        bg_ansi = AnsiColors.bg_rgb(bg_rgb.r, bg_rgb.g, bg_rgb.b)
        fg_ansi = AnsiColors.rgb_to_ansi(fg_rgb.r, fg_rgb.g, fg_rgb.b)
        # Create the "Aa" preview with actual colors
        preview = f"{bg_ansi}{fg_ansi} Aa {AnsiColors.RESET}"
        return f"{label:20} {preview}  {bg_rgb.hex} | {fg_rgb.hex}"

    def format_single_line(label: str, rgb: Any) -> str:
        """Format a single color line."""
        bg_ansi = AnsiColors.bg_rgb(rgb.r, rgb.g, rgb.b)
        # 10 spaces for visual block
        color_block = f"{bg_ansi}    {AnsiColors.RESET}"
        return f"{label:20} {color_block}  {rgb.hex}"

    print()  # Empty line at start

    # Main color pairs
    if "bg-primary" in theme and "text-primary" in theme:
        print(
            format_pair_line(
                "Primary Pair:", theme["bg-primary"], theme["text-primary"]
            )
        )

    if "bg-secondary" in theme and "text-secondary" in theme:
        print(
            format_pair_line(
                "Secondary Pair:", theme["bg-secondary"], theme["text-secondary"]
            )
        )

    if "bg-tertiary" in theme and "text-tertiary" in theme:
        print(
            format_pair_line(
                "Tertiary Pair:", theme["bg-tertiary"], theme["text-tertiary"]
            )
        )

    print()  # Empty line separator

    # Single colors
    single_colors = [
        ("Accent Primary:", "accent-primary"),
        ("Accent Secondary:", "accent-secondary"),
        ("Active Border:", "border-active"),
        ("Inactive Border:", "border-inactive"),
        ("Success Color:", "success-color"),
        ("Warning Color:", "warning-color"),
        ("Error Color:", "error-color"),
    ]

    for label, key in single_colors:
        if key in theme:
            print(format_single_line(label, theme[key]))

    # ANSI colors
    ansi_present = any(f"ansi-{i}" in theme for i in range(16))
    if ansi_present:
        print("\nTerminal Colors: ")

        # Normal/Dark variants
        normal_variants = []
        for i in range(8):
            key = f"ansi-{i}"
            if key in theme:
                color = theme[key]
                normal_variants.append(
                    f"{AnsiColors.bg_rgb(color.r, color.g, color.b)}{'    '}"
                )
        print("".join(normal_variants) + AnsiColors.RESET)

        # Bright/Light variants
        bright_variants = []
        for i in range(8, 16):
            key = f"ansi-{i}"
            if key in theme:
                color = theme[key]
                bright_variants.append(
                    f"{AnsiColors.bg_rgb(color.r, color.g, color.b)}{'    '}"
                )
        print("".join(bright_variants) + AnsiColors.RESET)

    print()  # Empty line at end

