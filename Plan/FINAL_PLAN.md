# Luminol Configuration and Plan

This document outlines the configuration, color palettes, and template system for Luminol.

## Available Semantic Colors

Luminol generates a standard set of UI and terminal colors. These names are used as source colors in your configuration.

### UI Semantic Colors

These **13 colors** are the foundation of the theming system.

<!-- prettier-ignore -->
```
bg-primary
bg-secondary
bg-tertiary
text-primary
text-secondary
text-tertiary
accent-primary
accent-secondary
error-color
warning-color
success-color
border-active
border-inactive
```

### Terminal (ANSI) Colors

These **16 colors** are generated for terminal emulators and **can also be used as source colors** in templates and
custom mappings.

<!-- prettier-ignore -->
```
ansi-0    # Black
ansi-1    # Red
ansi-2    # Green
ansi-3    # Yellow
ansi-4    # Blue
ansi-5    # Magenta
ansi-6    # Cyan
ansi-7    # White
ansi-8    # Bright Black
ansi-9    # Bright Red
ansi-10   # Bright Green
ansi-11   # Bright Yellow
ansi-12   # Bright Blue
ansi-13   # Bright Magenta
ansi-14   # Bright Cyan
ansi-15   # Bright White
```

**Total Available Source Colors**: 29 (13 UI + 16 ANSI)

## Configuration (`config.toml`)

Luminol is controlled by `config.toml` located in `$XDG_CONFIG_HOME/luminol/`.

### Global Settings

```toml
[global]
# Command template for setting the wallpaper.
# The placeholder {wallpaper_path} will be replaced with the actual image path.
# Placeholder is optional
# Example:
#   wallpaper-command = "swww img {wallpaper_path}"
#   wallpaper-command = "feh --bg-fill {wallpaper_path}"
wallpaper-command = "swww img {wallpaper_path}"
# it can be empty if you dont want to set wallpaper through luminol

# defaults to 'auto'
theme-type = "dark" # can be "auto","light" or "dark"

# Commands to run after wallpaper change (e.g., reload bars, compositors, etc.)
# These run sequentially after applying the wallpaper.
reload-commands = ["hyprctl reload", "killall -USR1 waybar"]
# it can be empty

# Whether to execute reload commands using the system shell.
# Default: false
use-shell = false

# Default: false
tty-reload = false # this will reload the tty colors, will be implemented in later version

# If true, stdout and stderr from reload commands and wallpaper command will be sent to a log file.
# Default: false
log-output = false
# Logs for each run are saved to a unique, timestamped directory:
# Path: $XDG_STATE_HOME/luminol/logs/YYYY-MM-DD_HH-MM-SS/<command>.log
# (defaults to ~/.local/state/luminol/logs/... if XDG_STATE_HOME is not set)
#
# Log Cleanup: To prevent logs from filling up disk space, directories older
# than 7 days are automatically deleted each time Luminol runs.

# ---------------------------------------------------------------------
# 🔧 Shell Execution Details
# ---------------------------------------------------------------------
# When use-shell = true:
#   - Commands are executed using the system shell (e.g., bash, zsh).
#   - Enables shell-specific syntax:
#       * Pipes (|), command chains (&&, ||)
#       * Environment variable expansion ($VAR)
#       * Redirection (> /dev/null 2>&1)
#   - Useful for complex reload or restart sequences.
#
# ⚠️ Risks:
#   - Can be a **security risk** if commands come from untrusted sources.
#   - Misused shell features can cause unexpected behavior or hanging.
#
# ✅ Recommended Usage:
#   - Keep `use-shell = false` for simple commands (safer, faster).
#   - Enable `use-shell = true` **only** when shell features are needed.
#
# ---------------------------------------------------------------------
# 💡 Examples
# ---------------------------------------------------------------------

# ✅ Safe, simple reloads (no shell features needed):
#   reload-commands = [
#       "hyprctl reload",
#       "killall waybar",
#       "waybar"
#   ]

# ⚙️ Complex reloads (requires shell=True):
#   reload-commands = [
#       "pkill waybar; setsid waybar",          # Restart detached
#       "pkill dunst; nohup dunst &",           # Run in background safely
#       "waybar </dev/null &>/dev/null &",      # Background, ignore I/O
#       "hyprctl reload"                        # Quick synchronous reload
#   ]

# - For simple reloads, prefer `use-shell = false` and list commands separately.
```

### Application Settings

Each application has its own section (e.g., `[rofi]`, `[dunst]`).

**Key Parameters:**

- `enabled`: (Required) `true` or `false`.
- `output-file`: (Required) Path to the output file.
    - If this is a full path (e.g., `~/.config/rofi/colors.rasi`), the file is written there.
    - If this is just a filename (e.g., `rofi.css`), the palette is stored in the cache at
      `$XDG_CACHE_HOME/luminol/<app_name>/<filename>`. defaults to ~/.cache/luminol/.. if not set.
- `color-format`: (Required) The output format for colors.
    - **Valid values**: `hex6`, `hex8`, `rgb`, `rgba`, `rgb_decimal`, `rgba_decimal`
    - Alpha channel in formats like `hex6` and `rgb` is ignored; use `hex8`, `rgba`, or `rgba_decimal` for transparency
      support.
- `syntax`: (Required) A pattern that defines how content is generated.
- `template`: (Optional) The path to a template file. If this is set, Template Mode is activated.
    - If `template` is a **filename** (e.g., `colors.rasi`, `style.css`), it must be located in
      `$XDG_CONFIG_HOME/luminol/templates/`. **Clarification**: When only a filename is provided, Luminol assumes the
      template resides in the standard templates directory (`$XDG_CONFIG_HOME/luminol/templates/`).
    - If `template` is an **absolute path** (e.g., `/home/user/.config/my_templates/custom.template`), it will be used
      directly.
- `remap-colors`: (Optional) `true` or `false`. Defaults to `false`. This is the master switch for custom mapping.

---

## Understanding Syntax and Placeholders

Before diving into the color generation modes, it's crucial to understand how the `syntax` parameter works and what
placeholders are.

### What is Syntax?

The `syntax` parameter is a **pattern template** that tells Luminol how to format each line of output in your generated
color file. Think of it as a recipe that defines the structure of each color definition.

### What are Placeholders?

Placeholders are **special keywords** that Luminol replaces with actual values when generating your color files. There
are different types of placeholders depending on which mode you're using:

#### Universal Placeholders (used in syntax patterns)

- `{name}` - Replaced with the color's variable name
- `{color}` - Replaced with the actual color value in your specified format
- `{placeholder}` - A special keyword used ONLY in Template Mode (explained below)

### How Syntax Works: Detailed Examples

Let's break down syntax patterns step by step:

#### Example 1: Basic CSS Variable Syntax

```toml
syntax = "--{name}: {color};"
color-format = "hex6"
```

**What happens:**

- Luminol reads this pattern
- For each color, it replaces `{name}` with the color's name
- It replaces `{color}` with the color value in hex6 format
- Each line follows this exact pattern

**Generated output:**

```css
--bg-primary: #1e1e2e;
--bg-secondary: #2a2a3a;
--text-primary: #e0e0e0;
```

#### Example 2: Shell/Config Variable Syntax

```toml
syntax = "${name} = {color}"
color-format = "rgb"
```

**Generated output:**

```bash
$bg-primary = rgb(30, 30, 46)
$bg-secondary = rgb(42, 42, 58)
$text-primary = rgb(224, 224, 224)
```

#### Example 3: Rofi/SCSS Syntax

```toml
syntax = "*{{name}: {color};}"
color-format = "hex8"
```

**Generated output:**

<!-- prettier-ignore -->
```css
*{bg-primary: #1e1e2eff;}
*{bg-secondary: #2a2a3aff;}
*{text-primary: #e0e0e0ff;}
```

#### Example 4: TOML/INI Syntax

```toml
syntax = "{name} = \"{color}\""
color-format = "hex6"
```

**Generated output:**

```toml
bg-primary = "#1e1e2e"
bg-secondary = "#2a2a3a"
text-primary = "#e0e0e0"
```

#### Example 5: JSON-like Syntax

```toml
syntax = "  \"{name}\": \"{color}\","
color-format = "rgba"
```

**Generated output:**

```json
  "bg-primary": "rgba(30, 30, 46, 1.0)",
  "bg-secondary": "rgba(42, 42, 58, 1.0)",
  "text-primary": "rgba(224, 224, 224, 1.0)",
```

#### Example 6: Python Dictionary Syntax

```toml
syntax = "    '{name}': '{color}',"
color-format = "hex6"
```

**Generated output:**

```python
    'bg-primary': '#1e1e2e',
    'bg-secondary': '#2a2a3a',
    'text-primary': '#e0e0e0',
```

#### Example 7: Syntax with Only {color} (no names)

