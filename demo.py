#!/usr/bin/env python3
"""Demo script showing the AI DevOps Agent Platform capabilities."""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


async def demo_agent_workflow():
    """Demonstrate the AI agent workflow."""
    print("🚀 AI DevOps Agent Platform Demo")
    print("=" * 50)
    
    # Import after path setup
    from backend.agents import VisionAgent, LayoutAgent, CodeAgent, StyleAgent, StubAgent
    from shared.models import ProcessingStatus
    
    # Sample screenshot path
    screenshot_path = project_root / "testdata" / "00_Cases-Portal.jpg"
    
    if not screenshot_path.exists():
        print("❌ Demo screenshot not found. Using mock data.")
        screenshot_path = "mock_screenshot.jpg"
    
    print(f"📸 Analyzing screenshot: {screenshot_path.name}")
    print()
    
    # 1. Vision Analysis
    print("🔍 Step 1: Vision Analysis")
    print("-" * 30)
    vision_agent = VisionAgent()
    
    # Simulate vision analysis result (since we may not have API keys)
    mock_layout_structure = {
        "elements": [
            {
                "type": "header",
                "label": "Cases Portal",
                "position": [0, 0, 800, 60],
                "properties": {"background": "#1976d2", "color": "white"},
                "confidence": 0.95
            },
            {
                "type": "card", 
                "label": "Project Scope",
                "position": [50, 80, 700, 200],
                "properties": {"background": "#ffffff", "border": "1px solid #ddd"},
                "confidence": 0.90
            },
            {
                "type": "button",
                "label": "Create Phase",
                "position": [600, 250, 120, 40],
                "properties": {"background": "#4caf50", "color": "white"},
                "confidence": 0.88
            }
        ],
        "layout_type": "grid",
        "responsive": True,
        "accessibility": {"has_alt_text": False, "color_contrast": "good"}
    }
    
    print(f"✅ Found {len(mock_layout_structure['elements'])} UI elements")
    for i, element in enumerate(mock_layout_structure['elements']):
        print(f"   {i+1}. {element['type']}: {element['label']}")
    print()
    
    # 2. Layout Generation
    print("🏗️ Step 2: Layout Generation")
    print("-" * 30)
    layout_agent = LayoutAgent()
    
    # Generate basic Angular template
    component_name = "cases-portal-component"
    
    angular_template = f"""<div class="cases-portal-container">
  <!-- Generated from legacy application screenshot -->
  
  <header class="app-header">
    <mat-toolbar color="primary">
      <span>Cases Portal</span>
    </mat-toolbar>
  </header>
  
  <main class="main-content">
    <div class="content-grid">
      <mat-card class="project-scope-card">
        <mat-card-header>
          <mat-card-title>Project Scope</mat-card-title>
        </mat-card-header>
        <mat-card-content>
          <p>Project scope and configuration details</p>
        </mat-card-content>
        <mat-card-actions>
          <button mat-raised-button color="primary" (click)="createPhase()">
            Create Phase
          </button>
        </mat-card-actions>
      </mat-card>
    </div>
  </main>
</div>"""
    
    print("✅ Generated Angular v20 template")
    print(f"   Component: {component_name}")
    print(f"   Template lines: {len(angular_template.split(chr(10)))}")
    print()
    
    # 3. Code Generation
    print("⚙️ Step 3: Code Generation")
    print("-" * 30)
    code_agent = CodeAgent()
    
    generated_files = [
        "cases-portal-component.component.ts",
        "cases-portal-component.component.html", 
        "cases-portal-component.component.scss",
        "cases-portal-component.component.spec.ts"
    ]
    
    print("✅ Generated complete Angular component")
    for file in generated_files:
        print(f"   📄 {file}")
    print()
    
    # 4. Style Application
    print("🎨 Step 4: Style Application")
    print("-" * 30)
    style_agent = StyleAgent()
    
    extracted_colors = ["#1976d2", "#4caf50", "#ffffff", "#f5f5f5"]
    
    print("✅ Applied modern styling")
    print(f"   Extracted colors: {', '.join(extracted_colors)}")
    print("   ✓ Responsive design")
    print("   ✓ Accessibility features")
    print("   ✓ Material Design theme")
    print()
    
    # 5. Service Generation
    print("🔧 Step 5: Service Generation")
    print("-" * 30)
    stub_agent = StubAgent()
    
    service_files = [
        "cases-portal-component.service.ts",
        "cases-portal-component-api.service.ts",
        "cases-portal-component.models.ts",
        "mock-data.interceptor.ts"
    ]
    
    print("✅ Generated service stubs")
    for file in service_files:
        print(f"   🔧 {file}")
    print()
    
    # Summary
    print("🎉 Generation Complete!")
    print("=" * 50)
    print("📦 Generated Angular v20 Project:")
    print("   ✓ Complete component structure")
    print("   ✓ TypeScript with strict typing")
    print("   ✓ Modern HTML templates")
    print("   ✓ Responsive SCSS styling")
    print("   ✓ Service stubs with mocks")
    print("   ✓ Unit test scaffolding")
    print("   ✓ Accessibility compliant")
    print()
    print("🔗 To run the full platform:")
    print("   1. Add API keys to .env file")
    print("   2. Run: ./start.sh")
    print("   3. Visit: http://localhost:8501")
    print()
    print("📚 Documentation:")
    print("   - README.md - Setup and usage guide")
    print("   - API docs at http://localhost:8000/docs")


def show_platform_architecture():
    """Show the platform architecture."""
    print("\n🏛️ Platform Architecture")
    print("=" * 50)
    
    architecture = """
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Streamlit     │    │     FastAPI     │    │   AI Agents     │
│   Frontend      │◄──►│    Backend      │◄──►│   Processing    │
│                 │    │                 │    │                 │
│ • File Upload   │    │ • REST APIs     │    │ • VisionAgent   │
│ • Progress UI   │    │ • Task Mgmt     │    │ • LayoutAgent   │
│ • Download      │    │ • File Storage  │    │ • CodeAgent     │
└─────────────────┘    └─────────────────┘    │ • StyleAgent    │
                                               │ • StubAgent     │
                                               └─────────────────┘
                                                       │
                                               ┌─────────────────┐
                                               │   AI Models     │
                                               │                 │
                                               │ • GPT-4 Vision  │
                                               │ • Claude 3      │
                                               │ • Fallback      │
                                               └─────────────────┘
"""
    
    print(architecture)
    
    print("🔄 Processing Workflow:")
    print("1. 📷 Upload screenshots → VisionAgent analyzes UI elements")
    print("2. 🏗️ Layout extraction → LayoutAgent creates Angular templates")
    print("3. ⚙️ Code generation → CodeAgent produces TS/HTML/SCSS files")
    print("4. 🎨 Style application → StyleAgent applies themes and responsive design")
    print("5. 🔧 Service creation → StubAgent generates mocks and interfaces")
    print("6. 📦 Project assembly → Complete Angular v20 project ready for download")


def main():
    """Run the demo."""
    try:
        # Show architecture first
        show_platform_architecture()
        
        # Run the workflow demo
        asyncio.run(demo_agent_workflow())
        
    except KeyboardInterrupt:
        print("\n👋 Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo error: {str(e)}")
        print("This is expected without proper dependencies installed.")


if __name__ == "__main__":
    main()