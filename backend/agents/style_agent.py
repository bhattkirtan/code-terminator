"""
StyleAgent - Applies SCSS/themes from uploaded files or inferred design
"""
import logging
from typing import Dict, Any, List, Optional
import re

logger = logging.getLogger(__name__)

class StyleAgent:
    def __init__(self):
        self.name = "StyleAgent"
        self.version = "1.0.0"
        self.material_theme_colors = {
            "primary": "#1976d2",
            "accent": "#ff4081",
            "warn": "#f44336"
        }
    
    async def apply_styles(self, code_files: Dict[str, Any], screenshot_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Apply styling to generated code based on screenshot analysis and design patterns
        """
        logger.info("Applying styles to generated code")
        
        # Analyze design patterns from screenshots
        design_analysis = await self._analyze_design_patterns(screenshot_data)
        
        # Generate theme configuration
        theme_config = await self._generate_theme_config(design_analysis)
        
        # Update component styles
        styled_code = await self._apply_component_styles(code_files, theme_config, design_analysis)
        
        # Generate global styles
        global_styles = await self._generate_global_styles(theme_config, design_analysis)
        
        # Add theme files
        styled_code["styles"] = global_styles
        styled_code["theme_config"] = theme_config
        
        logger.info("Style application completed")
        return styled_code
    
    async def _analyze_design_patterns(self, screenshot_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze design patterns from screenshot data"""
        analysis = {
            "color_scheme": self._extract_color_scheme(screenshot_data),
            "typography": self._analyze_typography(screenshot_data),
            "spacing": self._analyze_spacing(screenshot_data),
            "layout_patterns": self._analyze_layout_patterns(screenshot_data),
            "component_styles": self._analyze_component_styles(screenshot_data),
            "responsive_patterns": self._analyze_responsive_patterns(screenshot_data)
        }
        
        return analysis
    
    def _extract_color_scheme(self, screenshot_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract color scheme from screenshots"""
        # In a real implementation, this would use computer vision to extract actual colors
        # For now, we'll use mock analysis based on semantic features
        
        color_schemes = []
        for data in screenshot_data:
            semantic_features = data.get("semantic_features", {})
            color_scheme = semantic_features.get("color_scheme", {})
            
            if color_scheme:
                color_schemes.append(color_scheme)
        
        # Generate consolidated color scheme
        if color_schemes:
            primary_colors = []
            for scheme in color_schemes:
                primary_colors.extend(scheme.get("primary_colors", []))
            
            # Use most common colors or defaults
            consolidated_scheme = {
                "primary": primary_colors[0] if primary_colors else "#2196F3",
                "secondary": primary_colors[1] if len(primary_colors) > 1 else "#FFC107",
                "accent": primary_colors[2] if len(primary_colors) > 2 else "#FF5722",
                "background": "#fafafa",
                "surface": "#ffffff",
                "text_primary": "#212121",
                "text_secondary": "#757575"
            }
        else:
            # Default Material Design colors
            consolidated_scheme = {
                "primary": "#2196F3",
                "secondary": "#FFC107",
                "accent": "#FF5722",
                "background": "#fafafa",
                "surface": "#ffffff",
                "text_primary": "#212121",
                "text_secondary": "#757575"
            }
        
        return consolidated_scheme
    
    def _analyze_typography(self, screenshot_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze typography patterns"""
        # Mock typography analysis
        return {
            "font_family": "Roboto, 'Helvetica Neue', sans-serif",
            "font_sizes": {
                "display-4": "112px",
                "display-3": "56px",
                "display-2": "45px",
                "display-1": "34px",
                "headline": "24px",
                "title": "20px",
                "subheading-2": "16px",
                "subheading-1": "15px",
                "body-2": "14px",
                "body-1": "14px",
                "caption": "12px",
                "button": "14px"
            },
            "font_weights": {
                "light": 300,
                "regular": 400,
                "medium": 500,
                "bold": 700
            },
            "line_heights": {
                "tight": 1.2,
                "normal": 1.5,
                "relaxed": 1.8
            }
        }
    
    def _analyze_spacing(self, screenshot_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze spacing patterns"""
        return {
            "base_unit": "8px",
            "spacing_scale": {
                "xs": "4px",
                "sm": "8px",
                "md": "16px",
                "lg": "24px",
                "xl": "32px",
                "xxl": "48px"
            },
            "container_padding": "20px",
            "section_margin": "32px",
            "component_gap": "16px"
        }
    
    def _analyze_layout_patterns(self, screenshot_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze layout patterns"""
        return {
            "grid_system": "12-column",
            "breakpoints": {
                "xs": "0px",
                "sm": "600px",
                "md": "960px",
                "lg": "1280px",
                "xl": "1920px"
            },
            "container_max_width": "1200px",
            "sidebar_width": "280px",
            "header_height": "64px",
            "footer_height": "48px"
        }
    
    def _analyze_component_styles(self, screenshot_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze component-specific styling patterns"""
        return {
            "cards": {
                "border_radius": "8px",
                "elevation": "2px",
                "padding": "16px",
                "margin": "8px"
            },
            "buttons": {
                "border_radius": "4px",
                "padding": "8px 16px",
                "font_weight": "500",
                "text_transform": "uppercase"
            },
            "tables": {
                "border": "1px solid #e0e0e0",
                "header_background": "#f5f5f5",
                "row_hover": "#f0f0f0",
                "cell_padding": "12px"
            },
            "forms": {
                "field_margin": "16px",
                "label_color": "#666",
                "border_color": "#ddd",
                "focus_color": "#2196F3"
            }
        }
    
    def _analyze_responsive_patterns(self, screenshot_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze responsive design patterns"""
        return {
            "mobile_first": True,
            "fluid_grid": True,
            "flexible_images": True,
            "responsive_typography": True,
            "adaptive_navigation": True
        }
    
    async def _generate_theme_config(self, design_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Angular Material theme configuration"""
        color_scheme = design_analysis["color_scheme"]
        typography = design_analysis["typography"]
        spacing = design_analysis["spacing"]
        
        theme_config = {
            "colors": {
                "primary": {
                    "50": self._lighten_color(color_scheme["primary"], 0.9),
                    "100": self._lighten_color(color_scheme["primary"], 0.7),
                    "200": self._lighten_color(color_scheme["primary"], 0.5),
                    "300": self._lighten_color(color_scheme["primary"], 0.3),
                    "400": self._lighten_color(color_scheme["primary"], 0.15),
                    "500": color_scheme["primary"],
                    "600": self._darken_color(color_scheme["primary"], 0.15),
                    "700": self._darken_color(color_scheme["primary"], 0.3),
                    "800": self._darken_color(color_scheme["primary"], 0.5),
                    "900": self._darken_color(color_scheme["primary"], 0.7),
                    "contrast": {
                        "50": "#000000",
                        "100": "#000000",
                        "200": "#000000",
                        "300": "#000000",
                        "400": "#ffffff",
                        "500": "#ffffff",
                        "600": "#ffffff",
                        "700": "#ffffff",
                        "800": "#ffffff",
                        "900": "#ffffff"
                    }
                },
                "accent": color_scheme["accent"],
                "warn": "#f44336",
                "background": color_scheme["background"],
                "surface": color_scheme["surface"],
                "text": {
                    "primary": color_scheme["text_primary"],
                    "secondary": color_scheme["text_secondary"]
                }
            },
            "typography": typography,
            "spacing": spacing
        }
        
        return theme_config
    
    def _lighten_color(self, color: str, amount: float) -> str:
        """Lighten a hex color by a given amount"""
        # Simplified color manipulation - in practice, use a proper color library
        return color  # Return original for now
    
    def _darken_color(self, color: str, amount: float) -> str:
        """Darken a hex color by a given amount"""
        # Simplified color manipulation - in practice, use a proper color library
        return color  # Return original for now
    
    async def _apply_component_styles(self, code_files: Dict[str, Any], theme_config: Dict[str, Any], design_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Apply styles to individual components"""
        styled_code = code_files.copy()
        
        # Update component SCSS files
        if "components" in styled_code:
            for component_name, component_files in styled_code["components"].items():
                if "component.scss" in component_files:
                    enhanced_scss = await self._enhance_component_scss(
                        component_files["component.scss"],
                        component_name,
                        theme_config,
                        design_analysis
                    )
                    styled_code["components"][component_name]["component.scss"] = enhanced_scss
        
        return styled_code
    
    async def _enhance_component_scss(self, existing_scss: str, component_name: str, theme_config: Dict[str, Any], design_analysis: Dict[str, Any]) -> str:
        """Enhance component SCSS with theme variables and design patterns"""
        color_scheme = design_analysis["color_scheme"]
        spacing = design_analysis["spacing"]
        component_styles = design_analysis["component_styles"]
        
        # Add theme variables at the top
        theme_variables = f'''// Theme Variables
$primary-color: {color_scheme["primary"]};
$secondary-color: {color_scheme["secondary"]};
$accent-color: {color_scheme["accent"]};
$background-color: {color_scheme["background"]};
$surface-color: {color_scheme["surface"]};
$text-primary: {color_scheme["text_primary"]};
$text-secondary: {color_scheme["text_secondary"]};

// Spacing Variables
$spacing-xs: {spacing["spacing_scale"]["xs"]};
$spacing-sm: {spacing["spacing_scale"]["sm"]};
$spacing-md: {spacing["spacing_scale"]["md"]};
$spacing-lg: {spacing["spacing_scale"]["lg"]};
$spacing-xl: {spacing["spacing_scale"]["xl"]};

'''
        
        # Add component-specific mixins and styles
        component_mixins = self._generate_component_mixins(component_name, component_styles, theme_config)
        
        # Enhanced styles with theme integration
        enhanced_styles = f'''
// Enhanced component styles with theme integration
.{component_name}-container {{
  // Apply theme colors
  background-color: $surface-color;
  color: $text-primary;
  
  // Apply responsive spacing
  padding: $spacing-md;
  
  @media (max-width: 768px) {{
    padding: $spacing-sm;
  }}
  
  // Material Design elevation
  &.elevated {{
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }}
  
  // Theme-aware hover states
  &:hover {{
    background-color: lighten($surface-color, 2%);
  }}
}}

// Component-specific theme overrides
.mat-card {{
  background-color: $surface-color;
  border-radius: {component_styles["cards"]["border_radius"]};
  
  .mat-card-header {{
    background-color: lighten($primary-color, 45%);
    color: $text-primary;
  }}
}}

.mat-button, .mat-raised-button {{
  border-radius: {component_styles["buttons"]["border_radius"]};
  font-weight: {component_styles["buttons"]["font_weight"]};
  text-transform: {component_styles["buttons"]["text_transform"]};
}}

.mat-table {{
  background-color: $surface-color;
  
  .mat-header-cell {{
    background-color: {component_styles["tables"]["header_background"]};
    color: $text-primary;
    font-weight: 500;
  }}
  
  .mat-row:hover {{
    background-color: {component_styles["tables"]["row_hover"]};
  }}
}}

{component_mixins}
'''
        
        # Combine everything
        return theme_variables + enhanced_styles + "\n" + existing_scss
    
    def _generate_component_mixins(self, component_name: str, component_styles: Dict[str, Any], theme_config: Dict[str, Any]) -> str:
        """Generate component-specific SCSS mixins"""
        mixins = f'''
// Component-specific mixins for {component_name}
@mixin {component_name}-theme($theme) {{
  $primary: map-get($theme, primary);
  $accent: map-get($theme, accent);
  $warn: map-get($theme, warn);
  $background: map-get($theme, background);
  $foreground: map-get($theme, foreground);
  
  .{component_name}-container {{
    background: mat-color($background, card);
    color: mat-color($foreground, text);
  }}
  
  .{component_name}-primary {{
    background: mat-color($primary);
    color: mat-color($primary, default-contrast);
  }}
  
  .{component_name}-accent {{
    background: mat-color($accent);
    color: mat-color($accent, default-contrast);
  }}
}}

// Responsive mixins
@mixin respond-to($breakpoint) {{
  @if $breakpoint == mobile {{
    @media (max-width: 767px) {{ @content; }}
  }}
  @if $breakpoint == tablet {{
    @media (min-width: 768px) and (max-width: 1023px) {{ @content; }}
  }}
  @if $breakpoint == desktop {{
    @media (min-width: 1024px) {{ @content; }}
  }}
}}

// Animation mixins
@mixin smooth-transition($property: all, $duration: 0.3s) {{
  transition: $property $duration ease-in-out;
}}
'''
        return mixins
    
    async def _generate_global_styles(self, theme_config: Dict[str, Any], design_analysis: Dict[str, Any]) -> Dict[str, str]:
        """Generate global style files"""
        return {
            "styles.scss": self._generate_main_styles(theme_config, design_analysis),
            "theme.scss": self._generate_theme_styles(theme_config),
            "variables.scss": self._generate_variables(theme_config, design_analysis),
            "mixins.scss": self._generate_global_mixins(design_analysis),
            "responsive.scss": self._generate_responsive_styles(design_analysis)
        }
    
    def _generate_main_styles(self, theme_config: Dict[str, Any], design_analysis: Dict[str, Any]) -> str:
        """Generate main styles.scss file"""
        color_scheme = design_analysis["color_scheme"]
        typography = design_analysis["typography"]
        spacing = design_analysis["spacing"]
        
        return f'''/* Global Styles */
@import '~@angular/material/theming';
@import './theme.scss';
@import './variables.scss';
@import './mixins.scss';
@import './responsive.scss';

// Include material theme
@include mat-core();
@include angular-material-theme($app-theme);

/* Reset and Base Styles */
* {{
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}}

html, body {{
  height: 100%;
  font-family: {typography["font_family"]};
  background-color: {color_scheme["background"]};
  color: {color_scheme["text_primary"]};
  line-height: {typography["line_heights"]["normal"]};
}}

/* Typography */
h1, h2, h3, h4, h5, h6 {{
  font-weight: {typography["font_weights"]["medium"]};
  line-height: {typography["line_heights"]["tight"]};
  margin-bottom: {spacing["spacing_scale"]["md"]};
}}

h1 {{ font-size: {typography["font_sizes"]["display-1"]}; }}
h2 {{ font-size: {typography["font_sizes"]["headline"]}; }}
h3 {{ font-size: {typography["font_sizes"]["title"]}; }}
h4 {{ font-size: {typography["font_sizes"]["subheading-1"]}; }}

p {{
  margin-bottom: {spacing["spacing_scale"]["md"]};
  line-height: {typography["line_heights"]["normal"]};
}}

/* Layout Utilities */
.container {{
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 {spacing["container_padding"]};
}}

.row {{
  display: flex;
  flex-wrap: wrap;
  margin: 0 -{spacing["spacing_scale"]["sm"]};
}}

.col {{
  flex: 1;
  padding: 0 {spacing["spacing_scale"]["sm"]};
}}

/* Spacing Utilities */
.m-0 {{ margin: 0; }}
.m-1 {{ margin: {spacing["spacing_scale"]["xs"]}; }}
.m-2 {{ margin: {spacing["spacing_scale"]["sm"]}; }}
.m-3 {{ margin: {spacing["spacing_scale"]["md"]}; }}
.m-4 {{ margin: {spacing["spacing_scale"]["lg"]}; }}

.p-0 {{ padding: 0; }}
.p-1 {{ padding: {spacing["spacing_scale"]["xs"]}; }}
.p-2 {{ padding: {spacing["spacing_scale"]["sm"]}; }}
.p-3 {{ padding: {spacing["spacing_scale"]["md"]}; }}
.p-4 {{ padding: {spacing["spacing_scale"]["lg"]}; }}

/* Flexbox Utilities */
.d-flex {{ display: flex; }}
.justify-center {{ justify-content: center; }}
.justify-between {{ justify-content: space-between; }}
.align-center {{ align-items: center; }}
.flex-column {{ flex-direction: column; }}

/* Text Utilities */
.text-center {{ text-align: center; }}
.text-left {{ text-align: left; }}
.text-right {{ text-align: right; }}
.text-primary {{ color: {color_scheme["primary"]}; }}
.text-secondary {{ color: {color_scheme["text_secondary"]}; }}

/* Custom Scrollbar */
::-webkit-scrollbar {{
  width: 8px;
}}

::-webkit-scrollbar-track {{
  background: {color_scheme["background"]};
}}

::-webkit-scrollbar-thumb {{
  background: {color_scheme["text_secondary"]};
  border-radius: 4px;
}}

::-webkit-scrollbar-thumb:hover {{
  background: {color_scheme["text_primary"]};
}}

/* Focus States */
*:focus {{
  outline: 2px solid {color_scheme["primary"]};
  outline-offset: 2px;
}}

/* Animation */
* {{
  transition: color 0.3s ease, background-color 0.3s ease, border-color 0.3s ease;
}}
'''

    def _generate_theme_styles(self, theme_config: Dict[str, Any]) -> str:
        """Generate theme.scss file"""
        colors = theme_config["colors"]
        
        return f'''/* Angular Material Theme Configuration */
@import '~@angular/material/theming';

// Define custom palettes
$app-primary: mat-palette($mat-blue, 500, 100, 900);
$app-accent: mat-palette($mat-orange, 500, 100, 900);
$app-warn: mat-palette($mat-red);

// Create theme
$app-theme: mat-light-theme((
  color: (
    primary: $app-primary,
    accent: $app-accent,
    warn: $app-warn,
  )
));

// Dark theme (optional)
$app-dark-theme: mat-dark-theme((
  color: (
    primary: $app-primary,
    accent: $app-accent,
    warn: $app-warn,
  )
));

// Custom theme colors
:root {{
  --primary-color: {colors["primary"]["500"]};
  --primary-light: {colors["primary"]["300"]};
  --primary-dark: {colors["primary"]["700"]};
  --accent-color: {colors["accent"]};
  --warn-color: {colors["warn"]};
  --background-color: {colors["background"]};
  --surface-color: {colors["surface"]};
  --text-primary: {colors["text"]["primary"]};
  --text-secondary: {colors["text"]["secondary"]};
}}

// Dark theme variables
[data-theme="dark"] {{
  --background-color: #303030;
  --surface-color: #424242;
  --text-primary: #ffffff;
  --text-secondary: #b0b0b0;
}}
'''

    def _generate_variables(self, theme_config: Dict[str, Any], design_analysis: Dict[str, Any]) -> str:
        """Generate variables.scss file"""
        spacing = design_analysis["spacing"]
        layout = design_analysis["layout_patterns"]
        
        return f'''/* SCSS Variables */

// Colors
$primary: {theme_config["colors"]["primary"]["500"]};
$accent: {theme_config["colors"]["accent"]};
$warn: {theme_config["colors"]["warn"]};
$background: {theme_config["colors"]["background"]};
$surface: {theme_config["colors"]["surface"]};
$text-primary: {theme_config["colors"]["text"]["primary"]};
$text-secondary: {theme_config["colors"]["text"]["secondary"]};

// Spacing
$spacing-xs: {spacing["spacing_scale"]["xs"]};
$spacing-sm: {spacing["spacing_scale"]["sm"]};
$spacing-md: {spacing["spacing_scale"]["md"]};
$spacing-lg: {spacing["spacing_scale"]["lg"]};
$spacing-xl: {spacing["spacing_scale"]["xl"]};
$spacing-xxl: {spacing["spacing_scale"]["xxl"]};

// Breakpoints
$breakpoint-xs: {layout["breakpoints"]["xs"]};
$breakpoint-sm: {layout["breakpoints"]["sm"]};
$breakpoint-md: {layout["breakpoints"]["md"]};
$breakpoint-lg: {layout["breakpoints"]["lg"]};
$breakpoint-xl: {layout["breakpoints"]["xl"]};

// Layout
$container-max-width: {layout["container_max_width"]};
$sidebar-width: {layout["sidebar_width"]};
$header-height: {layout["header_height"]};
$footer-height: {layout["footer_height"]};

// Border Radius
$border-radius-sm: 4px;
$border-radius-md: 8px;
$border-radius-lg: 12px;

// Shadows
$shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.12);
$shadow-md: 0 4px 6px rgba(0, 0, 0, 0.15);
$shadow-lg: 0 10px 25px rgba(0, 0, 0, 0.19);

// Z-index scale
$z-dropdown: 1000;
$z-sticky: 1020;
$z-fixed: 1030;
$z-modal-backdrop: 1040;
$z-modal: 1050;
$z-popover: 1060;
$z-tooltip: 1070;
'''

    def _generate_global_mixins(self, design_analysis: Dict[str, Any]) -> str:
        """Generate mixins.scss file"""
        return '''/* SCSS Mixins */

// Responsive mixins
@mixin respond-to($breakpoint) {
  @if $breakpoint == xs {
    @media (max-width: 599px) { @content; }
  }
  @if $breakpoint == sm {
    @media (min-width: 600px) and (max-width: 959px) { @content; }
  }
  @if $breakpoint == md {
    @media (min-width: 960px) and (max-width: 1279px) { @content; }
  }
  @if $breakpoint == lg {
    @media (min-width: 1280px) and (max-width: 1919px) { @content; }
  }
  @if $breakpoint == xl {
    @media (min-width: 1920px) { @content; }
  }
}

// Flexbox mixins
@mixin flex-center {
  display: flex;
  align-items: center;
  justify-content: center;
}

@mixin flex-between {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

// Button mixins
@mixin button-variant($bg-color, $text-color) {
  background-color: $bg-color;
  color: $text-color;
  border: none;
  padding: $spacing-sm $spacing-md;
  border-radius: $border-radius-sm;
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover {
    background-color: darken($bg-color, 10%);
  }
  
  &:focus {
    outline: 2px solid lighten($bg-color, 20%);
    outline-offset: 2px;
  }
}

// Card mixins
@mixin card-style($padding: $spacing-md) {
  background: $surface;
  border-radius: $border-radius-md;
  box-shadow: $shadow-sm;
  padding: $padding;
  transition: box-shadow 0.3s ease;
  
  &:hover {
    box-shadow: $shadow-md;
  }
}

// Text mixins
@mixin text-truncate {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

@mixin text-clamp($lines) {
  display: -webkit-box;
  -webkit-line-clamp: $lines;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

// Animation mixins
@mixin smooth-transition($property: all, $duration: 0.3s, $timing: ease) {
  transition: $property $duration $timing;
}

@mixin fade-in($duration: 0.3s) {
  animation: fadeIn $duration ease-in-out;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

// Accessibility mixins
@mixin sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

@mixin focus-outline($color: $primary) {
  outline: 2px solid $color;
  outline-offset: 2px;
}
'''

    def _generate_responsive_styles(self, design_analysis: Dict[str, Any]) -> str:
        """Generate responsive.scss file"""
        return '''/* Responsive Styles */

// Mobile first approach
.container {
  width: 100%;
  padding: 0 $spacing-md;
  
  @include respond-to(sm) {
    max-width: 540px;
    margin: 0 auto;
  }
  
  @include respond-to(md) {
    max-width: 720px;
  }
  
  @include respond-to(lg) {
    max-width: 960px;
  }
  
  @include respond-to(xl) {
    max-width: 1140px;
  }
}

// Grid system
.row {
  display: flex;
  flex-wrap: wrap;
  margin: 0 -#{$spacing-sm};
}

.col {
  flex: 1;
  padding: 0 $spacing-sm;
  
  &-1 { flex: 0 0 8.333333%; max-width: 8.333333%; }
  &-2 { flex: 0 0 16.666667%; max-width: 16.666667%; }
  &-3 { flex: 0 0 25%; max-width: 25%; }
  &-4 { flex: 0 0 33.333333%; max-width: 33.333333%; }
  &-6 { flex: 0 0 50%; max-width: 50%; }
  &-8 { flex: 0 0 66.666667%; max-width: 66.666667%; }
  &-9 { flex: 0 0 75%; max-width: 75%; }
  &-12 { flex: 0 0 100%; max-width: 100%; }
}

// Responsive visibility
.d-none { display: none !important; }
.d-block { display: block !important; }
.d-flex { display: flex !important; }

@include respond-to(xs) {
  .d-xs-none { display: none !important; }
  .d-xs-block { display: block !important; }
  .d-xs-flex { display: flex !important; }
}

@include respond-to(sm) {
  .d-sm-none { display: none !important; }
  .d-sm-block { display: block !important; }
  .d-sm-flex { display: flex !important; }
}

@include respond-to(md) {
  .d-md-none { display: none !important; }
  .d-md-block { display: block !important; }
  .d-md-flex { display: flex !important; }
}

// Responsive text alignment
@include respond-to(xs) {
  .text-xs-center { text-align: center !important; }
  .text-xs-left { text-align: left !important; }
  .text-xs-right { text-align: right !important; }
}

@include respond-to(sm) {
  .text-sm-center { text-align: center !important; }
  .text-sm-left { text-align: left !important; }
  .text-sm-right { text-align: right !important; }
}

// Component responsive styles
.mat-sidenav-container {
  @include respond-to(xs) {
    .mat-sidenav {
      width: 100vw;
    }
  }
}

.mat-table {
  @include respond-to(xs) {
    font-size: 12px;
    
    .mat-header-cell,
    .mat-cell {
      padding: $spacing-xs;
    }
  }
}

.mat-card {
  @include respond-to(xs) {
    margin: $spacing-xs;
    
    .mat-card-content {
      padding: $spacing-sm;
    }
  }
}
'''

    async def get_status(self) -> Dict[str, Any]:
        """Get agent status"""
        return {
            "name": self.name,
            "version": self.version,
            "status": "active",
            "capabilities": [
                "Design pattern analysis",
                "Color scheme extraction",
                "Typography analysis",
                "SCSS generation",
                "Angular Material theming",
                "Responsive styling",
                "Component style enhancement",
                "Global style configuration"
            ]
        }