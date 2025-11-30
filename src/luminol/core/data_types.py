"""
Core color data structures for the Luminol application.

This module provides immutable, memory-efficient color representations with
automatic conversions between color spaces (RGB, HSL, HSV) and perceptual
brightness calculations.

Classes:
    RGB: Standard RGB color (0-255 per channel)
    RGBA: RGB with alpha transparency (0.0-1.0)
    HSL: Hue, Saturation, Lightness representation
    HSV: Hue, Saturation, Value representation
    ColorData: RGB color paired with coverage percentage

Examples:
    Create and manipulate RGB colors:
        >>> orange = RGB(255, 128, 0)
        >>> orange.hex
        '#ff8000'
        >>> orange.luma  # Perceptual brightness
        142.7
        >>> orange.hsl
        HSL(0.083, 1.000, 0.500)

    Work with transparency:
        >>> semi_transparent = RGBA(255, 128, 0, 0.5)
        >>> semi_transparent.hex   # Without alpha
        '#ff8000'
        >>> semi_transparent.hex8  # With alpha
        '#ff800080'

    Convert between color spaces:
        >>> hsl = HSL(0.083, 1.0, 0.5)
        >>> hsl.rgb
        RGB(255, 128, 0)

    Track color coverage in images:
        >>> color_info = ColorData(RGB(255, 128, 0), coverage=72.5)
        >>> print(color_info)
        #ff8000 Coverage=72.500
        >>> color_info.coverage
        72.5

    Access RGB from ColorData:
        >>> color_info = ColorData(RGB(255, 128, 0), coverage=72.5)
        >>> rgb = color_info.rgb
        >>> rgb.r, rgb.g, rgb.b
        (255, 128, 0)

    Get HSV saturation from ColorData:
        >>> color_info = ColorData(RGB(255, 128, 0), coverage=72.5)
        >>> saturation = color_info.rgb.hsv.s
        >>> saturation
        1.0

Notes:
    - All color classes are immutable and support equality comparison
    - RGB values must be integers in range [0, 255]
    - HSL/HSV values are floats in range [0.0, 1.0]
    - Alpha values are floats in range [0.0, 1.0]
    - Luma calculations use perceptually-weighted linear RGB
    - Access color space conversions through chained properties: colordata.rgb.hsv.s
"""

import colorsys
from ..cli.term_colors import AnsiColors


GAMMA = 2.4


def _to_linear(c: int) -> float:
    """Helper to convert a single color channel to linear space."""
    c_norm = c / 255.0
    if c_norm <= 0.04045:
        return c_norm / 12.92
    return ((c_norm + 0.055) / 1.055) ** GAMMA


class RGB:
    """
    Immutable RGB color representation.

    Represents a color using red, green, and blue channels with values
    from 0 to 255. Provides conversions to hex strings, HSL, HSV, and
    perceptual brightness (luma) calculations.

    Args:
        r: Red channel (0-255)
        g: Green channel (0-255)
        b: Blue channel (0-255)

    Attributes:
        r: Red channel value
        g: Green channel value
        b: Blue channel value
        hex: 6-digit hex string (#rrggbb)
        luma: Perceptual brightness (0-255)
        hsl: HSL color space representation
        hsv: HSV color space representation

    Raises:
        ValueError: If any channel is outside [0, 255]

    Examples:
        >>> color = RGB(255, 128, 0)
        >>> color.hex
        '#ff8000'
        >>> color.luma
        142.7
    """

    __slots__ = ("r", "g", "b")

    def __init__(self, r: int, g: int, b: int):
        if not (0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255):
            raise ValueError("RGB values must be between 0 and 255.")
        object.__setattr__(self, "r", r)
        object.__setattr__(self, "g", g)
        object.__setattr__(self, "b", b)

    def __repr__(self) -> str:
        return f"RGB({self.r}, {self.g}, {self.b})"

    def __str__(self) -> str:
        bg_ansi = AnsiColors.bg_rgb(self.r, self.g, self.b)
        hex_str = self.hex
        reset_ansi = AnsiColors.RESET
        return f"{bg_ansi}{hex_str}{reset_ansi}"

    def __eq__(self, other) -> bool:
        if not isinstance(other, RGB):
            return NotImplemented
        return self.r == other.r and self.g == other.g and self.b == other.b

    def __setattr__(self, name, value):
        raise AttributeError("Cannot modify immutable RGB color.")

    @property
    def luma(self) -> float:
        """Calculate perceived brightness (luma)."""
        r_lin = _to_linear(self.r)
        g_lin = _to_linear(self.g)
        b_lin = _to_linear(self.b)
        luma_linear = 0.2126 * r_lin + 0.7152 * g_lin + 0.0722 * b_lin
        return luma_linear * 255.0

    @property
    def hsl(self) -> "HSL":
        """Convert RGB to HSL."""
        h, l, s = colorsys.rgb_to_hls(self.r / 255.0, self.g / 255.0, self.b / 255.0)
        return HSL(h, s, l)

    @property
    def hsv(self) -> "HSV":
        """Convert RGB to HSV."""
        h, s, v = colorsys.rgb_to_hsv(self.r / 255.0, self.g / 255.0, self.b / 255.0)
        return HSV(h, s, v)

    @property
    def hex(self) -> str:
        """Convert RGB to a 6-digit hex string."""
        return f"#{self.r:02x}{self.g:02x}{self.b:02x}"


