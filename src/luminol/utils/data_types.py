from collections import namedtuple
from ..cli.term_colors import AnsiColors as AC
from typing import cast, Type

RGB = namedtuple("RGB", ["r", "g", "b"])
RGB.__str__ = lambda self: (
    f"{AC.bg_rgb(r=self.r, g=self.g, b=self.b)}{rgb_to_hex6(self)}{AC.RESET}"
)
RGBA = namedtuple("RGBA", ["r", "g", "b", "a"])


def rgb_to_hex6(rgb: RGB) -> str:
    """Convert an RGB namedtuple to a HEX string."""
    return "#{:02X}{:02X}{:02X}".format(rgb.r, rgb.g, rgb.b)


def rgba_to_hex6(rgba: RGBA) -> str:
    """Convert an RGB namedtuple to a HEX string."""
    return "#{:02X}{:02X}{:02X}".format(rgba.r, rgba.g, rgba.b)


def rgba_to_hex8(rgba: RGBA) -> str:
    # Clamp alpha to 0–1, then scale to 0–255
    a = max(0, min(255, round(rgba.a * 255)))
    return f"#{rgba.r:02X}{rgba.g:02X}{rgba.b:02X}{a:02X}"


# Tell Python we're treating RGB and RGBA like normal classes (not just namedtuples)
RGB_t = cast(Type, RGB)
RGBA_t = cast(Type, RGBA)

RGB_t.hex = property(lambda self: rgb_to_hex6(self))
RGBA_t.hex6 = property(lambda self: rgba_to_hex6(self))
RGBA_t.hex8 = property(lambda self: rgba_to_hex8(self))

ColorData = namedtuple("ColorData", ["rgb", "coverage", "luma"])
ColorData.__str__ = lambda self: (
    f"{AC.bg_rgb(r=self.rgb.r, g=self.rgb.g, b=self.rgb.b)}"
    f"{rgb_to_hex6(self.rgb)}{AC.RESET} Luma={self.luma:.3f} Coverage={self.coverage:.3f}"
)

# examples
"""
Color data structures and conversion utilities.

This module provides RGB/RGBA color representations and conversion functions
for the Luminol theme engine.

Examples:
    Basic RGB usage:
        >>> rgb = RGB(255, 128, 0)
        >>> rgb.r
        255
        >>> rgb.hex
        '#FF8000'
    
    RGBA with alpha channel:
        >>> rgba = RGBA(255, 128, 0, 0.5)
        >>> rgba.hex6  # Ignores alpha
        '#FF8000'
        >>> rgba.hex8  # Includes alpha
        '#FF800080'
    
    ColorData with metrics:
        >>> color = ColorData(RGB(255, 128, 0), coverage=0.45, luma=72)
        >>> color.rgb
        RGB(r=255, g=128, b=0)
        >>> color.luma
        72
        >>> color.coverage
        0.45
        >>> color.rgb.r
        255
"""