```toml
syntax = "COLOR: {color};"
color-format = "rgb_decimal"
```

**Generated output:**

```
COLOR: (240, 21, 15);
COLOR: (240, 16, 20);
COLOR: (0, 0, 88);
```

#### Example 8: Syntax with Only {name} (no color values)

```toml
syntax = "export const {name};"
```

**Generated output:**

```javascript
export const bg-primary;
export const bg-secondary;
export const text-primary;
```

#### Example 9: Syntax with Neither Placeholder

```toml
syntax = "/* Color entry */"
```

**Generated output:**

```css
/* Color entry */
/* Color entry */
/* Color entry */
```

This creates one line per color, but all lines are identical. This is rarely useful but demonstrates the flexibility.

#### Example 10: Complex Multi-Part Syntax

```toml
syntax = "@define-color {name} {color}; /* Theme color */"
color-format = "hex6"
```

**Generated output:**

```css
@define-color bg-primary #1e1e2e; /* Theme color */
@define-color bg-secondary #2a2a3a; /* Theme color */
@define-color text-primary #e0e0e0; /* Theme color */
```

### Using Literal Curly Braces in Syntax

Sometimes you need literal curly braces in your output. Only `{name}`, `{color}`, and `{placeholder}` are treated as
special keywords. Any other text enclosed in single curly braces will be treated as a literal string.

```toml
# To get literal {static}, simply use single braces
syntax = "color: {static}; var: {color};"
```

**Generated output:**

```css
color: {static}; var: #1e1e2e;
color: {static}; var: #2a2a3a;
```

---

## Color Generation Modes

Luminol has three main modes for generating color files. They are processed in this order of priority:

### Mode Priority Order

1. **Template Mode** - Activated if `template` key is present
2. **Custom Mapping Mode** - Activated if `remap-colors = true` and no template
3. **Default Mode** - Used when neither template nor remap-colors is enabled

---

### ⚠️ Important: Understanding Generation Modes and File Formats

#### A Note on the Examples

The configuration snippets and output shown in this document are for **illustration purposes**. While they aim to be
realistic, always refer to the official documentation for each application to ensure you are using the correct syntax.

#### Choosing the Right Mode for Your File Format

The best mode to use depends on how your target application handles its configuration.

**1. Use Default or Custom Mapping Mode when...**

Your application supports importing or sourcing a separate file for colors. This is the most common and recommended
workflow.

- **How it works:** You generate a simple, color-only file (e.g., `colors.css`, `colors.conf`) and then use an import
  statement in your main application config to load it.
- **Examples:**
    - **Waybar/Rofi:** Use `@import "colors.css";` in your `style.css`.
    - **Hyprland:** Use `source = ~/.config/hypr/colors.conf` in your `hyprland.conf`.
    - **Kitty:** Use `include ./colors.conf` in your `kitty.conf`.
- **Benefit:** This keeps your color definitions separate from your main configuration, making it cleaner and easier to
  manage. You avoid the "burden of templates."

**2. Use Template Mode when...**

Your application's configuration is a single, monolithic file that does not support imports.

- **How it works:** You use your entire application config file as a template, and Luminol replaces color placeholders
  within it, generating a new, complete config file.
- **Use Cases:**
    - An application that requires all settings to be in one file.
    - You prefer to manage a single configuration file instead of multiple.
    - The file format is complex (like JSON or YAML) and requires specific wrappers (`{...}`) that Default Mode cannot
      create.

---

## Mode 1: Default Mode

This is the **simplest mode** and the fallback when neither `template` is set nor `remap-colors` is `true`.

### What It Does

- Exports the **entire 13-color UI semantic palette** automatically
- **ANSI colors are NOT exported** (only the 13 UI colors)
- Uses your `syntax` pattern to format each color
- Perfect for simple color file generation

### Key Characteristics

- ✅ No additional configuration needed beyond basic parameters
- ✅ All 13 UI semantic colors are included automatically
- ✅ Simple and quick to set up
- ❌ No customization of color names
- ❌ Cannot include ANSI terminal colors
- ❌ Cannot apply transformations

### Configuration Parameters

```toml
[app_name]
enabled = true                          # Required
output-file = "/path/to/output"         # Required
color-format = "hex6"                   # Required: hex6, hex8, rgb, rgba, rgb_decimal,rgba_decimal
syntax = "*{{name}: {color};}"          # Required: pattern with {name} and/or {color}
# remap-colors defaults to false
# template is not set
```

### The syntax Parameter in Default Mode

In Default Mode, the `syntax` can contain:

- `{name}` - Will be replaced with the semantic color name
- `{color}` - Will be replaced with the color value
- Both, one, or neither (though including both is most common)

### Example 1: Basic Rofi Configuration

```toml
[rofi]
enabled = true
output-file = "~/.config/rofi/colors.rasi"
color-format = "hex8"
syntax = "*{{name}: {color};}"
```

**Generated output (`colors.rasi`):**

<!-- prettier-ignore -->
```css
*{bg-primary: #1e1e2eff;}
*{bg-secondary: #2a2a3aff;}
*{bg-tertiary: #3a3a4aff;}
*{text-primary: #e0e0e0ff;}
*{text-secondary: #b0b0b0ff;}
*{text-tertiary: #808080ff;}
*{accent-primary: #6495ffff;}
*{accent-secondary: #ff6495ff;}
*{error-color: #ff4444ff;}
*{warning-color: #ffaa44ff;}
*{success-color: #44ff44ff;}
*{border-active: #6495ffff;}
*{border-inactive: #404040ff;}
```

### Example 2: CSS Custom Properties

```toml
[gtk]
enabled = true
output-file = "~/.config/gtk-3.0/colors.css"
color-format = "rgb"
syntax = "--{name}: {color};"
```

**Generated output (`colors.css`):**

```css
--bg-primary: rgb(30, 30, 46);
--bg-secondary: rgb(42, 42, 58);
--bg-tertiary: rgb(58, 58, 74);
--text-primary: rgb(224, 224, 224);
--text-secondary: rgb(176, 176, 176);
--text-tertiary: rgb(128, 128, 128);
--accent-primary: rgb(100, 149, 255);
--accent-secondary: rgb(255, 100, 149);
--error-color: rgb(255, 68, 68);
--warning-color: rgb(255, 170, 68);
--success-color: rgb(68, 255, 68);
--border-active: rgb(100, 149, 255);
--border-inactive: rgb(64, 64, 64);
```

### Example 3: Shell Variables

```toml
[shell]
enabled = true
output-file = "~/.config/shell/colors.sh"
color-format = "hex6"
syntax = "export {name}=\"{color}\""
```

**Generated output (`colors.sh`):**

```bash
export bg-primary="#1e1e2e"
export bg-secondary="#2a2a3a"
export bg-tertiary="#3a3a4a"
export text-primary="#e0e0e0"
export text-secondary="#b0b0b0"
export text-tertiary="#808080"
export accent-primary="#6495ff"
export accent-secondary="#ff6495"
export error-color="#ff4444"
export warning-color="#ffaa44"
export success-color="#44ff44"
export border-active="#6495ff"
export border-inactive="#404040"
```

### Example 4: GTK Color Scheme Format

```toml
[gtk-scheme]
enabled = true
output-file = "~/.themes/MyTheme/gtk.css"
color-format = "hex6"
syntax = "@define-color {name} {color};"
```

**Generated output:**

```css
@define-color bg-primary #1e1e2e;
@define-color bg-secondary #2a2a3a;
@define-color bg-tertiary #3a3a4a;
@define-color text-primary #e0e0e0;
@define-color text-secondary #b0b0b0;
@define-color text-tertiary #808080;
@define-color accent-primary #6495ff;
@define-color accent-secondary #ff6495;
@define-color error-color #ff4444;
@define-color warning-color #ffaa44;
@define-color success-color #44ff44;
@define-color border-active #6495ff;
@define-color border-inactive #404040;
```

### Example 5: SCSS Variables

```toml
[scss]
enabled = true
output-file = "~/.config/styles/_colors.scss"
color-format = "rgba"
syntax = "${name}: {color};"
```

**Generated output (`_colors.scss`):**

```scss
$bg-primary: rgba(30, 30, 46, 1);
$bg-secondary: rgba(42, 42, 58, 1);
$bg-tertiary: rgba(58, 58, 74, 1);
$text-primary: rgba(224, 224, 224, 1);
$text-secondary: rgba(176, 176, 176, 1);
$text-tertiary: rgba(128, 128, 128, 1);
$accent-primary: rgba(100, 149, 255, 1);
$accent-secondary: rgba(255, 100, 149, 1);
$error-color: rgba(255, 68, 68, 1);
$warning-color: rgba(255, 170, 68, 1);
$success-color: rgba(68, 255, 68, 1);
$border-active: rgba(100, 149, 255, 1);
$border-inactive: rgba(64, 64, 64, 1);
```

