# Configuration System

Luminol is controlled by a single configuration file, `config.toml`, located in `$XDG_CONFIG_HOME/luminol/`. This file allows you to enable, disable, and customize the output for various applications.

## Master Configuration Format

The configuration is composed of a `[global]` section and individual sections for each application (e.g., `[waybar]`, `[rofi]`).

```toml
# Global settings for Luminol
[global]
wallpaper-command = "swww img {wallpaper_path}"  #Optional
# Command to set the wallpaper. This is the first command executed after the configuration is loaded.
# The {wallpaper_path} placeholder is replaced with the image path.
# If it is empty or not defined, no wallpaper is set by the tool.

theme-type = "auto" # auto, light, dark (overridden by --theme CLI flag)

reload-commands = [ # Optional 
    #commands to run after generation and copy of color files
    "hyprctl reload",
    "killall -USR1 waybar",
]

# --- Application Configurations ---

[hyprland]
enabled = true
color-format = "rgba"
file = "~/.config/hypr/colors.conf"
syntax = "${name} = {color}"
remap-colors = true # Enable custom color mapping

# Custom color names for hyprland
[hyprland.colors]
active-border = "accent-primary" # only remmap without any transformation
inactive-border = ["bg-tertiary", "brightness=0.8"] # Remap with a transformation

[rofi]
enabled = true
color-format = "hex8"
# remap-colors is false by default, so it will get all semantic colors.
file = "~/.config/rofi/colors.rasi"
syntax = "*{{name}: {color};}"

[dunst]
enabled = true
color-format = "hex6"
file = "~/.config/dunst/dunstrc"
syntax = "{placeholder}" # This app uses a template file
template = "dunst.template"

# Placeholders to be replaced in the dunst.template file
[dunst.placeholders]
col1 = "accent-primary"
text1 = "text-primary"
error = "error-color"
```

### How the `syntax` Key Works

The `syntax` key is a template for each line in the generated file. Luminol replaces two special placeholders:
-   `{name}`: This is replaced by the color's name (e.g., `bg-primary`, or a custom name like `theme-background` if you are using `remap-colors`).
-   `{color}`: This is replaced by the final, calculated color value in the specified `color-format`.

**Example:**
Given this configuration:
```toml
[rofi]
color-format = "hex8"
syntax = "*{{name}: {color};}"
```
Luminol will generate lines like:
```css
*{bg-primary: #1e1e2eff;}
*{text-primary: #cdd6f4ff;}
```

**Key Parameters for each application:**
-   `enabled`: (Required) `true` or `false`.
-   `color-format`: (Required) The output format for colors (e.g., `hex8`, `rgba`).
-   `file`: (Required) The absolute path to the output file.
-   `syntax`: (Required) A pattern that defines how each color variable is written to the file.
-   `remap-colors`: (Optional) `true` or `false`. Defaults to `false`.
-   `template`: (Optional) The name of a template file to use.

## Semantic Palette

Regardless of configuration, Luminol **always** generates a standard set of 12 semantic colors. These are the source colors available for remapping and transformations.

-   **Backgrounds**: `bg-primary`, `bg-secondary`, `bg-tertiary`
-   **Text**: `text-primary`, `text-secondary`
-   **Accents**: `accent-primary`, `accent-secondary`
-   **Status**: `error-color`, `warning-color`, `success-color`
-   **Borders**: `border-active`, `border-inactive`

## Color Remapping and Transformations

This is Luminol's most powerful feature. For each application, you can choose one of two modes:

### Default Mode (`remap-colors = false`)

If `remap-colors` is `false` or not present, Luminol exports the **entire semantic palette** with the standard names.

### Custom Mapping Mode (`remap-colors = true`)

If `remap-colors = true`, you gain fine-grained control. You **must** provide an `[app.colors]` (or `[app.placeholders]`) table that defines your custom color names.

-   **Only mapped colors are exported.**
-   You can rename colors (e.g., `my-background = "bg-primary"`).
-   You can apply on-the-fly **transformations** to any source color.

#### Color Transformations

To apply a transformation, use an array syntax where the first element is the source color and subsequent elements are transformations:

`custom-name = ["source-color", "transformation1", "transformation2"]`

**Example**: A brighter, semi-transparent accent color.
`active-border = ["accent-primary", "brightness=1.2", "opacity=0.8"]`

##### Supported Transformations

###### Essential Transformations

**Brightness Adjustment**
Controls the overall lightness or darkness of a color. Values range from 0.0 (completely black) to 2.0+ (much brighter), with 1.0 being unchanged.

**Use Cases:**
- Creating subtle background variants
- Adjusting text contrast
- Making hover states lighter/darker

**Examples:**
- `brightness=0.8` - 20% darker
- `brightness=1.3` - 30% brighter

**Saturation Control**
Adjusts how vibrant or muted a color appears. Values range from 0.0 (completely gray) to 2.0+ (highly saturated), with 1.0 being unchanged.

**Use Cases:**
- Creating muted accent variants
- Making colors more or less vivid
- Generating subtle background tones

**Examples:**
- `saturation=0.4` - More muted/gray
- `saturation=1.5` - More vibrant

**Opacity/Alpha Channel**
Controls transparency level. Values range from 0.0 (completely transparent) to 1.0 (fully opaque).

**Use Cases:**
- Transparent backgrounds
- Overlay effects
- Modern glass-morphism aesthetics
- Subtle color bleeding

**Examples:**
- `opacity=0.8` - 20% transparent
- `opacity=0.3` - Mostly transparent overlay

**Hue Shifting**
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

###### Advanced Transformations

**Temperature Adjustment**
A more intuitive way to make colors warmer (more red/orange) or cooler (more blue). Values range from -100 to +100.

**Use Cases:**
- Matching color temperature across themes
- Creating warm/cool variants
- Seasonal theme adjustments

**Examples:**
- `temperature=20` - Warmer, more orange
- `temperature=-15` - Cooler, more blue

**Contrast Enhancement**
Adjusts color contrast relative to typical backgrounds. Values range from 0.0 to 2.0+, with 1.0 being unchanged.

**Use Cases:**
- Improving accessibility
- Better text readability
- High contrast themes

**Examples:**
- `contrast=1.4` - Higher contrast
- `contrast=0.7` - Lower contrast

## Supported Color Formats

Luminol can output colors in various formats, specified by the `color-format` key:

```python
{
    "hex6": "#ff5733",         # #RRGGBB
    "hex8": "#ff5733ff",       # #RRGGBBAA
    "rgb": "rgb(255, 87, 51)",
    "rgba": "rgba(255, 87, 51, 1.0)",
    "rgb_decimal": "255,87,51",
    "rgba_decimal": "255,87,51,1.0",
}
```

```
