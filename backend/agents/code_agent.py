"""Code Agent for generating complete Angular v20 components."""

import json
from typing import Any, Dict, List

import openai
from anthropic import Anthropic

from config.settings import settings
from shared.models import AgentResult, ComponentFile, GeneratedComponent
from shared.utils import estimate_tokens, format_angular_code, sanitize_component_name
from .base_agent import BaseAgent


class CodeAgent(BaseAgent):
    """Agent that generates complete Angular v20 components with TypeScript, HTML, and SCSS."""
    
    def __init__(self):
        super().__init__("CodeAgent")
        self.openai_client = None
        self.anthropic_client = None
        
        if settings.openai_api_key:
            self.openai_client = openai.OpenAI(api_key=settings.openai_api_key)
        if settings.anthropic_api_key:
            self.anthropic_client = Anthropic(api_key=settings.anthropic_api_key)
    
    async def process(self, input_data: Dict[str, Any]) -> AgentResult:
        """Generate complete Angular component files."""
        template = input_data.get("angular_template", "")
        component_structure = input_data.get("component_structure", {})
        styles = input_data.get("styles", "")
        
        component_name = component_structure.get("name", "generated-component")
        
        try:
            # Generate all component files
            component = await self._generate_component(
                template, component_structure, styles, component_name
            )
            
            total_tokens = sum(estimate_tokens(file.content) for file in component.files)
            
            return AgentResult(
                agent_name=self.name,
                success=True,
                output={
                    "component": component.dict(),
                    "files_generated": len(component.files)
                },
                tokens_used=total_tokens,
                carbon_emission=self._calculate_carbon_emission(
                    total_tokens,
                    settings.default_code_model
                )
            )
            
        except Exception as e:
            return AgentResult(
                agent_name=self.name,
                success=False,
                error=f"Code generation failed: {str(e)}"
            )
    
    async def _generate_component(
        self, 
        template: str, 
        structure: Dict[str, Any], 
        styles: str,
        component_name: str
    ) -> GeneratedComponent:
        """Generate complete Angular component."""
        
        files = []
        clean_name = sanitize_component_name(component_name)
        
        # Generate TypeScript file
        typescript_content = await self._generate_typescript(template, structure, clean_name)
        files.append(ComponentFile(
            filename=f"{clean_name}.component.ts",
            content=typescript_content,
            file_type="ts"
        ))
        
        # Generate HTML template
        html_content = await self._generate_html(template, structure, clean_name)
        files.append(ComponentFile(
            filename=f"{clean_name}.component.html",
            content=html_content,
            file_type="html"
        ))
        
        # Generate SCSS styles
        scss_content = await self._generate_scss(styles, structure, clean_name)
        files.append(ComponentFile(
            filename=f"{clean_name}.component.scss",
            content=scss_content,
            file_type="scss"
        ))
        
        # Generate test file
        spec_content = await self._generate_spec(structure, clean_name)
        files.append(ComponentFile(
            filename=f"{clean_name}.component.spec.ts",
            content=spec_content,
            file_type="spec.ts"
        ))
        
        return GeneratedComponent(
            name=clean_name,
            files=files,
            dependencies=structure.get("dependencies", []),
            imports=structure.get("imports", [])
        )
    
    async def _generate_typescript(self, template: str, structure: Dict[str, Any], name: str) -> str:
        """Generate TypeScript component file."""
        if self.openai_client and "gpt" in settings.default_code_model:
            return await self._generate_ts_with_ai(template, structure, name)
        else:
            return self._generate_basic_typescript(template, structure, name)
    
    async def _generate_ts_with_ai(self, template: str, structure: Dict[str, Any], name: str) -> str:
        """Generate TypeScript using AI."""
        prompt = f"""
        Generate an Angular v20 TypeScript component class for the following template and structure:
        
        Component Name: {name}
        Selector: app-{name}
        Dependencies: {structure.get('dependencies', [])}
        Imports: {structure.get('imports', [])}
        
        Template Structure:
        {template}
        
        Requirements:
        1. Use Angular v20 syntax and best practices
        2. Implement OnInit lifecycle hook
        3. Include proper TypeScript typing
        4. Add JSDoc comments for methods
        5. Implement data binding properties for template
        6. Include proper imports for Angular and Material components
        7. Use signals if appropriate (Angular 17+)
        8. Follow Angular style guide conventions
        9. Include form handling if forms are present
        10. Add proper error handling
        
        Generate only the TypeScript class content.
        """
        
        response = self.openai_client.chat.completions.create(
            model=settings.default_code_model,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert Angular v20 developer. Generate clean, type-safe TypeScript code following Angular best practices."
                },
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000,
            temperature=0.1
        )
        
        return format_angular_code(response.choices[0].message.content, "typescript")
    
    def _generate_basic_typescript(self, template: str, structure: Dict[str, Any], name: str) -> str:
        """Generate basic TypeScript component."""
        class_name = "".join(word.capitalize() for word in name.split("-"))
        imports = structure.get("imports", ["Component", "OnInit"])
        dependencies = structure.get("dependencies", [])
        
        # Build imports
        angular_imports = [imp for imp in imports if imp in ["Component", "OnInit", "Input", "Output", "EventEmitter"]]
        form_imports = [imp for imp in imports if "Form" in imp or imp in ["Validators"]]
        
        import_lines = [
            f"import {{ {', '.join(angular_imports)} }} from '@angular/core';"
        ]
        
        if form_imports:
            import_lines.append(f"import {{ {', '.join(form_imports)} }} from '@angular/forms';")
        
        if "MatTableDataSource" in imports:
            import_lines.append("import { MatTableDataSource } from '@angular/material/table';")
        
        # Build component decorator
        component_decorator = f"""@Component({{
  selector: 'app-{name}',
  templateUrl: './{name}.component.html',
  styleUrls: ['./{name}.component.scss']
}})"""
        
        # Build class
        class_content = [
            f"export class {class_name}Component implements OnInit {{",
            "",
            "  // Component properties",
            "  public data: any[] = [];",
            "  public loading = false;",
            ""
        ]
        
        # Add form properties if needed
        if any("form" in imp.lower() for imp in imports):
            class_content.extend([
                "  public form!: FormGroup;",
                ""
            ])
        
        # Add table properties if needed
        if "MatTableDataSource" in imports:
            class_content.extend([
                "  public dataSource = new MatTableDataSource(this.data);",
                "  public displayedColumns: string[] = ['column1', 'column2', 'actions'];",
                ""
            ])
        
        class_content.extend([
            "  constructor() {",
            "    // Initialize component",
            "  }",
            "",
            "  ngOnInit(): void {",
            "    this.initializeComponent();",
            "  }",
            "",
            "  /**",
            "   * Initialize component data and setup",
            "   */",
            "  private initializeComponent(): void {",
            "    this.loading = true;",
            "    // Component initialization logic",
            "    this.loading = false;",
            "  }",
            "",
            "  /**",
            "   * Handle button click events",
            "   */",
            "  public onButtonClick(action: string): void {",
            "    console.log('Button clicked:', action);",
            "  }",
            "}"
        ])
        
        # Combine everything
        full_content = "\n".join(import_lines) + "\n\n" + component_decorator + "\n" + "\n".join(class_content)
        
        return format_angular_code(full_content, "typescript")
    
    async def _generate_html(self, template: str, structure: Dict[str, Any], name: str) -> str:
        """Generate HTML template."""
        if template and template.strip():
            # Clean up the template if it came from AI
            return self._clean_html_template(template)
        else:
            return self._generate_basic_html(structure, name)
    
    def _clean_html_template(self, template: str) -> str:
        """Clean and format HTML template."""
        # Remove any markdown code blocks
        if "```html" in template:
            start = template.find("```html") + 7
            end = template.find("```", start)
            template = template[start:end]
        elif "```" in template:
            start = template.find("```") + 3
            end = template.find("```", start)
            template = template[start:end]
        
        return template.strip()
    
    def _generate_basic_html(self, structure: Dict[str, Any], name: str) -> str:
        """Generate basic HTML template."""
        return f"""<div class="{name}-container">
  <div class="header">
    <h2>Generated Component</h2>
  </div>
  
  <div class="content">
    <mat-card>
      <mat-card-header>
        <mat-card-title>Component Content</mat-card-title>
      </mat-card-header>
      <mat-card-content>
        <p>This component was generated from a legacy application screenshot.</p>
        
        <div class="actions">
          <button mat-raised-button color="primary" (click)="onButtonClick('primary')">
            Primary Action
          </button>
          <button mat-stroked-button (click)="onButtonClick('secondary')">
            Secondary Action
          </button>
        </div>
      </mat-card-content>
    </mat-card>
  </div>
  
  <div class="loading-spinner" *ngIf="loading">
    <mat-spinner></mat-spinner>
  </div>
</div>"""
    
    async def _generate_scss(self, styles: str, structure: Dict[str, Any], name: str) -> str:
        """Generate SCSS styles."""
        if styles and styles.strip():
            base_styles = styles
        else:
            base_styles = self._generate_basic_scss(name)
        
        # Add responsive design
        responsive_styles = """
// Responsive design
@media (max-width: 768px) {
  .content {
    padding: 8px;
  }
  
  .actions {
    flex-direction: column;
    
    button {
      margin: 4px 0;
      width: 100%;
    }
  }
}

@media (max-width: 480px) {
  .header h2 {
    font-size: 1.2rem;
  }
}
"""
        
        return base_styles + responsive_styles
    
    def _generate_basic_scss(self, name: str) -> str:
        """Generate basic SCSS styles."""
        return f""".{name}-container {{
  padding: 16px;
  max-width: 1200px;
  margin: 0 auto;
}}

.header {{
  margin-bottom: 24px;
  
  h2 {{
    color: var(--primary-color, #1976d2);
    font-weight: 500;
  }}
}}

.content {{
  margin-bottom: 16px;
}}

.actions {{
  display: flex;
  gap: 12px;
  margin-top: 16px;
  
  button {{
    min-width: 120px;
  }}
}}

.loading-spinner {{
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 24px;
}}

// Component-specific styles
mat-card {{
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border-radius: 8px;
}}

mat-card-header {{
  margin-bottom: 16px;
}}

mat-card-title {{
  font-size: 1.25rem;
  font-weight: 500;
}}
"""
    
    async def _generate_spec(self, structure: Dict[str, Any], name: str) -> str:
        """Generate test specification file."""
        class_name = "".join(word.capitalize() for word in name.split("-"))
        
        return f"""import {{ ComponentFixture, TestBed }} from '@angular/core/testing';
import {{ {class_name}Component }} from './{name}.component';

describe('{class_name}Component', () => {{
  let component: {class_name}Component;
  let fixture: ComponentFixture<{class_name}Component>;

  beforeEach(async () => {{
    await TestBed.configureTestingModule({{
      declarations: [ {class_name}Component ]
    }})
    .compileComponents();

    fixture = TestBed.createComponent({class_name}Component);
    component = fixture.componentInstance;
    fixture.detectChanges();
  }});

  it('should create', () => {{
    expect(component).toBeTruthy();
  }});

  it('should initialize component', () => {{
    component.ngOnInit();
    expect(component.loading).toBeFalsy();
  }});

  it('should handle button clicks', () => {{
    spyOn(console, 'log');
    component.onButtonClick('test');
    expect(console.log).toHaveBeenCalledWith('Button clicked:', 'test');
  }});
}});
"""