### Important Notes for Default Mode

1. **[app.colors] table is ignored**: If you accidentally include a `[app.colors]` table, it will be silently ignored
   (no error, no warning).

2. **Only UI colors are exported**: The 13 semantic UI colors are exported, but ANSI terminal colors are not.

3. **No transformations possible**: You cannot modify colors with brightness, saturation, etc. in this mode.

4. **Fixed color set**: You always get all 13 colors - you cannot pick and choose which ones to include.

---

## Mode 2: Custom Mapping Mode (Default + Remap Enabled)

This mode gives you **full control** over which colors are exported, what they're named, and how they're transformed.

### What It Does

- Exports **only the colors you explicitly define** in the `[app.colors]` table
- Allows you to rename colors to match your application's naming conventions
- Supports all 29 source colors (13 UI + 16 ANSI)
- Enables on-the-fly color transformations (brightness, saturation, opacity, etc.)
- Uses your `syntax` pattern to format output

### Activation Requirements

```toml
remap-colors = true          # Must be set to true
# template is not set        # Template must not be specified
[app.colors]                 # This table is REQUIRED
# ... your color mappings
```

⚠️ **Error Condition**: If `remap-colors = true` but the `[app.colors]` table is missing, Luminol will raise a
configuration error.

### Key Characteristics

- ✅ Complete control over color selection
- ✅ Custom variable naming
- ✅ Access to all 29 source colors (UI + ANSI)
- ✅ Apply transformations to any color
- ✅ Export only what you need
- ❌ More configuration required
- ❌ Must manually specify each color you want

### Configuration Parameters

```toml
[app_name]
enabled = true
output-file = "/path/to/output"
color-format = "rgba"                    # Any valid format
syntax = "${name} = {color}"             # Pattern with {name} and/or {color}
remap-colors = true                      # REQUIRED for this mode

[app_name.colors]
custom-name-1 = { source = "bg-primary" }
custom-name-2 = { source = "ansi-4", brightness = 1.2 }
# ... more color definitions
```

### The syntax Parameter in Custom Mapping Mode

The `syntax` can contain:

- `{name}` - Replaced with your custom color name from `[app.colors]` keys
- `{color}` - Replaced with the color value (possibly transformed)
- Both, one, or neither

### The [app.colors] Table Structure

Each entry in the `[app.colors]` table has this structure:

```toml
your-custom-name = { source = "semantic-color-name", transformation1 = value, transformation2 = value }
```

- **Key** (`your-custom-name`): The variable name used in output
- **source**: One of the 29 available semantic colors (required)
- **Transformations**: Optional modifications (brightness, saturation, etc.)

### Example 1: Hyprland Configuration

```toml
[hyprland]
enabled = true
output-file = "~/.config/hypr/colors.conf"
color-format = "rgba"
syntax = "${name} = {color}"
remap-colors = true

[hyprland.colors]
# Custom names matching Hyprland's expectations
active-border = { source = "accent-primary" }
inactive-border = { source = "bg-tertiary", brightness = 0.8 }
background = { source = "bg-primary" }
foreground = { source = "text-primary" }
# Using ANSI colors for terminal integration
terminal-red = { source = "ansi-1", opacity = 0.9 }
terminal-blue = { source = "ansi-4" }
```

**Generated output (`colors.conf`):**

```
$active-border = rgba(100, 149, 255, 1.0)
$inactive-border = rgba(46, 46, 59, 1.0)
$background = rgba(30, 30, 46, 1.0)
$foreground = rgba(224, 224, 224, 1.0)
$terminal-red = rgba(255, 50, 50, 0.9)
$terminal-blue = rgba(80, 120, 255, 1.0)
```

### Example 2: Waybar with Descriptive Names

```toml
[waybar]
enabled = true
output-file = "waybar-colors.css"  # Relative path - goes to cache
color-format = "hex8"
syntax = "@define-color {name} {color};"
remap-colors = true

[waybar.colors]
# Semantic naming for UI components
bar-background = { source = "bg-secondary", opacity = 0.95 }
bar-foreground = { source = "text-primary" }
workspace-active-bg = { source = "accent-primary" }
workspace-active-fg = { source = "bg-primary" }
workspace-inactive = { source = "text-tertiary" }
module-bg = { source = "bg-tertiary" }
module-fg = { source = "text-secondary" }
critical-alert = { source = "error-color", brightness = 1.2 }
warning-alert = { source = "warning-color" }
```

**Generated output (in cache):**

```css
@define-color bar-background #2a2a3af2;
@define-color bar-foreground #e0e0e0ff;
@define-color workspace-active-bg #6495ffff;
@define-color workspace-active-fg #1e1e2eff;
@define-color workspace-inactive #808080ff;
@define-color module-bg #3a3a4aff;
@define-color module-fg #b0b0b0ff;
@define-color critical-alert #ff6060ff;
@define-color warning-alert #ffaa44ff;
```

### Example 3: Kitty Terminal Configuration

```toml
[kitty]
enabled = true
output-file = "~/.config/kitty/colors.conf"
color-format = "hex6"
syntax = "{name} {color}"
remap-colors = true

[kitty.colors]
# Kitty-specific naming convention
background = { source = "bg-primary" }
foreground = { source = "text-primary" }
selection_background = { source = "accent-primary", brightness = 0.8 }
selection_foreground = { source = "bg-primary" }
cursor = { source = "accent-primary" }
cursor_text_color = { source = "bg-primary" }
# Standard ANSI colors
color0 = { source = "ansi-0" }
color1 = { source = "ansi-1" }
color2 = { source = "ansi-2" }
color3 = { source = "ansi-3" }
color4 = { source = "ansi-4" }
color5 = { source = "ansi-5" }
color6 = { source = "ansi-6" }
color7 = { source = "ansi-7" }
color8 = { source = "ansi-8" }
color9 = { source = "ansi-9" }
color10 = { source = "ansi-10" }
color11 = { source = "ansi-11" }
color12 = { source = "ansi-12" }
color13 = { source = "ansi-13" }
color14 = { source = "ansi-14" }
color15 = { source = "ansi-15" }
```

**Generated output (`colors.conf`):**

```
background #1e1e2e
foreground #e0e0e0
selection_background #5276cc
selection_foreground #1e1e2e
cursor #6495ff
cursor_text_color #1e1e2e
color0 #000000
color1 #ff3232
color2 #32ff32
color3 #ffff32
color4 #5078ff
color5 #ff32ff
color6 #32ffff
color7 #e0e0e0
color8 #808080
color9 #ff6464
color10 #64ff64
color11 #ffff64
color12 #8296ff
color13 #ff64ff
color14 #64ffff
color15 #ffffff
```

### Example 4: Minimal Selection

You can export just a few colors if that's all you need:

```toml
[simple-app]
enabled = true
output-file = "colors.conf"
color-format = "rgb"
syntax = "set {name} \"{color}\""
remap-colors = true

[simple-app.colors]
# Only three colors needed
primary = { source = "accent-primary" }
bg = { source = "bg-primary" }
fg = { source = "text-primary" }
```

**Generated output:**

```
set primary "rgb(100, 149, 255)"
set bg "rgb(30, 30, 46)"
set fg "rgb(224, 224, 224)"
```

### Example 5: Syntax Without {name}

```toml
[color-list]
enabled = true
output-file = "palette.txt"
color-format = "hex6"
syntax = "Color: {color}"
remap-colors = true

[color-list.colors]
primary = { source = "accent-primary" }
secondary = { source = "accent-secondary" }
bg = { source = "bg-primary" }
```

**Generated output:**

```
Color: #6495ff
Color: #ff6495
Color: #1e1e2e
```

### Example 6: Syntax Without {color}

```toml
[color-names]
enabled = true
output-file = "names.txt"
color-format = "hex6"
syntax = "Available: {name}"
remap-colors = true

[color-names.colors]
primary-accent = { source = "accent-primary" }
main-bg = { source = "bg-primary" }
main-text = { source = "text-primary" }
```

**Generated output:**

```
Available: primary-accent
Available: main-bg
Available: main-text
```

### Important Notes for Custom Mapping Mode

1. **Only mapped colors are exported**: Unlike Default Mode, you only get the colors you explicitly define.

2. **Custom names**: The keys in `[app.colors]` become your variable names - use names that match your application's
   conventions.

3. **All 29 source colors available**: You can use any of the 13 UI colors or 16 ANSI colors as sources.

4. **Transformations are optional**: Simple remapping without transformations is perfectly valid.

5. **Order matters**: Colors appear in the output file in the order you define them in `[app.colors]`.

---

## Mode 3: Template Mode

Template Mode is the **most powerful and flexible** mode, designed for complex configuration files where you need
precise control over the entire file structure.

