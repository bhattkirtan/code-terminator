"""
Enhanced Code Agent FastAPI for Angular 20 Project Generation
Takes project name and context path, uses local Gemini CLI to generate, build, and run Angular projects
"""

import json
import os
import asyncio
import shutil
import time
from typing import List, Optional, Dict, Any
from pathlib import Path

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import aiofiles
from dotenv import load_dotenv
import subprocess

# Load environment variables
load_dotenv()

app = FastAPI(
    title="SnapIt Code Agent - Enhanced",
    description="Enhanced AI-powered code agent that generates, builds, and runs Angular 20 projects using local Gemini CLI",
    version="2.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
GEMINI_CLI_PATH = os.getenv(
    "GEMINI_CLI_PATH", "C:/Users/subha/AppData/Roaming/npm/gemini.cmd"
)
PROJECTS_ROOT = Path("./generated_projects")
PROJECTS_ROOT.mkdir(exist_ok=True)


# Pydantic models
class ProjectRequest(BaseModel):
    project_name: str
    context_file_path: Optional[str] = None
    auto_build: bool = True
    auto_run: bool = False
    fix_issues: bool = True


class ProjectResponse(BaseModel):
    project_id: str
    status: str
    message: str
    project_path: Optional[str] = None
    build_output: Optional[str] = None
    run_url: Optional[str] = None
    errors: List[str] = []
    fixes_applied: List[str] = []


class ProjectStatus(BaseModel):
    project_id: str
    status: str
    current_step: str
    progress: int
    logs: List[str] = []
    errors: List[str] = []


# Global status tracking
project_status_cache = {}


async def run_command(
    cmd: List[str], cwd: Path = None, timeout: int = 300
) -> Dict[str, Any]:
    """Run a command and return result with output and error handling"""
    try:
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=cwd,
        )

        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout)

        return {
            "success": process.returncode == 0,
            "returncode": process.returncode,
            "stdout": stdout.decode("utf-8", errors="ignore"),
            "stderr": stderr.decode("utf-8", errors="ignore"),
            "command": " ".join(cmd),
        }
    except asyncio.TimeoutError:
        return {
            "success": False,
            "returncode": -1,
            "stdout": "",
            "stderr": f"Command timed out after {timeout} seconds",
            "command": " ".join(cmd),
        }
    except Exception as e:
        return {
            "success": False,
            "returncode": -1,
            "stdout": "",
            "stderr": str(e),
            "command": " ".join(cmd),
        }


async def check_prerequisites() -> Dict[str, bool]:
    """Check if all required tools are available"""
    tools = {}

    # Check Gemini CLI
    result = await run_command([GEMINI_CLI_PATH, "--version"])
    tools["gemini"] = result["success"]

    # Check Node.js
    result = await run_command(["node", "--version"])
    tools["node"] = result["success"]

    # Check npm
    result = await run_command(["npm", "--version"])
    tools["npm"] = result["success"]

    # Check Angular CLI
    result = await run_command(["ng", "version"])
    tools["angular_cli"] = result["success"]

    return tools


async def read_context_files(context_path: str) -> str:
    """Read and combine context files"""
    context_content = ""
    context_dir = Path(context_path)

    if not context_dir.exists():
        return "No context files found."

    if context_dir.is_file():
        # Single file
        async with aiofiles.open(context_dir, "r", encoding="utf-8") as f:
            content = await f.read()
            context_content = f"--- {context_dir.name} ---\n{content}\n"
    else:
        # Directory with multiple files
        for file_path in context_dir.glob("*"):
            if file_path.is_file() and file_path.suffix in [".txt", ".md", ".json"]:
                async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
                    content = await f.read()
                    context_content += f"\n--- {file_path.name} ---\n{content}\n"

    return context_content


