# credits goes to https://github.com/ciembor/4bit
# author: Maciej Ciemborowicz

from ...core.data_types import RGB, HSL


def _blend_dye(base: RGB, dye: RGB, alpha: float) -> RGB:
    """
    Blends a base RGB color with a dye RGB color by a given alpha factor.
    alpha = 0 -> returns base
    alpha = 1 -> returns dye
    """
    r = round(base.r + (dye.r - base.r) * alpha)
    g = round(base.g + (dye.g - base.g) * alpha)
    b = round(base.b + (dye.b - base.b) * alpha)
    return RGB(r, g, b)


class ColorScheme:
    """
    Generates the raw HSL values for a 4-bit terminal color scheme.
    Does not handle dyeing, which is now a post-processing step.
    """

    def __init__(
        self,
        hue: float = -15,
        saturation: float = 0.5,
        normal_lightness: float = 0.5,
        bright_lightness: float = 0.75,
        black_lightness: float = 0.0,
        bright_black_lightness: float = 0.125,
        white_lightness: float = 0.875,
        bright_white_lightness: float = 1.0,
        background_lightness: float = 0.0,
        foreground_lightness: float = 1.0,
    ):
        self.hue = hue
        self.saturation = saturation
        self.normal_lightness = normal_lightness
        self.bright_lightness = bright_lightness
        self.black_lightness = black_lightness
        self.bright_black_lightness = bright_black_lightness
        self.white_lightness = white_lightness
        self.bright_white_lightness = bright_white_lightness
        self.background_lightness = background_lightness
        self.foreground_lightness = foreground_lightness
        self.colors: dict[str, HSL] = {}
        self._initialize_colors()

    def _initialize_colors(self):
        """Initialize HSL colors and populate the colors dictionary."""
        degrees = [0, 60, 120, 180, 240, 300]
        hue_normalized = (self.hue % 360) / 360.0

        # Create colors dictionary
        self.colors = {
            "background": HSL(0, 0, self.background_lightness),
            "foreground": HSL(0, 0, self.foreground_lightness),
            "black": HSL(0, 0, self.black_lightness),
            "bright_black": HSL(0, 0, self.bright_black_lightness),
            "red": HSL(
                hue_normalized + (degrees[0] / 360.0),
                self.saturation,
                self.normal_lightness,
            ),
            "bright_red": HSL(
                hue_normalized + (degrees[0] / 360.0),
                self.saturation,
                self.bright_lightness,
            ),
            "green": HSL(
                hue_normalized + (degrees[2] / 360.0),
                self.saturation,
                self.normal_lightness,
            ),
            "bright_green": HSL(
                hue_normalized + (degrees[2] / 360.0),
                self.saturation,
                self.bright_lightness,
            ),
            "yellow": HSL(
                hue_normalized + (degrees[1] / 360.0),
                self.saturation,
                self.normal_lightness,
            ),
            "bright_yellow": HSL(
                hue_normalized + (degrees[1] / 360.0),
                self.saturation,
                self.bright_lightness,
            ),
            "blue": HSL(
                hue_normalized + (degrees[4] / 360.0),
                self.saturation,
                self.normal_lightness,
            ),
            "bright_blue": HSL(
                hue_normalized + (degrees[4] / 360.0),
                self.saturation,
                self.bright_lightness,
            ),
            "magenta": HSL(
                hue_normalized + (degrees[5] / 360.0),
                self.saturation,
                self.normal_lightness,
            ),
            "bright_magenta": HSL(
                hue_normalized + (degrees[5] / 360.0),
                self.saturation,
                self.bright_lightness,
            ),
            "cyan": HSL(
                hue_normalized + (degrees[3] / 360.0),
                self.saturation,
                self.normal_lightness,
            ),
            "bright_cyan": HSL(
                hue_normalized + (degrees[3] / 360.0),
                self.saturation,
                self.bright_lightness,
            ),
            "white": HSL(0, 0, self.white_lightness),
            "bright_white": HSL(0, 0, self.bright_white_lightness),
        }

    def get_theme_as_rgb_objects(self) -> dict[str, RGB]:
        """Get all colors as a dictionary with ansi-X keys and RGB objects."""
        # Standard ANSI color order
        ansi_map = [
            "black",
            "red",
            "green",
            "yellow",
            "blue",
            "magenta",
            "cyan",
            "white",
            "bright_black",
            "bright_red",
            "bright_green",
            "bright_yellow",
            "bright_blue",
            "bright_magenta",
            "bright_cyan",
            "bright_white",
        ]
        # Create the dictionary with ansi-N keys
        ansi_dict = {
            f"ansi-{i}": self.colors[name].rgb for i, name in enumerate(ansi_map)
        }
        return ansi_dict


def generate_color_scheme(
    hue: float = -15,
    saturation: float = 0.5,
    normal_lightness: float = 0.5,
    bright_lightness: float = 0.75,
    black_lightness: float = 0.0,
    bright_black_lightness: float = 0.125,
    white_lightness: float = 0.875,
    bright_white_lightness: float = 1.0,
    background_lightness: float = 0.0,
    foreground_lightness: float = 1.0,
    dye_h: float = 0,
    dye_s: float = 0,
    dye_l: float = 0,
    dye_a: float = 0,
    dye_type: str = "none",
) -> dict[str, RGB]:
    """
    Generate a terminal color scheme using the exact logic from 4bit website.
    Dyeing is applied as a post-processing step.
    """
    scheme = ColorScheme(
        hue=hue,
        saturation=saturation,
        normal_lightness=normal_lightness,
        bright_lightness=bright_lightness,
        black_lightness=black_lightness,
        bright_black_lightness=bright_black_lightness,
        white_lightness=white_lightness,
        bright_white_lightness=bright_white_lightness,
        background_lightness=background_lightness,
        foreground_lightness=foreground_lightness,
    )

    raw_theme = scheme.get_theme_as_rgb_objects()

    # Apply dye if specified
    if dye_type == "none" or dye_a == 0:
        return raw_theme

    dyed_theme = {}
    dye_color = HSL(dye_h / 360.0, dye_s, dye_l).rgb

    achromatic_keys = {"ansi-0", "ansi-7", "ansi-8", "ansi-15"}
    color_keys = {f"ansi-{i}" for i in [1, 2, 3, 4, 5, 6, 9, 10, 11, 12, 13, 14]}

    keys_to_dye = set()
    if dye_type == "all":
        # Exclude background/foreground as original script did not seem to dye them
        keys_to_dye = achromatic_keys.union(color_keys)
    elif dye_type == "color":
        keys_to_dye = color_keys
    elif dye_type == "achromatic":
        keys_to_dye = achromatic_keys

    for key, color in raw_theme.items():
        if key in keys_to_dye:
            dyed_theme[key] = _blend_dye(color, dye_color, dye_a)
        else:
            dyed_theme[key] = color

    return dyed_theme
