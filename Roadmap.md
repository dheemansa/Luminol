# Luminol - Implementation Roadmap

## Overview
This document outlines the phased implementation approach for Luminol, starting with basic functionality and progressively adding complexity. Each phase builds upon the previous one, ensuring a stable and testable development process.

## Phase 1: Core Foundation (Week 1-2) - **Complexity: Low**
**Goal**: Basic configuration parsing and color file generation with preset colors

### 1.1 Configuration System (Days 1-3)
**Complexity**: (Low)

**Objectives:**
- Parse TOML configuration files
- Load configuration from `$XDG_CONFIG_HOME/luminol/config.toml` (falling back to `$HOME/.config/luminol/config.toml`)
- Validate configuration structure make sure correct type and structure is used
- Handle missing configuration gracefully

**Implementation Tasks:**
- [ ] Create TOML parser with error handling
- [ ] Implement configuration validation schema
- [ ] Add configuration path resolution logic (using XDG specification)
- [ ] Handle missing user configuration file gracefully (e.g., with a clear error message)

**Files to implement:**
```
src/
├── config/
│   ├── __init__.py
│   ├── parser.py          # TOML parsing and validation
│   ├── validator.py       # Configuration validation
│   └── defaults.py        # Default values for *optional* fields
```

**Expected Output:**
```python
config = load_config()  # Loads from `$XDG_CONFIG_HOME/luminol/config.toml` or `$HOME/.config/luminol/config.toml`
print(config.global_settings.theme_type)  # "auto"
```

**Testing:**
- Valid TOML parsing
- Invalid TOML error handling
- Missing file fallback to defaults
- Configuration validation

### 1.2 Preset Color System (Days 4-5)
**Complexity**:  (Low)

**Objectives:**
- Create hardcoded semantic color palettes just for testing (light/dark themes)
- Implement color format conversions (hex6, hex8, rgb, rgba, etc.)
- Build semantic color name system

**Implementation Tasks:**
- [ ] Define semantic color structure
- [ ] Create preset light/dark palettes
- [ ] Implement color format conversion utilities
- [ ] Create color validation functions
- [ ] Add color contrast calculation helpers

**Files to implement:**
```
src/
├── colors/
│   ├── __init__.py
│   ├── formats.py         # Color format conversions
│   ├── presets.py         # Hardcoded color palettes
│   ├── semantic.py        # Semantic color definitions
│   └── utils.py           # Color utilities and validation
```

**Preset Palettes:**
```python
# Example preset palettes
DARK_PRESET = {
    "bg-primary": "#1e1e2e",
    "bg-secondary": "#313244", 
    "bg-tertiary": "#45475a",
    "text-primary": "#cdd6f4",
    "text-secondary": "#bac2de",
    "accent-primary": "#8af4da",
    "accent-secondary": "#f38ba8",
    "error-color": "#f38ba8",
    "warning-color": "#f9e2af",
    "success-color": "#a6e3a1",
    "border-active": "#cdd6f4",
    "border-inactive": "#313244"
}

LIGHT_PRESET = {
    # Light theme equivalents...
}
```

**Color Format Support:**
```python
convert_color("#ff5733", "hex6")      # "#ff5733"
convert_color("#ff5733", "hex8")      # "#ff5733ff"
convert_color("#ff5733", "rgb")       # "rgb(255, 87, 51)"
convert_color("#ff5733", "rgba")      # "rgba(255, 87, 51, 1.0)"
convert_color("#ff5733", "rgb_decimal") # "255,87,51"
```

**Testing:**
- Color format conversions
- Preset palette loading
- Color validation functions
- Semantic color structure

### 1.3 Basic File Generation (Days 6-7)
**Complexity**:  (Medium-Low)

**Objectives:**
- Implement syntax-based color file generation
- Support basic applications (Waybar, Rofi, GTK)
- File writing with proper permissions
- Directory creation if needed

**Implementation Tasks:**
- [ ] Create file generation framework
- [ ] Implement syntax pattern processing
- [ ] Add file I/O with error handling
- [ ] Create directory structure as needed
- [ ] Add backup functionality for existing files