async def generate_project_with_gemini(
    project_name: str, context_content: str, project_path: Path
) -> Dict[str, Any]:
    """Use Gemini CLI to generate Angular 20 project"""

    prompt = f"""
    \"Create a complete Angular 20 project named '{project_name}-angular20' based on the following context and requirements:

    CONTEXT path:
    @C:/Users/subha/Desktop/MCP-POC/snapit/{context_content}

    PROJECT REQUIREMENTS:
    - Project name: {project_name}-angular20
    - Framework: Angular 20 
    - Use TypeScript with strict mode
    - Implement all UI components as described in the context
    - Follow Angular best practices and style guide
    - Use Angular Material for UI components
    - Implement responsive design
    - Include proper error handling
    - Set up routing and navigation
    - Create services for data management
    - Include unit test files
    - Implement dark/light theme support
    - Follow accessibility guidelines (WCAG 2.1 AA)

    IMPORTANT INSTRUCTIONS:
    1. Generate ONLY the Angular project files and structure
    2. Create a complete package.json with all necessary dependencies
    3. Include angular.json configuration
    4. Create all component files (.ts, .html, .css)
    5. Create service files and modules
    6. Include proper TypeScript configurations
    7. Set up environment files
    8. Create a comprehensive README.md with setup instructions
    9. Ensure all imports and dependencies are correctly specified
    10. Make the project ready to build and run with 'ng serve'

    OUTPUT FORMAT:
    Provide a complete project structure with file contents. Each file should be clearly separated and named.
    Start with a project structure overview, then provide the content for each file.
     \" 
     """.replace("\n", " ").strip()

    # Create project directory
    print(f"📁 Creating project directory: {project_path}")
    project_path.mkdir(parents=True, exist_ok=True)
    print(f"📁 Created project directory: {project_path}")
    print(GEMINI_CLI_PATH, "--prompt", prompt, "--yolo")
    result = subprocess.run(
        [GEMINI_CLI_PATH, "--prompt", prompt, "--yolo"],
        check=True,
        text=True,
        capture_output=True,
    )
    print("Command executed successfully!")
    print("Output:", result.stdout)

    if not result["success"]:
        return {
            "success": False,
            "error": f"Gemini CLI failed: {result['stderr']}",
            "output": result["stdout"],
        }

    # Try to create basic Angular project structure if Gemini output is not parseable
    try:
        await print(result["stdout"])
        return {
            "success": True,
            "output": result["stdout"],
            "message": "Project files created successfully",
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to create project files: {str(e)}",
            "output": result["stdout"],
        }


async def install_dependencies(project_path: Path) -> Dict[str, Any]:
    """Install npm dependencies"""
    return await run_command(["npm", "install"], cwd=project_path, timeout=600)


async def build_project(project_path: Path) -> Dict[str, Any]:
    """Build the Angular project"""
    return await run_command(["ng", "build"], cwd=project_path, timeout=600)


async def run_project(project_path: Path, port: int = 4200) -> Dict[str, Any]:
    """Start the Angular development server"""
    return await run_command(
        ["ng", "serve", "--port", str(port), "--open"], cwd=project_path
    )


async def fix_common_issues(
    project_path: Path, build_result: Dict[str, Any]
) -> List[str]:
    """Analyze build errors and apply common fixes"""
    fixes_applied = []

    if not build_result["success"]:
        error_output = build_result["stderr"] + build_result["stdout"]

        # Fix common Angular issues
        if "Cannot find module" in error_output:
            # Try to install missing dependencies
            result = await run_command(
                ["npm", "install", "--save-dev", "@types/node"], cwd=project_path
            )
            if result["success"]:
                fixes_applied.append("Installed missing @types/node dependency")

        if "Strict mode" in error_output or "strictTemplates" in error_output:
            # Adjust TypeScript strict settings
            tsconfig_path = project_path / "tsconfig.json"
            if tsconfig_path.exists():
                # Read and modify tsconfig
                async with aiofiles.open(tsconfig_path, "r") as f:
                    content = await f.read()

                # Make strict mode less restrictive for auto-generated code
                content = content.replace('"strict": true', '"strict": false')
                content = content.replace(
                    '"strictTemplates": true', '"strictTemplates": false'
                )

                async with aiofiles.open(tsconfig_path, "w") as f:
                    await f.write(content)

                fixes_applied.append("Relaxed TypeScript strict mode settings")

        if "Package not found" in error_output:
            # Try to install Angular Material if missing
            result = await run_command(
                ["ng", "add", "@angular/material", "--skip-confirmation"],
                cwd=project_path,
            )
            if result["success"]:
                fixes_applied.append("Added Angular Material")

    return fixes_applied


async def update_project_status(
    project_id: str,
    status: str,
    step: str,
    progress: int,
    logs: List[str] = None,
    errors: List[str] = None,
):
    """Update project status in cache"""
    project_status_cache[project_id] = ProjectStatus(
        project_id=project_id,
        status=status,
        current_step=step,
        progress=progress,
        logs=logs or [],
        errors=errors or [],
    )


