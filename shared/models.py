"""Shared data models for AI DevOps Agent Platform."""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class ProcessingStatus(str, Enum):
    """Status of processing tasks."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class UIElementType(str, Enum):
    """Types of UI elements that can be detected."""
    BUTTON = "button"
    INPUT = "input"
    CARD = "card"
    TABLE = "table"
    NAVIGATION = "navigation"
    HEADER = "header"
    FOOTER = "footer"
    SIDEBAR = "sidebar"
    MODAL = "modal"
    FORM = "form"
    LIST = "list"
    CHART = "chart"
    IMAGE = "image"
    TEXT = "text"


class UIElement(BaseModel):
    """Represents a detected UI element."""
    type: UIElementType
    label: str
    position: List[int] = Field(description="[x, y, width, height]")
    properties: Dict[str, Any] = Field(default_factory=dict)
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)


class LayoutStructure(BaseModel):
    """Represents the overall layout structure."""
    elements: List[UIElement]
    layout_type: str = "grid"  # grid, flex, absolute
    responsive: bool = True
    accessibility: Dict[str, Any] = Field(default_factory=dict)


class ComponentFile(BaseModel):
    """Represents a generated component file."""
    filename: str
    content: str
    file_type: str  # ts, html, scss, spec.ts


class GeneratedComponent(BaseModel):
    """Represents a complete Angular component."""
    name: str
    files: List[ComponentFile]
    dependencies: List[str] = Field(default_factory=list)
    imports: List[str] = Field(default_factory=list)


class ProcessingTask(BaseModel):
    """Represents a processing task."""
    task_id: str
    status: ProcessingStatus
    progress: float = Field(default=0.0, ge=0.0, le=100.0)
    message: str = ""
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    error: Optional[str] = None
    result: Optional[Dict[str, Any]] = None


class UploadedFile(BaseModel):
    """Represents an uploaded file."""
    filename: str
    content_type: str
    size: int
    path: str
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)


class ProjectGeneration(BaseModel):
    """Represents a complete project generation request."""
    task_id: str
    uploaded_files: List[UploadedFile]
    reference_styles: Optional[List[UploadedFile]] = None
    target_framework: str = "angular-v20"
    project_name: str
    description: Optional[str] = None
    additional_requirements: Optional[str] = None
    

class CarbonEmission(BaseModel):
    """Represents carbon emission tracking."""
    task_id: str
    agent_name: str
    model_name: str
    tokens_used: int
    estimated_co2_grams: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class AgentResult(BaseModel):
    """Represents the result from an agent."""
    agent_name: str
    success: bool
    output: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None
    execution_time: float = 0.0
    tokens_used: int = 0
    carbon_emission: Optional[CarbonEmission] = None