"""Style Agent for applying themes and styles to generated components."""

import re
from typing import Any, Dict, List

from config.settings import settings
from shared.models import AgentResult
from shared.utils import extract_colors_from_image, estimate_tokens
from .base_agent import BaseAgent


class StyleAgent(BaseAgent):
    """Agent that applies styles and themes to generated components."""
    
    def __init__(self):
        super().__init__("StyleAgent")
    
    async def process(self, input_data: Dict[str, Any]) -> AgentResult:
        """Apply styles and themes to component."""
        reference_styles = input_data.get("reference_styles", "")
        reference_images = input_data.get("reference_images", [])
        component_scss = input_data.get("component_scss", "")
        
        try:
            # Extract colors and styling from references
            extracted_styles = await self._extract_styles(reference_styles, reference_images)
            
            # Generate enhanced SCSS
            enhanced_scss = await self._enhance_component_styles(
                component_scss, extracted_styles
            )
            
            # Generate global theme
            global_theme = await self._generate_global_theme(extracted_styles)
            
            tokens_used = estimate_tokens(enhanced_scss + global_theme)
            
            return AgentResult(
                agent_name=self.name,
                success=True,
                output={
                    "enhanced_scss": enhanced_scss,
                    "global_theme": global_theme,
                    "extracted_styles": extracted_styles
                },
                tokens_used=tokens_used,
                carbon_emission=self._calculate_carbon_emission(
                    tokens_used,
                    "style-processing"
                )
            )
            
        except Exception as e:
            return AgentResult(
                agent_name=self.name,
                success=False,
                error=f"Style generation failed: {str(e)}"
            )
    
    async def _extract_styles(self, reference_styles: str, reference_images: List[str]) -> Dict[str, Any]:
        """Extract styling information from references."""
        extracted = {
            "colors": {
                "primary": "#1976d2",
                "accent": "#ffc107", 
                "warn": "#f44336",
                "background": "#fafafa",
                "surface": "#ffffff"
            },
            "typography": {
                "font_family": "Roboto, sans-serif",
                "font_sizes": {
                    "h1": "2rem",
                    "h2": "1.5rem",
                    "body": "1rem",
                    "caption": "0.875rem"
                }
            },
            "spacing": {
                "xs": "4px",
                "sm": "8px", 
                "md": "16px",
                "lg": "24px",
                "xl": "32px"
            },
            "borders": {
                "radius": "4px",
                "width": "1px"
            }
        }
        
        # Extract colors from reference images
        if reference_images:
            for image_path in reference_images:
                try:
                    colors = extract_colors_from_image(image_path, 5)
                    if colors:
                        extracted["colors"]["primary"] = colors[0]
                        if len(colors) > 1:
                            extracted["colors"]["accent"] = colors[1]
                        if len(colors) > 2:
                            extracted["colors"]["surface"] = colors[2]
                except Exception:
                    continue
        
        # Parse reference styles (CSS/SCSS)
        if reference_styles and reference_styles.strip():
            parsed_styles = self._parse_css_styles(reference_styles)
            extracted.update(parsed_styles)
        
        return extracted
    
    def _parse_css_styles(self, css_content: str) -> Dict[str, Any]:
        """Parse CSS/SCSS content to extract styling information."""
        styles = {
            "colors": {},
            "typography": {},
            "spacing": {}
        }
        
        # Extract CSS custom properties (CSS variables)
        css_vars = re.findall(r'--([^:]+):\s*([^;]+);', css_content)
        for var_name, var_value in css_vars:
            if 'color' in var_name.lower():
                styles["colors"][var_name.replace('-', '_')] = var_value.strip()
            elif 'font' in var_name.lower():
                styles["typography"][var_name.replace('-', '_')] = var_value.strip()
            elif any(keyword in var_name.lower() for keyword in ['margin', 'padding', 'gap', 'space']):
                styles["spacing"][var_name.replace('-', '_')] = var_value.strip()
        
        # Extract color values from hex/rgb patterns
        color_patterns = re.findall(r'#([0-9a-fA-F]{3,6})', css_content)
        rgb_patterns = re.findall(r'rgb\([^)]+\)', css_content)
        
        if color_patterns:
            styles["colors"]["extracted_hex"] = [f"#{color}" for color in color_patterns[:5]]
        if rgb_patterns:
            styles["colors"]["extracted_rgb"] = rgb_patterns[:5]
        
        # Extract font families
        font_families = re.findall(r'font-family:\s*([^;]+);', css_content, re.IGNORECASE)
        if font_families:
            styles["typography"]["font_family"] = font_families[0].strip().strip('"\'')
        
        return styles
    
    async def _enhance_component_styles(self, base_scss: str, extracted_styles: Dict[str, Any]) -> str:
        """Enhance component SCSS with extracted styles."""
        colors = extracted_styles.get("colors", {})
        typography = extracted_styles.get("typography", {})
        spacing = extracted_styles.get("spacing", {})
        
        # Create enhanced SCSS
        enhanced_parts = []
        
        # Add custom properties at the top
        enhanced_parts.append("// Enhanced styles based on reference design")
        enhanced_parts.append(":host {")
        
        # Add color variables
        if colors:
            enhanced_parts.append("  // Color palette")
            for color_name, color_value in colors.items():
                if isinstance(color_value, str) and (color_value.startswith('#') or color_value.startswith('rgb')):
                    enhanced_parts.append(f"  --{color_name.replace('_', '-')}: {color_value};")
        
        # Add spacing variables
        if spacing:
            enhanced_parts.append("  // Spacing system")
            for space_name, space_value in spacing.items():
                enhanced_parts.append(f"  --{space_name.replace('_', '-')}: {space_value};")
        
        enhanced_parts.append("}")
        enhanced_parts.append("")
        
        # Add typography styles
        if typography.get("font_family"):
            enhanced_parts.append(f"// Typography")
            enhanced_parts.append(f".component-container {{")
            enhanced_parts.append(f"  font-family: {typography['font_family']};")
            enhanced_parts.append("}")
            enhanced_parts.append("")
        
        # Add the original SCSS
        enhanced_parts.append("// Base component styles")
        enhanced_parts.append(base_scss)
        
        # Add enhanced theme-specific styles
        enhanced_parts.append("")
        enhanced_parts.append("// Theme-specific enhancements")
        enhanced_parts.append(self._generate_theme_enhancements(colors))
        
        return "\n".join(enhanced_parts)
    
    def _generate_theme_enhancements(self, colors: Dict[str, Any]) -> str:
        """Generate theme-specific style enhancements."""
        primary_color = colors.get("primary", "#1976d2")
        accent_color = colors.get("accent", "#ffc107")
        
        return f"""
// Primary color theming
.mat-mdc-raised-button.mat-primary {{
  background-color: {primary_color} !important;
}}

.mat-mdc-card {{
  border-left: 3px solid {primary_color};
}}

// Accent color theming
.mat-mdc-raised-button.mat-accent {{
  background-color: {accent_color} !important;
}}

// Hover effects
.mat-mdc-raised-button:hover {{
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transition: all 0.2s ease;
}}

// Focus indicators for accessibility
.mat-mdc-button:focus,
.mat-mdc-raised-button:focus {{
  outline: 2px solid {primary_color};
  outline-offset: 2px;
}}
"""
    
    async def _generate_global_theme(self, extracted_styles: Dict[str, Any]) -> str:
        """Generate global theme file."""
        colors = extracted_styles.get("colors", {})
        typography = extracted_styles.get("typography", {})
        
        primary_color = colors.get("primary", "#1976d2")
        accent_color = colors.get("accent", "#ffc107")
        warn_color = colors.get("warn", "#f44336")
        
        return f"""// Global theme file - theme.scss
// This file should be imported in your main styles.scss

@use '@angular/material' as mat;

// Define custom color palette
$custom-primary: mat.m2-define-palette((
  50: {self._lighten_color(primary_color, 0.9)},
  100: {self._lighten_color(primary_color, 0.7)},
  200: {self._lighten_color(primary_color, 0.5)},
  300: {self._lighten_color(primary_color, 0.3)},
  400: {self._lighten_color(primary_color, 0.1)},
  500: {primary_color},
  600: {self._darken_color(primary_color, 0.1)},
  700: {self._darken_color(primary_color, 0.2)},
  800: {self._darken_color(primary_color, 0.3)},
  900: {self._darken_color(primary_color, 0.4)},
  contrast: (
    50: rgba(black, 0.87),
    100: rgba(black, 0.87),
    200: rgba(black, 0.87),
    300: rgba(black, 0.87),
    400: white,
    500: white,
    600: white,
    700: white,
    800: white,
    900: white,
  )
));

$custom-accent: mat.m2-define-palette((
  500: {accent_color},
  contrast: (500: rgba(black, 0.87))
));

$custom-warn: mat.m2-define-palette((
  500: {warn_color},
  contrast: (500: white)
));

// Create theme
$custom-theme: mat.m2-define-light-theme((
  color: (
    primary: $custom-primary,
    accent: $custom-accent,
    warn: $custom-warn,
  ),
  typography: mat.m2-define-typography-config(),
  density: 0,
));

// Include theme styles for core and each component
@include mat.all-component-themes($custom-theme);

// Global custom styles
:root {{
  --primary-color: {primary_color};
  --accent-color: {accent_color};
  --warn-color: {warn_color};
  --background-color: {colors.get("background", "#fafafa")};
  --surface-color: {colors.get("surface", "#ffffff")};
  --text-color: #333333;
  --border-radius: {extracted_styles.get("borders", {}).get("radius", "4px")};
}}

// Typography
body {{
  font-family: {typography.get("font_family", "Roboto, sans-serif")};
  color: var(--text-color);
  line-height: 1.5;
}}

// Common utility classes
.text-primary {{ color: var(--primary-color); }}
.text-accent {{ color: var(--accent-color); }}
.text-warn {{ color: var(--warn-color); }}

.bg-primary {{ background-color: var(--primary-color); }}
.bg-accent {{ background-color: var(--accent-color); }}
.bg-surface {{ background-color: var(--surface-color); }}

// Responsive utilities
.container {{
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 16px;
}}

@media (max-width: 768px) {{
  .container {{
    padding: 0 8px;
  }}
}}
"""
    
    def _lighten_color(self, hex_color: str, factor: float) -> str:
        """Lighten a hex color by a factor (0-1)."""
        if not hex_color.startswith('#'):
            return hex_color
        
        try:
            # Remove # and convert to RGB
            hex_color = hex_color[1:]
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            
            # Lighten
            r = min(255, int(r + (255 - r) * factor))
            g = min(255, int(g + (255 - g) * factor))
            b = min(255, int(b + (255 - b) * factor))
            
            return f"#{r:02x}{g:02x}{b:02x}"
        except:
            return hex_color
    
    def _darken_color(self, hex_color: str, factor: float) -> str:
        """Darken a hex color by a factor (0-1)."""
        if not hex_color.startswith('#'):
            return hex_color
        
        try:
            # Remove # and convert to RGB
            hex_color = hex_color[1:]
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            
            # Darken
            r = max(0, int(r * (1 - factor)))
            g = max(0, int(g * (1 - factor)))
            b = max(0, int(b * (1 - factor)))
            
            return f"#{r:02x}{g:02x}{b:02x}"
        except:
            return hex_color