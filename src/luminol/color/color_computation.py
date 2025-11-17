from ..core.data_types import RGB

GAMMA = 2.4
INV_GAMMA = 1 / GAMMA


def to_linear(c) -> float:
    c = c / 255.0
    if c <= 0.04045:
        return c / 12.92

    return ((c + 0.055) / 1.055) ** GAMMA


def linear_to_standard(l) -> int:
    if l <= 0.0031308:
        return round(12.92 * l * 255)

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
    # 1 refers to the base color, 2 refers to the blend_with color

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


def _find_optimal_blend_for_contrast(
    target_contrast: float,
    darker_rgb: RGB,
    lighter_rgb: RGB,
    brighten_toward: RGB | None = None,
    darken_toward: RGB | None = None,
    max_blend: float = 1.0,
) -> float:
    """
    Find blend ratio to achieve target contrast.

    Args:
        darker_rgb: The darker color in the pair
        lighter_rgb: The lighter color in the pair
        brighten_toward: RGB to blend WITH to brighten (for dark themes)
        darken_toward: RGB to blend WITH to darken (for light themes)
        max_blend: Maximum blend amount (0-1)

    Returns:
        Blend ratio (0-1), or -1 if target unreachable
    """

    if brighten_toward is None and darken_toward is None:
        raise ValueError("Must specify either brighten_toward or darken_toward")

    if brighten_toward and darken_toward:
        raise ValueError("Cannot specify both brighten_toward and darken_toward")

    darker_luma = darker_rgb.luma / 255.0
    lighter_luma = lighter_rgb.luma / 255.0

    # Check current contrast
    current_contrast = (lighter_luma + 0.05) / (darker_luma + 0.05)
    if current_contrast >= target_contrast:
        return 0.0

    if brighten_toward:
        # Brighten the lighter color
        target_luma = brighten_toward.luma / 255.0
        source_luma = lighter_luma
        L_required = target_contrast * (darker_luma + 0.05) - 0.05

        if target_luma < L_required:
            return -1.0

        denominator = target_luma - source_luma
        if abs(denominator) < 1e-6:
            return 0.0

        t = (L_required - source_luma) / denominator

    else:  # darken_toward
        # Darken the darker color
        target_luma = darken_toward.luma / 255.0
        source_luma = darker_luma
        L_required = (lighter_luma + 0.05) / target_contrast - 0.05

        if target_luma > L_required:
            return -1.0

        denominator = target_luma - source_luma
        if abs(denominator) < 1e-6:
            return 0.0

        t = (L_required - source_luma) / denominator

    return max(0.0, min(max_blend, t))


def _is_near_white(color: RGB, max_channel_diff: int = 50, min_luma: int = 130) -> bool:
    """
    Check if a color is close to white (desaturated and bright).

    A color is "kinda white" if:
    1. All RGB channels are similar (low saturation)
    2. The color is bright enough (high luma)

    Args:
        color: RGB color to check
        max_channel_diff: Maximum allowed difference between RGB channels (desaturation check)
        min_luma: Minimum luma value for brightness (0-255)

    Returns:
        True if color is whitish, False otherwise
    """

    # Check if desaturated (channels are similar)
    min_val = min(color.r, color.g, color.b)
    max_val = max(color.r, color.g, color.b)
    is_desaturated = (max_val - min_val) <= max_channel_diff

    # Check if bright enough
    color_luma = luma(color.r, color.g, color.b)
    is_bright = color_luma >= min_luma

    return is_desaturated and is_bright