class HSL:
    """
    Immutable HSL (Hue, Saturation, Lightness) color representation.

    Args:
        h: Hue (0.0-1.0, where 0=red, 0.33=green, 0.67=blue)
        s: Saturation (0.0=gray, 1.0=full color)
        l: Lightness (0.0=black, 0.5=pure color, 1.0=white)

    Attributes:
        h: Hue value
        s: Saturation value
        l: Lightness value
        rgb: Converted RGB representation

    Examples:
        >>> hsl = HSL(0.083, 1.0, 0.5)  # Orange
        >>> hsl.rgb
        RGB(255, 128, 0)
    """

    __slots__ = ("h", "s", "l")

    def __init__(self, h: float, s: float, l: float):
        object.__setattr__(self, "h", h)
        object.__setattr__(self, "s", s)
        object.__setattr__(self, "l", l)

    def __repr__(self) -> str:
        return f"HSL({self.h:.3f}, {self.s:.3f}, {self.l:.3f})"

    def __eq__(self, other) -> bool:
        if not isinstance(other, HSL):
            return NotImplemented
        return self.h == other.h and self.s == other.s and self.l == other.l

    def __setattr__(self, name, value):
        raise AttributeError("Cannot modify immutable HSL color.")

    @property
    def rgb(self) -> RGB:
        """Convert HSL to RGB."""
        r, g, b = colorsys.hls_to_rgb(self.h, self.l, self.s)
        return RGB(round(r * 255), round(g * 255), round(b * 255))


class HSV:
    """
    Immutable HSV (Hue, Saturation, Value) color representation.

    Args:
        h: Hue (0.0-1.0, where 0=red, 0.33=green, 0.67=blue)
        s: Saturation (0.0=white, 1.0=pure color)
        v: Value/brightness (0.0=black, 1.0=full brightness)

    Attributes:
        h: Hue value
        s: Saturation value
        v: Value/brightness
        rgb: Converted RGB representation

    Examples:
        >>> hsv = HSV(0.083, 1.0, 1.0)  # Bright orange
        >>> hsv.rgb
        RGB(255, 128, 0)
    """

    __slots__ = ("h", "s", "v")

    def __init__(self, h: float, s: float, v: float):
        object.__setattr__(self, "h", h)
        object.__setattr__(self, "s", s)
        object.__setattr__(self, "v", v)

    def __repr__(self) -> str:
        return f"HSV({self.h:.3f}, {self.s:.3f}, {self.v:.3f})"

    def __eq__(self, other) -> bool:
        if not isinstance(other, HSV):
            return NotImplemented
        return self.h == other.h and self.s == other.s and self.v == other.v

    def __setattr__(self, name, value):
        raise AttributeError("Cannot modify immutable HSV color.")

    @property
    def rgb(self) -> RGB:
        """Convert HSV to RGB."""
        r, g, b = colorsys.hsv_to_rgb(self.h, self.s, self.v)
        return RGB(round(r * 255), round(g * 255), round(b * 255))


