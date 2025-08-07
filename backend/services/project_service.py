"""Project service for managing project generation workflow."""

import os
import shutil
import zipfile
from pathlib import Path
from typing import Any, Dict, List, Optional

import aiofiles
from fastapi import UploadFile
from loguru import logger

from config.settings import settings
from shared.models import ProjectGeneration, ProcessingStatus, LayoutStructure
from shared.utils import save_uploaded_file, create_project_structure, sanitize_component_name
from backend.agents import VisionAgent, LayoutAgent, CodeAgent, StyleAgent, StubAgent
from backend.services.task_service import TaskService


class ProjectService:
    """Service for managing project generation workflow."""
    
    def __init__(self):
        self.task_service = TaskService()
        
        # Initialize agents
        self.vision_agent = VisionAgent()
        self.layout_agent = LayoutAgent()
        self.code_agent = CodeAgent()
        self.style_agent = StyleAgent()
        self.stub_agent = StubAgent()
    
    async def save_uploaded_file(self, file: UploadFile, task_id: str) -> str:
        """Save uploaded file and return path."""
        upload_dir = Path(settings.upload_folder) / task_id
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        file_content = await file.read()
        file_path = await save_uploaded_file(file_content, file.filename, str(upload_dir))
        
        logger.info(f"Saved uploaded file: {file_path}")
        return file_path
    
    async def process_project_generation(
        self,
        request: ProjectGeneration,
        screenshot_paths: List[str],
        style_paths: List[str]
    ) -> None:
        """Process complete project generation workflow."""
        task_id = request.task_id
        
        try:
            await self.task_service.update_task(
                task_id,
                status=ProcessingStatus.PROCESSING,
                progress=0.0,
                message="Starting project generation"
            )
            
            # Step 1: Analyze screenshots with VisionAgent
            await self.task_service.update_task(task_id, progress=10.0, message="Analyzing screenshots")
            layouts = []
            
            for i, screenshot_path in enumerate(screenshot_paths):
                result = await self.vision_agent.execute({
                    "image_path": screenshot_path
                }, task_id)
                
                if not result.success:
                    raise Exception(f"Vision analysis failed for {screenshot_path}: {result.error}")
                
                layouts.append(result.output["layout_structure"])
                
                # Update progress
                progress = 10.0 + (i + 1) / len(screenshot_paths) * 20.0
                await self.task_service.update_task(task_id, progress=progress)
            
            # Step 2: Generate layouts with LayoutAgent
            await self.task_service.update_task(task_id, progress=30.0, message="Generating Angular layouts")
            generated_layouts = []
            
            for i, layout in enumerate(layouts):
                component_name = f"{sanitize_component_name(request.project_name)}-component-{i+1}"
                
                result = await self.layout_agent.execute({
                    "layout_structure": layout,
                    "component_name": component_name
                }, task_id)
                
                if not result.success:
                    raise Exception(f"Layout generation failed: {result.error}")
                
                generated_layouts.append(result.output)
                
                # Update progress
                progress = 30.0 + (i + 1) / len(layouts) * 20.0
                await self.task_service.update_task(task_id, progress=progress)
            
            # Step 3: Apply styles with StyleAgent
            await self.task_service.update_task(task_id, progress=50.0, message="Applying styles and themes")
            
            # Read reference styles
            reference_styles_content = ""
            if style_paths:
                for style_path in style_paths:
                    async with aiofiles.open(style_path, 'r') as f:
                        content = await f.read()
                        reference_styles_content += content + "\n"
            
            style_result = await self.style_agent.execute({
                "reference_styles": reference_styles_content,
                "reference_images": screenshot_paths,
                "component_scss": ""  # Will be enhanced per component
            }, task_id)
            
            if not style_result.success:
                raise Exception(f"Style generation failed: {style_result.error}")
            
            # Step 4: Generate code with CodeAgent
            await self.task_service.update_task(task_id, progress=60.0, message="Generating Angular components")
            generated_components = []
            
            for i, layout_output in enumerate(generated_layouts):
                result = await self.code_agent.execute({
                    "angular_template": layout_output["angular_template"],
                    "component_structure": layout_output["component_structure"],
                    "styles": style_result.output["enhanced_scss"]
                }, task_id)
                
                if not result.success:
                    raise Exception(f"Code generation failed for component {i+1}: {result.error}")
                
                generated_components.append(result.output["component"])
                
                # Update progress
                progress = 60.0 + (i + 1) / len(generated_layouts) * 20.0
                await self.task_service.update_task(task_id, progress=progress)
            
            # Step 5: Generate service stubs with StubAgent
            await self.task_service.update_task(task_id, progress=80.0, message="Generating service stubs")
            
            stub_result = await self.stub_agent.execute({
                "component_name": sanitize_component_name(request.project_name),
                "component_structure": generated_layouts[0]["component_structure"] if generated_layouts else {}
            }, task_id)
            
            if not stub_result.success:
                logger.warning(f"Stub generation failed: {stub_result.error}")
                stub_result.output = {"service_files": [], "mock_data": {}}
            
            # Step 6: Create project structure and files
            await self.task_service.update_task(task_id, progress=90.0, message="Creating project files")
            
            project_path = await self._create_angular_project(
                request.project_name,
                generated_components,
                style_result.output,
                stub_result.output,
                task_id
            )
            
            # Step 7: Complete
            await self.task_service.update_task(
                task_id,
                status=ProcessingStatus.COMPLETED,
                progress=100.0,
                message="Project generation completed successfully",
                result={
                    "project_path": project_path,
                    "components_count": len(generated_components),
                    "has_styles": bool(style_result.success),
                    "has_stubs": bool(stub_result.success),
                    "carbon_emissions": self._calculate_total_emissions([
                        self.vision_agent, self.layout_agent, self.code_agent, 
                        self.style_agent, self.stub_agent
                    ])
                }
            )
            
            logger.info(f"Project generation completed for task {task_id}")
            
        except Exception as e:
            logger.error(f"Project generation failed for task {task_id}: {str(e)}")
            await self.task_service.update_task(
                task_id,
                status=ProcessingStatus.FAILED,
                error=str(e),
                message="Project generation failed"
            )
    
    async def _create_angular_project(
        self,
        project_name: str,
        components: List[Dict],
        styles: Dict[str, Any],
        stubs: Dict[str, Any],
        task_id: str
    ) -> str:
        """Create complete Angular project structure."""
        
        project_dir = Path(settings.output_folder) / task_id / sanitize_component_name(project_name)
        project_paths = create_project_structure(project_name, str(project_dir.parent))
        
        # Create package.json
        await self._create_package_json(project_paths["project_root"], project_name)
        
        # Create angular.json
        await self._create_angular_json(project_paths["project_root"], project_name)
        
        # Create tsconfig files
        await self._create_tsconfig_files(project_paths["project_root"])
        
        # Create app module
        await self._create_app_module(project_paths["app"], components)
        
        # Create app component
        await self._create_app_component(project_paths["app"], project_name)
        
        # Create individual components
        for component in components:
            await self._create_component_files(project_paths["components"], component)
        
        # Create styles
        await self._create_global_styles(project_paths["src"], styles)
        
        # Create services
        if stubs.get("service_files"):
            await self._create_service_files(project_paths["services"], stubs["service_files"])
        
        # Create environment files
        await self._create_environment_files(project_paths["src"])
        
        return project_paths["project_root"]
    
    async def _create_package_json(self, project_root: str, project_name: str) -> None:
        """Create package.json file."""
        package_json = {
            "name": sanitize_component_name(project_name),
            "version": "0.0.0",
            "scripts": {
                "ng": "ng",
                "start": "ng serve",
                "build": "ng build",
                "watch": "ng build --watch --configuration development",
                "test": "ng test",
                "serve:ssr": "node dist/server/main.js"
            },
            "dependencies": {
                "@angular/animations": "^17.0.0",
                "@angular/cdk": "^17.0.0",
                "@angular/common": "^17.0.0",
                "@angular/compiler": "^17.0.0",
                "@angular/core": "^17.0.0",
                "@angular/forms": "^17.0.0",
                "@angular/material": "^17.0.0",
                "@angular/platform-browser": "^17.0.0",
                "@angular/platform-browser-dynamic": "^17.0.0",
                "@angular/router": "^17.0.0",
                "rxjs": "~7.8.0",
                "tslib": "^2.3.0",
                "zone.js": "~0.14.0"
            },
            "devDependencies": {
                "@angular-devkit/build-angular": "^17.0.0",
                "@angular/cli": "^17.0.0",
                "@angular/compiler-cli": "^17.0.0",
                "@types/jasmine": "~5.1.0",
                "jasmine-core": "~5.1.0",
                "karma": "~6.4.0",
                "karma-chrome-headless": "~3.1.0",
                "karma-coverage": "~2.2.0",
                "karma-jasmine": "~5.1.0",
                "karma-jasmine-html-reporter": "~2.1.0",
                "typescript": "~5.2.0"
            }
        }
        
        async with aiofiles.open(Path(project_root) / "package.json", 'w') as f:
            import json
            await f.write(json.dumps(package_json, indent=2))
    
    async def _create_angular_json(self, project_root: str, project_name: str) -> None:
        """Create angular.json configuration."""
        clean_name = sanitize_component_name(project_name)
        
        angular_json = {
            "$schema": "./node_modules/@angular/cli/lib/config/schema.json",
            "version": 1,
            "newProjectRoot": "projects",
            "projects": {
                clean_name: {
                    "projectType": "application",
                    "schematics": {
                        "@schematics/angular:component": {
                            "style": "scss"
                        }
                    },
                    "root": "",
                    "sourceRoot": "src",
                    "prefix": "app",
                    "architect": {
                        "build": {
                            "builder": "@angular-devkit/build-angular:browser",
                            "options": {
                                "outputPath": "dist",
                                "index": "src/index.html",
                                "main": "src/main.ts",
                                "polyfills": ["zone.js"],
                                "tsConfig": "tsconfig.app.json",
                                "inlineStyleLanguage": "scss",
                                "assets": ["src/favicon.ico", "src/assets"],
                                "styles": ["src/styles.scss"],
                                "scripts": []
                            }
                        },
                        "serve": {
                            "builder": "@angular-devkit/build-angular:dev-server",
                            "configurations": {
                                "production": {"browserTarget": f"{clean_name}:build:production"},
                                "development": {"browserTarget": f"{clean_name}:build:development"}
                            },
                            "defaultConfiguration": "development"
                        }
                    }
                }
            }
        }
        
        async with aiofiles.open(Path(project_root) / "angular.json", 'w') as f:
            import json
            await f.write(json.dumps(angular_json, indent=2))
    
    async def _create_tsconfig_files(self, project_root: str) -> None:
        """Create TypeScript configuration files."""
        # Main tsconfig.json
        tsconfig = {
            "compileOnSave": False,
            "compilerOptions": {
                "baseUrl": "./",
                "outDir": "./dist/out-tsc",
                "forceConsistentCasingInFileNames": True,
                "strict": True,
                "noImplicitOverride": True,
                "noPropertyAccessFromIndexSignature": True,
                "noImplicitReturns": True,
                "noFallthroughCasesInSwitch": True,
                "sourceMap": True,
                "declaration": False,
                "downlevelIteration": True,
                "experimentalDecorators": True,
                "moduleResolution": "node",
                "importHelpers": True,
                "target": "ES2022",
                "module": "ES2022",
                "useDefineForClassFields": False,
                "lib": ["ES2022", "dom"]
            }
        }
        
        async with aiofiles.open(Path(project_root) / "tsconfig.json", 'w') as f:
            import json
            await f.write(json.dumps(tsconfig, indent=2))
    
    async def _create_app_module(self, app_path: str, components: List[Dict]) -> None:
        """Create app.module.ts file."""
        component_imports = []
        component_declarations = []
        
        for component in components:
            name = component["name"]
            class_name = "".join(word.capitalize() for word in name.split("-"))
            component_imports.append(f"import {{ {class_name}Component }} from './components/{name}/{name}.component';")
            component_declarations.append(f"    {class_name}Component")
        
        module_content = f"""import {{ NgModule }} from '@angular/core';
import {{ BrowserModule }} from '@angular/platform-browser';
import {{ BrowserAnimationsModule }} from '@angular/platform-browser/animations';
import {{ HttpClientModule }} from '@angular/common/http';
import {{ ReactiveFormsModule }} from '@angular/forms';

// Angular Material
import {{ MatToolbarModule }} from '@angular/material/toolbar';
import {{ MatButtonModule }} from '@angular/material/button';
import {{ MatCardModule }} from '@angular/material/card';
import {{ MatInputModule }} from '@angular/material/input';
import {{ MatFormFieldModule }} from '@angular/material/form-field';
import {{ MatProgressSpinnerModule }} from '@angular/material/progress-spinner';
import {{ MatTableModule }} from '@angular/material/table';
import {{ MatIconModule }} from '@angular/material/icon';

import {{ AppComponent }} from './app.component';
{chr(10).join(component_imports)}

@NgModule({{
  declarations: [
    AppComponent,
{chr(10).join(component_declarations)}
  ],
  imports: [
    BrowserModule,
    BrowserAnimationsModule,
    HttpClientModule,
    ReactiveFormsModule,
    MatToolbarModule,
    MatButtonModule,
    MatCardModule,
    MatInputModule,
    MatFormFieldModule,
    MatProgressSpinnerModule,
    MatTableModule,
    MatIconModule
  ],
  providers: [],
  bootstrap: [AppComponent]
}})
export class AppModule {{ }}
"""
        
        async with aiofiles.open(Path(app_path) / "app.module.ts", 'w') as f:
            await f.write(module_content)
    
    async def _create_app_component(self, app_path: str, project_name: str) -> None:
        """Create main app component."""
        component_content = f"""import {{ Component }} from '@angular/core';

@Component({{
  selector: 'app-root',
  template: \`
    <mat-toolbar color="primary">
      <span>{project_name}</span>
    </mat-toolbar>
    
    <div class="main-content">
      <h1>Welcome to {project_name}</h1>
      <p>This application was generated from legacy screenshots using AI.</p>
      
      <!-- Generated components will be displayed here -->
      <div class="components-container">
        <!-- Add your generated components here -->
      </div>
    </div>
  \`,
  styles: [\`
    .main-content {{
      padding: 20px;
      max-width: 1200px;
      margin: 0 auto;
    }}
    
    .components-container {{
      margin-top: 20px;
    }}
  \`]
}})
export class AppComponent {{
  title = '{project_name}';
}}
"""
        
        async with aiofiles.open(Path(app_path) / "app.component.ts", 'w') as f:
            await f.write(component_content)
    
    async def _create_component_files(self, components_path: str, component: Dict) -> None:
        """Create individual component files."""
        component_name = component["name"]
        component_dir = Path(components_path) / component_name
        component_dir.mkdir(parents=True, exist_ok=True)
        
        for file_data in component["files"]:
            file_path = component_dir / file_data["filename"]
            async with aiofiles.open(file_path, 'w') as f:
                await f.write(file_data["content"])
    
    async def _create_global_styles(self, src_path: str, styles: Dict[str, Any]) -> None:
        """Create global styles.scss file."""
        global_theme = styles.get("global_theme", "")
        
        styles_content = f"""/* Global styles for the application */
@import '@angular/material/prebuilt-themes/indigo-pink.css';

{global_theme}

/* Application-wide styles */
html, body {{
  height: 100%;
  margin: 0;
  font-family: Roboto, "Helvetica Neue", sans-serif;
}}

.main-content {{
  min-height: calc(100vh - 64px);
}}
"""
        
        async with aiofiles.open(Path(src_path) / "styles.scss", 'w') as f:
            await f.write(styles_content)
    
    async def _create_service_files(self, services_path: str, service_files: List[Dict]) -> None:
        """Create service files."""
        for service_file in service_files:
            file_path = Path(services_path) / service_file["filename"]
            async with aiofiles.open(file_path, 'w') as f:
                await f.write(service_file["content"])
    
    async def _create_environment_files(self, src_path: str) -> None:
        """Create environment configuration files."""
        env_dir = Path(src_path) / "environments"
        env_dir.mkdir(exist_ok=True)
        
        # Development environment
        dev_env = """export const environment = {
  production: false,
  apiUrl: 'http://localhost:3000/api'
};
"""
        
        async with aiofiles.open(env_dir / "environment.ts", 'w') as f:
            await f.write(dev_env)
        
        # Production environment
        prod_env = """export const environment = {
  production: true,
  apiUrl: '/api'
};
"""
        
        async with aiofiles.open(env_dir / "environment.prod.ts", 'w') as f:
            await f.write(prod_env)
    
    async def analyze_single_screenshot(self, image_path: str) -> Dict[str, Any]:
        """Analyze a single screenshot for testing."""
        result = await self.vision_agent.execute({"image_path": image_path})
        return {
            "success": result.success,
            "layout_structure": result.output.get("layout_structure") if result.success else None,
            "error": result.error,
            "execution_time": result.execution_time
        }
    
    async def create_project_zip(self, task_id: str) -> str:
        """Create ZIP file of generated project."""
        task = await self.task_service.get_task(task_id)
        if not task or not task.result:
            raise Exception("Task not found or not completed")
        
        project_path = task.result["project_path"]
        zip_path = f"{project_path}.zip"
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(project_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, project_path)
                    zipf.write(file_path, arcname)
        
        return zip_path
    
    async def get_project_preview(self, task_id: str) -> Dict[str, Any]:
        """Get project preview/structure."""
        task = await self.task_service.get_task(task_id)
        if not task:
            raise Exception("Task not found")
        
        if task.result and "project_path" in task.result:
            project_path = task.result["project_path"]
            structure = self._get_directory_structure(project_path)
            return {
                "structure": structure,
                "stats": task.result
            }
        
        return {"structure": {}, "stats": {}}
    
    def _get_directory_structure(self, path: str, max_depth: int = 3, current_depth: int = 0) -> Dict[str, Any]:
        """Get directory structure for preview."""
        if current_depth >= max_depth:
            return {}
        
        structure = {}
        try:
            for item in sorted(os.listdir(path)):
                if item.startswith('.'):
                    continue
                
                item_path = os.path.join(path, item)
                if os.path.isdir(item_path):
                    structure[item] = self._get_directory_structure(
                        item_path, max_depth, current_depth + 1
                    )
                else:
                    structure[item] = {"type": "file", "size": os.path.getsize(item_path)}
        except PermissionError:
            pass
        
        return structure
    
    def _calculate_total_emissions(self, agents: List) -> Dict[str, float]:
        """Calculate total carbon emissions from all agents."""
        total_emissions = 0.0
        agent_emissions = {}
        
        for agent in agents:
            if hasattr(agent, '_last_emission') and agent._last_emission:
                emissions = agent._last_emission.estimated_co2_grams
                agent_emissions[agent.name] = emissions
                total_emissions += emissions
        
        return {
            "total_grams": total_emissions,
            "by_agent": agent_emissions
        }