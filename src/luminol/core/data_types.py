from collections import namedtuple
from typing import TYPE_CHECKING
from ..cli.term_colors import AnsiColors as AC

# NOTE: type_checking logic was generated/suggested by AI


if TYPE_CHECKING:
    # Type checkers see this clean definition
    from typing import NamedTuple as _NamedTuple

    class RGB(_NamedTuple):
        """RGB color representation with hex conversion."""

        r: int
        g: int
        b: int

        @property
        def hex(self) -> str:
            """6-digit hex representation (#RRGGBB)."""
            ...  # pylint: disable = unnecessary-ellipsis

        def __str__(self) -> str: ...  # pylint: disable = unnecessary-ellipsis

else:
    # Runtime uses fast immutable namedtuple
    RGB = namedtuple("RGB", ["r", "g", "b"])

    # Add hex property
    RGB.hex = property(lambda self: f"#{self.r:02X}{self.g:02X}{self.b:02X}")

    # Add __str__ method with ANSI color background
    RGB.__str__ = lambda self: (
        f"{AC.bg_rgb(r=self.r, g=self.g, b=self.b)}{self.hex}{AC.RESET}"
    )


if TYPE_CHECKING:

    class RGBA(_NamedTuple):
        """RGBA color representation with alpha channel."""

        r: int
        g: int
        b: int
        a: float

        @property
        def hex6(self) -> str:
            """6-digit hex ignoring alpha (#RRGGBB)."""
            ...  # pylint: disable = unnecessary-ellipsis

        @property
        def hex8(self) -> str:
            """8-digit hex including alpha (#RRGGBBAA)."""
            ...  # pylint: disable = unnecessary-ellipsis

else:
    RGBA = namedtuple("RGBA", ["r", "g", "b", "a"])

    # Add hex6 property (ignores alpha)
    RGBA.hex6 = property(lambda self: f"#{self.r:02X}{self.g:02X}{self.b:02X}")

    # Add hex8 property (includes alpha)
    def _rgba_hex8(self) -> str:
        a = max(0, min(255, round(self.a * 255)))
        return f"#{self.r:02X}{self.g:02X}{self.b:02X}{a:02X}"

    RGBA.hex8 = property(_rgba_hex8)


if TYPE_CHECKING:

    class ColorData(_NamedTuple):
        """Color with additional metrics (coverage and luminance)."""

        rgb: RGB
        coverage: float
        luma: float

        def __str__(self) -> str: ...  # pylint: disable = unnecessary-ellipsis

else:
    ColorData = namedtuple("ColorData", ["rgb", "coverage", "luma"])

    # Add __str__ method
    ColorData.__str__ = lambda self: (
        f"{AC.bg_rgb(r=self.rgb.r, g=self.rgb.g, b=self.rgb.b)}"
        f"{self.rgb.hex}{AC.RESET} "
        f"Luma={self.luma:.3f} Coverage={self.coverage:.3f}"
    )


"""
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
        >>> color = ColorData(RGB(255, 128, 0), coverage=0.45, luma=72.5)
        >>> color.rgb.hex
        '#FF8000'
        >>> color.luma
        72.5
"""
