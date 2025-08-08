#!/usr/bin/env python3
"""
Accuracy Validator with Carbon Tracking Integration
Shows how to add carbon awareness to your existing LLM workflows
"""

import os
import sys
import time
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.carbon.llm_carbon_calculator import LLMCarbonCalculator
from src.agents.skadoosh_agents import AccuracyValidatorAgent, CarbonAgent, AgentContext

class CarbonAwareAccuracyValidator:
    """Accuracy validator with integrated carbon tracking"""
    
    def __init__(self):
        self.accuracy_validator = AccuracyValidatorAgent()
        self.carbon_calculator = LLMCarbonCalculator()
        self.carbon_agent = CarbonAgent()
        
        print("🌍 Carbon-Aware Accuracy Validator Initialized")
        print(f"   Carbon Calculator: {'✅ Enhanced' if self.carbon_agent.carbon_calculator else '⚠️  Basic'}")
    
    def validate_with_carbon_tracking(self, expected_image_path: str, actual_image_path: str, 
                                    use_llm: bool = True, llm_model: str = "gpt-4o") -> dict:
        """Run accuracy validation with carbon footprint tracking"""
        
        print(f"\n🔍 Starting Carbon-Aware Validation")
        print(f"   Expected: {os.path.basename(expected_image_path)}")
        print(f"   Actual: {os.path.basename(actual_image_path)}")
        print(f"   LLM Mode: {'Enabled' if use_llm else 'Disabled'}")
        if use_llm:
            print(f"   Model: {llm_model}")
        
        # Create context for tracking
        context = AgentContext(
            project_name="Carbon-Aware Validation",
            framework="Image Accuracy Testing"
        )
        
        # Track carbon usage during validation
        start_time = time.time()
        carbon_start = self.carbon_calculator.calculate_session_emissions()
        
        # Run accuracy validation
        validation_data = {
            "expected_image": expected_image_path,
            "actual_image": actual_image_path,
            "use_llm_enhancement": use_llm,
            "llm_model": llm_model if use_llm else None
        }
        
        try:
            # Execute accuracy validation
            accuracy_result = self.accuracy_validator.execute(context, validation_data)
            validation_success = True
            
            # If LLM was used, log the usage for carbon tracking
            if use_llm and validation_success:
                # Estimate token usage based on operation
                # These are estimates - in real integration you'd get actual tokens from the LLM API
                estimated_input_tokens = 1200  # Base prompt + image description
                estimated_output_tokens = 600   # Analysis response
                processing_time = time.time() - start_time
                
                # Log LLM usage
                usage_id = self.carbon_calculator.log_llm_usage(
                    llm_model,
                    estimated_input_tokens,
                    estimated_output_tokens, 
                    processing_time,
                    "vision"
                )
                
                print(f"   📊 LLM Usage Logged: {usage_id}")
                
                # Add to context for carbon agent
                context.execution_trace.append({
                    "agent": "AccuracyValidatorAgent",
                    "model": llm_model,
                    "tokens": {
                        "input": estimated_input_tokens,
                        "output": estimated_output_tokens
                    },
                    "operation_type": "vision",
                    "duration": processing_time,
                    "timestamp": datetime.now().isoformat()
                })
            
        except Exception as e:
            print(f"   ❌ Validation failed: {e}")
            accuracy_result = {"error": str(e), "validation_passed": False}
            validation_success = False
        
        # Calculate carbon footprint
        carbon_end = self.carbon_calculator.calculate_session_emissions()
        carbon_result = self.carbon_agent.execute(context, {"analysis_type": "validation"})
        
        # Combine results
        total_time = time.time() - start_time
        
        combined_result = {
            "validation_results": accuracy_result,
            "carbon_analysis": {
                "session_emissions_gco2": carbon_end["total_gco2"] - carbon_start["total_gco2"],
                "total_emissions_kg": carbon_result["total_emissions_kg"],
                "llm_emissions_kg": carbon_result.get("llm_emissions_kg", 0),
                "carbon_efficiency_score": carbon_result.get("green_score", 0),
                "optimization_recommendations": carbon_result["optimization_recommendations"]
            },
            "performance_metrics": {
                "total_processing_time": round(total_time, 2),
                "validation_success": validation_success,
                "llm_used": use_llm,
                "model_used": llm_model if use_llm else "cv_only"
            },
            "sustainability_summary": self._generate_sustainability_summary(
                carbon_result, use_llm, llm_model, total_time
            )
        }
        
        return combined_result
    
    def _generate_sustainability_summary(self, carbon_result: dict, used_llm: bool, 
                                       model: str, processing_time: float) -> dict:
        """Generate sustainability insights for the validation"""
        
        total_emissions = carbon_result["total_emissions_kg"]
        
        # Sustainability rating
        if total_emissions < 0.001:
            rating = "🟢 Excellent"
            impact = "Very low carbon footprint"
        elif total_emissions < 0.01:
            rating = "🟡 Good"  
            impact = "Moderate carbon footprint"
        else:
            rating = "🔴 High"
            impact = "Consider optimization"
        
        # Efficiency suggestions
        suggestions = []
        if used_llm and "gpt-4" in model:
            suggestions.append("Consider gpt-3.5-turbo for simpler validations")
        if processing_time > 5:
            suggestions.append("Optimize image preprocessing for faster validation")
        if total_emissions > 0.01:
            suggestions.append("Use local models for development testing")
        
        return {
            "sustainability_rating": rating,
            "environmental_impact": impact,
            "carbon_cost_per_validation": f"{total_emissions:.6f} kg CO2e",
            "efficiency_suggestions": suggestions,
            "carbon_offset_needed": {
                "trees": max(1, round(total_emissions * 50)),
                "cost_usd": round(total_emissions * 0.02, 6)
            }
        }
    
    def run_carbon_comparison_test(self):
        """Compare carbon footprint of different validation approaches"""
        
        print(f"\n🔬 Carbon Footprint Comparison Test")
        print("=" * 50)
        
        # Test with sample images (using test images if they exist)
        test_images_dir = "test_images"
        if os.path.exists(test_images_dir):
            test_files = [f for f in os.listdir(test_images_dir) if f.endswith(('.png', '.jpg', '.jpeg'))]
            if len(test_files) >= 1:
                expected_image = os.path.join(test_images_dir, test_files[0])
                actual_image = expected_image  # Using same image for demo
            else:
                print("⚠️  No test images found, creating mock validation")
                return self._mock_carbon_comparison()
        else:
            print("⚠️  Test images directory not found, creating mock validation")
            return self._mock_carbon_comparison()
        
        # Test different approaches
        approaches = [
            {"name": "Traditional CV Only", "use_llm": False, "model": None},
            {"name": "GPT-4o Vision", "use_llm": True, "model": "gpt-4o"},
            {"name": "GPT-3.5 Turbo", "use_llm": True, "model": "gpt-3.5-turbo"},
        ]
        
        results = []
        
        for approach in approaches:
            print(f"\n🧪 Testing: {approach['name']}")
            
            try:
                result = self.validate_with_carbon_tracking(
                    expected_image,
                    actual_image,
                    approach["use_llm"],
                    approach.get("model", "gpt-4o")
                )
                
                results.append({
                    "approach": approach["name"],
                    "carbon_kg": result["carbon_analysis"]["total_emissions_kg"],
                    "time_seconds": result["performance_metrics"]["total_processing_time"],
                    "success": result["performance_metrics"]["validation_success"],
                    "rating": result["sustainability_summary"]["sustainability_rating"]
                })
                
                print(f"   ✅ Completed: {result['sustainability_summary']['sustainability_rating']}")
                print(f"   📊 Emissions: {result['carbon_analysis']['total_emissions_kg']:.6f} kg CO2e")
                print(f"   ⏱️  Time: {result['performance_metrics']['total_processing_time']:.2f}s")
                
            except Exception as e:
                print(f"   ❌ Failed: {e}")
                results.append({
                    "approach": approach["name"],
                    "carbon_kg": 0,
                    "time_seconds": 0,
                    "success": False,
                    "rating": "❌ Failed"
                })
        
        # Display comparison
        print(f"\n📊 Carbon Footprint Comparison Results")
        print("-" * 60)
        print(f"{'Approach':<20} | {'Carbon (kg CO2e)':<15} | {'Time (s)':<10} | {'Rating'}")
        print("-" * 60)
        
        for result in results:
            if result["success"]:
                print(f"{result['approach']:<20} | {result['carbon_kg']:<15.6f} | {result['time_seconds']:<10.2f} | {result['rating']}")
            else:
                print(f"{result['approach']:<20} | {'Failed':<15} | {'N/A':<10} | {result['rating']}")
        
        return results
    
    def _mock_carbon_comparison(self):
        """Generate mock carbon comparison when no test images available"""
        
        print("🎭 Generating mock carbon comparison...")
        
        # Simulate different approaches with estimated values
        mock_results = [
            {
                "approach": "Traditional CV Only",
                "carbon_kg": 0.000001,  # Very low - local processing
                "time_seconds": 0.5,
                "success": True,
                "rating": "🟢 Excellent"
            },
            {
                "approach": "GPT-4o Vision",
                "carbon_kg": 0.015,  # Higher - cloud API
                "time_seconds": 3.2,
                "success": True,
                "rating": "🔴 High"
            },
            {
                "approach": "GPT-3.5 Turbo",
                "carbon_kg": 0.002,  # Medium - smaller model
                "time_seconds": 1.8,
                "success": True,
                "rating": "🟡 Good"
            }
        ]
        
        print(f"\n📊 Mock Carbon Footprint Comparison")
        print("-" * 60)
        print(f"{'Approach':<20} | {'Carbon (kg CO2e)':<15} | {'Time (s)':<10} | {'Rating'}")
        print("-" * 60)
        
        for result in mock_results:
            print(f"{result['approach']:<20} | {result['carbon_kg']:<15.6f} | {result['time_seconds']:<10.1f} | {result['rating']}")
        
        print(f"\n💡 Key Insights from Mock Data:")
        print(f"   • Traditional CV is ~15,000x more carbon efficient")
        print(f"   • GPT-3.5 uses ~7.5x less carbon than GPT-4o")
        print(f"   • Local processing eliminates API carbon costs")
        
        return mock_results

def main():
    """Demo the carbon-aware accuracy validator"""
    
    print("🚀 Carbon-Aware Accuracy Validator Demo")
    print("=" * 50)
    
    try:
        # Initialize carbon-aware validator
        validator = CarbonAwareAccuracyValidator()
        
        # Run carbon comparison test
        comparison_results = validator.run_carbon_comparison_test()
        
        # Generate session report
        session_report = validator.carbon_calculator.calculate_session_emissions()
        
        print(f"\n🌍 Session Carbon Summary")
        print("=" * 30)
        print(f"Total Emissions: {session_report['total_gco2']} gCO2e")
        print(f"Total Requests: {session_report['total_requests']}")
        print(f"Efficiency Score: {session_report['carbon_efficiency_score']}/100")
        
        # Recommendations
        recommendations = validator.carbon_calculator.get_optimization_recommendations()
        print(f"\n💡 Carbon Optimization Recommendations:")
        for i, rec in enumerate(recommendations, 1):
            print(f"   {i}. {rec}")
        
        print(f"\n✅ Demo Complete!")
        print(f"   Use this pattern to add carbon awareness to any LLM workflow")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