### What It Does

- Takes an existing template file and replaces color placeholders with actual color values
- Preserves all other content in the template (comments, formatting, non-color settings)
- Perfect for applications with complex config files
- Supports both semantic color names and custom color mappings

### Activation Requirements

```toml
template = "my-theme.conf"   # OR absolute path
# This automatically activates Template Mode
```

### Key Characteristics

- ✅ Complete control over file structure
- ✅ Preserves all non-color content
- ✅ Works with any file format
- ✅ Supports comments and formatting
- ✅ Can use semantic names OR custom names
- ❌ Requires creating a template file
- ❌ More setup work initially
- ❌ Syntax parameter has different meaning

---

### Understanding Template Mode Concepts

#### The Template File

A template file is a copy of your application's configuration file where color values are replaced with **placeholder
markers**. Luminol reads this template and substitutes the placeholders with actual colors.

#### The Placeholder Keyword

In Template Mode, the word **`placeholder`** in your `syntax` parameter has a special meaning:

- It's a **literal keyword** that you must include in `syntax`
- Luminol replaces the word `placeholder` with each color name to create search patterns
- The rest of the `syntax` defines what characters surround the color names in your template

**This is completely different from `{name}` and `{color}` in other modes!**

#### How Placeholder Pattern Matching Works

The `syntax` parameter creates a search pattern. Here's how it works:

```toml
# If your syntax is:
syntax = "{placeholder}"

# Luminol will search your template for:
{bg-primary}
{bg-secondary}
{text-primary}
{ansi-0}
{ansi-1}
# ... etc for all available colors

# And replace them with actual color values
```

Let's see more examples:

```toml
# Syntax with square brackets
syntax = "[placeholder]"

# Searches for:
[bg-primary]
[bg-secondary]
[text-primary]
# etc.
```

```toml
# Syntax with prefix
syntax = "COLOR_placeholder"

# Searches for:
COLOR_bg-primary
COLOR_bg-secondary
COLOR_text-primary
COLOR_ansi-0
# etc.
```

```toml
# Syntax with prefix and suffix
syntax = "{{placeholder}}"

# Searches for:
{{bg-primary}}
{{bg-secondary}}
{{text-primary}}
# etc.
```

```toml
# Just the bare word
syntax = "placeholder"

# Searches for:
bg-primary
bg-secondary
text-primary
# etc. (no delimiters at all)
```

⚠️ **Critical**: The syntax in Template Mode does NOT use `{name}` or `{color}` - it ONLY uses the word `placeholder`.

⚠️ **A Note on Choosing a Syntax Pattern**

You are right to be cautious. While you can use any characters to define your `syntax`, it is **highly recommended to
avoid using single or double quotes** as part of your pattern (e.g., `syntax = '"{placeholder}"'`).

Automated code formatters may change the quotes, causing your placeholders to no longer be recognized.

A more robust approach is to use delimiters that are not quotes, such as:

- `syntax = "{placeholder}"`
- `syntax = "@@placeholder@@"`
- `syntax = "##placeholder##"`
- `syntax = "%%placeholder%%"`

This makes your templates less likely to break when using formatters or other tooling.

---

### Template Mode: Two Scenarios

Template Mode works in two distinct ways depending on whether you're using custom color mapping:

---

## Scenario A: Template Mode with Semantic Names

**When**: `template` is set, `remap-colors` is `false` (or not specified)

**Available placeholders**: Only the 29 semantic color names

### Configuration Structure

```toml
[app_name]
enabled = true
output-file = "/path/to/output"
color-format = "hex6"
template = "my-app.conf"    # Activates Template Mode
syntax = "{placeholder}"               # Must contain word "placeholder"
remap-colors = false                   # Explicit (or omit - defaults to false)

# [app.colors] table is IGNORED even if present
```

### Available Placeholder Names

You can use these **29 semantic names** in your template:

**UI Colors (13):**

- `bg-primary`, `bg-secondary`, `bg-tertiary`
- `text-primary`, `text-secondary`, `text-tertiary`
- `accent-primary`, `accent-secondary`
- `error-color`, `warning-color`, `success-color`
- `border-active`, `border-inactive`

**ANSI Colors (16):**

- `ansi-0` through `ansi-15`

### Example 1: Dunst Notification Configuration

**Config (`config.toml`):**

```toml
[dunst]
enabled = true
output-file = "~/.config/dunst/dunstrc"
color-format = "hex6"
template = "dunstrc-template"
syntax = "{placeholder}"
```

**Template file (`dunstrc-template`):**

```ini
# Dunst notification daemon configuration

[global]
    font = Monospace 10
    markup = full
    format = "<b>%s</b>\n%b"
    frame_width = 2
    separator_height = 2

[urgency_low]
    background = "{bg-primary}"
    foreground = "{text-secondary}"
    frame_color = "{border-inactive}"
    timeout = 5

[urgency_normal]
    background = "{bg-secondary}"
    foreground = "{text-primary}"
    frame_color = "{accent-primary}"
    timeout = 10

[urgency_critical]
    background = "{error-color}"
    foreground = "{text-primary}"
    frame_color = "{error-color}"
    timeout = 0

[shortcuts]
    close = ctrl+space
    # Terminal colors for icon coloring
    icon_foreground = "{ansi-7}"
```

**Generated output (`dunstrc`):**

```ini
# Dunst notification daemon configuration

[global]
    font = Monospace 10
    markup = full
    format = "<b>%s</b>\n%b"
    frame_width = 2
    separator_height = 2

[urgency_low]
    background = "#1e1e2e"
    foreground = "#b0b0b0"
    frame_color = "#404040"
    timeout = 5

[urgency_normal]
    background = "#2a2a3a"
    foreground = "#e0e0e0"
    frame_color = "#6495ff"
    timeout = 10

[urgency_critical]
    background = "#ff4444"
    foreground = "#e0e0e0"
    frame_color = "#ff4444"
    timeout = 0

[shortcuts]
    close = ctrl+space
    # Terminal colors for icon coloring
    icon_foreground = "#e0e0e0"
```

**Note**: All non-color content (comments, settings, formatting) is preserved exactly.

### Example 2: Alacritty Terminal

**Config (`config.toml`):**

```toml
[alacritty]
enabled = true
output-file = "~/.config/alacritty/colors.yml"
color-format = "hex6"
template = "alacritty-colors.yml"
syntax = "_placeholder"
```

**Template file (`alacritty-colors.yml`):**

<!-- prettier-ignore -->
```yaml
# Alacritty color scheme

colors:
    primary:
        background: '_bg-primary'
        foreground: '_text-primary'

    cursor:
        text: '_bg-primary'
        cursor: '_accent-primary'

    selection:
        text: '_bg-primary'
        background: '_accent-primary'

    normal:
        black: '_ansi-0'
        red: '_ansi-1'
        green: '_ansi-2'
        yellow: '_ansi-3'
        blue: '_ansi-4'
        magenta: '_ansi-5'
        cyan: '_ansi-6'
        white: '_ansi-7'

    bright:
        black: '_ansi-8'
        red: '_ansi-9'
        green: '_ansi-10'
        yellow: '_ansi-11'
        blue: '_ansi-12'
        magenta: '_ansi-13'
        cyan: '_ansi-14'
        white: '_ansi-15'
```

**Generated output (`colors.yml`):**

<!-- prettier-ignore -->
```yaml
# Alacritty color scheme

colors:
    primary:
        background: '#1e1e2e'
        foreground: '#e0e0e0'

    cursor:
        text: '#1e1e2e'
        cursor: '#6495ff'

    selection:
        text: '#1e1e2e'
        background: '#6495ff'

    normal:
        black: '#000000'
        red: '#ff3232'
        green: '#32ff32'
        yellow: '#ffff32'
        blue: '#5078ff'
        magenta: '#ff32ff'
        cyan: '#32ffff'
        white: '#e0e0e0'

    bright:
        black: '#808080'
        red: '#ff6464'
        green: '#64ff64'
        yellow: '#ffff64'
        blue: '#8296ff'
        magenta: '#ff64ff'
        cyan: '#64ffff'
        white: '#ffffff'
```

### Example 3: i3 Window Manager

**Config (`config.toml`):**

```toml

[i3]

enabled = true

output-file = "~/.config/i3/colors"

color-format = "hex6"

template = "i3-colors.conf"

syntax = "$placeholder"  # Dollar sign prefix

```

**Template file (`i3-colors.conf`):**

