import glob
from pathlib import Path
import logging

from ..color.ansi_colors.assign_ansi import generate_ansi
from .data_types import ColorData, RGB


def tty_color_sequence(theme: dict[str, RGB]) -> str:
    """
    Generates a string of OSC escape sequences to theme a terminal.

    Args:
        theme: A dictionary with 'background', 'foreground', and 'ansi-0'...'ansi-15' keys.

    Returns:
        A single string containing all necessary OSC escape codes.
    """
    sequence = ""

    # Set background color (OSC 11)
    if "background" in theme:
        sequence += f"\033]11;{theme['background'].hex}\007"

    # Set foreground/text color (OSC 10)
    if "foreground" in theme:
        sequence += f"\033]10;{theme['foreground'].hex}\007"

    # Set cursor color (OSC 12)
    if "cursor" in theme:
        sequence += f"\033]12;{theme['cursor'].hex}\007"
    elif "foreground" in theme:  # Fallback cursor to foreground
        sequence += f"\033]12;{theme['foreground'].hex}\007"

    # Set ANSI colors 0-15 (OSC 4)
    for i in range(16):
        ansi_key = f"ansi-{i}"
        if ansi_key in theme:
            sequence += f"\033]4;{i};{theme[ansi_key].hex}\007"

    return sequence


def tty_colors_pywal(
    assigned_dict: dict[str, RGB], color_data: list[ColorData]
) -> dict[str, RGB]:
    """
    Takes the theme dict and creates a dict for terminal theming using pywal's logic.
    It arranges the extracted colors into the 16 ANSI slots.
    """

    if len(color_data) > 8:
        color_data = color_data[:8]

    # unnescessary, but this is how imagemagick output colors are sorted by default
    color_data.sort(key=lambda col: col.rgb.r**2 + col.rgb.g**2 + col.rgb.b**2)

    colors = [c.rgb for c in color_data]

    tty_theme = {}

    # Set background, foreground, and cursor from the main theme dict
    tty_theme["background"] = assigned_dict["bg-primary"]
    tty_theme["foreground"] = assigned_dict["text-primary"]
    tty_theme["cursor"] = assigned_dict["accent-primary"]

    for i in range(8):
        tty_theme[f"ansi-{i}"] = colors[i]

    for i in range(8, 16):
        tty_theme[f"ansi-{i}"] = colors[i - 8]

    # Override specific slots for a more conventional terminal theme
    # This follows pywal's general structure
    tty_theme["ansi-0"] = tty_theme["background"]  # Black
    tty_theme["ansi-7"] = tty_theme["foreground"]  # White (slightly dimmed)
    tty_theme["ansi-8"] = assigned_dict["bg-secondary"]
    tty_theme["ansi-15"] = tty_theme["foreground"]  # Bright White

    return tty_theme


def tty_colors_default(
    assigned_dict: dict[str, RGB], color_data: list[ColorData]
) -> dict[str, RGB]:
    """
    Takes the theme dict and creates a dict for terminal theming using a default
    algorithmic approach.
    """
    base_theme = generate_ansi(color_data, assigned_dict)

    # Integrate the generated colors with the primary theme colors
    base_theme["background"] = assigned_dict["bg-primary"]
    base_theme["foreground"] = assigned_dict["text-primary"]
    base_theme["cursor"] = assigned_dict["text-primary"]

    return base_theme


def get_ttys() -> list[str]:
    """
    Get a list of all active TTYs
    This logic is adapted from pywal by Dylan Araps.
    https://github.com/dylanaraps/pywal
    """
    tty_pattern = "/dev/pts/[0-9]*"
    return glob.glob(tty_pattern)


def reload_tty_and_save_sequence(
    color_data: list[ColorData],
    assigned_dict: dict[str, RGB],
    style: str = "default",
    sequence_file: str | Path | None = None,
):
    if style == "default":
        colors = tty_colors_default(assigned_dict, color_data)
    elif style == "pywal":
        colors = tty_colors_pywal(assigned_dict, color_data)
    else:
        raise ValueError("Invalid terminal color style:", style)

    sequence = tty_color_sequence(colors)

    for tty in get_ttys():
        try:
            with open(tty, "w") as f:
                f.write(sequence)
        except PermissionError:
            logging.error(f"Could not open tty: {tty} for writing.")

    if not sequence_file:
        return

    try:
        with open(sequence_file, "w") as f:
            f.write(sequence)

    except PermissionError:
        logging.error(f"Could not save the ansi sequence to :'{sequence_file}'")