**Files to implement:**
```
src/
├── generators/
│   ├── __init__.py
│   ├── base.py            # Base generator class
│   ├── syntax.py          # Syntax-based generator
│   └── file_manager.py    # File I/O operations
```

**Syntax Pattern Examples:**
```python
SYNTAX_PATTERNS = {
    "waybar": "@define-color {name} {color};",
    "hyprland": "${name} = {color}",
    "rofi": "*{{{name}}}: {color};",
    "gtk": "@define-color {name} {color};"
}
```

**Expected Output Files:**

**Waybar** (`~/.config/waybar/colors.css`):
```css
@define-color bg-primary #1e1e2e;
@define-color bg-secondary #313244;
@define-color text-primary #cdd6f4;
@define-color accent-primary #8af4da;
```

**Rofi** (`~/.config/rofi/colors.rasi`):
```css
*bg-primary: #1e1e2e;
*bg-secondary: #313244;
*text-primary: #cdd6f4;
*accent-primary: #8af4da;
```

**Testing:**
- File generation for each supported app
- Directory creation
- File permission handling
- Backup creation and restoration

### 1.4 Command Line Interface (Days 8-9)
**Complexity**:  (Low)

**Objectives:**
- Create basic CLI with argument parsing
- Support theme selection (light/dark)
- Add verbose output option
- Implement help system

**Implementation Tasks:**
- [ ] Create CLI argument parser
- [ ] Add theme selection options
- [ ] Implement verbose logging
- [ ] Create help documentation
- [ ] Add basic error reporting

**Files to implement:**
```
src/
├── cli/
│   ├── __init__.py
│   ├── parser.py          # Argument parsing
│   ├── commands.py        # CLI commands
│   └── output.py          # Output formatting
└── luminol.py             # Main entry point
```

**CLI Interface:**
```bash
luminol --theme dark wallpaper.png --verbose
luminol --theme light another-wallpaper.png
luminol --help
```

**Testing:**
- Argument parsing
- Help output
- Error handling
- Theme selection

### 1.5 Testing & Integration (Days 10)
**Complexity**:  (Low)

**Objectives:**
- Comprehensive unit testing
- Integration testing
- End-to-end workflow testing
- Documentation examples

**Implementation Tasks:**
- [ ] Unit tests for all modules
- [ ] Integration tests for complete workflow
- [ ] Test with actual applications (Waybar, Rofi)
- [ ] Performance testing with different configurations
- [ ] Error handling validation

**Files to implement:**
```
tests/
├── __init__.py
├── test_config.py         # Configuration testing
├── test_colors.py         # Color system testing
├── test_generators.py     # File generation testing
├── test_cli.py           # CLI testing
├── test_integration.py    # End-to-end testing
└── fixtures/             # Test data
    ├── configs/
    └── expected_outputs/
```

**Phase 1 Deliverable:**
- Working configuration system
- Preset color palette support
- Basic file generation for Waybar, Rofi, GTK
- Command-line interface
- Comprehensive testing suite

---

## Phase 2: Remap System (Week 3) - **Complexity: Medium**
**Goal**: Implement color remapping functionality

### 2.1 Remap Configuration Parsing (Days 1-2)
**Complexity**:  (Medium)

**Objectives:**
- Parse `remap-colors` boolean flag
- Handle `[app.colors]` sections
- Validate color mappings
- Error handling for invalid mappings

**Implementation Tasks:**
- [ ] Extend configuration parser for remap sections
- [ ] Add mapping validation logic
- [ ] Create error reporting for invalid mappings
- [ ] Support nested configuration sections

**Enhanced Configuration Format:**
```toml
[waybar]
enabled = true
remap-colors = true
file = "~/.config/waybar/colors.css"
syntax = "@define-color {name} {color};"

[waybar.colors]
theme-background = "bg-primary"
theme-text = "text-primary"
theme-accent = "accent-primary"
```

**Files to enhance:**
```
src/config/
├── parser.py              # Enhanced with remap parsing
├── remap_validator.py     # Remap-specific validation
└── mapping.py             # Color mapping logic
```

