from ..core.data_types import RGB

GAMMA = 2.4
INV_GAMMA = 1 / GAMMA


def to_linear(c) -> float:
    c = c / 255.0
    if c <= 0.04045:
        return c / 12.92

    return ((c + 0.055) / 1.055) ** GAMMA


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
    Calculate WCAG 2.1 contrast ratio between two colors.

    Args:
        luma1, luma2: Luminance values (0-255 scale)

    Returns:
        Contrast ratio (1.0-21.0). Higher = more contrast.

    Formula: (L_lighter + 0.05) / (L_darker + 0.05) where L in [0,1]
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

    def linear_to_standard(l) -> int:
        if l <= 0.0031308:
            return round(12.92 * l * 255)

        return round(255 * (1.055 * l ** (INV_GAMMA) - 0.055))

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


def find_optimal_blend(
    base_col: RGB,
    blend_col: RGB,
    contrast_with: RGB,
    target_contrast: float,
    max_blend: float = 1.0,
) -> float:
    """
    Finds the optimal blend ratio to meet a target contrast.

    This function calculates the necessary amount to blend the `base_col`
    with the `blend_col` to achieve the `target_contrast` against the
    `contrast_with` color. It uses a direct formula by solving for the
    required luminance in the WCAG contrast ratio equation.

    Args:
        base_col: The color to be modified.
        blend_col: The color to blend toward.
        contrast_with: The color to measure contrast against.
        target_contrast: The desired contrast ratio.
        max_blend: The maximum allowable blend amount (0.0 to 1.0).

    Returns:
        The required blend amount (0.0 to 1.0), or -1.0 if the target
        contrast is not achievable by blending toward `blend_col`.
    """
    # Lumas are normalized to the 0-1 range for the formula
    base_luma = base_col.luma / 255.0
    blend_luma = blend_col.luma / 255.0
    contrast_with_luma = contrast_with.luma / 255.0

    # If contrast is already good, no blend is needed.
    if contrast_ratio(base_col.luma, contrast_with.luma) >= target_contrast:
        return 0.0

    # Determine if the base color is lighter or darker than the one to contrast with.
    if base_luma >= contrast_with_luma:
        # Case 1: base_col is the lighter color. We solve for its new target luma.
        L_required = target_contrast * (contrast_with_luma + 0.05) - 0.05
    else:
        # Case 2: base_col is the darker color. We solve for its new target luma.
        L_required = (contrast_with_luma + 0.05) / target_contrast - 0.05

    # We use the linear interpolation formula L_required = (1-t)*base + t*blend
    # and solve for t: t = (L_required - base) / (blend - base)
    denominator = blend_luma - base_luma

    if abs(denominator) < 1e-6:
        # The blend color is identical to the base color, so we can't change the luma.
        return -1.0 if abs(L_required - base_luma) > 1e-6 else 0.0

    t = (L_required - base_luma) / denominator

    # If t is not between 0 and 1, the target luma is outside the range
    # achievable by blending these two colors.
    if not (0 <= t <= 1):
        return -1.0

    # Clamp to the user-defined max_blend and return.
    return max(0.0, min(max_blend, t))
