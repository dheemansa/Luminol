# Luminol - Complete Project Specification

## Project Overview
Luminol is a robust color palette generator designed for Linux desktop environments, extracting intelligent color schemes from wallpapers for consistent theming across applications like Hyprland, Waybar, Rofi, GTK themes, and other desktop components.

## Core Technical Requirements

### Input/Output Specifications
- **Input**: Wallpaper images (PNG, JPG, WebP) up to 10MB
- **Output**: Standardized color palettes in multiple formats
- **Performance**: <2 seconds processing for typical wallpapers
- **Reliability**: Consistent results across different image types

## Color Extraction Algorithm

### Color Processing Data Flow
Luminol follows a structured pipeline to ensure high-quality, perceptually accurate color extraction.

1.  **RGB Image Loading**: Load the source image and access its raw pixel data in 8-bit RGB format (0-255).
2.  **Preprocessing**: Resize the image for performance, apply a light blur to reduce noise, and sample a representative subset of pixels.
3.  **RGB → LAB Conversion**: Convert all sampled RGB pixels into the perceptually uniform LAB color space. This is a critical step for ensuring the accuracy of the clustering algorithm.
4.  **K-Means Clustering**: Perform K-Means clustering on the LAB pixel data to identify the dominant color centroids.
5.  **Color Object Creation**: For each dominant LAB color, create a rich `Color` object that contains the original LAB value and automatically computes and caches its RGB and HSL representations for later use.
6.  **Quality Scoring**: Score and rank the extracted colors based on properties like pixel coverage and perceptual uniqueness (using distance in LAB space).
7.  **Semantic Assignment**: Use the intuitive HSL color space (from the `Color` object) to classify the ranked colors into semantic roles like `bg-primary`, `accent-primary`, etc.
8.  **Transformations**: If configured, apply color transformations (e.g., brightness, saturation) using the HSL representation for predictable, visually appealing results.
9.  **Export**: Convert the final colors to the application-specific formats (e.g., hex, rgba) using their RGB representation.

### Multi-Method Color Extraction

#### Enhanced K-Means Clustering
```
Algorithm: Perceptual K-Means in LAB Space
1. Preprocessing:
   - Resize image to a max width of 800px, maintaining aspect ratio.
   - Apply a light gaussian blur to reduce image noise.
   - Convert the image's pixels from RGB to the LAB color space.

2. Sampling Strategy:
   - Sample a representative subset of pixels for performance.
   - Skip transparent pixels (alpha < 128).
   - Weight center pixels higher to avoid edge artifacts.

3. Clustering Process:
   - Perform k-means++ clustering directly on the LAB pixel data.
   - Iterate until cluster centroids converge (max 20 iterations).
   - Merge visually similar clusters (ΔE < 12).
   - Result: 5-8 dominant colors, represented in LAB space.

Color Distance (LAB space):
ΔE = √[(L₁-L₂)² + (a₁-a₂)² + (b₁-b₂)²]
```

#### Histogram-Based Analysis
```
Algorithm: Frequency Analysis
1. Generate color histogram with 64 bins per channel
2. Find peaks in histogram representing dominant colors
3. Group nearby peaks to avoid oversegmentation
4. Weight by spatial distribution (center vs edges)
5. Combine with k-means results for validation

Spatial Weight Calculation:
weight(x,y) = 1.0 - distance_from_center / max_distance * 0.3
```

### Color Quality Assessment
```
Quality Scoring System:
The scoring system leverages the properties of the LAB color space to rank colors.

1. **Coverage Score**: `log(pixel_count) / log(total_pixels)`
   (Measures how much of the image the color represents).
2. **Uniqueness Score**: `min_deltaE_to_other_colors / 50`
   (Ensures colors are visually distinct from each other).
3. **Chroma Score**: `sqrt(a² + b²) / 140`
   (Chroma is the LAB equivalent of saturation/vibrancy).
4. **Lightness Balance**: `1 - |L - 50| / 50`
   (Favors colors that are not extreme black or white).

Final Color Score = weighted_sum(all_scores)
Keep top 10-15 colors based on final score
```

## Intelligent Color Assignment