class RGBA:
    """
    Immutable RGBA color with transparency.

    Extends RGB with an alpha (transparency) channel. Does not inherit
    from RGB to maintain proper type checking with isinstance().

    Args:
        r: Red channel (0-255)
        g: Green channel (0-255)
        b: Blue channel (0-255)
        a: Alpha/transparency (0.0=transparent, 1.0=opaque)

    Attributes:
        r: Red channel value
        g: Green channel value
        b: Blue channel value
        a: Alpha channel value
        hex: 6-digit hex without alpha (#rrggbb)
        hex8: 8-digit hex with alpha (#rrggbbaa)
        luma: Perceptual brightness (0-255)
        hsl: HSL representation (ignoring alpha)
        hsv: HSV representation (ignoring alpha)

    Raises:
        ValueError: If RGB values outside [0, 255] or alpha outside [0.0, 1.0]

    Examples:
        >>> color = RGBA(255, 128, 0, 0.5)
        >>> color.hex8
        '#ff800080'
        >>> isinstance(color, RGB)
        False
    """

    __slots__ = ("_rgb", "a")

    def __init__(self, r: int, g: int, b: int, a: float):
        object.__setattr__(self, "_rgb", RGB(r, g, b))
        if not (0.0 <= a <= 1.0):
            raise ValueError("Alpha value must be between 0.0 and 1.0.")
        object.__setattr__(self, "a", a)

    @property
    def r(self) -> int:
        return self._rgb.r

    @property
    def g(self) -> int:
        return self._rgb.g

    @property
    def b(self) -> int:
        return self._rgb.b

    @property
    def luma(self) -> float:
        return self._rgb.luma

    @property
    def hsl(self) -> "HSL":
        return self._rgb.hsl

    @property
    def hsv(self) -> "HSV":
        return self._rgb.hsv

    @property
    def hex(self) -> str:
        """Return the 6-digit hex string (without alpha)."""
        return self._rgb.hex

    @property
    def hex8(self) -> str:
        """Convert RGBA to an 8-digit hex string."""
        alpha_hex = f"{round(self.a * 255):02x}"
        return f"{self.hex}{alpha_hex}"

    def __repr__(self) -> str:
        return f"RGBA({self.r}, {self.g}, {self.b}, {self.a})"

    def __str__(self) -> str:
        bg_ansi = AnsiColors.bg_rgb(self.r, self.g, self.b)
        hex_str = self.hex8
        reset_ansi = AnsiColors.RESET
        return f"{bg_ansi}{hex_str}{reset_ansi}"

    def __eq__(self, other) -> bool:
        if not isinstance(other, RGBA):
            return NotImplemented
        return (
            self.r == other.r
            and self.g == other.g
            and self.b == other.b
            and self.a == other.a
        )

    def __setattr__(self, name, value):
        raise AttributeError("Cannot modify immutable RGBA color.")


class ColorData:
    """
    Immutable color with coverage metric.

    Pairs an RGB color with a coverage percentage, typically used for
    tracking color distribution in image analysis.

    Args:
        rgb: The RGB color
        coverage: Coverage percentage (typically 0.0-100.0)

    Attributes:
        rgb: The RGB color object
        coverage: Coverage percentage value

    Examples:
        >>> data = ColorData(RGB(255, 128, 0), coverage=72.5)
        >>> print(data)
        #ff8000 Coverage=72.500
        >>> data.rgb.hex
        '#ff8000'
    """

    __slots__ = ("rgb", "coverage")

    def __init__(self, rgb: RGB, coverage: float):
        object.__setattr__(self, "rgb", rgb)
        object.__setattr__(self, "coverage", coverage)

    def __repr__(self) -> str:
        return f"ColorData({self.rgb!r}, coverage={self.coverage})"

    def __str__(self) -> str:
        bg_ansi = AnsiColors.bg_rgb(self.rgb.r, self.rgb.g, self.rgb.b)
        hex_str = self.rgb.hex
        reset_ansi = AnsiColors.RESET
        return f"{bg_ansi}{hex_str}{reset_ansi} Coverage={self.coverage:.3f}"

    def __eq__(self, other) -> bool:
        if not isinstance(other, ColorData):
            return NotImplemented
        return self.rgb == other.rgb and self.coverage == other.coverage

    def __setattr__(self, name, value):
        raise AttributeError("Cannot modify immutable ColorData.")
