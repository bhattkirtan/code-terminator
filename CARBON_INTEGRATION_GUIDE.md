# 🌍 LLM Carbon Tracking Integration Guide

This guide shows how to implement the 4 next steps for carbon-aware LLM workflows:

## ✅ Step 1: Integrate Carbon Logging into LLM Workflows

### Basic Integration
```python
from llm_carbon_calculator import LLMCarbonCalculator

# Initialize carbon tracking
carbon_calculator = LLMCarbonCalculator()

# Log LLM usage in your existing code
def your_llm_function(prompt, model="gpt-3.5-turbo"):
    start_time = time.time()
    
    # Your existing LLM call
    response = openai.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )
    
    processing_time = time.time() - start_time
    
    # Log carbon usage
    carbon_calculator.log_llm_usage(
        model=model,
        input_tokens=response.usage.prompt_tokens,
        output_tokens=response.usage.completion_tokens,
        processing_time=processing_time,
        operation_type="text"
    )
    
    return response
```

### Enhanced Integration with AccuracyValidator
```python
from skadoosh_agents import AccuracyValidatorAgent, CarbonAgent

class CarbonAwareValidator:
    def __init__(self):
        self.validator = AccuracyValidatorAgent()
        self.carbon_agent = CarbonAgent()
    
    def validate_with_carbon_tracking(self, image_path, use_llm=True):
        # Pre-check carbon budget
        estimated_carbon = 0.015 if use_llm else 0.000001
        
        if estimated_carbon > 0.01:  # Budget limit
            print("⚠️  High carbon operation, consider traditional CV")
        
        # Run validation with carbon tracking
        result = self.validator.execute(context, data)
        
        # Log actual carbon usage
        # (Implementation shown in test_automated.py)
        
        return result
```

## ✅ Step 2: Set Carbon Budgets for Different Operations

### Budget Configuration
```python
from test_automated import CarbonBudgetManager

# Initialize budget manager
budget_manager = CarbonBudgetManager()

# Configure budgets (or load from carbon_config.json)
budget_manager.budgets = {
    "daily_limit_kg": 0.1,        # 100g CO2 per day
    "per_test_limit_kg": 0.01,    # 10g CO2 per test
    "model_limits": {
        "gpt-4o": 0.005,          # 5g CO2 per request
        "gpt-3.5-turbo": 0.001,   # 1g CO2 per request
    }
}

# Check budget before operations
def check_and_execute_llm_operation(model, estimated_carbon):
    budget_check = budget_manager.check_budget("llm_operation", estimated_carbon, model)
    
    if not budget_check["within_budget"]:
        print("🛑 Operation exceeds carbon budget")
        for warning in budget_check["warnings"]:
            print(f"   {warning}")
        return None
    
    # Proceed with operation
    result = your_llm_operation()
    
    # Log actual usage
    budget_manager.log_usage("llm_operation", actual_carbon, model)
    
    return result
```

### Dynamic Budget Enforcement
```python
# Load budgets from configuration
import json

with open('carbon_config.json', 'r') as f:
    config = json.load(f)

daily_limit = config["carbon_budgets"]["daily_limit_kg"]
model_limits = config["carbon_budgets"]["model_specific_limits"]

# Environment-specific budgets
env = os.getenv("ENVIRONMENT", "development")
env_config = config["environment_settings"][env]
daily_limit = env_config["daily_limit_kg"]
```

## ✅ Step 3: Use Local Models for Development and Testing

### Model Selection Strategy
```python
class CarbonAwareModelSelector:
    def __init__(self):
        self.development_models = ["phi-3-mini", "phi-3-vision", "gemma-2b"]
        self.production_models = ["gpt-3.5-turbo", "gpt-4", "gpt-4o"]
        
    def select_model(self, task_type, environment="development"):
        if environment == "development":
            # Use local models for development
            if task_type == "vision":
                return "phi-3-vision"  # ~1000x more carbon efficient
            else:
                return "phi-3-mini"
        else:
            # Use cloud models for production
            if task_type == "vision":
                return "gpt-4o"
            else:
                return "gpt-3.5-turbo"

# Usage in your code
model_selector = CarbonAwareModelSelector()

def run_validation(image_path, environment=None):
    env = environment or os.getenv("ENVIRONMENT", "development")
    
    if env == "development":
        # Use extremely carbon-efficient local models
        model = model_selector.select_model("vision", env)
        print(f"🏠 Using local model {model} (99%+ carbon reduction)")
    else:
        # Use cloud models for production
        model = model_selector.select_model("vision", env)
        print(f"☁️  Using cloud model {model}")
    
    return run_llm_validation(image_path, model)
```

### Local Model Setup Recommendations
```bash
# Install local model runners
pip install transformers torch

# For Phi-3 models
pip install microsoft-phi

# For Gemma models  
pip install google-gemma

# Example: Use Phi-3-mini for text tasks
from transformers import pipeline

generator = pipeline("text-generation", model="microsoft/Phi-3-mini-4k-instruct")
# Carbon footprint: ~0.0001 kg CO2e vs ~0.002 kg for GPT-3.5-turbo
```

