from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import logging
import asyncio
from datetime import datetime

from backend.agents.prompt_enhancer_agent import PromptEnhancerAgent
from backend.agents.embedding_agent import EmbeddingAgent
from backend.agents.vision_agent import VisionAgent
from backend.agents.layout_agent import LayoutAgent
from backend.agents.code_agent import CodeAgent
from backend.agents.style_agent import StyleAgent
from backend.agents.stub_agent import StubAgent
from backend.agents.validation_agent import ValidationAgent
from backend.agents.code_review_agent import CodeReviewAgent
from backend.agents.enhancement_agent import EnhancementAgent
from backend.agents.documentation_agent import DocumentationAgent
from backend.agents.pipeline_agent import PipelineAgent
from backend.agents.carbon_agent import CarbonAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI DevOps Agent Platform",
    description="A comprehensive platform for generating Angular applications from UI screenshots using AI agents",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request/response
class UserPrompt(BaseModel):
    text: str
    design_goals: Optional[str] = None
    ux_intent: Optional[str] = None
    architecture_hints: Optional[str] = None

class ProcessingResult(BaseModel):
    status: str
    message: str
    data: Dict[str, Any]
    carbon_footprint: Optional[float] = None
    processing_time: Optional[float] = None

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    agents_status: Dict[str, str]

# Initialize agents
agents = {
    "prompt_enhancer": PromptEnhancerAgent(),
    "embedding": EmbeddingAgent(),
    "vision": VisionAgent(),
    "layout": LayoutAgent(),
    "code": CodeAgent(),
    "style": StyleAgent(),
    "stub": StubAgent(),
    "validation": ValidationAgent(),
    "code_review": CodeReviewAgent(),
    "enhancement": EnhancementAgent(),
    "documentation": DocumentationAgent(),
    "pipeline": PipelineAgent(),
    "carbon": CarbonAgent()
}

