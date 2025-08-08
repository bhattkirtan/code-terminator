# Enhanced Code Agent PowerShell Management Script
# Manages the enhanced code agent API and project generation

param(
    [Parameter(Position=0)]
    [string]$Action = "help",
    
    [Parameter(Position=1)]
    [string]$ProjectName = "",
    
    [Parameter(Position=2)]
    [string]$ContextPath = ""
)

$ErrorActionPreference = "Stop"

function Show-Help {
    Write-Host "Enhanced Code Agent - Management Script" -ForegroundColor Cyan
    Write-Host "=======================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Usage: .\run_code_agent.ps1 [action] [project_name] [context_path]" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Actions:" -ForegroundColor Yellow
    Write-Host "  start        - Start the enhanced code agent API"
    Write-Host "  test         - Run API tests"
    Write-Host "  generate     - Generate a new project (requires project_name)"
    Write-Host "  status       - Check system status and prerequisites"
    Write-Host "  projects     - List all generated projects"
    Write-Host "  demo         - Run full demo workflow"
    Write-Host "  clean        - Clean generated projects"
    Write-Host "  help         - Show this help message"
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor Yellow
    Write-Host "  .\run_code_agent.ps1 start"
    Write-Host "  .\run_code_agent.ps1 generate my-app ../test-demo/context"
    Write-Host "  .\run_code_agent.ps1 demo"
    Write-Host ""
}

function Test-Prerequisites {
    Write-Host "Checking system prerequisites..." -ForegroundColor Yellow
    
    $allGood = $true
    
    # Check Python
    try {
        $pythonVersion = python --version 2>$null
        Write-Host "✅ Python: $pythonVersion" -ForegroundColor Green
    }
    catch {
        Write-Host "❌ Python not found" -ForegroundColor Red
        $allGood = $false
    }
    
    # Check Node.js
    try {
        $nodeVersion = node --version 2>$null
        Write-Host "✅ Node.js: $nodeVersion" -ForegroundColor Green
    }
    catch {
        Write-Host "❌ Node.js not found" -ForegroundColor Red
        $allGood = $false
    }
    
    # Check npm
    try {
        $npmVersion = npm --version 2>$null
        Write-Host "✅ npm: $npmVersion" -ForegroundColor Green
    }
    catch {
        Write-Host "❌ npm not found" -ForegroundColor Red
        $allGood = $false
    }
    
    # Check Angular CLI
    try {
        $ngVersion = ng version --skip-git 2>$null | Select-String "Angular CLI"
        Write-Host "✅ Angular CLI: $ngVersion" -ForegroundColor Green
    }
    catch {
        Write-Host "❌ Angular CLI not found" -ForegroundColor Red
        Write-Host "   Install with: npm install -g @angular/cli" -ForegroundColor Yellow
        $allGood = $false
    }
    
    # Check Gemini CLI
    try {
        $geminiVersion = gemini --version 2>$null
        Write-Host "✅ Gemini CLI: $geminiVersion" -ForegroundColor Green
    }
    catch {
        Write-Host "❌ Gemini CLI not found" -ForegroundColor Red
        Write-Host "   Install from: https://github.com/google/generative-ai-docs" -ForegroundColor Yellow
        $allGood = $false
    }
    
    return $allGood
}

function Start-CodeAgent {
    Write-Host "Starting Enhanced Code Agent API..." -ForegroundColor Yellow
    
    if (!(Test-Path "code_agent.py")) {
        Write-Host "❌ code_agent.py not found!" -ForegroundColor Red
        return $false
    }
    
    try {
        Write-Host "🚀 Starting API server on http://localhost:8001" -ForegroundColor Green
        Write-Host "📚 API documentation: http://localhost:8001/docs" -ForegroundColor Green
        Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
        Write-Host ""
        
        python code_agent.py
    }
    catch {
        Write-Host "❌ Failed to start API: $_" -ForegroundColor Red
        return $false
    }
}

function Test-CodeAgent {
    Write-Host "Testing Enhanced Code Agent API..." -ForegroundColor Yellow
    
    if (!(Test-Path "test_code_agent.py")) {
        Write-Host "❌ test_code_agent.py not found!" -ForegroundColor Red
        return $false
    }
    
    try {
        python test_code_agent.py
    }
    catch {
        Write-Host "❌ Failed to run tests: $_" -ForegroundColor Red
        return $false
    }
}