**Testing:**
- Remap configuration parsing
- Mapping validation
- Error handling for invalid mappings

### 2.2 Remap Logic Implementation (Days 3-4)
**Complexity**:  (Medium)

**Objectives:**
- Implement dual-mode color generation
- Selective color export (remap=true)
- Full palette export (remap=false, default)
- Custom color name substitution

**Implementation Tasks:**
- [ ] Create remap processor class
- [ ] Implement selective color filtering
- [ ] Add custom name substitution
- [ ] Maintain backward compatibility

**Files to implement:**
```
src/
├── remap/
│   ├── __init__.py
│   ├── processor.py       # Core remapping logic
│   ├── mapper.py          # Color name mapping
│   └── validator.py       # Mapping validation
```

**Processing Logic:**
```python
def process_colors(semantic_palette, app_config):
    if app_config.remap_colors:
        # Custom mapping mode
        return apply_custom_mapping(semantic_palette, app_config.colors)
    else:
        # Default mode - export all semantic colors
        return semantic_palette
```

**Testing:**
- Remap logic for both modes
- Custom name substitution
- Backward compatibility

### 2.3 Enhanced File Generation (Days 5-6)
**Complexity**:  (Medium)

**Objectives:**
- Integrate remap system with file generation
- Support both syntax and template-based generation
- Maintain clean, readable output files

**Implementation Tasks:**
- [ ] Modify generators to use remap system
- [ ] Update syntax processor for custom names
- [ ] Ensure clean output formatting
- [ ] Add generation mode indicators in comments

**Enhanced Generators:**
```python
class SyntaxGenerator:
    def generate(self, colors, app_config):
        if app_config.remap_colors:
            colors = self.remap_processor.process(colors, app_config)
        return self.apply_syntax(colors, app_config.syntax)
```

**Output Examples:**

**With Remapping** (`remap-colors = true`):
```css
/* Generated by Luminol with custom color mapping */
@define-color theme-background #1e1e2e;
@define-color theme-text #cdd6f4;
@define-color theme-accent #8af4da;
```

**Without Remapping** (`remap-colors = false`):
```css
/* Generated by Luminol with full semantic palette */
@define-color bg-primary #1e1e2e;
@define-color bg-secondary #313244;
@define-color bg-tertiary #45475a;
/* ... all semantic colors ... */
```

**Testing:**
- Both generation modes
- Output file validation
- Integration with existing apps

### 2.4 Testing & Documentation (Day 7)
**Complexity**:  (Low)

**Objectives:**
- Comprehensive testing of remap functionality
- Update documentation with examples
- User guide for remap feature

**Phase 2 Deliverable:**
- Full remapping system implementation
- Both export modes working
- Updated documentation
- Comprehensive testing

---

## Phase 3: Color Transformation System (Week 4) - **Complexity: Medium-High**
**Goal**: Implement color transformations (e.g., brightness, saturation) within the remap system.

### 3.1 Transformation-Aware Configuration (Days 1-2)
**Complexity**: (Medium)

**Objectives**:
- Extend the configuration parser to handle array syntax for transformations.
- Example: `bar-bg = ["bg-primary", "opacity=0.8"]`
- Validate transformation syntax and values.

**Implementation Tasks**:
- [ ] Update TOML parser for string-or-array values.
- [ ] Add validation for transformation functions and their arguments.
- [ ] Provide clear error messages for malformed transformations.

**Files to enhance**:
```
src/config/
├── parser.py
└── validator.py
```

### 3.2 Transformation Logic (Days 3-4)
**Complexity**: (Medium-High)

**Objectives**:
- Implement the color modification logic for all supported transformations.
- Ensure a predictable order of operations.

**Implementation Tasks**:
- [ ] Create a `transform.py` module within `src/colors/`.
- [ ] Implement functions for brightness, saturation, opacity, hue, etc.
- [ ] Define and apply a fixed transformation pipeline (e.g., Hue -> Saturation -> Brightness).

**Files to implement**:
```
src/colors/
└── transform.py
```

### 3.3 Integration and Testing (Days 5-7)
**Complexity**: (Medium)

