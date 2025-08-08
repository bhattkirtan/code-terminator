#!/usr/bin/env python3
"""
LLM Carbon Calculator Test & Demo
Demonstrates carbon footprint calculation for LLM usage
"""

import os
import sys
import json
import time
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.carbon.llm_carbon_calculator import LLMCarbonCalculator
from src.agents.skadoosh_agents import CarbonAgent, AgentContext

def simulate_llm_usage_session():
    """Simulate a realistic LLM usage session for carbon tracking"""
    
    print("🌍 LLM Carbon Footprint Calculator - Demo Session")
    print("=" * 60)
    
    # Initialize calculator
    calculator = LLMCarbonCalculator()
    
    # Simulate various LLM operations
    print("\n📊 Simulating LLM Usage Session...")
    
    # Vision analysis task (high carbon cost)
    print("   🔍 Vision Analysis Task...")
    calculator.log_llm_usage("gpt-4o", 1200, 600, 3.2, "vision")
    vision_emissions = calculator.calculate_request_emissions("gpt-4o", 1200, 600, "vision")
    print(f"      Emissions: {vision_emissions['total_gco2']} gCO2e")
    
    # Text generation tasks
    print("   ✍️  Text Generation Tasks...")
    calculator.log_llm_usage("gpt-4", 800, 1200, 2.1, "text")
    calculator.log_llm_usage("gpt-3.5-turbo", 500, 300, 1.5, "text")
    calculator.log_llm_usage("gpt-3.5-turbo", 600, 400, 1.8, "text")
    
    # Local model usage (much lower emissions)
    print("   🏠 Local Model Tasks...")
    calculator.log_llm_usage("phi-3-mini", 400, 250, 0.9, "text")
    calculator.log_llm_usage("phi-3-vision", 800, 300, 1.2, "vision")
    calculator.log_llm_usage("gemma-2b", 300, 200, 0.7, "text")
    
    # Calculate session emissions
    session_report = calculator.calculate_session_emissions()
    
    print(f"\n🌱 Session Carbon Footprint Analysis")
    print("-" * 40)
    print(f"Total Requests: {session_report['total_requests']}")
    print(f"Total Emissions: {session_report['total_gco2']} gCO2e")
    print(f"Total Emissions: {session_report['total_kg_co2']} kg CO2e")
    print(f"Efficiency Score: {session_report['carbon_efficiency_score']}/100")
    print(f"Session Duration: {session_report['session_duration_minutes']:.1f} minutes")
    
    # Model breakdown
    print(f"\n📈 Emissions by Model:")
    for model, data in session_report['model_breakdown'].items():
        print(f"   {model:15} | {data['requests']:2} requests | {data['total_gco2']:8.4f} gCO2e")
    
    # Operation breakdown
    print(f"\n🔧 Emissions by Operation:")
    for operation, data in session_report['operation_breakdown'].items():
        print(f"   {operation:10} | {data['requests']:2} requests | {data['total_gco2']:8.4f} gCO2e")
    
    # Optimization recommendations
    print(f"\n💡 Carbon Optimization Recommendations:")
    recommendations = calculator.get_optimization_recommendations()
    for i, rec in enumerate(recommendations, 1):
        print(f"   {i}. {rec}")
    
    # Carbon offset suggestions
    offset_suggestions = calculator.get_carbon_offset_suggestions(session_report['total_kg_co2'])
    print(f"\n🌳 Carbon Offset Suggestions:")
    print(f"   Trees to Plant: {offset_suggestions['trees_to_plant']}")
    print(f"   Renewable Energy: {offset_suggestions['renewable_energy_kwh']} kWh")
    print(f"   Estimated Cost: ${offset_suggestions['cost_estimate_usd']}")
    
    print(f"\n🌍 Environmental Impact Context:")
    for action in offset_suggestions['equivalent_actions']:
        print(f"   • {action}")
    
    return calculator, session_report