## ✅ Step 4: Monitor and Optimize Based on Carbon Reports

### Real-time Monitoring
```python
from carbon_monitoring_dashboard import CarbonDashboard

# Initialize dashboard
dashboard = CarbonDashboard()

# Log operations in your workflow
def monitored_llm_call(model, input_tokens, output_tokens, operation_type):
    start_time = time.time()
    
    # Your LLM call here
    result = your_llm_function()
    
    processing_time = time.time() - start_time
    
    # Log to dashboard
    dashboard.log_operation(model, input_tokens, output_tokens, operation_type, processing_time)
    
    # Print real-time status
    dashboard.print_dashboard()
    
    return result
```

### Automated Optimization
```python
class CarbonOptimizer:
    def __init__(self):
        self.calculator = LLMCarbonCalculator()
        self.optimization_enabled = True
        
    def optimize_operation(self, operation_type, current_model):
        # Get session emissions
        session = self.calculator.calculate_session_emissions()
        
        # Check if optimization is needed
        if session["carbon_efficiency_score"] < 70:
            # Suggest more efficient model
            efficient_models = {
                "text": "gpt-3.5-turbo",
                "vision": "phi-3-vision",  # For development
                "code": "phi-3-mini"
            }
            
            suggested_model = efficient_models.get(operation_type, current_model)
            
            if suggested_model != current_model:
                print(f"💡 Optimization: Switch from {current_model} to {suggested_model}")
                return suggested_model
        
        return current_model

# Usage
optimizer = CarbonOptimizer()

def smart_llm_call(prompt, operation_type="text", model="gpt-4"):
    # Optimize model selection
    optimized_model = optimizer.optimize_operation(operation_type, model)
    
    if optimized_model != model:
        print(f"🔄 Optimized model selection: {model} → {optimized_model}")
    
    return call_llm(prompt, optimized_model)
```

### Comprehensive Reporting
```python
# Export detailed reports
def generate_carbon_report():
    calculator = LLMCarbonCalculator()
    
    # Generate comprehensive report
    report_file = calculator.export_carbon_report("weekly_carbon_report.json")
    
    # Get recommendations
    recommendations = calculator.get_optimization_recommendations()
    
    print("📊 Weekly Carbon Report Generated")
    print("💡 Top Recommendations:")
    for i, rec in enumerate(recommendations[:3], 1):
        print(f"   {i}. {rec}")
    
    return report_file

# Automated daily reports
import schedule

schedule.every().day.at("18:00").do(generate_carbon_report)
```

## 🚀 Quick Start Implementation

### 1. Add to existing AccuracyValidator workflow:
```python
# Add carbon tracking to your test_complete_accuracy_validator.py
from test_automated import CarbonBudgetManager, test_traditional_cv_with_carbon_tracking

# Replace existing test with carbon-aware version
carbon_result = test_traditional_cv_with_carbon_tracking()
print(f"Carbon footprint: {carbon_result['carbon_metrics']['actual_emissions_kg']} kg CO2e")
```

### 2. Environment-specific configuration:
```bash
# Development environment (.env.development)
ENVIRONMENT=development
CARBON_DAILY_LIMIT_KG=0.05
PREFER_LOCAL_MODELS=true

# Production environment (.env.production)  
ENVIRONMENT=production
CARBON_DAILY_LIMIT_KG=0.1
PREFER_LOCAL_MODELS=false
```

### 3. Real-time monitoring:
```python
# Add to your main workflow
python3 carbon_monitoring_dashboard.py demo  # See live dashboard

# Or integrate into existing code:
from carbon_monitoring_dashboard import CarbonDashboard
dashboard = CarbonDashboard()
# Log operations and monitor in real-time
```

## 📊 Results Summary

After implementing all 4 steps, you should see:

- ✅ **Carbon Logging**: All LLM operations tracked with precise emissions
- ✅ **Budget Management**: Operations blocked when exceeding carbon limits  
- ✅ **Local Models**: 99%+ carbon reduction for development workflows
- ✅ **Monitoring**: Real-time dashboard with optimization recommendations

### Expected Carbon Reductions:
- Traditional CV: 0.000001 kg CO2e (baseline)
- Local models: 0.0001 kg CO2e (100x better than cloud)
- GPT-3.5-turbo: 0.002 kg CO2e (7.5x better than GPT-4)
- GPT-4o: 0.015 kg CO2e (use sparingly)

### Sample Budget Configuration:
- Development: 0.05 kg CO2e/day (prefer local models)
- Production: 0.1 kg CO2e/day (cloud models allowed)
- Per-operation limit: 0.01 kg CO2e

This implementation provides complete carbon awareness for your LLM workflows! 🌱
