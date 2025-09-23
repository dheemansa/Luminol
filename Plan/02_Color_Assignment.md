# Intelligent Color Assignment

After extracting a palette, Luminol assigns semantic roles to the colors (e.g., `bg-primary`, `accent-primary`). This allows for intelligent and accessible theme generation.

## Role-Based Color Classification

### Background Color Selection
```
Background Criteria:
1. High coverage (>15% of image)
2. Low-medium saturation (<50 for neutrals)
3. Appropriate luminance for theme type
4. Good text contrast potential

Scoring Formula:
bg_score = coverage * 0.4 + neutrality * 0.3 + contrast_potential * 0.3

Where:
- coverage = pixel_percentage / 100
- neutrality = (100 - saturation) / 100  
- contrast_potential = max(white_contrast, black_contrast) / 21
```

### Text Color Optimization
```
Algorithm: Accessible Text Colors
1. For each background candidate:
   - Test contrast with white: (Lbg + 0.05) / (Lwhite + 0.05)
   - Test contrast with black: (Lblack + 0.05) / (Lbg + 0.05)
   - Generate gray alternatives if needed

2. Requirements:
   - Primary text: ≥4.5:1 contrast (WCAG AA)
   - Secondary text: ≥3:1 contrast minimum
   - Prefer higher contrast when available

3. Color Temperature Matching:
   - Warm backgrounds → slightly warm text colors
   - Cool backgrounds → neutral/cool text colors
```

### Accent Color Intelligence
```
Accent Selection Process:
1. Identify high-saturation colors (>40%)
2. Ensure contrast with backgrounds (>3:1)
3. Check visual distinctness from other colors
4. Prefer emotionally engaging colors

Primary Accent Scoring:
accent_score = saturation * 0.35 + contrast * 0.25 + uniqueness * 0.25 + coverage * 0.15

Secondary Accent Selection:
- Choose complementary or analogous to primary
- Ensure sufficient differentiation (ΔE > 15)
- Maintain accessibility standards
```

## Theme Generation Logic

### Automatic Light/Dark Detection
```
Algorithm: Theme Classification
1. Calculate average luminance: L_avg = Σ(L_i * coverage_i)
2. Analyze luminance distribution variance
3. Theme decision:
   - Light theme: L_avg > 60 and low variance
   - Dark theme: L_avg < 40 and low variance  
   - Dual theme: Generate both if unclear
   
4. Adjust colors for theme consistency:
   - Light theme: prefer lighter backgrounds, darker text
   - Dark theme: prefer darker backgrounds, lighter text
```

### Color Harmony Validation
```
Harmony Rules:
- Ensure colors work well together visually
- Check for sufficient contrast between interactive elements
- Validate that accent colors stand out appropriately
- Maintain consistent color temperature across palette

Validation Checks:
✓ Background-text contrast ≥4.5:1
✓ Accent-background contrast ≥3:1  
✓ Colors distinguishable for UI elements (ΔE ≥10)
✓ No jarring color combinations
```