### Role-Based Color Classification

#### Background Color Selection
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

#### Text Color Optimization
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

#### Accent Color Intelligence
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

### Theme Generation Logic

#### Automatic Light/Dark Detection
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

#### Color Harmony Validation
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

## Configuration System

### Semantic Palette Generation

Luminol always generates a standard semantic palette from the wallpaper, regardless of configuration. This ensures consistent color naming and availability across all applications.

#### Standard Semantic Palette (Always Generated)
No matter what, Luminol first produces a **standard semantic palette** from the wallpaper. Example (generated after extraction):

```
# Internal palette (not user config, just for reference)
bg-primary     = #1e1e2e
bg-secondary   = #313244
bg-tertiary    = #45475a
text-primary   = #cdd6f4
text-secondary = #bac2de
accent-primary = #8af4da
accent-secondary = #f38ba8
error-color    = #f38ba8
warning-color  = #f9e2af
success-color  = #a6e3a1
border-active  = #cdd6f4
border-inactive = #313244
```

These names (`bg-primary`, `text-primary`, etc.) are always available.

### Color Remapping System

Each application can choose between two export modes:

#### Default Mode (remap-colors = false)
- Exports the **full semantic palette** with canonical names
- All semantic colors are available in the output file
- Uses standard naming convention

#### Custom Mapping Mode (remap-colors = true)  
- Exports **only explicitly mapped colors** 
- Uses user-defined color names
- Requires `[app.colors]` section with mappings

## Remap Functionality Explained

The `remap-colors` feature provides flexible color naming and selective export control for different applications. This system allows users to customize which colors are exported and what they're called in the output files.

### How Remap Works

#### Step 1: Standard Semantic Palette (Always Generated)
Regardless of configuration, Luminol first extracts colors from the wallpaper and creates a standard semantic palette:

```
# Internal semantic palette (always available)
bg-primary     → #1e1e2e
bg-secondary   → #313244  
bg-tertiary    → #45475a
text-primary   → #cdd6f4
text-secondary → #bac2de
accent-primary → #8af4da
accent-secondary → #f38ba8
error-color    → #f38ba8
warning-color  → #f9e2af
success-color  → #a6e3a1
border-active  → #cdd6f4
border-inactive → #313244
```

#### Step 2: Export Decision (Per Application)

**When `remap-colors = false` (Default Behavior):**
```toml
[rofi]
enabled = true
# No remap-colors specified → defaults to false
file = "~/.config/rofi/colors.rasi"
syntax = "*{{name}: {color};}"
```

**Output:** All semantic colors are exported with their original names:
```css
*bg-primary: #1e1e2e;
*bg-secondary: #313244;
*bg-tertiary: #45475a;
*text-primary: #cdd6f4;
*text-secondary: #bac2de;
*accent-primary: #8af4da;
*accent-secondary: #f38ba8;
*error-color: #f38ba8;
*warning-color: #f9e2af;
*success-color: #a6e3a1;
*border-active: #cdd6f4;
*border-inactive: #313244;
```

**When `remap-colors = true` (Custom Mapping):**
```toml
[waybar]
enabled = true
remap-colors = true
file = "~/.config/waybar/colors.css"
syntax = "@define-color {name} {color};"

[waybar.colors]
theme-background = "bg-primary"
theme-text       = "text-primary"
theme-accent     = "accent-primary"
```

**Output:** Only mapped colors are exported with custom names:
```css
@define-color theme-background #1e1e2e;
@define-color theme-text #cdd6f4;
@define-color theme-accent #8af4da;
```

### Remap Benefits

1. **Selective Export**: Only export the colors your application actually uses
2. **Custom Naming**: Use application-specific color names that match your existing themes
3. **Cleaner Configs**: Avoid cluttering config files with unused color definitions
4. **Compatibility**: Maintain existing color names when migrating to Luminol

### Remap Configuration Examples

#### Example 1: Minimalist Waybar
```toml
[waybar]
enabled = true
remap-colors = true
file = "~/.config/waybar/colors.css"
syntax = "@define-color {name} {color};"

[waybar.colors]
bar-bg = "bg-primary"
bar-text = "text-primary"
active = "accent-primary"
inactive = "text-secondary"
```