```
# i3wm color configuration
# This file is sourced by the main i3 config

# Window colors
#                       border              background         text                 indicator
client.focused          $accent-primary     $accent-primary    $bg-primary          $success-color
client.focused_inactive $bg-tertiary        $bg-tertiary       $text-secondary      $bg-tertiary
client.unfocused        $bg-secondary       $bg-secondary      $text-tertiary       $bg-secondary
client.urgent           $error-color        $error-color       $text-primary        $warning-color
client.placeholder      $bg-primary         $bg-primary        $text-primary        $bg-primary

# Bar colors
bar {
    background $bg-primary
    statusline $text-primary
    separator  $border-inactive

    #                  border              background         text
    focused_workspace  $accent-primary     $accent-primary    $bg-primary
    active_workspace   $bg-tertiary        $bg-tertiary       $text-primary
    inactive_workspace $bg-secondary       $bg-secondary      $text-tertiary
    urgent_workspace   $error-color        $error-color       $text-primary
}
```

**Generated output:**

```
# i3wm color configuration
# This file is sourced by the main i3 config

# Window colors
#                       border      background  text        indicator
client.focused          #6495ff     #6495ff     #1e1e2e     #44ff44
client.focused_inactive #3a3a4a     #3a3a4a     #b0b0b0     #3a3a4a
client.unfocused        #2a2a3a     #2a2a3a     #808080     #2a2a3a
client.urgent           #ff4444     #ff4444     #e0e0e0     #ffaa44
client.placeholder      #1e1e2e     #1e1e2e     #e0e0e0     #1e1e2e

# Bar colors
bar {
    background #1e1e2e
    statusline #e0e0e0
    separator  #404040

    #                  border      background  text
    focused_workspace  #6495ff     #6495ff     #1e1e2e
    active_workspace   #3a3a4a     #3a3a4a     #e0e0e0
    inactive_workspace #2a2a3a     #2a2a3a     #808080
    urgent_workspace   #ff4444     #ff4444     #e0e0e0
}
```

### Example 4: CSS with Comments

**Config (`config.toml`):**

```toml
[web-theme]
enabled = true
output-file = "~/projects/website/theme.css"
color-format = "rgba"
template = "theme-template.css"
syntax = "var(--placeholder)"
```

**Template file (`theme-template.css`):**

```css
/**
 * Website Theme Colors
 * Auto-generated by Luminol
 */

:root {
    /* Primary backgrounds */
    --color-bg-main: var(--bg-primary);
    --color-bg-elevated: var(--bg-secondary);
    --color-bg-overlay: var(--bg-tertiary);

    /* Text colors */
    --color-text-heading: var(--text-primary);
    --color-text-body: var(--text-secondary);
    --color-text-muted: var(--text-tertiary);

    /* Accent colors */
    --color-brand: var(--accent-primary);
    --color-link: var(--accent-secondary);

    /* Status colors */
    --color-error: var(--error-color);
    --color-warning: var(--warning-color);
    --color-success: var(--success-color);

    /* Borders */
    --color-border-focus: var(--border-active);
    --color-border-default: var(--border-inactive);

    /* Terminal colors for code blocks */
    --code-black: var(--ansi-0);
    --code-red: var(--ansi-1);
    --code-green: var(--ansi-2);
    --code-blue: var(--ansi-4);
}

/* These classes won't be affected by Luminol */
.button-primary {
    background: var(--color-brand);
    color: var(--color-bg-main);
}
```

**Generated output (`theme.css`):**

```css
/**
 * Website Theme Colors
 * Auto-generated by Luminol
 */

:root {
    /* Primary backgrounds */
    --color-bg-main: rgba(30, 30, 46, 1);
    --color-bg-elevated: rgba(42, 42, 58, 1);
    --color-bg-overlay: rgba(58, 58, 74, 1);

    /* Text colors */
    --color-text-heading: rgba(224, 224, 224, 1);
    --color-text-body: rgba(176, 176, 176, 1);
    --color-text-muted: rgba(128, 128, 128, 1);

    /* Accent colors */
    --color-brand: rgba(100, 149, 255, 1);
    --color-link: rgba(255, 100, 149, 1);

    /* Status colors */
    --color-error: rgba(255, 68, 68, 1);
    --color-warning: rgba(255, 170, 68, 1);
    --color-success: rgba(68, 255, 68, 1);

    /* Borders */
    --color-border-focus: rgba(100, 149, 255, 1);
    --color-border-default: rgba(64, 64, 64, 1);

    /* Terminal colors for code blocks */
    --code-black: rgba(0, 0, 0, 1);
    --code-red: rgba(255, 50, 50, 1);
    --code-green: rgba(50, 255, 50, 1);
    --code-blue: rgba(80, 120, 255, 1);
}

/* These classes won't be affected by Luminol */
.button-primary {
    background: var(--color-brand);
    color: var(--color-bg-main);
}
```

### Unmatched Placeholders

If a placeholder in your template doesn't match any semantic color name, it remains unchanged:

**Template:**

```
background = {bg-primary}      # ✅ Matched - replaced
foreground = {text-primary}    # ✅ Matched - replaced
custom = {my-custom-color}     # ❌ Not matched - stays as-is
```

**Output:**

```
background = #1e1e2e           # Replaced
foreground = #e0e0e0           # Replaced
custom = {my-custom-color}     # Unchanged
```

---

## Scenario B: Template Mode with Custom Mapping

**When**: `template` is set AND `remap-colors = true`

**Available placeholders**: Only the custom names you define in `[app.colors]`

### Configuration Structure

```toml
[app_name]
enabled = true
output-file = "/path/to/output"
color-format = "hex6"
template = "template-file.template"
syntax = "{placeholder}"
remap-colors = true              # Enables custom names

[app_name.colors]                # REQUIRED when remap-colors = true
custom-name-1 = { source = "bg-primary" }
custom-name-2 = { source = "ansi-1", brightness = 1.2 }
# These keys become your placeholder names
```

⚠️ **Error Condition**: If `remap-colors = true` but `[app.colors]` is missing, you'll get a configuration error.

### How It Works

1. You define custom color names in `[app.colors]`
2. The **keys** of `[app.colors]` become your only available placeholder names
3. You can apply transformations to these colors
4. Use these custom names in your template file

### Example 1: Dunst with Custom Names

**Config (`config.toml`):**

```toml

[dunst]

enabled = true

output-file = "~/.config/dunst/dunstrc"

color-format = "hex6"

template = "dunstrc-template"

syntax = "{placeholder}"

remap-colors = true



[dunst.colors]

# Define custom names that match Dunst's structure

frame_color = { source = "accent-primary" }

bg_low = { source = "bg-primary" }

fg_low = { source = "text-primary" }

bg_normal = { source = "bg-secondary" }

fg_normal = { source = "text-primary" }

bg_critical = { source = "error-color" }

fg_critical = { source = "text-primary" }

my_custom_accent = { source = "accent-secondary", brightness = 1.2 }

terminal_red = { source = "ansi-1" }

```

**Template file (`dunstrc-template`):**

```ini
[global]
    font = Monospace 10

[urgency_low]
    background = "{bg_low}"           # ✅ Will be replaced
    foreground = "{fg_low}"           # ✅ Will be replaced
    frame_color = "{frame_color}"     # ✅ Will be replaced

[urgency_normal]
    background = "{bg_normal}"        # ✅ Will be replaced
    foreground = "{fg_normal}"        # ✅ Will be replaced
    frame_color = "{my_custom_accent}" # ✅ Will be replaced

[urgency_critical]
    background = "{bg_critical}"      # ✅ Will be replaced
    foreground = "{fg_critical}"      # ✅ Will be replaced
    frame_color = "{terminal_red}"    # ✅ Will be replaced
    icon = "{bg-primary}"             # ❌ NOT in [dunst.colors] - stays as-is
```

**Generated output (`dunstrc`):**

```ini
[global]
    font = Monospace 10

[urgency_low]
    background = "#1e1e2e"
    foreground = "#e0e0e0"
    frame_color = "#6495ff"

[urgency_normal]
    background = "#2a2a3a"
    foreground = "#e0e0e0"
    frame_color = "#7aa3ff"

[urgency_critical]
    background = "#ff4444"
    foreground = "#e0e0e0"
    frame_color = "#ff3232"
    icon = "{bg-primary}"              # Not replaced - not defined
```

### Example 2: Complex Rofi Configuration

**Config (`config.toml`):**

```toml

[rofi]

enabled = true

output-file = "~/.config/rofi/theme.rasi"

color-format = "hex8"

template = "rofi-theme.rasi"

syntax = "@placeholder"

remap-colors = true



[rofi.colors]

# Highly customized color scheme

window-bg = { source = "bg-primary", opacity = 0.95 }

window-border = { source = "accent-primary" }

input-bg = { source = "bg-secondary" }

input-text = { source = "text-primary" }

list-bg = { source = "bg-primary" }

list-text = { source = "text-secondary" }

selected-bg = { source = "accent-primary" }

selected-text = { source = "bg-primary" }

alternate-bg = { source = "bg-tertiary", brightness = 0.9 }

urgent-bg = { source = "error-color", saturation = 0.8 }

active-bg = { source = "success-color" }

# Using ANSI colors for mode indicators

mode-normal = { source = "ansi-4" }

mode-urgent = { source = "ansi-1" }

mode-active = { source = "ansi-2" }

```

