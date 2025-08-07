"""Layout Agent for converting UI structure to Angular v20 layout."""

import json
from typing import Any, Dict

import openai
from anthropic import Anthropic

from config.settings import settings
from shared.models import AgentResult, LayoutStructure, UIElement, UIElementType
from shared.utils import estimate_tokens, sanitize_component_name
from .base_agent import BaseAgent


class LayoutAgent(BaseAgent):
    """Agent that converts UI structure to Angular v20 component layout."""
    
    def __init__(self):
        super().__init__("LayoutAgent")
        self.openai_client = None
        self.anthropic_client = None
        
        if settings.openai_api_key:
            self.openai_client = openai.OpenAI(api_key=settings.openai_api_key)
        if settings.anthropic_api_key:
            self.anthropic_client = Anthropic(api_key=settings.anthropic_api_key)
    
    async def process(self, input_data: Dict[str, Any]) -> AgentResult:
        """Convert layout structure to Angular v20 template."""
        layout_data = input_data.get("layout_structure")
        component_name = input_data.get("component_name", "generated-component")
        
        if not layout_data:
            return AgentResult(
                agent_name=self.name,
                success=False,
                error="No layout_structure provided"
            )
        
        try:
            # Parse layout structure
            if isinstance(layout_data, dict):
                layout = LayoutStructure(**layout_data)
            else:
                layout = layout_data
            
            # Generate Angular template
            template = await self._generate_angular_template(layout, component_name)
            
            # Generate component structure
            component_structure = self._generate_component_structure(layout, component_name)
            
            tokens_used = estimate_tokens(template + str(component_structure))
            
            return AgentResult(
                agent_name=self.name,
                success=True,
                output={
                    "angular_template": template,
                    "component_structure": component_structure,
                    "component_name": sanitize_component_name(component_name)
                },
                tokens_used=tokens_used,
                carbon_emission=self._calculate_carbon_emission(
                    tokens_used,
                    settings.default_layout_model
                )
            )
            
        except Exception as e:
            return AgentResult(
                agent_name=self.name,
                success=False,
                error=f"Layout generation failed: {str(e)}"
            )
    
    async def _generate_angular_template(self, layout: LayoutStructure, component_name: str) -> str:
        """Generate Angular v20 template from layout structure."""
        if self.openai_client and "gpt" in settings.default_layout_model:
            return await self._generate_with_openai(layout, component_name)
        elif self.anthropic_client and "claude" in settings.default_layout_model:
            return await self._generate_with_anthropic(layout, component_name)
        else:
            return self._generate_basic_template(layout, component_name)
    
    async def _generate_with_openai(self, layout: LayoutStructure, component_name: str) -> str:
        """Generate template using OpenAI."""
        prompt = self._create_layout_prompt(layout, component_name)
        
        response = self.openai_client.chat.completions.create(
            model=settings.default_layout_model,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert Angular v20 developer. Generate clean, modern Angular templates following best practices."
                },
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000,
            temperature=0.1
        )
        
        return response.choices[0].message.content
    
    async def _generate_with_anthropic(self, layout: LayoutStructure, component_name: str) -> str:
        """Generate template using Anthropic Claude."""
        prompt = self._create_layout_prompt(layout, component_name)
        
        message = self.anthropic_client.messages.create(
            model=settings.default_layout_model,
            max_tokens=2000,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        return message.content[0].text
    
    def _create_layout_prompt(self, layout: LayoutStructure, component_name: str) -> str:
        """Create prompt for layout generation."""
        elements_description = self._describe_elements(layout.elements)
        
        return f"""
        Generate an Angular v20 component template based on the following UI layout analysis:
        
        Component Name: {component_name}
        Layout Type: {layout.layout_type}
        Responsive: {layout.responsive}
        
        UI Elements Detected:
        {elements_description}
        
        Requirements:
        1. Use Angular v20 syntax and best practices
        2. Use Angular Material components where appropriate
        3. Implement responsive design using Angular Flex Layout or CSS Grid/Flexbox
        4. Include proper accessibility attributes (aria-labels, roles, etc.)
        5. Use semantic HTML elements
        6. Include data binding placeholders for dynamic content
        7. Add appropriate CSS classes for styling
        8. Use Angular directives (*ngFor, *ngIf) where needed
        
        Generate only the HTML template content. Do not include TypeScript or CSS.
        Use modern Angular v20 features and syntax.
        
        Template:
        """
    
    def _describe_elements(self, elements: list[UIElement]) -> str:
        """Create a description of UI elements for the prompt."""
        descriptions = []
        for i, element in enumerate(elements):
            desc = f"  {i+1}. {element.type.value}: '{element.label}' at position {element.position}"
            if element.properties:
                props = ", ".join([f"{k}={v}" for k, v in element.properties.items()])
                desc += f" (properties: {props})"
            descriptions.append(desc)
        
        return "\n".join(descriptions)
    
    def _generate_basic_template(self, layout: LayoutStructure, component_name: str) -> str:
        """Generate basic template without AI."""
        template_parts = [
            "<div class=\"component-container\">",
            "  <!-- Generated Angular v20 Component Template -->"
        ]
        
        # Group elements by type for better organization
        headers = [e for e in layout.elements if e.type == UIElementType.HEADER]
        navigation = [e for e in layout.elements if e.type == UIElementType.NAVIGATION]
        cards = [e for e in layout.elements if e.type == UIElementType.CARD]
        buttons = [e for e in layout.elements if e.type == UIElementType.BUTTON]
        forms = [e for e in layout.elements if e.type == UIElementType.FORM]
        tables = [e for e in layout.elements if e.type == UIElementType.TABLE]
        
        # Generate header section
        if headers:
            template_parts.append("  <!-- Header Section -->")
            template_parts.append("  <header class=\"app-header\">")
            for header in headers:
                template_parts.append(f"    <h1>{header.label or 'Application Header'}</h1>")
            template_parts.append("  </header>")
        
        # Generate navigation
        if navigation:
            template_parts.append("  <!-- Navigation -->")
            template_parts.append("  <nav class=\"app-navigation\">")
            template_parts.append("    <mat-toolbar>")
            for nav in navigation:
                template_parts.append(f"      <span>{nav.label or 'Navigation'}</span>")
            template_parts.append("    </mat-toolbar>")
            template_parts.append("  </nav>")
        
        # Generate main content area
        template_parts.append("  <!-- Main Content -->")
        template_parts.append("  <main class=\"main-content\">")
        
        # Generate cards
        if cards:
            template_parts.append("    <div class=\"cards-container\">")
            for card in cards:
                template_parts.append("      <mat-card class=\"content-card\">")
                template_parts.append("        <mat-card-header>")
                template_parts.append(f"          <mat-card-title>{card.label or 'Card Title'}</mat-card-title>")
                template_parts.append("        </mat-card-header>")
                template_parts.append("        <mat-card-content>")
                template_parts.append("          <p>Card content goes here</p>")
                template_parts.append("        </mat-card-content>")
                template_parts.append("      </mat-card>")
            template_parts.append("    </div>")
        
        # Generate forms
        if forms:
            for form in forms:
                template_parts.append("    <form class=\"app-form\">")
                template_parts.append(f"      <h3>{form.label or 'Form'}</h3>")
                template_parts.append("      <mat-form-field>")
                template_parts.append("        <mat-label>Input Field</mat-label>")
                template_parts.append("        <input matInput>")
                template_parts.append("      </mat-form-field>")
                template_parts.append("    </form>")
        
        # Generate tables
        if tables:
            for table in tables:
                template_parts.append("    <mat-table class=\"data-table\">")
                template_parts.append(f"      <mat-header-row>{table.label or 'Data Table'}</mat-header-row>")
                template_parts.append("      <!-- Table columns will be added by CodeAgent -->")
                template_parts.append("    </mat-table>")
        
        # Generate action buttons
        if buttons:
            template_parts.append("    <div class=\"actions-container\">")
            for button in buttons:
                template_parts.append(f"      <button mat-raised-button color=\"primary\">{button.label or 'Action'}</button>")
            template_parts.append("    </div>")
        
        template_parts.append("  </main>")
        template_parts.append("</div>")
        
        return "\n".join(template_parts)
    
    def _generate_component_structure(self, layout: LayoutStructure, component_name: str) -> Dict[str, Any]:
        """Generate component structure metadata."""
        return {
            "name": sanitize_component_name(component_name),
            "selector": f"app-{sanitize_component_name(component_name)}",
            "elements_count": len(layout.elements),
            "layout_type": layout.layout_type,
            "responsive": layout.responsive,
            "dependencies": self._get_required_dependencies(layout.elements),
            "imports": self._get_required_imports(layout.elements)
        }
    
    def _get_required_dependencies(self, elements: list[UIElement]) -> list[str]:
        """Determine required Angular Material components."""
        dependencies = set()
        
        for element in elements:
            if element.type == UIElementType.BUTTON:
                dependencies.add("MatButtonModule")
            elif element.type == UIElementType.CARD:
                dependencies.add("MatCardModule")
            elif element.type == UIElementType.INPUT:
                dependencies.add("MatInputModule")
                dependencies.add("MatFormFieldModule")
            elif element.type == UIElementType.TABLE:
                dependencies.add("MatTableModule")
            elif element.type == UIElementType.NAVIGATION:
                dependencies.add("MatToolbarModule")
        
        return list(dependencies)
    
    def _get_required_imports(self, elements: list[UIElement]) -> list[str]:
        """Determine required imports for the component."""
        imports = ["Component", "OnInit"]
        
        # Add common imports based on elements
        if any(e.type in [UIElementType.INPUT, UIElementType.FORM] for e in elements):
            imports.extend(["FormBuilder", "FormGroup", "Validators"])
        
        if any(e.type == UIElementType.TABLE for e in elements):
            imports.append("MatTableDataSource")
        
        return imports