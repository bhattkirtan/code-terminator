#!/usr/bin/env python3
"""
LLM Carbon Footprint Calculator
Calculates CO2 emissions for different LLM models and operations
"""

import json
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class LLMUsage:
    """Track LLM usage for carbon calculation"""
    model: str
    input_tokens: int
    output_tokens: int
    processing_time: float
    timestamp: datetime
    operation_type: str  # "vision", "text", "embedding"

class LLMCarbonCalculator:
    """Calculate carbon emissions for LLM usage"""
    
    def __init__(self):
        # Carbon intensity data (gCO2e per 1000 tokens)
        # Based on research from Strubell et al. and recent studies
        self.carbon_factors = {
            # OpenAI Models
            "gpt-4o": {
                "input_tokens_gco2_per_1k": 0.03,
                "output_tokens_gco2_per_1k": 0.06,
                "vision_processing_gco2": 0.15,  # Per image
                "base_request_gco2": 0.01
            },
            "gpt-4": {
                "input_tokens_gco2_per_1k": 0.025,
                "output_tokens_gco2_per_1k": 0.05,
                "vision_processing_gco2": 0.12,
                "base_request_gco2": 0.008
            },
            "gpt-3.5-turbo": {
                "input_tokens_gco2_per_1k": 0.002,
                "output_tokens_gco2_per_1k": 0.004,
                "vision_processing_gco2": 0.05,
                "base_request_gco2": 0.001
            },
            # Local Models (lower emissions)
            "phi-3-mini": {
                "input_tokens_gco2_per_1k": 0.0001,
                "output_tokens_gco2_per_1k": 0.0002,
                "vision_processing_gco2": 0.001,
                "base_request_gco2": 0.0001
            },
            "phi-3-vision": {
                "input_tokens_gco2_per_1k": 0.0005,
                "output_tokens_gco2_per_1k": 0.001,
                "vision_processing_gco2": 0.005,
                "base_request_gco2": 0.0002
            },
            "gemma-2b": {
                "input_tokens_gco2_per_1k": 0.0002,
                "output_tokens_gco2_per_1k": 0.0004,
                "vision_processing_gco2": 0.002,
                "base_request_gco2": 0.0001
            }
        }
        
        # Regional carbon intensity (gCO2/kWh)
        self.regional_factors = {
            "us-east": 0.4,      # Virginia (AWS us-east-1)
            "us-west": 0.3,      # California (cleaner grid)
            "europe": 0.2,       # EU average
            "global": 0.35       # Global average
        }
        
        # Usage tracking
        self.usage_log: List[LLMUsage] = []
    
    def log_llm_usage(self, model: str, input_tokens: int, output_tokens: int, 
                     processing_time: float, operation_type: str = "text") -> str:
        """Log LLM usage for carbon tracking"""
        
        usage = LLMUsage(
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            processing_time=processing_time,
            timestamp=datetime.now(),
            operation_type=operation_type
        )
        
        self.usage_log.append(usage)
        
        # Return usage ID for reference
        return f"usage_{len(self.usage_log)}"
    
    def calculate_request_emissions(self, model: str, input_tokens: int, 
                                  output_tokens: int, operation_type: str = "text",
                                  region: str = "global") -> Dict[str, Any]:
        """Calculate emissions for a single LLM request"""
        
        if model not in self.carbon_factors:
            print(f"⚠️  Unknown model {model}, using default values")
            model = "gpt-3.5-turbo"  # Default fallback
        
        factors = self.carbon_factors[model]
        regional_multiplier = self.regional_factors.get(region, 0.35)
        
        # Base emissions calculation
        input_emissions = (input_tokens / 1000) * factors["input_tokens_gco2_per_1k"]
        output_emissions = (output_tokens / 1000) * factors["output_tokens_gco2_per_1k"]
        base_emissions = factors["base_request_gco2"]
        
        # Additional emissions for vision tasks
        vision_emissions = 0
        if operation_type == "vision":
            vision_emissions = factors["vision_processing_gco2"]
        
        # Total emissions in gCO2e
        total_gco2 = (input_emissions + output_emissions + base_emissions + vision_emissions) * regional_multiplier
        
        return {
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "operation_type": operation_type,
            "emissions_breakdown": {
                "input_tokens_gco2": round(input_emissions * regional_multiplier, 6),
                "output_tokens_gco2": round(output_emissions * regional_multiplier, 6),
                "base_request_gco2": round(base_emissions * regional_multiplier, 6),
                "vision_processing_gco2": round(vision_emissions * regional_multiplier, 6),
                "regional_multiplier": regional_multiplier
            },
            "total_gco2": round(total_gco2, 6),
            "total_kg_co2": round(total_gco2 / 1000, 9),
            "region": region
        }
    
    def calculate_session_emissions(self, region: str = "global") -> Dict[str, Any]:
        """Calculate total emissions for the current session"""
        
        if not self.usage_log:
            return {
                "total_requests": 0,
                "total_gco2": 0,
                "total_kg_co2": 0,
                "session_breakdown": {}
            }
        
        total_emissions = 0
        model_breakdown = {}
        operation_breakdown = {}
        
        for usage in self.usage_log:
            # Calculate emissions for this usage
            emissions = self.calculate_request_emissions(
                usage.model, 
                usage.input_tokens, 
                usage.output_tokens,
                usage.operation_type,
                region
            )
            
            total_emissions += emissions["total_gco2"]
            
            # Track by model
            if usage.model not in model_breakdown:
                model_breakdown[usage.model] = {
                    "requests": 0,
                    "total_tokens": 0,
                    "total_gco2": 0
                }
            
            model_breakdown[usage.model]["requests"] += 1
            model_breakdown[usage.model]["total_tokens"] += usage.input_tokens + usage.output_tokens
            model_breakdown[usage.model]["total_gco2"] += emissions["total_gco2"]
            
            # Track by operation type
            if usage.operation_type not in operation_breakdown:
                operation_breakdown[usage.operation_type] = {
                    "requests": 0,
                    "total_gco2": 0
                }
            
            operation_breakdown[usage.operation_type]["requests"] += 1
            operation_breakdown[usage.operation_type]["total_gco2"] += emissions["total_gco2"]
        
        return {
            "total_requests": len(self.usage_log),
            "total_gco2": round(total_emissions, 6),
            "total_kg_co2": round(total_emissions / 1000, 9),
            "session_duration_minutes": self._get_session_duration(),
            "model_breakdown": model_breakdown,
            "operation_breakdown": operation_breakdown,
            "region": region,
            "carbon_efficiency_score": self._calculate_efficiency_score()
        }
    
    def get_optimization_recommendations(self) -> List[str]:
        """Generate carbon optimization recommendations"""
        
        recommendations = []
        
        if not self.usage_log:
            return ["Start using LLMs to get carbon optimization recommendations"]
        
        # Analyze usage patterns
        total_emissions = sum(self.calculate_request_emissions(
            u.model, u.input_tokens, u.output_tokens, u.operation_type
        )["total_gco2"] for u in self.usage_log)
        
        model_usage = {}
        for usage in self.usage_log:
            model_usage[usage.model] = model_usage.get(usage.model, 0) + 1
        
        # Model optimization recommendations
        if any("gpt-4" in model for model in model_usage.keys()):
            recommendations.append("🔄 Consider using gpt-3.5-turbo for simpler tasks to reduce emissions by ~90%")
        
        if total_emissions > 1.0:  # More than 1g CO2
            recommendations.append("🌱 High emissions detected - consider local models for development")
        
        # Token optimization
        avg_tokens = sum(u.input_tokens + u.output_tokens for u in self.usage_log) / len(self.usage_log)
        if avg_tokens > 2000:
            recommendations.append("📝 Optimize prompts to reduce token usage and emissions")
        
        # Caching recommendations
        if len(self.usage_log) > 5:
            recommendations.append("💾 Implement response caching to avoid duplicate LLM calls")
        
        # Regional recommendations
        recommendations.append("🌍 Use EU or US-West regions for lower carbon intensity")
        
        return recommendations
    
    def get_carbon_offset_suggestions(self, total_kg_co2: float) -> Dict[str, Any]:
        """Suggest carbon offset options"""
        
        return {
            "trees_to_plant": max(1, round(total_kg_co2 * 50)),  # ~20g CO2 per tree per year
            "renewable_energy_kwh": round(total_kg_co2 * 2.5, 2),  # Offset via renewable energy
            "cost_estimate_usd": round(total_kg_co2 * 0.02, 4),  # ~$20 per ton CO2
            "equivalent_actions": [
                f"Walking {round(total_kg_co2 * 4, 1)} meters instead of driving",
                f"Using renewable energy for {round(total_kg_co2 * 2.5, 1)} kWh",
                f"Planting {max(1, round(total_kg_co2 * 50))} tree(s)"
            ]
        }
    
    def _get_session_duration(self) -> float:
        """Calculate session duration in minutes"""
        if len(self.usage_log) < 2:
            return 0
        
        start_time = min(u.timestamp for u in self.usage_log)
        end_time = max(u.timestamp for u in self.usage_log)
        
        return (end_time - start_time).total_seconds() / 60
    
    def _calculate_efficiency_score(self) -> int:
        """Calculate carbon efficiency score (0-100)"""
        if not self.usage_log:
            return 100
        
        # Score based on model choices and usage patterns
        score = 100
        
        # Penalize for using large models
        gpt4_usage = sum(1 for u in self.usage_log if "gpt-4" in u.model)
        if gpt4_usage > 0:
            score -= min(30, gpt4_usage * 10)
        
        # Reward for using smaller models
        local_usage = sum(1 for u in self.usage_log if u.model in ["phi-3-mini", "gemma-2b"])
        if local_usage > 0:
            score += min(20, local_usage * 5)
        
        return max(0, min(100, score))
    
    def export_carbon_report(self, filepath: str = None) -> str:
        """Export carbon footprint report as JSON"""
        
        report = {
            "report_timestamp": datetime.now().isoformat(),
            "session_summary": self.calculate_session_emissions(),
            "detailed_usage": [
                {
                    "timestamp": u.timestamp.isoformat(),
                    "model": u.model,
                    "input_tokens": u.input_tokens,
                    "output_tokens": u.output_tokens,
                    "operation_type": u.operation_type,
                    "processing_time": u.processing_time,
                    "emissions": self.calculate_request_emissions(
                        u.model, u.input_tokens, u.output_tokens, u.operation_type
                    )
                } for u in self.usage_log
            ],
            "optimization_recommendations": self.get_optimization_recommendations(),
            "offset_suggestions": self.get_carbon_offset_suggestions(
                self.calculate_session_emissions()["total_kg_co2"]
            )
        }
        
        if filepath:
            with open(filepath, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"📊 Carbon report exported to: {filepath}")
        
        return json.dumps(report, indent=2)

# Example usage
if __name__ == "__main__":
    # Demo carbon calculation
    calculator = LLMCarbonCalculator()
    
    # Log some sample LLM usage
    calculator.log_llm_usage("gpt-4o", 1500, 800, 2.5, "vision")
    calculator.log_llm_usage("gpt-3.5-turbo", 800, 400, 1.2, "text")
    calculator.log_llm_usage("phi-3-mini", 500, 300, 0.8, "text")
    
    # Calculate emissions
    session_report = calculator.calculate_session_emissions()
    
    print("🌍 LLM Carbon Footprint Analysis")
    print("=" * 40)
    print(f"Total Emissions: {session_report['total_gco2']} gCO2e")
    print(f"Total Emissions: {session_report['total_kg_co2']} kg CO2e")
    print(f"Efficiency Score: {session_report['carbon_efficiency_score']}/100")
    
    print("\n💡 Optimization Recommendations:")
    for rec in calculator.get_optimization_recommendations():
        print(f"   {rec}")