**Generates:**
```css
@define-color bar-bg #1e1e2e;
@define-color bar-text #cdd6f4;
@define-color active #8af4da;
@define-color inactive #bac2de;
```


#### Example 2: Full Semantic Export (Default)
```toml
[gtk]
enabled = true
# remap-colors defaults to false
file = "~/.config/gtk-3.0/colors.css"
syntax = "@define-color {name} {color};"
```

**Generates all semantic colors:**
```css
@define-color bg-primary #1e1e2e;
@define-color bg-secondary #313244;
@define-color bg-tertiary #45475a;
/* ... all other semantic colors ... */
```

### Remap Rules and Validation

1. **Valid Semantic Sources**: Can only map to existing semantic palette names
2. **Unique Custom Names**: Custom color names within an app must be unique
3. **Required Section**: If `remap-colors = true`, the `[app.colors]` section must exist
4. **Error Handling**: Invalid mappings will generate warnings and fall back to default behavior

### When to Use Remap vs Default

**Use Remap (`remap-colors = true`) when:**
- You want specific color names for your application
- You only need a subset of the color palette
- You're integrating with existing themes that have established color names
- You want cleaner, more focused config files

**Use Default (`remap-colors = false`) when:**
- You want access to the full color palette
- You prefer standard semantic naming
- You're creating new themes from scratch
- You want consistency across multiple applications

## Color Transformation System

### Overview
The color transformation system extends Luminol's color remapping functionality by allowing users to modify colors during the mapping process. Instead of only being able to rename semantic colors, users can now apply visual transformations like adjusting brightness, saturation, opacity, and other properties to create perfectly tailored color variants for their applications.

### Core Concept
The transformation system works within the existing remap-colors framework, adding the ability to modify source colors before exporting them. Users can choose between simple direct mapping or enhanced mapping with transformations, providing a smooth upgrade path from basic to advanced color customization.

### Configuration Syntax
#### Simple Mapping (Existing Functionality)
When users want direct color mapping without modifications, they use the existing string syntax:

```toml
[waybar.colors]
bar-bg = "bg-primary"
bar-text = "text-primary"
accent-color = "accent-primary"
```

This continues to work exactly as before, mapping semantic colors directly to application-specific names.

#### Transform Mapping (New Functionality)
When users want to modify colors during mapping, they use an array syntax where the first element is the source color and subsequent elements are transformations:

```toml
[waybar.colors]
bar-bg = ["bg-primary", "opacity=0.8"]
active-module = ["accent-primary", "brightness=1.2", "saturation=0.8"]
dim-text = ["text-secondary", "brightness=0.7"]
```

The system automatically detects the format:
- String value = simple mapping
- Array value = source color + transformations

### Supported Transformations

#### Essential Transformations

##### Brightness Adjustment
Controls the overall lightness or darkness of a color. Values range from 0.0 (completely black) to 2.0+ (much brighter), with 1.0 being unchanged.

**Use Cases:**
- Creating subtle background variants
- Adjusting text contrast
- Making hover states lighter/darker

**Examples:**
- `brightness=0.8` - 20% darker
- `brightness=1.3` - 30% brighter

##### Saturation Control
Adjusts how vibrant or muted a color appears. Values range from 0.0 (completely gray) to 2.0+ (highly saturated), with 1.0 being unchanged.

**Use Cases:**
- Creating muted accent variants
- Making colors more or less vivid
- Generating subtle background tones

**Examples:**
- `saturation=0.4` - More muted/gray
- `saturation=1.5` - More vibrant

##### Opacity/Alpha Channel
Controls transparency level. Values range from 0.0 (completely transparent) to 1.0 (fully opaque).

**Use Cases:**
- Transparent backgrounds
- Overlay effects
- Modern glass-morphism aesthetics
- Subtle color bleeding

**Examples:**
- `opacity=0.8` - 20% transparent
- `opacity=0.3` - Mostly transparent overlay

##### Hue Shifting
Rotates the color around the color wheel. Values are in degrees from -360 to +360.