**Template file (`rofi-theme.rasi`):**

```css
* {
    background-color: @window-bg;
    border-color: @window-border;
    text-color: @input-text;
}

window {
    background-color: @window-bg;
    border: 2px;
    border-color: @window-border;
}

inputbar {
    background-color: @input-bg;
    text-color: @input-text;
}

listview {
    background-color: @list-bg;
}

element {
    background-color: @list-bg;
    text-color: @list-text;
}

element alternate {
    background-color: @alternate-bg;
}

element selected {
    background-color: @selected-bg;
    text-color: @selected-text;
}

element urgent {
    background-color: @urgent-bg;
}

element active {
    background-color: @active-bg;
}

/* Mode indicators */
mode-switcher {
    background-color: @list-bg;
}

button normal {
    background-color: @mode-normal;
}

button urgent {
    background-color: @mode-urgent;
}

button active {
    background-color: @mode-active;
}
```

**Generated output (`theme.rasi`):**

```css
* {
    background-color: #1e1e2ef2;
    border-color: #6495ffff;
    text-color: #e0e0e0ff;
}

window {
    background-color: #1e1e2ef2;
    border: 2px;
    border-color: #6495ffff;
}

inputbar {
    background-color: #2a2a3aff;
    text-color: #e0e0e0ff;
}

listview {
    background-color: #1e1e2eff;
}

element {
    background-color: #1e1e2eff;
    text-color: #b0b0b0ff;
}

element alternate {
    background-color: #343444ff;
}

element selected {
    background-color: #6495ffff;
    text-color: #1e1e2eff;
}

element urgent {
    background-color: #cc5555ff;
}

element active {
    background-color: #44ff44ff;
}

/* Mode indicators */
mode-switcher {
    background-color: #1e1e2eff;
}

button normal {
    background-color: #5078ffff;
}

button urgent {
    background-color: #ff3232ff;
}

button active {
    background-color: #32ff32ff;
}
```

### Example 3: Minimal Custom Mapping

You don't have to define many colors - just what you need:

**Config (`config.toml`):**

```toml

[simple]

enabled = true

output-file = "colors.conf"

color-format = "rgb"

template = "simple.conf"

syntax = "COLOR_placeholder"

remap-colors = true



[simple.colors]

primary = { source = "accent-primary" }

secondary = { source = "accent-secondary" }

background = { source = "bg-primary", brightness = 0.8 }

```

**Template file (`simple.conf`):**

```
[theme]
main = COLOR_primary
alt = COLOR_secondary
bg = COLOR_background
other_setting = some_value
```

**Generated output:**

```
[theme]
main = rgb(100, 149, 255)
alt = rgb(255, 100, 149)
bg = rgb(24, 24, 37)
other_setting = some_value
```

### Example 4: Using Only ANSI Colors

**Config (`config.toml`):**

```toml

[terminal-scheme]

enabled = true

output-file = "term-colors.conf"

color-format = "hex6"

template = "term.conf"

syntax = "[placeholder]"

remap-colors = true



[terminal-scheme.colors]

# Only using ANSI colors with custom names

term-black = { source = "ansi-0" }

term-red = { source = "ansi-1", brightness = 0.9 }

term-green = { source = "ansi-2" }

term-yellow = { source = "ansi-3", saturation = 1.2 }

term-blue = { source = "ansi-4" }

term-magenta = { source = "ansi-5" }

term-cyan = { source = "ansi-6" }

term-white = { source = "ansi-7" }

```

**Template file (`term.conf`):**

```
black=[term-black]
red=[term-red]
green=[term-green]
yellow=[term-yellow]
blue=[term-blue]
magenta=[term-magenta]
cyan=[term-cyan]
white=[term-white]
```

**Generated output:**

```
black=#000000
red=#e62e2e
green=#32ff32
yellow=#ffff3d
blue=#5078ff
magenta=#ff32ff
cyan=#32ffff
white=#e0e0e0
```

---

### Template Mode Summary

| Scenario           | remap-colors      | [app.colors] Required?  | Available Placeholders | Can Transform? |
| ------------------ | ----------------- | ----------------------- | ---------------------- | -------------- |
| **Semantic Names** | `false` (default) | No (ignored if present) | 29 semantic names only | No             |
| **Custom Mapping** | `true`            | Yes (error if missing)  | Keys from [app.colors] | Yes            |

---

## Color Transformations

When using the `[app.colors]` table (in Custom Mapping Mode or Template Mode with `remap-colors = true`), you can apply
transformations to any source color.

```toml
[my_app.colors]
# Simple remapping
custom-name = { source = "bg-primary" }

# Using ANSI color as source
terminal-accent = { source = "ansi-4" }

# Remapping with transformations
custom-name-2 = { source = "text-primary", brightness = 1.2, opacity = 0.8 }
```

### Order of Transformation

Transformations are always applied in a fixed, predictable order to ensure consistent results:

1. **Hue**
2. **Saturation**
3. **Brightness**
4. **Contrast**
5. **Temperature**
6. **Opacity**

This means that a `brightness` adjustment will happen _after_ a `saturation` change, which can affect the final
appearance.

**Important**: When the output `color-format` does not support alpha (e.g., `hex6`, `rgb`), the `opacity` transformation
is ignored and the color is treated as fully opaque.

### Supported Transformations

#### 1. Hue

Rotates the color around the color wheel. This is useful for creating analogous or complementary colors.

- **Values**: A number between `-360` and `360` (degrees).
- **Behavior**: Values outside this range are wrapped around (e.g., `370` becomes `10`).
- **Example**:
    ```toml
    accent_analogous = { source = "accent-primary", hue = 30 } # Shift hue by 30 degrees
    accent_complementary = { source = "accent-primary", hue = 180 } # Get the opposite color
    ```

#### 2. Saturation

Adjusts the intensity or vibrancy of a color. Lower values make the color more grayish, while higher values make it more
vivid.

- **Values**: A number, where `1.0` is the original saturation.
    - `0.0` is completely desaturated (grayscale).
    - `0.5` is 50% less saturated.
    - `1.5` is 50% more saturated.

- **Range Clarification**: While any positive number is technically accepted, values significantly outside the `0.0` to
  `3.0` range may lead to colors that are either fully desaturated or maximally vibrant, potentially losing nuance. The
  recommended range of `0.0` to `3.0` is for predictable and visually pleasing results.

- **Behavior**: Values are clamped internally to prevent extreme results, but it's best to stay within recommended
  ranges.

- **Example**:
    ```toml
    muted_accent = { source = "accent-primary", saturation = 0.5 }
    vibrant_accent = { source = "accent-primary", saturation = 1.5 }
    ```

#### 3. Brightness

Adjusts the overall lightness or darkness of a color.

- **Values**: A number, where `1.0` is the original brightness.
    - `0.0` is completely black.
    - `0.8` makes the color 20% darker.
    - `1.2` makes the color 20% brighter.

- **Range Clarification**: While any positive number is technically accepted, values significantly outside the `0.0` to
  `3.0` range may lead to colors that are either fully black or maximally bright, potentially losing nuance. The
  recommended range of `0.0` to `3.0` is for predictable and visually pleasing results.

- **Behavior**: Values are clamped internally to prevent extreme results, but it's best to stay within recommended
  ranges.

- **Example**:
    ```toml
    darker_bg = { source = "bg-secondary", brightness = 0.8 }
    brighter_accent = { source = "accent-primary", brightness = 1.1 }
    ```

#### 4. Contrast

Adjusts the color's contrast by pushing it towards pure black or white, making it more distinct against a neutral
background.

- **Values**: A number, where `1.0` is the original contrast.
    - Values > `1.0` increase contrast.
    - Values < `1.0` decrease contrast.
    - `0.0` results in a neutral gray.
- **Behavior**: This transformation adjusts the color's distance from a neutral middle gray. Increasing contrast pushes
  the color's components (red, green, blue) further towards the extremes (0 or 255), while decreasing it pulls them
  closer to the middle (128).
- **Example**:
    ```toml
    high_contrast_text = { source = "text-primary", contrast = 1.2 } # Push text closer to pure white
    low_contrast_bg = { source = "bg-secondary", contrast = 0.8 } # Mute the background
    ```

#### 5. Temperature

Makes the color "warmer" (more red/orange) or "cooler" (more blue). This is an intuitive way to shift color tones.

- **Values**: A number between `-100` (coolest) and `100` (warmest). `0` is neutral.
- **Behavior**: Values outside `-100` to `100` are clamped to these limits.
- **Example**:
    ```toml
    warm_bg = { source = "bg-primary", temperature = 20 }
    cool_text = { source = "text-primary", temperature = -15 }
    ```