**Objectives**:
- Integrate the transformation system into the main generation pipeline.
- Write comprehensive tests to verify output.

**Implementation Tasks**:
- [ ] Modify the `remap/processor.py` to apply transformations when detected.
- [ ] Add unit tests for each transformation function.
- [ ] Add integration tests for end-to-end validation.
- [ ] Update documentation with examples.

**Phase 3 Deliverable**:
- Fully working color transformation system.
- Updated configuration parsing and validation.
- Comprehensive tests and documentation for the new feature.

---

## Phase 4: Template System (Week 5) - **Complexity: Medium-High**
**Goal**: Implement template-based file generation for complex applications

### 4.1 Template Engine (Days 1-3)
**Complexity**:  (Medium-High)

**Objectives:**
- Template file loading and parsing
- Placeholder substitution system
- Template validation
- Error handling for malformed templates

**Implementation Tasks:**
- [ ] Create template parsing engine
- [ ] Implement placeholder substitution
- [ ] Add template validation
- [ ] Support nested placeholders
- [ ] Create template inheritance system

**Files to implement:**
```
src/
├── templates/
│   ├── __init__.py
│   ├── engine.py          # Template processing engine
│   ├── loader.py          # Template file loading
│   ├── validator.py       # Template validation
│   └── substitutor.py     # Placeholder substitution
```

**Template Processing:**
```python
# Load template
template = load_template("dunst.template")

# Apply color mapping
colors = {
    "col1": "#8af4da",
    "col2": "#1e1e2e", 
    "text1": "#cdd6f4"
}

# Generate final config
output = template.substitute(colors)
```

### 4.2 Template-Based Applications (Days 4-5)
**Complexity**:  (Medium)

**Objectives:**
- Support for Dunst, i3, Sway configurations
- Template file management
- Integration with remap system

**Template Examples:**

**Dunst Template** (`$XDG_CONFIG_HOME/luminol/templates/dunst.template`):
```ini
[global]
frame_color = "{col1}"
separator_color = frame

[urgency_low]
background = "{col2}"
foreground = "{text1}"

[urgency_normal]
background = "{col3}"
foreground = "{text1}"

[urgency_critical]
background = "{error}"
foreground = "{text2}"
```

**i3 Template** (`$XDG_CONFIG_HOME/luminol/templates/i3.template`):
```
client.focused          {focused}    {focused}    {text}    {focused}
client.focused_inactive {unfocused}  {unfocused}  {text}    {unfocused}
client.unfocused        {unfocused}  {background} {text}    {unfocused}
client.urgent           {urgent}     {urgent}     {text}    {urgent}
```

### 4.3 Integration & Testing (Days 6-7)
**Complexity**:  (Medium)

**Phase 4 Deliverable:**
- Template system working
- Support for complex applications
- Template validation and error handling

---

## Phase 5: Image Processing (Week 6-7) - **Complexity: High**
**Goal**: Replace preset colors with actual wallpaper color extraction

### 5.1 Basic Color Extraction (Days 1-3)
**Complexity**:  (High)

**Objectives:**
- Image loading and preprocessing
- Basic k-means clustering implementation
- Dominant color identification

**Implementation Tasks:**
- [ ] Image loading with PIL/OpenCV
- [ ] Image preprocessing (resize, blur)
- [ ] K-means clustering implementation
- [ ] Color quality assessment
- [ ] Performance optimization

**Files to implement:**
```
src/
├── extraction/
│   ├── __init__.py
│   ├── image_loader.py    # Image loading and preprocessing
│   ├── kmeans.py          # K-means clustering
│   ├── quality.py         # Color quality assessment
│   └── optimizer.py       # Performance optimizations
```

### 5.2 Intelligent Color Assignment (Days 4-5)
**Complexity**:  (Very High)

**Objectives:**
- Background color selection logic
- Text color optimization for accessibility
- Accent color intelligence
- Theme detection (light/dark)

### 5.3 Integration & Testing (Days 6-7)
**Complexity**:  (High)

**Phase 5 Deliverable:**
- Working color extraction from images
- Intelligent color role assignment
- Performance optimized processing

---

