"""FastAPI main application for AI DevOps Agent Platform."""

import os
import uuid
from contextlib import asynccontextmanager
from typing import List, Optional

import uvicorn
from fastapi import FastAPI, File, HTTPException, UploadFile, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from loguru import logger
from pydantic import BaseModel

from config.settings import settings, ensure_directories
from shared.models import ProcessingTask, ProjectGeneration, ProcessingStatus
from backend.services.project_service import ProjectService
from backend.services.task_service import TaskService


# Initialize services
task_service = TaskService()
project_service = ProjectService()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting AI DevOps Agent Platform")
    ensure_directories()
    yield
    # Shutdown
    logger.info("Shutting down AI DevOps Agent Platform")


# Create FastAPI app
app = FastAPI(
    title="AI DevOps Agent Platform",
    description="AI-powered tool for modernizing legacy applications",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://localhost:3000"],  # Streamlit and dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response models
class GenerationRequest(BaseModel):
    project_name: str
    description: Optional[str] = None
    target_framework: str = "angular-v20"
    additional_requirements: Optional[str] = None


class TaskResponse(BaseModel):
    task_id: str
    status: str
    message: str


class ComponentGenerationResponse(BaseModel):
    task_id: str
    components: List[dict]
    project_structure: dict


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "AI DevOps Agent Platform API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": task_service.get_current_timestamp(),
        "settings": {
            "has_openai_key": bool(settings.openai_api_key),
            "has_anthropic_key": bool(settings.anthropic_api_key),
            "carbon_tracking": settings.enable_carbon_tracking
        }
    }


@app.post("/api/projects/generate", response_model=TaskResponse)
async def generate_project(
    background_tasks: BackgroundTasks,
    project_name: str,
    target_framework: str = "angular-v20",
    description: Optional[str] = None,
    additional_requirements: Optional[str] = None,
    screenshots: List[UploadFile] = File(...),
    reference_styles: Optional[List[UploadFile]] = File(None)
):
    """Generate Angular project from screenshots."""
    try:
        # Validate inputs
        if not screenshots:
            raise HTTPException(status_code=400, detail="At least one screenshot is required")
        
        if not project_name.strip():
            raise HTTPException(status_code=400, detail="Project name is required")
        
        # Create task
        task_id = str(uuid.uuid4())
        task = ProcessingTask(
            task_id=task_id,
            status=ProcessingStatus.PENDING,
            message="Project generation started"
        )
        
        await task_service.create_task(task)
        
        # Save uploaded files
        uploaded_screenshots = []
        for screenshot in screenshots:
            if not screenshot.content_type.startswith('image/'):
                raise HTTPException(status_code=400, detail=f"File {screenshot.filename} is not an image")
            
            file_path = await project_service.save_uploaded_file(screenshot, task_id)
            uploaded_screenshots.append(file_path)
        
        uploaded_styles = []
        if reference_styles:
            for style_file in reference_styles:
                file_path = await project_service.save_uploaded_file(style_file, task_id)
                uploaded_styles.append(file_path)
        
        # Create generation request
        generation_request = ProjectGeneration(
            task_id=task_id,
            uploaded_files=[],  # Will be populated by service
            project_name=project_name,
            description=description,
            additional_requirements=additional_requirements,
            target_framework=target_framework
        )
        
        # Start background processing
        background_tasks.add_task(
            project_service.process_project_generation,
            generation_request,
            uploaded_screenshots,
            uploaded_styles
        )
        
        return TaskResponse(
            task_id=task_id,
            status="pending",
            message="Project generation started successfully"
        )
        
    except Exception as e:
        logger.error(f"Project generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/tasks/{task_id}")
async def get_task_status(task_id: str):
    """Get task status and progress."""
    task = await task_service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return {
        "task_id": task.task_id,
        "status": task.status.value,
        "progress": task.progress,
        "message": task.message,
        "created_at": task.created_at,
        "updated_at": task.updated_at,
        "error": task.error,
        "result": task.result
    }


@app.get("/api/projects/{task_id}/download")
async def download_project(task_id: str):
    """Download generated project as ZIP file."""
    task = await task_service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task.status != ProcessingStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Project generation not completed")
    
    # Generate ZIP file
    zip_path = await project_service.create_project_zip(task_id)
    
    if not os.path.exists(zip_path):
        raise HTTPException(status_code=404, detail="Generated project not found")
    
    return FileResponse(
        path=zip_path,
        media_type="application/zip",
        filename=f"generated-project-{task_id}.zip"
    )


@app.get("/api/projects/{task_id}/preview")
async def preview_project(task_id: str):
    """Get preview of generated project structure."""
    task = await task_service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task.status not in [ProcessingStatus.COMPLETED, ProcessingStatus.PROCESSING]:
        raise HTTPException(status_code=400, detail="No preview available")
    
    preview = await project_service.get_project_preview(task_id)
    return preview


@app.delete("/api/tasks/{task_id}")
async def cancel_task(task_id: str):
    """Cancel a running task."""
    success = await task_service.cancel_task(task_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found or cannot be cancelled")
    
    return {"message": "Task cancelled successfully"}


@app.get("/api/settings")
async def get_settings():
    """Get current application settings."""
    return {
        "target_frameworks": ["angular-v20", "react", "vue"],
        "max_upload_size": settings.max_upload_size,
        "supported_image_types": ["image/jpeg", "image/png", "image/webp"],
        "ai_models": {
            "vision": settings.default_vision_model,
            "code": settings.default_code_model,
            "layout": settings.default_layout_model
        }
    }


@app.post("/api/test/analyze-screenshot")
async def test_analyze_screenshot(screenshot: UploadFile = File(...)):
    """Test endpoint for analyzing a single screenshot."""
    if not screenshot.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Save temporary file
    temp_path = await project_service.save_uploaded_file(screenshot, "test")
    
    try:
        # Quick analysis
        result = await project_service.analyze_single_screenshot(temp_path)
        return result
    finally:
        # Clean up
        if os.path.exists(temp_path):
            os.remove(temp_path)


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.backend_host,
        port=settings.backend_port,
        reload=settings.debug,
        log_level="info"
    )