**Use Cases:**
- Creating color harmonies
- Generating complementary colors
- Fine-tuning color temperature
- Creating themed variations

**Examples:**
- `hue=30` - Shift toward yellow/orange
- `hue=-45` - Shift toward blue/purple
- `hue=180` - Complete opposite color

#### Advanced Transformations

##### Temperature Adjustment
A more intuitive way to make colors warmer (more red/orange) or cooler (more blue). Values range from -100 to +100.

**Use Cases:**
- Matching color temperature across themes
- Creating warm/cool variants
- Seasonal theme adjustments

**Examples:**
- `temperature=20` - Warmer, more orange
- `temperature=-15` - Cooler, more blue

##### Contrast Enhancement
Adjusts color contrast relative to typical backgrounds. Values range from 0.0 to 2.0+, with 1.0 being unchanged.

**Use Cases:**
- Improving accessibility
- Better text readability
- High contrast themes

**Examples:**
- `contrast=1.4` - Higher contrast
- `contrast=0.7` - Lower contrast

### Mixed Configuration Examples

#### Waybar with Progressive Enhancement
```toml
[waybar.colors]
# Simple mappings for standard elements
workspace-text = "text-primary"
border-color = "border-active"
error-color = "error-color"

# Enhanced mappings for custom styling
bar-background = ["bg-primary", "opacity=0.85"]
active-workspace = ["accent-primary", "brightness=1.1"]
inactive-workspace = ["bg-secondary", "brightness=0.7"]
urgent-workspace = ["error-color", "opacity=0.9", "brightness=0.8"]
hover-effect = ["accent-primary", "opacity=0.6"]
```

#### Transformation Template Integration
```toml
[dunst]
enabled = true
template = "dunst.template"
syntax = "{placeholder}"

[dunst.placeholders]
col1 = ["accent-primary", "brightness=0.9"]
col2 = ["bg-primary", "opacity=0.8"]
col3 = ["bg-secondary", "brightness=1.1"]
text1 = "text-primary"
text2 = ["text-primary", "contrast=1.3"]
error = ["error-color", "brightness=0.8", "opacity=0.9"]
warning = "warning-color"
```

### Complex Multi-Application Setup
```toml
[hyprland.colors]
active-border = ["accent-primary", "brightness=1.2"]
inactive-border = ["bg-tertiary", "brightness=0.8"]
urgent-border = ["error-color", "saturation=0.8"]

[rofi.colors]
background = ["bg-primary", "opacity=0.9"]
selected = ["accent-primary", "brightness=1.1", "opacity=0.8"]
text = "text-primary"
text-selected = ["text-primary", "contrast=1.2"]
border = ["accent-primary", "brightness=0.9"]
```

### Processing Logic

#### Automatic Format Detection
The system examines each color mapping value and automatically determines the processing method:

1. **String Detection**: If the value is a simple string, treat it as direct semantic mapping
2. **Array Detection**: If the value is an array, treat the first element as source and remaining elements as transformations
3. **Validation**: Ensure source color exists in semantic palette and transformations are valid

#### Transform Application Order
Transformations are applied in a specific order to ensure predictable results:

1. **Color Space Conversion**: Convert to appropriate working color space (HSL/LAB)
2. **Hue Adjustments**: Apply hue shifts first
3. **Temperature Adjustments**: Apply warm/cool modifications
4. **Saturation Changes**: Modify color vibrancy
5. **Brightness/Lightness**: Adjust luminosity
6. **Contrast Enhancement**: Apply contrast modifications
7. **Opacity Application**: Set alpha channel last
8. **Format Conversion**: Convert to target application's color format

#### Error Handling and Validation

##### Invalid Source Colors
When a specified source color doesn't exist in the semantic palette:
- Generate clear error message indicating available colors
- Fall back to closest semantic color if possible
- Provide suggestions for likely intended colors

##### Invalid Transformation Values
When transformation parameters are out of valid ranges:
- Clamp values to acceptable ranges with warnings
- Provide clear feedback about acceptable value ranges
- Continue processing other valid transformations