## Phase 6: Advanced Features (Week 8-9) - **Complexity: Medium**
**Goal**: Polish, optimization, and advanced features

### 6.1 Performance Optimization
- Caching system
- Parallel processing
- Memory optimization

### 6.2 Advanced CLI Features
- Interactive mode
- Configuration wizard
- Dry-run mode

### 6.3 Error Handling & Logging
- Comprehensive error handling
- Structured logging
- User-friendly error messages

### 6.4 Documentation & Examples
- User documentation
- Configuration examples
- Integration guides

---

## Development Guidelines

### Code Quality Standards
- **Type hints**: All functions must have type annotations
- **Documentation**: Comprehensive docstrings for all public APIs
- **Testing**: Minimum 90% code coverage
- **Linting**: Use black, isort, and mypy
- **Error handling**: Graceful degradation, never crash

### Project Structure
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

### Dependencies
- **Core**: `click`, `toml`, `Pillow`
- **Development**: `pytest`, `black`, `isort`, `mypy`
- **Optional**: `opencv-python`, `scikit-learn`

### Testing Strategy
- **Unit Tests**: Test individual functions and classes
- **Integration Tests**: Test complete workflows
- **End-to-End Tests**: Test with real applications
- **Performance Tests**: Benchmark critical paths

## Success Metrics

### Phase 1 Success Criteria
- [ ] Configuration parsing works without errors
- [ ] All color format conversions are accurate
- [ ] Generated files parse correctly in target applications
- [ ] CLI provides helpful error messages
- [ ] Test coverage > 90%

### Phase 2 Success Criteria
- [ ] Remap functionality works for all supported applications
- [ ] Both export modes generate correct output
- [ ] Backward compatibility maintained
- [ ] User documentation is clear and comprehensive

### Phase 3 Success Criteria
- [ ] All transformation functions (brightness, saturation, etc.) produce correct color values.
- [ ] Transformation array syntax is parsed and validated correctly.
- [ ] Errors in transformations are handled gracefully.
- [ ] Documentation for transformations is clear.

### Phase 4 Success Criteria
- [ ] Template system handles complex configurations.
- [ ] All placeholder substitutions work correctly.
- [ ] Generated configs are syntactically valid.
- [ ] Template validation catches common errors.

### Phase 5 Success Criteria
- [ ] Color extraction works on various image types.
- [ ] Generated themes are visually appealing.
- [ ] Processing time < 2 seconds for typical wallpapers.
- [ ] Color accessibility standards are met.

### Phase 6 Success Criteria
- [ ] Performance targets are met.
- [ ] Error handling is comprehensive.
- [ ] Documentation is complete.
- [ ] Project is ready for public release.

## Risk Assessment

### Phase 1 Risks
- **Low Risk**: Configuration parsing, file generation
- **Mitigation**: Extensive testing, clear error messages

### Phase 2 Risks  
- **Medium Risk**: Complex configuration logic
- **Mitigation**: Incremental development, comprehensive testing

### Phase 4 Risks
- **Medium-High Risk**: Parsing complex, non-standard config files. Ensuring placeholder substitution is robust and doesn't lead to broken configs.
- **Mitigation**: Extensive testing, clear error messages for template authors.

### Phase 5 Risks
- **High Risk**: Color extraction quality, performance
- **Mitigation**: Algorithm research, performance profiling, fallback options

## Timeline Summary

| Phase | Duration | Complexity  | Key Deliverable                  |
|-------|----------|-------------|----------------------------------|
| 1     | 2 weeks  | Low         | Basic functionality with presets |
| 2     | 1 week   | Medium      | Color remapping system           |
| 3     | 1 week   | Medium-High | Color transformation system      |
| 4     | 1 week   | Medium-High | Template system                  |
| 5     | 2 weeks  | High        | Image color extraction           |
| 6     | 2 weeks  | Medium      | Polish and advanced features     |

**Total Project Duration**: 9 weeks
**MVP Ready**: After Phase 2 (3 weeks)
**Feature Complete**: After Phase 5 (7 weeks)
**Production Ready**: After Phase 6 (9 weeks)