@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint providing API information"""
    return {
        "message": "AI DevOps Agent Platform API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    agent_statuses = {}
    for name, agent in agents.items():
        try:
            # Simple health check for each agent
            agent_statuses[name] = "healthy"
        except Exception as e:
            agent_statuses[name] = f"unhealthy: {str(e)}"
            logger.error(f"Agent {name} health check failed: {e}")
    
    return HealthResponse(
        status="healthy" if all(status == "healthy" for status in agent_statuses.values()) else "partial",
        timestamp=datetime.now().isoformat(),
        agents_status=agent_statuses
    )

@app.post("/process", response_model=ProcessingResult)
async def process_ui_modernization(
    prompt: str = Form(...),
    screenshots: List[UploadFile] = File(...),
    design_goals: Optional[str] = Form(None),
    ux_intent: Optional[str] = Form(None),
    architecture_hints: Optional[str] = Form(None)
):
    """
    Main endpoint for processing UI modernization requests.
    Follows the agent flow: Input → Generation → Validation → Improvement → Finalization
    """
    start_time = datetime.now()
    session_id = f"session_{int(start_time.timestamp())}"
    
    try:
        logger.info(f"Starting processing session {session_id}")
        
        # Step 1: Input Processing
        logger.info("Step 1: Processing input with PromptEnhancer and Embedding agents")
        
        # Enhance the user prompt
        enhanced_prompt = await agents["prompt_enhancer"].enhance_prompt(
            prompt, design_goals, ux_intent, architecture_hints
        )
        
        # Process screenshots with embedding agent
        screenshot_data = []
        for screenshot in screenshots:
            content = await screenshot.read()
            embedded_data = await agents["embedding"].process_screenshot(content, screenshot.filename)
            screenshot_data.append(embedded_data)
        
        # Step 2: Generation
        logger.info("Step 2: Generation phase - Vision, Layout, Code, Style, Stub agents")
        
        # Parse screenshots with vision agent
        ui_elements = []
        for data in screenshot_data:
            elements = await agents["vision"].detect_ui_elements(data["content"])
            ui_elements.extend(elements)
        
        # Generate layout
        layout = await agents["layout"].generate_layout(ui_elements, enhanced_prompt)
        
        # Generate code
        code_files = await agents["code"].generate_code(layout, enhanced_prompt)
        
        # Apply styling
        styled_code = await agents["style"].apply_styles(code_files, screenshot_data)
        
        # Create service stubs
        service_stubs = await agents["stub"].create_service_stubs(styled_code)
        
        # Step 3: Validation (with retry logic)
        logger.info("Step 3: Validation phase")
        max_retries = 3
        validation_passed = False
        
        for attempt in range(max_retries):
            validation_result = await agents["validation"].validate_code(styled_code, service_stubs)
            
            if validation_result["success"]:
                validation_passed = True
                break
            else:
                logger.warning(f"Validation failed (attempt {attempt + 1}): {validation_result['errors']}")
                # Retry with code agent
                styled_code = await agents["code"].fix_validation_errors(
                    styled_code, validation_result["errors"]
                )
        
        if not validation_passed:
            raise HTTPException(status_code=422, detail="Code validation failed after maximum retries")
        
        # Step 4: Improvement
        logger.info("Step 4: Improvement phase - Code Review and Enhancement")
        
        review_result = await agents["code_review"].review_code(styled_code, enhanced_prompt)
        
        if review_result["needs_improvement"]:
            enhanced_code = await agents["enhancement"].enhance_code(
                styled_code, review_result["suggestions"]
            )
            styled_code = enhanced_code
        
        # Step 5: Finalization
        logger.info("Step 5: Finalization - Documentation, Pipeline, Carbon tracking")
        
        # Generate documentation
        documentation = await agents["documentation"].generate_documentation(
            styled_code, enhanced_prompt, ui_elements
        )
        
        # Generate CI/CD pipeline
        pipeline_config = await agents["pipeline"].generate_pipeline(styled_code)
        
        # Calculate carbon footprint
        carbon_footprint = await agents["carbon"].calculate_footprint(session_id)
        
        # Prepare final result
        processing_time = (datetime.now() - start_time).total_seconds()
        
        result_data = {
            "session_id": session_id,
            "enhanced_prompt": enhanced_prompt,
            "ui_elements": ui_elements,
            "layout": layout,
            "code_files": styled_code,
            "service_stubs": service_stubs,
            "documentation": documentation,
            "pipeline_config": pipeline_config,
            "validation_result": validation_result,
            "review_result": review_result,
            "screenshot_analysis": screenshot_data
        }
        
        logger.info(f"Processing completed successfully for session {session_id}")
        
        return ProcessingResult(
            status="success",
            message="UI modernization completed successfully",
            data=result_data,
            carbon_footprint=carbon_footprint,
            processing_time=processing_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Processing failed for session {session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

@app.post("/enhance-prompt", response_model=Dict[str, Any])
async def enhance_prompt_endpoint(prompt: UserPrompt):
    """Standalone endpoint for prompt enhancement"""
    try:
        enhanced = await agents["prompt_enhancer"].enhance_prompt(
            prompt.text, prompt.design_goals, prompt.ux_intent, prompt.architecture_hints
        )
        return {"enhanced_prompt": enhanced}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prompt enhancement failed: {str(e)}")

@app.post("/analyze-screenshot")
async def analyze_screenshot(screenshot: UploadFile = File(...)):
    """Standalone endpoint for screenshot analysis"""
    try:
        content = await screenshot.read()
        embedded_data = await agents["embedding"].process_screenshot(content, screenshot.filename)
        ui_elements = await agents["vision"].detect_ui_elements(embedded_data["content"])
        
        return {
            "filename": screenshot.filename,
            "embedded_data": embedded_data,
            "ui_elements": ui_elements
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Screenshot analysis failed: {str(e)}")

@app.get("/agents/status")
async def get_agents_status():
    """Get detailed status of all agents"""
    status = {}
    for name, agent in agents.items():
        try:
            agent_info = await agent.get_status() if hasattr(agent, 'get_status') else {"status": "active"}
            status[name] = agent_info
        except Exception as e:
            status[name] = {"status": "error", "error": str(e)}
    
    return {"agents": status}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)