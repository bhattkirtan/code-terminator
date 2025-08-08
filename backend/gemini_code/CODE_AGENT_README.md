# Enhanced SnapIt Code Agent

A powerful FastAPI application that automatically generates, builds, and runs complete Angular 20 projects using local Gemini CLI based on project context and requirements.

## 🌟 Features

### 🚀 **Complete Project Lifecycle**
- **Generate**: Create complete Angular 20 projects from context files
- **Build**: Automatically build the generated projects  
- **Run**: Start development server with live reload
- **Fix**: Automatically detect and fix common build issues

### 🤖 **AI-Powered Generation**
- Uses local Gemini CLI for privacy and control
- Context-aware project generation
- Follows Angular 20 best practices
- Implements responsive design with Angular Material

### 🔧 **Smart Issue Resolution**
- Automatic dependency installation
- Common build error detection and fixing
- TypeScript configuration optimization
- Missing package auto-installation

### 📊 **Real-time Monitoring**
- Live progress tracking
- Detailed status reporting
- Comprehensive logging
- Error reporting with suggested fixes

## 📋 Prerequisites

Before using the Enhanced Code Agent, ensure you have the following tools installed:

### Required Tools
- **Python 3.8+** - For running the API
- **Node.js 18+** - For Angular development
- **npm 8+** - Package manager
- **Angular CLI 20+** - Angular project management
- **Gemini CLI** - Local AI processing

### Installation Commands
```bash
# Install Angular CLI globally
npm install -g @angular/cli@20

# Install Gemini CLI (follow official docs)
# https://github.com/google/generative-ai-docs
```

## 🚀 Quick Start

### 1. **Check Prerequisites**
```powershell
.\run_code_agent.ps1 status
```

### 2. **Start the API Server**
```powershell
.\run_code_agent.ps1 start
```
The API will be available at `http://localhost:8001`

### 3. **Generate Your First Project**
```powershell
.\run_code_agent.ps1 generate my-app ../test-demo/context
```

### 4. **Run Complete Demo**
```powershell
.\run_code_agent.ps1 demo
```

## 🛠️ Usage

### **Command Line Interface**

#### **Start API Server**
```powershell
.\run_code_agent.ps1 start
```

#### **Generate Project**
```powershell
# With context files
.\run_code_agent.ps1 generate project-name path/to/context

# Without context
.\run_code_agent.ps1 generate project-name
```

#### **Check System Status**
```powershell
.\run_code_agent.ps1 status
```

#### **List Projects**
```powershell
.\run_code_agent.ps1 projects
```

#### **Run Demo**
```powershell
.\run_code_agent.ps1 demo
```

#### **Clean Projects**
```powershell
.\run_code_agent.ps1 clean
```

### **REST API Endpoints**

#### **Generate Project**
```http
POST /generate
Content-Type: application/json

{
  "project_name": "my-angular-app",
  "context_file_path": "../test-demo/context",
  "auto_build": true,
  "auto_run": false,
  "fix_issues": true
}
```

#### **Check Status**
```http
GET /status/{project_id}
```

#### **List Projects**
```http
GET /projects
```

#### **Check Prerequisites**
```http
GET /prerequisites
```

#### **Health Check**
```http
GET /health
```

## 📁 Project Structure

```
backend/
├── code_agent.py              # Enhanced FastAPI application
├── test_code_agent.py         # Comprehensive test client
├── run_code_agent.ps1         # PowerShell management script
├── generated_projects/        # Output directory for projects
└── requirements.txt           # Python dependencies

test-demo/
└── context/                   # Context files for project generation
    └── example-context.md     # Example context with requirements
```

## ⚙️ Configuration

### **Environment Variables**
Create a `.env` file to customize configuration:

```env
# Gemini CLI path (optional)
GEMINI_CLI_PATH=gemini

# API server settings
HOST=0.0.0.0
PORT=8001

# Project settings
PROJECTS_ROOT=./generated_projects
```

### **Context Files**
Context files provide additional information for better project generation:

- **Markdown files** (`.md`) - Requirements and specifications
- **JSON files** (`.json`) - Structured configuration data
- **Text files** (`.txt`) - Additional documentation

## 🔄 Workflow

### **1. Project Generation**
```
Input: Project name + Context files
↓
Gemini CLI Analysis
↓
Angular 20 Project Structure
↓
File Creation with TypeScript/Angular Material
```

### **2. Build Process**
```
Generated Project
↓
npm install (dependencies)
↓
ng build (compilation)
↓
Automatic issue detection and fixing
↓
Ready-to-run project
```

