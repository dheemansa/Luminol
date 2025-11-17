from typing import Any

from ..color.transformation import _transform_color
from ..core.constants import SUPPORTED_COLOR_FORMATS
from ..core.data_types import RGB, RGBA


def _convert_format(color: RGB | RGBA, color_format: str) -> str:
    if color_format not in SUPPORTED_COLOR_FORMATS:
        raise ValueError(
            f"{color_format} is not a supported color format, \
            Supported formats are {', '.join(SUPPORTED_COLOR_FORMATS)}"
        )

    if color_format == "hex6":
        if isinstance(color, RGB):
            final_color: str = color.hex
        else:
            final_color: str = color.hex6

        return final_color

    if color_format == "rgb":
        if isinstance(color, RGB):
            r, g, b = color
        else:
            r, g, b, a = color

        final_color = f"rgb({r}, {g}, {b})"
        return final_color

    if color_format == "rgb_decimal":
        if isinstance(color, RGB):
            r, g, b = color
        else:
            r, g, b, a = color

        final_color = f"{r}, {g}, {b}"
        return final_color

    if color_format == "hex8":
        if isinstance(color, RGB):
            # force opacity to max
            final_color = f"{color.hex}FF"
        else:
            final_color = f"{color.hex8}"
        return final_color

    if color_format == "rgba":
        if isinstance(color, RGB):
            # force opacity to max
            r, g, b = color
            final_color = f"rgba({r}, {g}, {b}, 1.0)"
        else:
            r, g, b, a = color
            final_color = f"rgba({r}, {g}, {b}, {a})"
        return final_color

    if color_format == "rgba_decimal":
        if isinstance(color, RGB):
            # force opacity to max
            r, g, b = color
            final_color = f"{r}, {g}, {b}, 1.0"
        else:
            r, g, b, a = color
            final_color = f"{r}, {g}, {b}, {a}"
        return final_color


def compile_color_syntax(
    named_colors: dict[str, RGB],
    syntax: str,
    color_format: str,
    remap: dict[str, Any] | None = None,
) -> list:
    """
    Compile color definitions into formatted strings using a template syntax.

    This function takes a dictionary of named RGB colors
    and formats them according to a template string and color
    format specification. Optionally applies
    color transformations through remapping.

    Args:
        named_colors: Dictionary mapping color names to RGB color objects.
            Example: {"primary": RGB(255, 128, 0),
                      "secondary": RGB(0, 128, 255)}

        syntax: Template string with {name} and/or {color} placeholders.
            - {name}: Replaced with the color name
            - {color}: Replaced with the formatted color value
            Examples:
                ${name}: {color};       → $primary: #FF8000;
                --{name}: {color};      → --primary: rgb(255, 128, 0);
                {color}                 → #FF8000
                #using escape sequence
                \"{name}\": \"{color}\"→ "bg-primary": "rgba(255, 128, 0, 1.0)"

        color_format: Output format for color values. Options:
            - "hex6": 6-digit hex (#RRGGBB)
            - "hex8": 8-digit hex with alpha (#RRGGBBAA)
            - "rgb": CSS rgb() format → "rgb(255, 128, 0)"
            - "rgba": CSS rgba() format → "rgba(255, 128, 0, 1.0)"
            - "rgb_decimal": Comma-separated decimals → "255, 128, 0"
            - "rgba_decimal": Decimals with alpha → "255, 128, 0, 1.0"

        remap: Optional dictionary for creating
               derived colors with transformations.
            Structure: {
                "new_color_name": {
                    "source": "base_color_name",  # Required: source color
                    "hue": 30,
                    "saturation": 1.2,
                    "brightness": 0.8,
                    "contrast": 1.1,
                    "temp": 20,
                    "opacity": 0.7
                }
            }
            Example:
                {
                    "active-border": {"source": "accent-primary"},
                    "inactive-border": {"source": "bg-tertiary",
                                        "brightness": 0.8, "opacity": 0.5}
                }

    Returns:
        List of formatted strings, one per color definition.
        Example output for syntax="${name}: {color};" and format="hex6":
            ["$primary: #FF8000;", "$secondary: #0080FF;"]

    Examples:
        >>> colors ={"primary":RGB(255, 128, 0), "secondary": RGB(0, 128, 255)}
        >>> compile_color_syntax(colors, "${name}: {color};", "hex6")
        ['$primary: #FF8000;', '$secondary: #0080FF;']

        >>> compile_color_syntax(colors, "--{name}: {color};", "rgb")
        ['--primary: rgb(255, 128, 0);', '--secondary: rgb(0, 128, 255);']

        >>> remap = {"highlight": {"source": "primary", "brightness": 1.2}}
        >>> compile_color_syntax(colors,"{name}: {color}", "hex6", remap=remap)
        ['highlight: #FFB84D']

    Notes:
        - When remap is None, all colors in named_colors are processed
        - When remap is provided, only the remapped colors are output
        - Opacity transforms create RGBA colors;
          hex8/rgba formats include alpha
    """
    content: list = []
    if remap is None:
        for final_name, palette_color in named_colors.items():
            final_color: str = _convert_format(
                color=palette_color, color_format=color_format
            )
            # replace {color} with final_color and {name} with final_name
            line: str = syntax.replace("{color}", final_color).replace(
                "{name}", final_name
            )
            content.append(line)
        return content

    else:
        for final_name, params in remap.items():
            source: str = params["source"]
            source_color: RGB = named_colors[source]

            transformed_color: RGBA = _transform_color(
                rgb=source_color,
                hue=params.get("hue", None),
                saturation=params.get("saturation", None),
                brightness=params.get("brightness", None),
                contrast=params.get("contrast", None),
                temp=params.get("temperature", None),
                opacity=params.get("opacity", None),
            )

            final_color: str = _convert_format(
                color=transformed_color, color_format=color_format
            )
            # replace {color} with final_color and {name} with final_name
            line: str = syntax.replace("{color}", final_color).replace(
                "{name}", final_name
            )
            content.append(line)

    return content


def compile_template(
    named_colors: dict[str, RGB],
    syntax: str,
    template: str,
    color_format: str,
    remap: dict[str, Any] | None = None,
) -> str:
    if remap is None:  # use semantic names as find key
        for col_name, color in named_colors.items():
            find_key = syntax.replace("placeholder", col_name)

            final_color = _convert_format(color=color, color_format=color_format)
            template = template.replace(find_key, final_color)

        return template
    else:  # use remap names as find key
        for final_name, params in remap.items():
            find_key = syntax.replace("placeholder", final_name)
            source: str = params["source"]
            source_color: RGB = named_colors[source]

            transformed_color: RGBA = _transform_color(
                rgb=source_color,
                hue=params.get("hue", None),
                saturation=params.get("saturation", None),
                brightness=params.get("brightness", None),
                contrast=params.get("contrast", None),
                temp=params.get("temperature", None),
                opacity=params.get("opacity", None),
            )

            final_color: str = _convert_format(
                color=transformed_color, color_format=color_format
            )

            template = template.replace(find_key, final_color)

        return template