def test_enhanced_carbon_agent():
    """Test the enhanced CarbonAgent integration"""
    
    print("\n" + "=" * 60)
    print("🤖 Enhanced CarbonAgent Integration Test")
    print("=" * 60)
    
    # Create agent context with LLM usage data
    context = AgentContext(
        project_name="LLM Carbon Test",
        framework="Python ML Pipeline"
    )
    
    # Add execution trace with LLM usage
    context.execution_trace = [
        {
            "agent": "VisionAgent",
            "model": "gpt-4o",
            "tokens": {"input": 1200, "output": 600},
            "operation_type": "vision",
            "duration": 3.2,
            "timestamp": datetime.now().isoformat()
        },
        {
            "agent": "CodeAgent", 
            "model": "gpt-4",
            "tokens": {"input": 800, "output": 1200},
            "operation_type": "text",
            "duration": 2.1,
            "timestamp": datetime.now().isoformat()
        },
        {
            "agent": "LocalAgent",
            "model": "phi-3-mini", 
            "tokens": {"input": 400, "output": 250},
            "operation_type": "text",
            "duration": 0.9,
            "timestamp": datetime.now().isoformat()
        }
    ]
    
    # Initialize and execute CarbonAgent
    carbon_agent = CarbonAgent()
    
    # Log LLM usage if enhanced calculator is available
    if carbon_agent.carbon_calculator:
        print("\n📋 Logging LLM Usage...")
        for entry in context.execution_trace:
            tokens = entry.get("tokens", {})
            if "input" in tokens and "output" in tokens:
                usage_id = carbon_agent.log_llm_usage(
                    entry["model"],
                    tokens["input"], 
                    tokens["output"],
                    entry["duration"],
                    entry["operation_type"]
                )
                print(f"   Logged {entry['model']} usage: {usage_id}")
    
    # Execute carbon analysis
    result = carbon_agent.execute(context, {"analysis_type": "comprehensive"})
    
    print(f"\n🌱 CarbonAgent Analysis Results:")
    print("-" * 40)
    print(f"Calculation Method: {result['carbon_awareness_level']}")
    print(f"Total Emissions: {result['total_emissions_kg']} kg CO2e")
    
    if result['calculation_enhanced']:
        print(f"LLM Emissions: {result['llm_emissions_kg']} kg CO2e")
        print(f"Traditional Emissions: {result['traditional_emissions_kg']} kg CO2e")
        
        session_report = result['session_report']
        print(f"Enhanced Analysis Available: Yes")
        print(f"Efficiency Score: {session_report.get('carbon_efficiency_score', 'N/A')}/100")
        print(f"Total Requests Tracked: {session_report.get('total_requests', 0)}")
    else:
        print(f"Enhanced Analysis Available: No (using fallback)")
    
    print(f"\n💡 Optimization Recommendations:")
    for i, rec in enumerate(result['optimization_recommendations'], 1):
        print(f"   {i}. {rec}")
    
    # Display offset suggestions
    offset_suggestions = result['offset_suggestions']
    if isinstance(offset_suggestions, dict):
        print(f"\n🌳 Carbon Offset Suggestions:")
        print(f"   Trees to Plant: {offset_suggestions.get('trees_to_plant', 'N/A')}")
        if 'cost_estimate_usd' in offset_suggestions:
            print(f"   Estimated Cost: ${offset_suggestions['cost_estimate_usd']}")
    else:
        print(f"\n🌳 Offset Suggestion: {offset_suggestions}")
    
    return result