#### 6. Opacity

Controls the transparency (alpha channel) of the color.

- **Values**: A number between `0.0` (fully transparent) and `1.0` (fully opaque).
- **Behavior**:
    - Values outside `0.0` to `1.0` are clamped to these limits.
    - **Ignored completely** if `color-format` doesn't support alpha (e.g., `hex6`, `rgb`).
- **Example**:
    ```toml
    transparent_bg = { source = "bg-primary", opacity = 0.8 } # 80% opaque (only works with hex8, rgba, rgba_decimal)
    ```

### Transformation Examples

#### Example 1: Creating Color Variations

```toml
[variations]
enabled = true
output-file = "colors.css"
color-format = "hex6"
syntax = "--{name}: {color};"
remap-colors = true

[variations.colors]
# Base color
primary = { source = "accent-primary" }

# Brightness variations
primary-light = { source = "accent-primary", brightness = 1.3 }
primary-lighter = { source = "accent-primary", brightness = 1.6 }
primary-dark = { source = "accent-primary", brightness = 0.7 }
primary-darker = { source = "accent-primary", brightness = 0.4 }

# Saturation variations
primary-muted = { source = "accent-primary", saturation = 0.5 }
primary-vibrant = { source = "accent-primary", saturation = 1.5 }

# Hue variations (color wheel)
primary-analogous-1 = { source = "accent-primary", hue = 30 }
primary-analogous-2 = { source = "accent-primary", hue = -30 }
primary-complementary = { source = "accent-primary", hue = 180 }
```

#### Example 2: Temperature Shifts

```toml
[temperature-demo]
enabled = true
output-file = "temp-colors.conf"
color-format = "rgb"
syntax = "{name} = {color}"
remap-colors = true

[temperature-demo.colors]
# Neutral base
neutral-bg = { source = "bg-primary" }

# Warm variations
warm-bg-subtle = { source = "bg-primary", temperature = 15 }
warm-bg-medium = { source = "bg-primary", temperature = 35 }
warm-bg-strong = { source = "bg-primary", temperature = 60 }

# Cool variations
cool-bg-subtle = { source = "bg-primary", temperature = -15 }
cool-bg-medium = { source = "bg-primary", temperature = -35 }
cool-bg-strong = { source = "bg-primary", temperature = -60 }
```

#### Example 3: Combined Transformations

```toml
[complex]
enabled = true
output-file = "complex.css"
color-format = "rgba"
syntax = "--{name}: {color};"
remap-colors = true

[complex.colors]
# Multiple transformations applied in order
highlight = {
    source = "accent-primary",
    hue = 15,              # 1. Shift hue first
    saturation = 1.2,      # 2. Then increase saturation
    brightness = 1.3,      # 3. Then brighten
    opacity = 0.9          # 4. Finally set opacity
}

# Muted, darker variant
muted-dark = {
    source = "accent-primary",
    saturation = 0.6,      # 1. Desaturate
    brightness = 0.5,      # 2. Darken
    temperature = -10      # 3. Cool slightly
}

# Warm, bright overlay
warm-overlay = {
    source = "bg-secondary",
    temperature = 25,      # 1. Warm
    brightness = 1.4,      # 2. Brighten
    opacity = 0.7          # 3. Make transparent
}
```

#### Example 4: ANSI Color Modifications

```toml
[terminal-custom]
enabled = true
output-file = "term.conf"
color-format = "hex8"
syntax = "color{name}={color}"
remap-colors = true

[terminal-custom.colors]
# Soften the standard red for better readability
0 = { source = "ansi-1", brightness = 0.85, saturation = 0.9 }

# Make green more vibrant
1 = { source = "ansi-2", saturation = 1.3 }

# Create a dimmed blue
2 = { source = "ansi-4", brightness = 0.7, opacity = 0.85 }

# Warm yellow for better contrast
3 = { source = "ansi-3", temperature = 10 }
```

---

## Mode Selection Guide

Use this guide to choose the right mode for your needs:

### Choose Default Mode When:

- ✅ You need a simple, quick color file
- ✅ The standard 13 UI semantic names work for your app
- ✅ You don't need ANSI terminal colors
- ✅ You don't need to transform colors
- ✅ You're okay with fixed color names

**Example use cases**: Simple CSS variables, basic shell scripts, straightforward config files

### Choose Custom Mapping Mode When:

- ✅ You need custom variable names
- ✅ You want to select specific colors (not all 13)
- ✅ You need ANSI terminal colors
- ✅ You want to transform colors (brightness, saturation, etc.)
- ✅ Your output file is simple (just color definitions)

**Example use cases**: Hyprland colors, Kitty terminal, Waybar, custom scripts

### Choose Template Mode When:

- ✅ Your config file has complex structure
- ✅ You need to preserve comments and formatting
- ✅ Colors are mixed with other settings
- ✅ The config file already exists
- ✅ You want precise control over file structure

**Example use cases**: Dunst, i3wm, Alacritty, Rofi with complex themes

### Template Mode Variant Decision:

- **Use Semantic Names** (no remap): When the 29 standard color names work for you
- **Use Custom Mapping** (remap = true): When you need custom names or transformations

---

## Complete Configuration Examples

### Example 1: Multi-App Setup with All Modes

```toml
[global]
wallpaper-command = "swww img {wallpaper_path}"
theme-type = "dark"
reload-commands = ["killall -USR1 waybar"]

# DEFAULT MODE: Simple Rofi colors
[rofi]
enabled = true
output-file = "~/.config/rofi/colors.rasi"
color-format = "hex8"
syntax = "*{{name}: {color};}"

# CUSTOM MAPPING MODE: Hyprland with custom names
[hyprland]
enabled = true
output-file = "~/.config/hypr/colors.conf"
color-format = "rgba"
syntax = "${name} = {color}"
remap-colors = true

[hyprland.colors]
active-border = { source = "accent-primary" }
inactive-border = { source = "bg-tertiary", brightness = 0.8 }
background = { source = "bg-primary" }
foreground = { source = "text-primary" }

# TEMPLATE MODE (Semantic): Dunst notifications
[dunst]
enabled = true
output-file = "~/.config/dunst/dunstrc"
color-format = "hex6"
template = "dunstrc.template"
syntax = '"{placeholder}"'

# TEMPLATE MODE (Custom): Kitty terminal with transformations
[kitty]
enabled = true
output-file = "~/.config/kitty/colors.conf"
color-format = "hex6"
template = "kitty.template"
syntax = "{placeholder}"
remap-colors = true

[kitty.colors]
background = { source = "bg-primary" }
foreground = { source = "text-primary" }
selection_bg = { source = "accent-primary", brightness = 0.8 }
selection_fg = { source = "bg-primary" }
cursor = { source = "accent-primary" }
color0 = { source = "ansi-0" }
color1 = { source = "ansi-1", brightness = 0.9 }
color2 = { source = "ansi-2" }
# ... more ANSI colors
```

### Example 2: Theming System for a Desktop Environment

```toml
[global]
wallpaper-command = "feh --bg-fill {wallpaper_path}"
theme-type = "auto"
reload-commands = [
    "killall waybar",
    "waybar",
    "killall dunst",
    "dunst"
]

# GTK theme colors (Default Mode)
[gtk]
enabled = true
output-file = "~/.config/gtk-3.0/colors.css"
color-format = "hex6"
syntax = "@define-color {name} {color};"

# Window manager (Template with semantic names)
[i3]
enabled = true
output-file = "~/.config/i3/colors"
color-format = "hex6"
template = "i3-colors.template"
syntax = "$placeholder"

# Status bar (Custom Mapping with transformations)
[waybar]
enabled = true
output-file = "~/.config/waybar/colors.css"
color-format = "hex8"
syntax = "@define-color {name} {color};"
remap-colors = true

[waybar.colors]
bar-bg = { source = "bg-primary", opacity = 0.95 }
bar-fg = { source = "text-primary" }
workspace-active-bg = { source = "accent-primary" }
workspace-active-fg = { source = "bg-primary" }
workspace-inactive-fg = { source = "text-tertiary" }
workspace-urgent-bg = { source = "error-color" }
module-bg = { source = "bg-tertiary" }
cpu-high = { source = "error-color", brightness = 1.1 }
cpu-medium = { source = "warning-color" }
cpu-low = { source = "success-color" }

# Terminal (Template with custom mapping)
[alacritty]
enabled = true
output-file = "~/.config/alacritty/colors.yml"
color-format = "hex6"
template = "alacritty-colors.yml"
syntax = "'placeholder'"
remap-colors = true

[alacritty.colors]
background = { source = "bg-primary" }
foreground = { source = "text-primary" }
cursor_bg = { source = "accent-primary" }
cursor_fg = { source = "bg-primary" }
# All 16 ANSI colors
black = { source = "ansi-0" }
red = { source = "ansi-1" }
green = { source = "ansi-2" }
yellow = { source = "ansi-3" }
blue = { source = "ansi-4" }
magenta = { source = "ansi-5" }
cyan = { source = "ansi-6" }
white = { source = "ansi-7" }
bright_black = { source = "ansi-8" }
bright_red = { source = "ansi-9" }
bright_green = { source = "ansi-10" }
bright_yellow = { source = "ansi-11" }
bright_blue = { source = "ansi-12" }
bright_magenta = { source = "ansi-13" }
bright_cyan = { source = "ansi-14" }
bright_white = { source = "ansi-15" }
```