##### Malformed Transformation Syntax
When transformation strings don't follow the expected format:
- Generate helpful error messages with correct syntax examples
- Skip malformed transformations while processing valid ones
- Suggest corrections for common mistakes

##### Missing Template File
If a template file specified in an application's configuration (e.g., `template = "my-theme.template"`) is not found in the `templates/` directory:
- Generate a clear error message indicating the missing file path.
- Skip all processing for that specific application.

### Master Configuration Format
```toml
[global]
wallpaper-command = "swww img \"{wallpaper_path}\""  # or "feh --bg-scale \"{wallpaper_path}\"", etc.
theme-type = "auto"             # auto, light, dark (overridden by --theme CLI flag)
reload-commands = [             #optional
    "hyprctl reload",
    "killall -USR1 waybar", 
    "pkill -USR1 dunst"
]

### Wallpaper Command Execution
The `wallpaper-command` is executed immediately after the configuration is validated, before color extraction begins. Luminol automatically replaces the `{wallpaper_path}` placeholder in the command with the absolute path to the source image. If this key is empty or not defined, only colors are generated and no wallpaper is set by the tool.

### Configuration Precedence
Settings provided via CLI arguments (e.g., `--theme`) will always override the corresponding values in the `config.toml` file.

# Application Configurations with Custom Mapping
[waybar]
enabled = true                  #needs to be defined 
remap-colors = true             #optional default = false
file = "~/.config/waybar/colors.css" #needs to be defined cant be empty
syntax = "@define-color {name} {color};" #needs to be defined
color_format = "rgba"

[waybar.colors]                 #needs to be defined when remap-colors is true
theme-background = "bg-primary"
theme-text       = "text-primary"
theme-accent     = "accent-primary"

[hyprland]
enabled = true
color_format = "rgba"
file = "~/.config/hypr/colors.conf"
syntax = "${name} = {color}"
remap-colors = true

[hyprland.colors]
active-border = "accent-primary"
inactive-border = ["bg-tertiary", "brightness=0.8"]
urgent-border = ["error-color", "saturation=0.8"]

# Application Configurations with Default Mapping
[rofi]
enabled = true
# remap-colors not defined → defaults to false
file = "~/.config/rofi/colors.rasi"
syntax = "*{{name}}: {color};"
color_format = "hex8"

[gtk]
enabled = true
color_format = "hex6"
file = "~/.config/gtk-3.0/colors.css"
syntax = "@define-color {name} {color};"

[dunst]
enabled = true
color_format = "hex6"
file = "~/.config/dunst/dunstrc"
syntax = "{placeholder}"
template = "i3.template"                      # Must be in `$XDG_CONFIG_HOME/luminol/templates/`
```

### Template Resolution Logic
```
Template Path Resolution:
- All template files must be located in `$XDG_CONFIG_HOME/luminol/templates/` (or `$HOME/.config/luminol/templates/` if unset).
- Only specify the filename in the configuration
- Luminol will automatically look in the templates directory

Examples:
- "dunst.template" → `$XDG_CONFIG_HOME/luminol/templates/dunst.template`
- "i3.template" → `$XDG_CONFIG_HOME/luminol/templates/i3.template`
- "custom.template" → `$XDG_CONFIG_HOME/luminol/templates/custom.template`

# Template placeholder mappings for template-based applications
[dunst.placeholders]
col1 = "accent-primary"
col2 = "bg-primary"
col3 = "bg-secondary"
text1 = "text-primary"
text2 = "text-secondary"
error = "error-color"
warning = "warning-color"

[i3]
enabled = false
color_format = "hex6"
file = "~/.config/i3/config"
syntax = "{placeholder}"
template = "i3.template"                      # Must be in ~/.config/luminol/templates/

[i3.placeholders]
focused = "accent-primary"
unfocused = "bg-secondary"
urgent = "error-color"
background = "bg-primary"
text = "text-primary"
```

### Color Format Support
```python
SUPPORTED_FORMATS = {
    "hex6": "#ff5733",                    # #RRGGBB
    "hex8": "#ff5733ff",                  # #RRGGBBAA
    "rgb": "rgb(255, 87, 51)",           # CSS rgb()
    "rgba": "rgba(255, 87, 51, 1.0)",    # CSS rgba()
    "rgb_decimal": "255,87,51",           # Comma-separated
    "rgba_decimal": "255,87,51,1.0",      # With alpha
}
```