### **3. Issue Resolution**
```
Build Error Detection
↓
Common Issue Analysis
↓
Automatic Fixes Applied
↓
Retry Build Process
↓
Success or Detailed Error Report
```

## 📊 Monitoring & Status

### **Real-time Progress**
- **Initializing** (0-10%) - Starting project generation
- **Reading Context** (10-20%) - Processing context files
- **Generating** (20-50%) - AI project generation
- **Installing** (50-70%) - Dependency installation
- **Building** (70-90%) - Project compilation
- **Completing** (90-100%) - Finalization

### **Status Types**
- `running` - Process in progress
- `completed` - Successfully completed
- `failed` - Process failed with errors

## 🔧 Common Issues & Solutions

### **Missing Tools**
```
❌ Angular CLI not found
💡 Solution: npm install -g @angular/cli@20
```

### **Build Errors**
```
❌ TypeScript strict mode errors
💡 Auto-fix: Relaxes strict mode settings
```

### **Dependency Issues**
```
❌ Missing @types/node
💡 Auto-fix: Installs missing type definitions
```

### **Context File Issues**
```
❌ Context path not found
💡 Solution: Check path exists and contains .md/.json files
```

## 🧪 Testing

### **Run Tests**
```powershell
.\run_code_agent.ps1 test
```

### **Interactive Testing**
```bash
python test_code_agent.py interactive
```

### **Manual API Testing**
Visit `http://localhost:8001/docs` for Swagger UI

## 📝 Generated Project Features

### **Angular 20 Features**
- ✅ Standalone components
- ✅ Angular Material integration
- ✅ Responsive design
- ✅ TypeScript with strict mode
- ✅ Routing and navigation
- ✅ Environment configuration
- ✅ Unit test structure

### **Project Structure**
```
my-angular-app/
├── src/
│   ├── app/
│   │   ├── components/
│   │   ├── services/
│   │   └── models/
│   ├── assets/
│   └── environments/
├── package.json
├── angular.json
├── tsconfig.json
└── README.md
```

### **Included Libraries**
- **@angular/material** - UI components
- **@angular/cdk** - Component development kit
- **RxJS** - Reactive programming
- **TypeScript** - Type safety

## 🚀 Advanced Usage

### **Custom Context Files**
Create detailed context files for better generation:

```markdown
# Project Requirements

## UI Framework
- Use Angular Material
- Implement dark/light theme
- Mobile-first responsive design

## Features
- User authentication
- Data tables with filtering
- Form validation
- Charts and analytics

## Technical Stack
- Angular 20 with TypeScript
- RxJS for state management
- Angular Router for navigation
```

### **Batch Project Generation**
```powershell
# Generate multiple projects
.\run_code_agent.ps1 generate project1 context1/
.\run_code_agent.ps1 generate project2 context2/
.\run_code_agent.ps1 generate project3 context3/
```

### **CI/CD Integration**
```yaml
# GitHub Actions example
- name: Generate Angular Project
  run: |
    python code_agent.py &
    sleep 10
    curl -X POST http://localhost:8001/generate \
      -H "Content-Type: application/json" \
      -d '{"project_name":"ci-project","auto_build":true}'
```

## 🤝 Development

### **Extending the API**
Add new endpoints in `code_agent.py`:

```python
@app.post("/custom-endpoint")
async def custom_function():
    # Your custom logic here
    pass
```

### **Custom Issue Fixes**
Extend the `fix_common_issues` function:

```python
async def fix_common_issues(project_path: Path, build_result: Dict[str, Any]) -> List[str]:
    fixes_applied = []
    # Add your custom fixes here
    return fixes_applied
```

## 📊 Performance

### **Generation Times**
- **Simple project**: 2-5 minutes
- **Complex project**: 5-10 minutes
- **With full build**: 10-15 minutes

### **Resource Usage**
- **Memory**: 500MB-1GB during generation
- **Disk**: 200-500MB per project
- **CPU**: High during AI generation and npm install

## 🔒 Security

### **Local Processing**
- All AI processing happens locally via Gemini CLI
- No data sent to external APIs
- Full control over generated code

### **File System Safety**
- Projects created in isolated directories
- No system file modification
- Safe cleanup and removal

## 🆘 Support

### **Troubleshooting**
1. Check prerequisites: `.\run_code_agent.ps1 status`
2. View API health: `http://localhost:8001/health`
3. Check logs in terminal output
4. Verify Gemini CLI: `gemini --version`

### **Getting Help**
- Check API documentation: `http://localhost:8001/docs`
- Review generated project README files
- Use interactive test mode for debugging

## 📄 License

This project is licensed under the MIT License.

---

**Ready to generate amazing Angular 20 projects with AI? Get started now!** 🚀
