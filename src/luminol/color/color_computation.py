from ..utils.data_types import RGB, ColorData

GAMMA = 2.4
INV_GAMMA = 1 / GAMMA


def to_linear(c) -> float:
    c = c / 255.0
    if c <= 0.04045:
        return c / 12.92
    else:
        return ((c + 0.055) / 1.055) ** GAMMA


def linear_to_standard(l) -> int:
    if l <= 0.0031308:
        return round(12.92 * l * 255)
    else:
        return round(255 * (1.055 * l ** (INV_GAMMA) - 0.055))


def luma(r: int, g: int, b: int) -> float:
    """
    Calculate perceived brightness (luma) from RGB values.

    Args:
        r: Red value (0-255)
        g: Green value (0-255)
        b: Blue value (0-255)

    Returns:
        float: Luma value from 0-255
    """

    r_lin = to_linear(r)
    g_lin = to_linear(g)
    b_lin = to_linear(b)

    # Apply coefficients in linear space
    luma_linear = 0.2126 * r_lin + 0.7152 * g_lin + 0.0722 * b_lin
    return luma_linear * 255.0


def contrast_ratio(luma1: float, luma2: float) -> float:
    """
    Calculate WCAG contrast ratio between two luma values (0-255 scale).

    Formula: (L1 + 0.05) / (L2 + 0.05) where L1 > L2
    where luma values are normalized to 0-1 range.
    """
    # Normalize to 0-1 range (relative luminance)
    L1 = max(luma1, luma2) / 255.0
    L2 = min(luma1, luma2) / 255.0

    return (L1 + 0.05) / (L2 + 0.05)


def blend(color: RGB, blend_with: RGB, amount: float) -> RGB:
    """
    Blend two colors in linear RGB space.

    Args:
        color: The base color
        blend_with: The color to blend with
        amount: How much of blend_with to use (0.0 = all color, 1.0 = all blend_with)
    """
    # naming convention in case i forget
    # 1 -> color
    # 2 -> blend_with

    r_lin1 = to_linear(color.r)
    g_lin1 = to_linear(color.g)
    b_lin1 = to_linear(color.b)

    r_lin2 = to_linear(blend_with.r)
    g_lin2 = to_linear(blend_with.g)
    b_lin2 = to_linear(blend_with.b)

    r_final = linear_to_standard((1 - amount) * r_lin1 + amount * r_lin2)
    g_final = linear_to_standard((1 - amount) * g_lin1 + amount * g_lin2)
    b_final = linear_to_standard((1 - amount) * b_lin1 + amount * b_lin2)

    return RGB(r_final, g_final, b_final)