### Semantic Color Names
The system generates these semantic color assignments:
- `bg-primary`, `bg-secondary`, `bg-tertiary` - Background colors
- `text-primary`, `text-secondary` - Text colors
- `accent-primary`, `accent-secondary` - Accent colors
- `error-color`, `warning-color`, `success-color` - Status colors
- `border-active`, `border-inactive` - Border colors

## Template System

### Directory Structure
```
luminol/
├── src/
│   ├── __init__.py
│   ├── config/
│   ├── colors/
│   ├── generators/
│   ├── remap/
│   ├── templates/
│   ├── extraction/
│   ├── cli/
│   └── luminol.py
├── tests/
├── docs/
├── examples/
└── pyproject.toml
```

# User configuration directory (`$XDG_CONFIG_HOME/luminol` or `$HOME/.config/luminol`)
`$XDG_CONFIG_HOME/luminol/`
├── config.toml                   # User configuration
└── templates/                    # User-provided template files
    ├── dunst.template
    ├── i3.template
    ├── sway.template
    └── custom.template
```

### Template Examples

#### Dunst Template (`templates/dunst.template`)
```ini
[global]
monitor = 0
follow = mouse
shrink = no
padding = 12
horizontal_padding = 12

width = 400
height = (70, 500)
offset = (16,60)
origin = top-right

frame_width = 2
separator_height = 2
frame_color = "{col1}"
separator_color = frame
gap_size = 10

sort = no
font = JetBrainsMono Nerd Font 13
markup = full
format = "<b>%s</b>\n%b"
alignment = left
show_age_threshold = 60
word_wrap = yes
ignore_newline = no
stack_duplicates = no
hide_duplicate_count = no
show_indicators = yes

icon_position = left
max_icon_size = 60
sticky_history = no
history_length = 6
corner_radius = 8

mouse_left_click = do_action,close_current
mouse_middle_click = close_current
mouse_right_click = close_all

[urgency_low]
background = "{col2}"
foreground = "{text1}"
timeout = 10

[urgency_normal]
background = "{col3}"
foreground = "{text1}"
timeout = 10

[urgency_critical]
background = "{error}"
foreground = "{text2}"
timeout = 0
```

#### i3 Template (`templates/i3.template`)
```
# i3 config file (v4)
# Color scheme from wallpaper

# class                 border       backgr.      text      indicator      child_border
client.focused          {focused}    {focused}    {text}    {focused}      {focused}
client.focused_inactive {unfocused}  {unfocused}  {text}    {unfocused}    {unfocused}
client.unfocused        {unfocused}  {background} {text}    {unfocused}    {unfocused}
client.urgent           {urgent}     {urgent}     {text}    {urgent}       {urgent}
client.placeholder      {background} {background} {text}    {background}   {background}

client.background       {background}

# Bar colors
bar {
    status_command i3status
    colors {
        background {background}
        statusline {text}
        separator {unfocused}

        focused_workspace  {focused} {focused} {text}
        active_workspace   {unfocused} {unfocused} {text}
        inactive_workspace {background} {background} {text}
        urgent_workspace   {urgent} {urgent} {text}
        binding_mode       {urgent} {urgent} {text}
    }
}
```

## Processing Pipeline

### Configuration Processing Steps
```
1. Load master config.toml
2. Extract colors from wallpaper using algorithms
3. Generate standard semantic palette:
   - bg-primary, bg-secondary, bg-tertiary
   - text-primary, text-secondary
   - accent-primary, accent-secondary
   - error-color, warning-color, success-color
   - border-active, border-inactive

4. For each enabled application:
   a. Check processing mode:
      - remap-colors = true: Use custom mapping from [app.colors]
      - remap-colors = false (default): Use all semantic names
   b. Check output type:
      - Template-based: Load template + mapping, substitute placeholders
      - Syntax-based: Generate color definitions using syntax format
   c. Apply appropriate color format conversion
   d. Write to specified file location

