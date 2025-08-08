# AI DevOps Agent Platform - FastAPI Backend

This is a comprehensive FastAPI backend implementation for the AI DevOps Agent Platform that generates Angular applications from UI screenshots using AI agents.

## Architecture

The backend implements a complete agent flow as described in the AI_DevOps_Agent_Platform_README.md:

```
Input → Generation → Validation → Improvement → Finalization
```

## Agents Implemented

### 🔄 Input Processing
- **PromptEnhancerAgent**: Enriches vague prompts with context (design goals, UX intent, architecture hints)
- **EmbeddingAgent**: Ingests screenshots and creates semantic memory for UI consistency

### 🏗️ Generation Phase  
- **VisionAgent**: Parses screenshots into structured UI elements
- **LayoutAgent**: Translates UI trees into Angular-compatible layout (HTML)
- **CodeAgent**: Generates Angular TS/HTML/SCSS following best practices
- **StyleAgent**: Applies SCSS/themes from uploaded files or inferred design
- **StubAgent**: Creates service stubs and mock HTTP endpoints

### ✅ Validation Phase
- **ValidationAgent**: Runs ng build, ng test, ng lint and parses errors

### 🔄 Improvement Phase
- **CodeReviewAgent**: Flags UI/UX violations, Angular antipatterns, accessibility issues
- **EnhancementAgent**: Recommends improvements and re-generates code if necessary

### 📝 Finalization Phase
- **DocumentationAgent**: Writes README, docstrings, and usage guides for all components
- **PipelineAgent**: Generates GitHub Actions, Dockerfiles, and CI/CD configs
- **CarbonAgent**: Tracks estimated CO₂ per model/token run

## Installation

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the development server:**
   ```bash
   python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
   ```

3. **Access the API:**
   - API Documentation: http://localhost:8000/docs
   - Alternative docs: http://localhost:8000/redoc
   - Health check: http://localhost:8000/health

## API Endpoints

### Main Processing
- `POST /process` - Main endpoint for UI modernization (accepts prompts + screenshots)
- `GET /health` - Health check for all agents
- `GET /agents/status` - Detailed status of all agents

### Individual Agent Operations
- `POST /enhance-prompt` - Standalone prompt enhancement
- `POST /analyze-screenshot` - Standalone screenshot analysis

## Usage Example

```python
import requests
import json

# Process UI modernization request
with open('screenshot.png', 'rb') as img:
    response = requests.post(
        'http://localhost:8000/process',
        data={
            'prompt': 'Modernize this UI to use Angular Material',
            'design_goals': 'Clean, modern, responsive design',
            'ux_intent': 'Dashboard interface for data visualization'
        },
        files={'screenshots': img}
    )

result = response.json()
print(json.dumps(result, indent=2))
```

## Features

### 🎯 Core Capabilities
- **Screenshot Analysis**: Computer vision for UI element detection
- **Angular Code Generation**: Complete TypeScript/HTML/SCSS generation
- **Material Design Integration**: Angular Material components and theming
- **Responsive Design**: Mobile-first responsive patterns
- **Accessibility**: WCAG 2.1 AA compliance
- **Performance Optimization**: OnPush change detection, lazy loading
- **Testing**: Unit and integration test generation
- **Documentation**: Comprehensive docs and guides
- **CI/CD**: Complete pipeline configurations
- **Carbon Tracking**: Environmental impact monitoring

### 🔧 Technical Features
- **Async Processing**: Non-blocking agent execution
- **Error Handling**: Comprehensive error recovery
- **Validation**: Multi-stage code validation
- **Enhancement**: Automatic code improvement
- **Extensibility**: Modular agent architecture

## Configuration

The system uses environment-based configuration. Each agent can be configured independently:

```python
# Example agent configuration
agents = {
    "prompt_enhancer": PromptEnhancerAgent(),
    "vision": VisionAgent(),
    "code": CodeAgent(),
    # ... other agents
}
```

## Development

### Project Structure
```
backend/
├── main.py              # FastAPI application
├── agents/              # AI agent implementations
│   ├── __init__.py
│   ├── prompt_enhancer_agent.py
│   ├── vision_agent.py
│   ├── code_agent.py
│   └── ...
└── __init__.py
```

### Adding New Agents
1. Create new agent class in `backend/agents/`
2. Implement required methods (`async def process(...)`)
3. Add to agent registry in `main.py`
4. Update API endpoints if needed

### Testing
```bash
# Run with test mode
uvicorn backend.main:app --reload --env test

# Health check
curl http://localhost:8000/health
```

## Production Deployment

### Docker
```bash
# Build image
docker build -t ai-devops-backend .

# Run container
docker run -p 8000:8000 ai-devops-backend
```

### Environment Variables
- `PORT`: Server port (default: 8000)
- `HOST`: Server host (default: 0.0.0.0)
- `RELOAD`: Enable auto-reload for development (default: False)

## API Response Format

All endpoints return structured responses:

```json
{
  "status": "success|error",
  "message": "Human readable message",
  "data": {
    "session_id": "unique_session_id",
    "code_files": { ... },
    "documentation": { ... },
    "pipeline_config": { ... }
  },
  "carbon_footprint": 0.001,
  "processing_time": 45.2
}
```

## Monitoring

### Health Monitoring
- Individual agent health checks
- System resource monitoring
- Carbon footprint tracking
- Performance metrics

### Logging
- Structured logging with timestamps
- Agent-specific log levels
- Processing session tracking
- Error reporting and debugging

## Contributing

1. Follow the existing agent pattern
2. Add comprehensive error handling
3. Include status reporting methods
4. Update documentation
5. Add appropriate logging

## License

This implementation is part of the AI DevOps Agent Platform project.

---

**Generated by**: AI DevOps Agent Platform  
**Version**: 1.0.0  
**Agents**: 13 specialized AI agents  
**Capabilities**: Complete Angular application generation from UI screenshots