function Generate-Project {
    param(
        [string]$Name,
        [string]$Context = ""
    )
    
    if (-not $Name) {
        Write-Host "❌ Project name is required!" -ForegroundColor Red
        Write-Host "Usage: .\run_code_agent.ps1 generate <project_name> [context_path]" -ForegroundColor Yellow
        return $false
    }
    
    Write-Host "🚀 Generating project: $Name" -ForegroundColor Yellow
    
    $requestBody = @{
        project_name = $Name
        auto_build = $true
        auto_run = $false
        fix_issues = $true
    }
    
    if ($Context) {
        $requestBody.context_file_path = $Context
        Write-Host "📁 Using context: $Context" -ForegroundColor Cyan
    }
    
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:8001/generate" -Method Post -Body ($requestBody | ConvertTo-Json) -ContentType "application/json"
        
        Write-Host "✅ Project generation started!" -ForegroundColor Green
        Write-Host "📋 Project ID: $($response.project_id)" -ForegroundColor Cyan
        Write-Host "📁 Project Path: $($response.project_path)" -ForegroundColor Cyan
        
        # Monitor progress
        Write-Host ""
        Write-Host "📊 Monitoring progress..." -ForegroundColor Yellow
        
        do {
            Start-Sleep -Seconds 5
            $status = Invoke-RestMethod -Uri "http://localhost:8001/status/$($response.project_id)" -Method Get
            
            Write-Host "   Status: $($status.status) | Step: $($status.current_step) | Progress: $($status.progress)%" -ForegroundColor Cyan
            
            if ($status.logs) {
                foreach ($log in $status.logs[-3..-1]) {
                    Write-Host "   📝 $log" -ForegroundColor Gray
                }
            }
            
            if ($status.errors) {
                foreach ($error in $status.errors) {
                    Write-Host "   ❌ $error" -ForegroundColor Red
                }
            }
            
        } while ($status.status -eq "running")
        
        if ($status.status -eq "completed") {
            Write-Host ""
            Write-Host "🎉 Project generation completed successfully!" -ForegroundColor Green
            Write-Host "📁 Project location: $($response.project_path)" -ForegroundColor Cyan
            Write-Host ""
            Write-Host "Next steps:" -ForegroundColor Yellow
            Write-Host "1. cd `"$($response.project_path)`"" -ForegroundColor Gray
            Write-Host "2. ng serve" -ForegroundColor Gray
            Write-Host "3. Open http://localhost:4200 in browser" -ForegroundColor Gray
        } else {
            Write-Host ""
            Write-Host "❌ Project generation failed!" -ForegroundColor Red
        }
        
    }
    catch {
        Write-Host "❌ Failed to generate project: $_" -ForegroundColor Red
        Write-Host "💡 Make sure the API is running: .\run_code_agent.ps1 start" -ForegroundColor Yellow
        return $false
    }
}

function Show-Projects {
    Write-Host "📁 Listing generated projects..." -ForegroundColor Yellow
    
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:8001/projects" -Method Get
        
        if ($response.projects.Count -eq 0) {
            Write-Host "   No projects found." -ForegroundColor Gray
        } else {
            Write-Host "   Found $($response.projects.Count) projects:" -ForegroundColor Green
            
            foreach ($project in $response.projects) {
                $buildStatus = if ($project.has_build) { "✅ Built" } else { "❌ Not built" }
                $depsStatus = if ($project.has_node_modules) { "✅ Dependencies" } else { "❌ No deps" }
                
                Write-Host "   📦 $($project.name)" -ForegroundColor Cyan
                Write-Host "      Path: $($project.path)" -ForegroundColor Gray
                Write-Host "      Created: $([DateTime]::FromUnixTimeSeconds($project.created))" -ForegroundColor Gray
                Write-Host "      Status: $buildStatus | $depsStatus" -ForegroundColor Gray
                Write-Host ""
            }
        }
    }
    catch {
        Write-Host "❌ Failed to list projects: $_" -ForegroundColor Red
        Write-Host "💡 Make sure the API is running: .\run_code_agent.ps1 start" -ForegroundColor Yellow
    }
}

function Run-Demo {
    Write-Host "🚀 Running Enhanced Code Agent Demo..." -ForegroundColor Yellow
    
    if (!(Test-Path "test_code_agent.py")) {
        Write-Host "❌ test_code_agent.py not found!" -ForegroundColor Red
        return $false
    }
    
    try {
        python test_code_agent.py
    }
    catch {
        Write-Host "❌ Failed to run demo: $_" -ForegroundColor Red
        return $false
    }
}

function Clean-Projects {
    Write-Host "🧹 Cleaning generated projects..." -ForegroundColor Yellow
    
    if (Test-Path "generated_projects") {
        Remove-Item "generated_projects\*" -Recurse -Force -ErrorAction SilentlyContinue
        Write-Host "✅ Generated projects cleaned" -ForegroundColor Green
    } else {
        Write-Host "   No projects to clean" -ForegroundColor Gray
    }
    
    # Clean Python cache
    Get-ChildItem -Path . -Name "__pycache__" -Recurse | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "✅ Python cache cleaned" -ForegroundColor Green
}

function Main {
    Write-Host "Enhanced Code Agent Manager" -ForegroundColor Cyan
    Write-Host "===========================" -ForegroundColor Cyan
    Write-Host ""
    
    switch ($Action.ToLower()) {
        "start" {
            Start-CodeAgent
        }
        "test" {
            Test-CodeAgent
        }
        "generate" {
            Generate-Project -Name $ProjectName -Context $ContextPath
        }
        "status" {
            Test-Prerequisites
        }
        "projects" {
            Show-Projects
        }
        "demo" {
            Run-Demo
        }
        "clean" {
            Clean-Projects
        }
        "help" {
            Show-Help
        }
        default {
            Write-Host "❌ Unknown action: $Action" -ForegroundColor Red
            Show-Help
        }
    }
}

# Run main function
Main