5. Execute reload commands
```

### Processing Logic Summary

1. **Extract wallpaper palette → semantic colors** (Standard semantic palette generation).
2. **For each app section** in config:
   * If `remap-colors = true` → use `[app.colors]` mapping with custom names.
   * If `remap-colors = false` (default) → directly export all semantic names.

### Export Behavior Summary

* **Default behavior (remap-colors = false):** App gets the **full semantic palette** as-is with canonical names.
* **Opt-in behavior (remap-colors = true):** App gets **only the colors explicitly mapped** in `[app.colors]`, renamed to whatever user defines.

### Processing Types
- **Syntax-based** (waybar, hyprland, rofi, gtk): Generate simple variable definitions using syntax pattern
- **Template-based** (dunst, i3): Complete file generation with placeholder substitution

## Output Examples

### Waybar Output (remap-colors = true)
Config asked for custom aliases (`theme-background`, `theme-text`, `theme-accent`). So output file is:

```css
@define-color theme-background #1e1e2e;
@define-color theme-text #cdd6f4;
@define-color theme-accent #8af4da;
```

Only mapped colors appear, with user-defined names.

### Rofi Output (remap-colors = false, default)
Rofi doesn't set `remap-colors`. So it directly exports **all semantic names**:

```css
*{bg-primary: #1e1e2e;}
*{bg-secondary: #313244;}
*{bg-tertiary: #45475a;}
*{text-primary: #cdd6f4;}
*{text-secondary: #bac2de;}
*{accent-primary: #8af4da;}
*{accent-secondary: #f38ba8;}
*{error-color: #f38ba8;}
*{warning-color: #f9e2af;}
*{success-color: #a6e3a1;}
*{border-active: #cdd6f4;}
*{border-inactive: #313244;}
```

No remapping → exports everything with canonical names.

### Legacy Examples (Full Semantic Export)

#### Full Waybar Output (`~/.config/waybar/colors.css`)
```css
@define-color bg-primary rgba(30,30,46,1.0);
@define-color bg-secondary rgba(49,50,68,1.0);
@define-color bg-tertiary rgba(69,71,90,1.0);
@define-color text-primary rgba(205,214,244,1.0);
@define-color text-secondary rgba(186,194,222,1.0);
@define-color accent-primary rgba(138,244,218,1.0);
@define-color accent-secondary rgba(243,139,168,1.0);
@define-color error-color rgba(243,139,168,1.0);
@define-color warning-color rgba(249,226,175,1.0);
@define-color success-color rgba(166,227,161,1.0);
```

### Hyprland Output (`~/.config/hypr/colors.conf`)
```
$bg-primary = rgba(30,30,46,1.0)
$bg-secondary = rgba(49,50,68,1.0)
$bg-tertiary = rgba(69,71,90,1.0)
$text-primary = rgba(205,214,244,1.0)
$text-secondary = rgba(186,194,222,1.0)
$accent-primary = rgba(138,244,218,1.0)
$accent-secondary = rgba(243,139,168,1.0)
$error-color = rgba(243,139,168,1.0)
$warning-color = rgba(249,226,175,1.0)
$success-color = rgba(166,227,161,1.0)
```

#### Full Rofi Output (`~/.config/rofi/colors.rasi`)
```css
*{bg-primary: #1e1e2eff;}
*{bg-secondary: #313244ff;}
*{bg-tertiary: #45475aff;}
*{text-primary: #cdd6f4ff;}
*{text-secondary: #bac2deff;}
*{accent-primary: #8af4daff;}
*{accent-secondary: #f38ba8ff;}
*{error-color: #f38ba8ff;}
*{warning-color: #f9e2afff;}
*{success-color: #a6e3a1ff;}
```

### GTK Output (`~/.config/gtk-3.0/colors.css`)
```css
@define-color bg-primary #1e1e2e;
@define-color bg-secondary #313244;
@define-color bg-tertiary #45475a;
@define-color text-primary #cdd6f4;
@define-color text-secondary #bac2de;
@define-color accent-primary #8af4da;
@define-color accent-secondary #f38ba8;
@define-color error-color #f38ba8;
@define-color warning-color #f9e2af;
@define-color success-color #a6e3a1;
```

### Dunst Output (`~/.config/dunst/dunstrc`) - Complete file from template
```ini
[global]
monitor = 0
follow = mouse
shrink = no
padding = 12
horizontal_padding = 12

width = 400
height = (70, 500)
offset = (16,60)
origin = top-right

frame_width = 2
separator_height = 2
frame_color = "#8af4da"
separator_color = frame
gap_size = 10

sort = no
font = JetBrainsMono Nerd Font 13
markup = full
format = "<b>%s</b>\n%b"
alignment = left
show_age_threshold = 60
word_wrap = yes
ignore_newline = no
stack_duplicates = no
hide_duplicate_count = no
show_indicators = yes

icon_position = left
max_icon_size = 60
sticky_history = no
history_length = 6
corner_radius = 8

mouse_left_click = do_action,close_current
mouse_middle_click = close_current
mouse_right_click = close_all

[urgency_low]
background = "#1e1e2e"
foreground = "#cdd6f4"
timeout = 10

[urgency_normal]
background = "#313244"
foreground = "#cdd6f4"
timeout = 10

[urgency_critical]
background = "#f38ba8"
foreground = "#bac2de"
timeout = 0
```

## Performance Optimization

### Processing Efficiency
```
Optimization Strategies:
1. Image Scaling: Process at optimal resolution (400-800px)
2. Pixel Sampling: Skip pixels for large images (every 4th-8th)
3. Early Termination: Stop clustering when convergence reached
4. Caching: Store intermediate results for similar images
5. Memory Management: Process in chunks for very large images

Target Performance:
- Small images (<1MB): <500ms
- Medium images (1-5MB): <1.5s  
- Large images (5-10MB): <3s
```

### Memory Management
```
Memory Optimization:
- Stream processing for large images
- Immediate cleanup of intermediate data
- Efficient color representation (16-bit vs 32-bit)
- Batch processing when handling multiple images
```

## Quality Assurance

### Validation Framework
```
Automated Testing:
1. Color Extraction Accuracy:
   - Test with standard color charts
   - Validate against known good results
   - Check consistency across runs

2. Accessibility Compliance:
   - WCAG contrast ratio verification
   - Color-blind simulation testing
   - Readability validation

3. Format Validation:
   - Generated configs parse correctly
   - Colors render as expected
   - Integration testing with target applications
```

### Error Handling
```
Robust Error Management:
1. Invalid Image Handling:
   - Graceful degradation for corrupted files
   - Fallback to default palette
   - Clear error reporting

2. Low Quality Input:
   - Detect low-contrast images
   - Generate artificial variety when needed
   - Warn about potential issues

3. Edge Cases:
   - Monochromatic images
   - Very dark/light images  
   - High noise images
```

## Command Line Interface
```
Usage: luminol [options] image_path

Options:
  -t, --theme THEME         Force theme type (light, dark). Overrides config file.
  -q, --quality LEVEL       Processing quality (fast, balanced, high).
  -v, --verbose             Enable verbose logging.
  -h, --help                Show this help message.

Examples:
  luminol wallpaper.jpg                    # Basic extraction
  luminol --theme dark image.jpg     # Force dark theme
```

## Integration Examples
```bash
# Automatic wallpaper-based theming
#!/bin/bash
WALLPAPER=$(cat ~/.current_wallpaper)
luminol "$WALLPAPER"

# Reload applications
hyprctl reload
killall -USR1 waybar
```

## Success Metrics

### Technical Targets
- **Processing Speed**: 95% of images processed under 2 seconds
- **Color Accuracy**: 90% user satisfaction with extracted colors
- **Accessibility**: 100% compliance with WCAG AA contrast standards
- **Format Coverage**: Support for 8+ major Linux desktop applications
- **Reliability**: <1% failure rate on valid image inputs

### User Experience Goals
- **Ease of Use**: Single command generates complete theme
- **Consistency**: Colors work harmoniously across all applications
- **Customization**: Easy manual adjustment when needed
- **Integration**: Seamless workflow with existing desktop setups