---

## Error Handling

### Configuration Errors

These errors will prevent Luminol from running:

- **Missing required fields**: `enabled`, `output-file`, `color-format`, or `syntax` not specified.
- **Invalid `color-format`**: Value is not one of: `hex6`, `hex8`, `rgb`, `rgba`, `rgb_decimal`, `rgba_decimal`.
- **`remap-colors = true` without `[app.colors]` table**: Explicit remapping intent requires color definitions.
- **Template file not found**: Specified template path doesn't exist.
- **Invalid `syntax` in Template Mode**: Syntax doesn't contain the word `placeholder`.
- **Invalid source color name**: Source refers to a non-existent semantic color.

### Runtime Behavior

These situations are handled gracefully:

- **Unmatched placeholders in templates**: Left as-is in the output file (no replacement).
- **Transformation values out of range**: Clamped to valid ranges (no error).
- **Opacity with incompatible format**: Silently ignored; color treated as fully opaque.
- **`[app.colors]` present in Default Mode**: Silently ignored (no error, no warning).

---

## Quick Reference Tables

### Syntax Components by Mode

| Mode                    | Syntax Contains           | Purpose                     |
| ----------------------- | ------------------------- | --------------------------- |
| **Default**             | `{name}` and/or `{color}` | Format for each color line  |
| **Custom Mapping**      | `{name}` and/or `{color}` | Format for each color line  |
| **Template (Semantic)** | `placeholder` keyword     | Pattern to find in template |
| **Template (Custom)**   | `placeholder` keyword     | Pattern to find in template |

### Available Colors by Mode

| Mode                    | Available Colors           | Count  |
| ----------------------- | -------------------------- | ------ |
| **Default**             | 13 UI semantic colors only | 13     |
| **Custom Mapping**      | All 29 (13 UI + 16 ANSI)   | 29     |
| **Template (Semantic)** | All 29 (13 UI + 16 ANSI)   | 29     |
| **Template (Custom)**   | Keys from [app.colors]     | Custom |

### Feature Support by Mode

| Feature                 | Default | Custom Mapping | Template (Semantic) | Template (Custom) |
| ----------------------- | ------- | -------------- | ------------------- | ----------------- |
| Custom color names      | ❌      | ✅             | ❌                  | ✅                |
| ANSI colors             | ❌      | ✅             | ✅                  | ✅                |
| Transformations         | ❌      | ✅             | ❌                  | ✅                |
| Preserve file structure | ❌      | ❌             | ✅                  | ✅                |
| Select specific colors  | ❌      | ✅             | ❌                  | ✅                |
| Simple setup            | ✅      | ⚠️             | ⚠️                  | ❌                |

---

## Best Practices

### General Guidelines

1. **Start simple**: Begin with Default Mode, then move to more complex modes as needed.

2. **Validate after changes**: Always check your output files after modifying configuration.

3. **Use descriptive names**: In Custom Mapping Mode, use names that make sense for your application.

4. **Keep transformations moderate**: Stay within recommended ranges (0.0-3.0 for brightness/saturation).

5. **Document your templates**: Add comments in template files to explain what each placeholder does.

6. **Test incrementally**: When setting up complex configurations, enable one app at a time.

### Syntax Best Practices

1. **Be consistent**: Use the same syntax style across similar applications.

2. **Match your app's format**: Make syntax match your application's native color format:

    ```toml
    # CSS-like apps
    syntax = "--{name}: {color};"

    # Shell/scripting
    syntax = "${name}={color}"

    # INI/config files
    syntax = "{name} = {color}"
    ```

3. **Include proper delimiters**: Ensure your syntax includes all necessary quotes, brackets, etc.

### Template Mode Best Practices

1. **Keep original config as reference**: Before creating a template, back up your original config.

2. **Test placeholder patterns**: Verify your `syntax` pattern matches exactly what's in the template.

3. **Use consistent placeholder style**: Don't mix different placeholder styles in the same template.

### Transformation Best Practices

1. **Apply transformations sparingly**: Too many transformations can make colors look unnatural.

2. **Test visibility**: Ensure transformed colors maintain sufficient contrast for readability.

3. **Use temperature for mood**: Warm temperatures for cozy themes, cool for professional themes.

4. **Combine carefully**: When using multiple transformations, test the final result thoroughly.

5. **Document complex transformations**: Add comments explaining why specific values were chosen:
    ```toml
    [app.colors]
    # Dimmed red for better readability in dark mode
    soft-red = { source = "ansi-1", brightness = 0.85, saturation = 0.9 }
    ```

### Performance Considerations

1. **Minimize enabled apps**: Only enable applications you actually use.

2. **Use cache for temporary files**: Use relative paths in `output-file` for frequently changing files.

3. **Batch reload commands**: Group related reload commands together to reduce overhead.

4. **Avoid shell when possible**: Set `use-shell = false` for better performance and security.

---

## Troubleshooting

### Common Issues and Solutions

#### Issue: Placeholders not being replaced in template

**Possible causes:**

- Syntax pattern doesn't match template exactly
- Using wrong placeholder names
- Missing `remap-colors = true` when using custom names

**Solutions:**

1. Check that `syntax` in config matches placeholders in template exactly
2. Verify you're using correct color names (semantic vs. custom)
3. Enable `remap-colors = true` if using `[app.colors]`

#### Issue: Colors look wrong after transformation

**Possible causes:**

- Transformation values out of reasonable range
- Transformations applied in wrong mental order
- Opacity ignored due to incompatible color format

**Solutions:**

1. Keep transformation values within recommended ranges
2. Remember transformations apply in fixed order (hue → saturation → brightness → contrast → temperature → opacity)
3. Use `hex8`, `rgba`, or `rgba_decimal` for opacity support

#### Issue: Configuration error about missing [app.colors]

**Possible causes:**

- Set `remap-colors = true` but forgot to add `[app.colors]` table

**Solutions:**

1. Add `[app.colors]` table with at least one color definition
2. Or set `remap-colors = false` if you don't need custom mapping

#### Issue: Output file is empty or has no colors

**Possible causes:**

- Template file path incorrect
- No colors match in template
- Syntax pattern malformed

**Solutions:**

1. Verify template file exists at specified path
2. Check that template contains matching placeholders
3. Ensure syntax pattern is properly formatted

---

## Migration Guide

### From Hardcoded Colors to Luminol

If you're migrating from hardcoded colors, follow these steps:

#### Step 1: Identify your current colors

List all color values currently in your config:

```
# Current colors in my config
background: #1e1e2e
foreground: #e0e0e0
accent: #6495ff
```

#### Step 2: Choose the appropriate mode

- **Simple config with all 13 colors?** → Default Mode
- **Need custom names or transformations?** → Custom Mapping Mode
- **Complex config with mixed settings?** → Template Mode

#### Step 3: Create your Luminol config

For Template Mode:

1. Copy your current config file
2. Replace color values with placeholders
3. Save as a template file
4. Create Luminol config entry

#### Step 4: Test and verify

1. Run Luminol
2. Compare generated file with original
3. Adjust syntax or placeholders as needed
4. Test with your application

---

## Appendix: Color Format Reference

### hex6

- Format: `#RRGGBB`
- Example: `#6495ff`
- Alpha support: No
- Best for: CSS, most config files

### hex8

- Format: `#RRGGBBAA`
- Example: `#6495ffcc`
- Alpha support: Yes
- Best for: Modern CSS, applications supporting alpha

### rgb

- Format: `rgb(R, G, B)`
- Example: `rgb(100, 149, 255)`
- Alpha support: No
- Best for: CSS, some config formats

### rgb_decimal

- Format: `(R, G, B)`
- Example: `(100, 149, 255)`
- Alpha support: No

### rgba

- Format: `rgba(R, G, B, A)`
- Example: `rgba(100, 149, 255, 0.8)`
- Alpha support: Yes
- Best for: CSS with transparency, Hyprland

### rgba_decimal

- Format: `(R, G, B, A)`
- Example: `(100, 149, 255, 0.8)`
- Alpha support: Yes