async def process_project_generation(project_request: ProjectRequest, project_id: str):
    """Background task to process project generation"""
    project_path = PROJECTS_ROOT / project_request.project_name
    logs = []
    errors = []
    fixes_applied = []

    try:
        context_content = project_request.context_file_path

        gemini_result = await generate_project_with_gemini(
            project_request.project_name, context_content, project_path
        )

        if not gemini_result["success"]:
            errors.append(f"Project generation failed: {gemini_result['error']}")
            await update_project_status(
                project_id, "failed", "Project generation failed", 30, logs, errors
            )
            return

        logs.append("Project files generated successfully")

        if project_request.auto_build:
            # Step 4: Install dependencies
            await update_project_status(
                project_id, "running", "Installing dependencies", 50, logs
            )
            install_result = await install_dependencies(project_path)

            if not install_result["success"]:
                errors.append(
                    f"Dependency installation failed: {install_result['stderr']}"
                )
                if not project_request.fix_issues:
                    await update_project_status(
                        project_id,
                        "failed",
                        "Dependency installation failed",
                        50,
                        logs,
                        errors,
                    )
                    return
            else:
                logs.append("Dependencies installed successfully")

            # Step 5: Build project
            await update_project_status(
                project_id, "running", "Building project", 70, logs
            )
            build_result = await build_project(project_path)

            if not build_result["success"] and project_request.fix_issues:
                logs.append("Build failed, attempting to fix issues...")
                applied_fixes = await fix_common_issues(project_path, build_result)
                fixes_applied.extend(applied_fixes)

                if applied_fixes:
                    # Retry build after fixes
                    logs.append("Retrying build after applying fixes...")
                    build_result = await build_project(project_path)

            if not build_result["success"]:
                errors.append(f"Build failed: {build_result['stderr']}")
                await update_project_status(
                    project_id, "failed", "Build failed", 70, logs, errors
                )
                return

            logs.append("Project built successfully")

            # Step 6: Run project (if requested)
            if project_request.auto_run:
                await update_project_status(
                    project_id, "running", "Starting development server", 90, logs
                )
                # Note: ng serve runs indefinitely, so we start it in background
                await run_project(project_path)
                logs.append("Development server started")

        # Complete
        await update_project_status(
            project_id, "completed", "Project ready", 100, logs, errors
        )

        # Update final status with results
        final_status = project_status_cache[project_id]
        final_status.logs = logs
        final_status.errors = errors

    except Exception as e:
        errors.append(f"Unexpected error: {str(e)}")
        await update_project_status(
            project_id, "failed", "Unexpected error occurred", 0, logs, errors
        )


# API Endpoints


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "SnapIt Code Agent - Enhanced",
        "version": "2.0.0",
        "description": "Enhanced AI-powered code agent for Angular 20 project generation, building, and running",
        "endpoints": {
            "generate": "/generate - Generate, build, and run Angular project",
            "status": "/status/{project_id} - Check project generation status",
            "projects": "/projects - List all projects",
            "prerequisites": "/prerequisites - Check system prerequisites",
        },
    }


@app.get("/prerequisites")
async def check_system_prerequisites():
    """Check if all required tools are available"""
    tools = await check_prerequisites()
    return {
        "tools": tools,
        "all_available": all(tools.values()),
        "missing": [tool for tool, available in tools.items() if not available],
    }


@app.post("/generate", response_model=ProjectResponse)
async def generate_project(
    project_request: ProjectRequest, background_tasks: BackgroundTasks
):
    """Generate, build, and run Angular 20 project"""

    project_id = f"{project_request.project_name}"
    project_path = PROJECTS_ROOT / project_request.project_name

    print(f"🚀 Generating project: {project_request.project_name}")

    # Validate project name
    if not project_request.project_name.replace("-", "").replace("_", "").isalnum():
        raise HTTPException(
            status_code=400,
            detail="Project name must be alphanumeric (hyphens and underscores allowed)",
        )

    # Initialize status
    await update_project_status(
        project_id, "initializing", "Starting project generation", 0
    )

    # Start background processing
    background_tasks.add_task(process_project_generation, project_request, project_id)

    return ProjectResponse(
        project_id=project_id,
        status="started",
        message="Project generation started. Use /status/{project_id} to check progress.",
        project_path=str(project_path),
    )


@app.get("/status/{project_id}", response_model=ProjectStatus)
async def get_project_status(project_id: str):
    """Get project generation status"""

    if project_id not in project_status_cache:
        raise HTTPException(status_code=404, detail="Project not found")

    return project_status_cache[project_id]


@app.get("/projects")
async def list_projects():
    """List all generated projects"""
    projects = []

    if PROJECTS_ROOT.exists():
        for project_dir in PROJECTS_ROOT.iterdir():
            if project_dir.is_dir():
                projects.append(
                    {
                        "name": project_dir.name,
                        "path": str(project_dir),
                        "created": project_dir.stat().st_ctime,
                        "has_build": (project_dir / "dist").exists(),
                        "has_node_modules": (project_dir / "node_modules").exists(),
                    }
                )

    return {"projects": projects}


@app.delete("/projects/{project_name}")
async def delete_project(project_name: str):
    """Delete a generated project"""
    project_path = PROJECTS_ROOT / project_name

    if not project_path.exists():
        raise HTTPException(status_code=404, detail="Project not found")

    shutil.rmtree(project_path)
    return {"message": f"Project '{project_name}' deleted successfully"}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    tools = await check_prerequisites()
    return {
        "status": "healthy" if all(tools.values()) else "warning",
        "timestamp": int(time.time()),
        "version": "2.0.0",
        "tools_available": tools,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
