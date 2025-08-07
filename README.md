# AI DevOps Agent Platform

[![Python](https://img.shields.io/badge/Python-3.10+-blue)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red)](https://streamlit.io)
[![Angular](https://img.shields.io/badge/Target-Angular%20v20-red)](https://angular.io)

> AI-powered tool for modernizing legacy applications by analyzing screenshots and generating modern Angular v20 code.

## 🎯 Overview

This platform uses advanced AI agents to automatically transform legacy application screenshots into production-ready Angular v20 code. The system analyzes UI layouts, generates component code, applies modern styling, and creates service stubs for seamless backend integration.

![Architecture Diagram](./AI_DevOps_Agent_Platform_README.md)

## ✨ Features

- **🔍 Vision Analysis** - AI-powered screenshot analysis using GPT-4 Vision or Claude
- **🏗️ Code Generation** - Complete Angular v20 components with TypeScript, HTML, and SCSS
- **🎨 Style Application** - Automatic theme generation from reference designs
- **🔧 Service Stubs** - Mock services for easy backend integration
- **📱 Responsive Design** - Mobile-first, accessibility-compliant components
- **🌱 Carbon Tracking** - Monitor AI model emissions
- **⚡ Real-time Monitoring** - Live progress tracking and status updates

## 🏗️ Architecture

The platform consists of specialized AI agents:

- **VisionAgent** - Analyzes screenshots and extracts UI elements
- **LayoutAgent** - Converts UI structure to Angular component layouts
- **CodeAgent** - Generates complete TypeScript/HTML/SCSS files
- **StyleAgent** - Applies themes and styling based on references
- **StubAgent** - Creates service mocks and API interfaces

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+ (for generated Angular projects)
- OpenAI API key or Anthropic API key

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd code-terminator
   ```

2. **Setup environment**
   ```bash
   # Copy environment template
   cp .env.example .env
   
   # Edit .env with your API keys
   nano .env
   ```

3. **Start the platform**
   ```bash
   ./start.sh
   ```

   Or manually:
   ```bash
   # Install dependencies
   pip install -r requirements.txt
   
   # Start backend
   cd backend
   uvicorn main:app --reload --port 8000 &
   
   # Start frontend
   cd ../frontend
   streamlit run main.py --server.port 8501
   ```

4. **Access the application**
   - Frontend: http://localhost:8501
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## 📖 Usage

### Basic Workflow

1. **Upload Screenshots** - Upload images of your legacy application
2. **Configure Project** - Set project name, framework, and requirements
3. **Add Reference Styles** - Optionally upload CSS files or design references
4. **Generate Code** - Let AI agents analyze and generate modern Angular code
5. **Download Project** - Get complete Angular v20 project with all files

### Advanced Features

#### Custom Styling
- Upload CSS/SCSS files for custom themes
- Include design reference images for color extraction
- Automatic responsive design implementation

#### Service Integration
- Generated service stubs with TypeScript interfaces
- Mock data for development and testing
- HTTP interceptors for API simulation

#### Quality Assurance
- Angular best practices compliance
- Accessibility features included
- TypeScript strict mode compatibility

## 🔧 Configuration

### Environment Variables

```bash
# AI API Keys
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here

# Backend Settings
BACKEND_HOST=localhost
BACKEND_PORT=8000
DEBUG=true

# Model Configuration
DEFAULT_VISION_MODEL=gpt-4-vision-preview
DEFAULT_CODE_MODEL=gpt-4-turbo-preview
DEFAULT_LAYOUT_MODEL=claude-3-sonnet-20240229

# File Upload
MAX_UPLOAD_SIZE=10485760  # 10MB
UPLOAD_FOLDER=./uploads

# Carbon Tracking
ENABLE_CARBON_TRACKING=true
```

### Supported Models

**Vision Analysis:**
- OpenAI GPT-4 Vision
- Anthropic Claude 3 Vision

**Code Generation:**
- OpenAI GPT-4 Turbo
- OpenAI GPT-4
- Anthropic Claude 3 Sonnet
- Anthropic Claude 3 Haiku

## 📁 Project Structure

```
code-terminator/
├── backend/
│   ├── agents/           # AI agent implementations
│   ├── services/         # Business logic services
│   ├── routers/          # API route handlers
│   └── main.py          # FastAPI application
├── frontend/
│   ├── main.py          # Streamlit application
│   └── pages/           # Additional pages
├── shared/
│   ├── models.py        # Pydantic data models
│   └── utils.py         # Shared utilities
├── config/
│   └── settings.py      # Configuration management
├── testdata/            # Sample screenshots and styles
├── requirements.txt     # Python dependencies
└── start.sh            # Startup script
```

## 🧪 Testing

### Test with Sample Data

The platform includes sample screenshots in `testdata/` for testing:

```bash
# Test single screenshot analysis
curl -X POST "http://localhost:8000/api/test/analyze-screenshot" \
  -F "screenshot=@testdata/00_Cases-Portal.jpg"

# Monitor test generation
curl "http://localhost:8000/api/tasks/{task_id}"
```

### Generated Project Testing

Once a project is generated:

```bash
cd output/{task_id}/{project_name}
npm install
ng serve
```

## 🌱 Carbon Emissions

The platform tracks AI model usage and estimates carbon emissions:

- **Real-time Tracking** - Monitor emissions per agent
- **Total Calculations** - Complete project generation footprint
- **Model Optimization** - Choose efficient models for different tasks

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Documentation**: Check the `/docs` endpoint for API documentation
- **Issues**: Report bugs via GitHub issues
- **Discussions**: Join community discussions for questions and ideas

## 🔮 Roadmap

- [ ] Support for React and Vue.js generation
- [ ] Enhanced accessibility features
- [ ] Advanced animation generation
- [ ] Integration with popular design systems
- [ ] Cloud deployment templates
- [ ] Advanced validation agents
- [ ] Multi-language support

---

**Built with ❤️ using AI and modern web technologies**