def demonstrate_model_comparison():
    """Compare carbon footprint of different models"""
    
    print("\n" + "=" * 60)
    print("⚖️  Model Carbon Footprint Comparison")
    print("=" * 60)
    
    calculator = LLMCarbonCalculator()
    
    # Standard task: 1000 input tokens, 500 output tokens
    task_tokens = {"input": 1000, "output": 500}
    models_to_compare = ["gpt-4o", "gpt-4", "gpt-3.5-turbo", "phi-3-mini", "phi-3-vision", "gemma-2b"]
    
    print(f"\nTask: {task_tokens['input']} input + {task_tokens['output']} output tokens")
    print(f"{'Model':<15} | {'CO2 (gCO2e)':<12} | {'Relative':<10} | {'Cost vs Smallest'}")
    print("-" * 60)
    
    emissions_data = []
    for model in models_to_compare:
        emissions = calculator.calculate_request_emissions(
            model, task_tokens["input"], task_tokens["output"], "text"
        )
        emissions_data.append((model, emissions["total_gco2"]))
    
    # Sort by emissions
    emissions_data.sort(key=lambda x: x[1])
    smallest_emission = emissions_data[0][1]
    
    for model, emission in emissions_data:
        relative_cost = emission / smallest_emission
        print(f"{model:<15} | {emission:8.4f}    | {relative_cost:6.1f}x    | {'🟢' if relative_cost < 2 else '🟡' if relative_cost < 10 else '🔴'}")
    
    print(f"\n📊 Key Insights:")
    best_model = emissions_data[0][0]
    worst_model = emissions_data[-1][0]
    improvement_factor = emissions_data[-1][1] / emissions_data[0][1]
    
    print(f"   • Most efficient: {best_model}")
    print(f"   • Least efficient: {worst_model}")
    print(f"   • Switching from {worst_model} to {best_model} reduces emissions by {improvement_factor:.0f}x")
    print(f"   • Local models (phi-3, gemma) are typically 100-1000x more carbon efficient")

def export_carbon_report_demo():
    """Demonstrate exporting a comprehensive carbon report"""
    
    print("\n" + "=" * 60)
    print("📊 Carbon Report Export Demo")
    print("=" * 60)
    
    calculator = LLMCarbonCalculator()
    
    # Add sample usage data
    models_and_usage = [
        ("gpt-4o", 1500, 800, 3.0, "vision"),
        ("gpt-4", 1000, 600, 2.5, "text"), 
        ("gpt-3.5-turbo", 800, 400, 1.5, "text"),
        ("phi-3-mini", 500, 300, 0.8, "text"),
        ("phi-3-vision", 700, 350, 1.2, "vision")
    ]
    
    for model, input_tokens, output_tokens, duration, operation in models_and_usage:
        calculator.log_llm_usage(model, input_tokens, output_tokens, duration, operation)
    
    # Export report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"carbon_report_{timestamp}.json"
    
    print(f"\n📄 Generating comprehensive carbon report...")
    report_json = calculator.export_carbon_report(report_file)
    
    print(f"✅ Report exported to: {report_file}")
    
    # Show summary from the report
    report_data = json.loads(report_json)
    session_summary = report_data["session_summary"]
    
    print(f"\n📋 Report Summary:")
    print(f"   Total Emissions: {session_summary['total_gco2']} gCO2e")
    print(f"   Total Requests: {session_summary['total_requests']}")
    print(f"   Efficiency Score: {session_summary['carbon_efficiency_score']}/100")
    print(f"   Report Timestamp: {report_data['report_timestamp']}")
    
    return report_file

def main():
    """Run all carbon calculation demos"""
    
    print("🚀 Starting LLM Carbon Calculator Demo Suite")
    print("=" * 60)
    
    try:
        # Demo 1: Basic LLM usage session
        calculator, session_report = simulate_llm_usage_session()
        
        # Demo 2: Enhanced CarbonAgent integration
        agent_result = test_enhanced_carbon_agent()
        
        # Demo 3: Model comparison
        demonstrate_model_comparison()
        
        # Demo 4: Export comprehensive report
        report_file = export_carbon_report_demo()
        
        print(f"\n🎉 Demo Complete!")
        print("=" * 60)
        print(f"✅ All carbon calculation features demonstrated")
        print(f"📊 Carbon report saved as: {report_file}")
        print(f"🌱 Total session emissions: {session_report['total_gco2']} gCO2e")
        print(f"💡 Recommendations: Use smaller models for dev, cache results, batch operations")
        
        # Cleanup recommendations
        print(f"\n🔧 Next Steps:")
        print(f"   1. Integrate carbon logging into your LLM workflows")
        print(f"   2. Set carbon budgets for different operations") 
        print(f"   3. Use local models for development and testing")
        print(f"   4. Monitor and optimize based on carbon reports")
        
    except Exception as e:
        print(f"❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
