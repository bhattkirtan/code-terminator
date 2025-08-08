"""
CarbonAgent - Tracks estimated CO₂ per model/token run
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)

class CarbonAgent:
    def __init__(self):
        self.name = "CarbonAgent"
        self.version = "1.0.0"
        self.carbon_tracking = {}
        
        # Carbon intensity factors (gCO2/kWh) by region
        self.carbon_intensity = {
            "us-east-1": 385,      # Virginia
            "us-west-2": 285,      # Oregon
            "eu-west-1": 350,      # Ireland
            "ap-southeast-1": 420, # Singapore
            "global-average": 475
        }
        
        # Model energy consumption estimates (Wh per 1000 tokens)
        self.model_energy_consumption = {
            "gpt-3.5-turbo": 0.002,
            "gpt-4": 0.008,
            "claude-2": 0.005,
            "claude-instant": 0.002,
            "local-llm": 0.001,
            "image-analysis": 0.003,
            "code-generation": 0.004
        }
    
    async def calculate_footprint(self, session_id: str) -> float:
        """
        Calculate carbon footprint for a session
        """
        logger.info(f"Calculating carbon footprint for session {session_id}")
        
        if session_id not in self.carbon_tracking:
            await self._initialize_session_tracking(session_id)
        
        session_data = self.carbon_tracking[session_id]
        
        # Calculate total energy consumption
        total_energy_kwh = 0
        
        for operation in session_data["operations"]:
            energy_consumption = self._calculate_operation_energy(operation)
            total_energy_kwh += energy_consumption
            operation["energy_kwh"] = energy_consumption
        
        # Calculate CO2 emissions
        region = session_data.get("region", "global-average")
        carbon_intensity = self.carbon_intensity.get(region, self.carbon_intensity["global-average"])
        
        total_co2_g = total_energy_kwh * carbon_intensity
        total_co2_kg = total_co2_g / 1000
        
        # Update session tracking
        session_data.update({
            "total_energy_kwh": total_energy_kwh,
            "total_co2_g": total_co2_g,
            "total_co2_kg": total_co2_kg,
            "carbon_intensity_region": region,
            "calculation_timestamp": datetime.now().isoformat()
        })
        
        # Log carbon impact
        await self._log_carbon_impact(session_id, total_co2_kg)
        
        logger.info(f"Carbon footprint calculated: {total_co2_kg:.6f} kg CO2")
        return total_co2_kg
    
    async def track_operation(self, session_id: str, operation_type: str, model: str, tokens: int, duration_ms: int) -> None:
        """
        Track an individual operation for carbon calculation
        """
        if session_id not in self.carbon_tracking:
            await self._initialize_session_tracking(session_id)
        
        operation = {
            "type": operation_type,
            "model": model,
            "tokens": tokens,
            "duration_ms": duration_ms,
            "timestamp": datetime.now().isoformat()
        }
        
        self.carbon_tracking[session_id]["operations"].append(operation)
        
        logger.debug(f"Tracked operation: {operation_type} with {tokens} tokens using {model}")
    
    async def _initialize_session_tracking(self, session_id: str) -> None:
        """Initialize tracking for a new session"""
        self.carbon_tracking[session_id] = {
            "session_id": session_id,
            "start_time": datetime.now().isoformat(),
            "operations": [],
            "region": "global-average",  # Default region
            "total_energy_kwh": 0,
            "total_co2_kg": 0
        }
    
    def _calculate_operation_energy(self, operation: Dict[str, Any]) -> float:
        """Calculate energy consumption for a specific operation"""
        model = operation.get("model", "unknown")
        tokens = operation.get("tokens", 0)
        duration_ms = operation.get("duration_ms", 0)
        
        # Base energy consumption based on model and tokens
        base_energy_wh = self.model_energy_consumption.get(model, 0.003) * (tokens / 1000)
        
        # Add overhead for processing time (simplified model)
        processing_overhead = (duration_ms / 1000) * 0.001  # 1mWh per second
        
        # Convert to kWh
        total_energy_kwh = (base_energy_wh + processing_overhead) / 1000
        
        return total_energy_kwh
    
    async def _log_carbon_impact(self, session_id: str, co2_kg: float) -> None:
        """Log carbon impact with contextual information"""
        impact_context = self._get_carbon_context(co2_kg)
        
        logger.info(f"Session {session_id} carbon impact: {co2_kg:.6f} kg CO2 ({impact_context})")
        
        # Store in persistent log (in production, this would go to a database)
        log_entry = {
            "session_id": session_id,
            "timestamp": datetime.now().isoformat(),
            "co2_kg": co2_kg,
            "context": impact_context,
            "operations_count": len(self.carbon_tracking[session_id]["operations"])
        }
        
        # In a real implementation, save to database or file
        await self._save_carbon_log(log_entry)
    
    def _get_carbon_context(self, co2_kg: float) -> str:
        """Provide context for carbon footprint amount"""
        # Convert to grams for better readability of small amounts
        co2_g = co2_kg * 1000
        
        if co2_g < 1:
            return f"{co2_g:.3f}g - equivalent to charging a smartphone for ~{co2_g * 100:.1f} minutes"
        elif co2_g < 10:
            return f"{co2_g:.2f}g - equivalent to a few minutes of LED light usage"
        elif co2_g < 100:
            return f"{co2_g:.1f}g - equivalent to ~{co2_g / 20:.1f} minutes of laptop usage"
        elif co2_kg < 1:
            return f"{co2_g:.0f}g - equivalent to ~{co2_kg * 1000 / 500:.1f} hours of smartphone usage"
        else:
            return f"{co2_kg:.3f}kg - equivalent to driving ~{co2_kg * 4:.1f}km in an average car"
    
    async def _save_carbon_log(self, log_entry: Dict[str, Any]) -> None:
        """Save carbon log entry (placeholder for database storage)"""
        # In production, this would save to a database
        # For now, we'll just log it
        logger.info(f"Carbon log saved: {json.dumps(log_entry, indent=2)}")
    
    async def get_session_report(self, session_id: str) -> Dict[str, Any]:
        """Get detailed carbon report for a session"""
        if session_id not in self.carbon_tracking:
            return {"error": "Session not found"}
        
        session_data = self.carbon_tracking[session_id]
        
        # Calculate operation breakdown
        operation_breakdown = {}
        for operation in session_data["operations"]:
            op_type = operation["type"]
            if op_type not in operation_breakdown:
                operation_breakdown[op_type] = {
                    "count": 0,
                    "total_tokens": 0,
                    "total_energy_kwh": 0,
                    "models_used": set()
                }
            
            operation_breakdown[op_type]["count"] += 1
            operation_breakdown[op_type]["total_tokens"] += operation.get("tokens", 0)
            operation_breakdown[op_type]["total_energy_kwh"] += operation.get("energy_kwh", 0)
            operation_breakdown[op_type]["models_used"].add(operation.get("model", "unknown"))
        
        # Convert sets to lists for JSON serialization
        for op_type in operation_breakdown:
            operation_breakdown[op_type]["models_used"] = list(operation_breakdown[op_type]["models_used"])
        
        report = {
            "session_id": session_id,
            "summary": {
                "total_operations": len(session_data["operations"]),
                "total_tokens": sum(op.get("tokens", 0) for op in session_data["operations"]),
                "total_energy_kwh": session_data.get("total_energy_kwh", 0),
                "total_co2_kg": session_data.get("total_co2_kg", 0),
                "carbon_intensity_region": session_data.get("carbon_intensity_region", "unknown")
            },
            "operation_breakdown": operation_breakdown,
            "recommendations": self._generate_carbon_recommendations(session_data),
            "comparison": self._generate_carbon_comparison(session_data.get("total_co2_kg", 0))
        }
        
        return report
    
    def _generate_carbon_recommendations(self, session_data: Dict[str, Any]) -> List[str]:
        """Generate recommendations to reduce carbon footprint"""
        recommendations = []
        operations = session_data.get("operations", [])
        
        if not operations:
            return recommendations
        
        # Analyze token usage
        total_tokens = sum(op.get("tokens", 0) for op in operations)
        avg_tokens_per_op = total_tokens / len(operations) if operations else 0
        
        if avg_tokens_per_op > 2000:
            recommendations.append("Consider breaking down large requests into smaller chunks to reduce token usage")
        
        # Analyze model usage
        models_used = [op.get("model") for op in operations]
        high_energy_models = ["gpt-4", "code-generation"]
        
        if any(model in high_energy_models for model in models_used):
            recommendations.append("Consider using more efficient models like gpt-3.5-turbo for simpler tasks")
        
        # Check for redundant operations
        operation_types = [op.get("type") for op in operations]
        if len(set(operation_types)) < len(operation_types) / 2:
            recommendations.append("Consider caching results to avoid redundant AI operations")
        
        # Region optimization
        region = session_data.get("region", "global-average")
        if region in ["us-east-1", "ap-southeast-1"]:
            recommendations.append("Consider using cloud regions with lower carbon intensity (e.g., us-west-2)")
        
        if not recommendations:
            recommendations.append("Great job! Your carbon footprint is already optimized")
        
        return recommendations
    
    def _generate_carbon_comparison(self, co2_kg: float) -> Dict[str, Any]:
        """Generate comparisons to put carbon footprint in context"""
        comparisons = {
            "equivalent_activities": [],
            "environmental_impact": {},
            "offset_suggestions": []
        }
        
        # Equivalent activities
        if co2_kg > 0:
            driving_km = co2_kg * 4  # Approximate km of driving
            smartphone_hours = co2_kg * 1000 / 0.5  # Hours of smartphone usage
            led_hours = co2_kg * 1000 / 0.1  # Hours of LED light usage
            
            comparisons["equivalent_activities"] = [
                f"Driving {driving_km:.2f} km in an average car",
                f"Using a smartphone for {smartphone_hours:.1f} hours",
                f"Running an LED bulb for {led_hours:.0f} hours"
            ]
            
            # Environmental impact
            trees_needed = co2_kg / 21  # Trees needed to offset (21kg CO2 per tree per year)
            comparisons["environmental_impact"] = {
                "trees_for_offset_per_year": trees_needed,
                "percentage_of_daily_personal_budget": (co2_kg / 16.4) * 100  # Global average daily CO2 budget
            }
            
            # Offset suggestions
            if co2_kg < 0.001:
                comparisons["offset_suggestions"] = ["Minimal impact - no offset needed"]
            elif co2_kg < 0.01:
                comparisons["offset_suggestions"] = ["Plant a small herb garden", "Use public transport for one trip"]
            elif co2_kg < 0.1:
                comparisons["offset_suggestions"] = ["Plant a tree sapling", "Bike instead of drive for one day"]
            else:
                comparisons["offset_suggestions"] = ["Support renewable energy projects", "Plant multiple trees", "Invest in carbon offset programs"]
        
        return comparisons
    
    async def get_aggregate_statistics(self, days: int = 30) -> Dict[str, Any]:
        """Get aggregate carbon statistics"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Filter sessions within the time period
        recent_sessions = {}
        for session_id, data in self.carbon_tracking.items():
            session_start = datetime.fromisoformat(data["start_time"])
            if session_start >= cutoff_date:
                recent_sessions[session_id] = data
        
        if not recent_sessions:
            return {
                "period_days": days,
                "total_sessions": 0,
                "total_co2_kg": 0,
                "message": "No sessions found in the specified period"
            }
        
        # Calculate aggregates
        total_co2 = sum(session.get("total_co2_kg", 0) for session in recent_sessions.values())
        total_operations = sum(len(session.get("operations", [])) for session in recent_sessions.values())
        total_tokens = sum(
            sum(op.get("tokens", 0) for op in session.get("operations", []))
            for session in recent_sessions.values()
        )
        
        # Model usage statistics
        model_usage = {}
        for session in recent_sessions.values():
            for operation in session.get("operations", []):
                model = operation.get("model", "unknown")
                if model not in model_usage:
                    model_usage[model] = {"count": 0, "tokens": 0, "co2_kg": 0}
                model_usage[model]["count"] += 1
                model_usage[model]["tokens"] += operation.get("tokens", 0)
                model_usage[model]["co2_kg"] += operation.get("energy_kwh", 0) * self.carbon_intensity["global-average"] / 1000
        
        statistics = {
            "period_days": days,
            "total_sessions": len(recent_sessions),
            "total_operations": total_operations,
            "total_tokens": total_tokens,
            "total_co2_kg": total_co2,
            "average_co2_per_session": total_co2 / len(recent_sessions) if recent_sessions else 0,
            "average_tokens_per_operation": total_tokens / total_operations if total_operations else 0,
            "model_usage_breakdown": model_usage,
            "environmental_context": self._generate_carbon_comparison(total_co2),
            "carbon_efficiency_trends": self._analyze_efficiency_trends(recent_sessions)
        }
        
        return statistics
    
    def _analyze_efficiency_trends(self, sessions: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze carbon efficiency trends over time"""
        if len(sessions) < 2:
            return {"message": "Not enough data for trend analysis"}
        
        # Sort sessions by start time
        sorted_sessions = sorted(
            sessions.values(),
            key=lambda x: datetime.fromisoformat(x["start_time"])
        )
        
        # Calculate efficiency metrics over time
        efficiency_metrics = []
        for session in sorted_sessions:
            operations = session.get("operations", [])
            if operations:
                total_tokens = sum(op.get("tokens", 0) for op in operations)
                total_co2 = session.get("total_co2_kg", 0)
                efficiency = total_tokens / (total_co2 * 1000) if total_co2 > 0 else 0  # tokens per gram CO2
                
                efficiency_metrics.append({
                    "timestamp": session["start_time"],
                    "tokens_per_gram_co2": efficiency,
                    "total_tokens": total_tokens,
                    "total_co2_kg": total_co2
                })
        
        # Calculate trend
        if len(efficiency_metrics) >= 2:
            first_efficiency = efficiency_metrics[0]["tokens_per_gram_co2"]
            last_efficiency = efficiency_metrics[-1]["tokens_per_gram_co2"]
            
            if first_efficiency > 0:
                trend_percentage = ((last_efficiency - first_efficiency) / first_efficiency) * 100
                trend_direction = "improving" if trend_percentage > 5 else "declining" if trend_percentage < -5 else "stable"
            else:
                trend_direction = "unknown"
                trend_percentage = 0
        else:
            trend_direction = "unknown"
            trend_percentage = 0
        
        return {
            "trend_direction": trend_direction,
            "trend_percentage": trend_percentage,
            "efficiency_over_time": efficiency_metrics,
            "recommendations": self._get_efficiency_recommendations(trend_direction, trend_percentage)
        }
    
    def _get_efficiency_recommendations(self, trend_direction: str, trend_percentage: float) -> List[str]:
        """Get recommendations based on efficiency trends"""
        recommendations = []
        
        if trend_direction == "declining":
            recommendations.extend([
                "Consider optimizing prompts to reduce token usage",
                "Review model selection - use lighter models for simple tasks",
                "Implement caching to avoid redundant operations"
            ])
        elif trend_direction == "stable":
            recommendations.extend([
                "Look for opportunities to improve carbon efficiency",
                "Consider batch processing for multiple similar requests"
            ])
        elif trend_direction == "improving":
            recommendations.extend([
                "Great progress on carbon efficiency!",
                "Continue current optimization practices",
                "Share efficiency improvements with the team"
            ])
        
        return recommendations
    
    async def set_region(self, session_id: str, region: str) -> None:
        """Set the compute region for carbon intensity calculation"""
        if session_id in self.carbon_tracking:
            if region in self.carbon_intensity:
                self.carbon_tracking[session_id]["region"] = region
                logger.info(f"Set region for session {session_id} to {region}")
            else:
                logger.warning(f"Unknown region {region}, using global average")
                self.carbon_tracking[session_id]["region"] = "global-average"
        else:
            logger.warning(f"Session {session_id} not found")
    
    async def export_carbon_data(self, session_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        """Export carbon tracking data for analysis"""
        if session_ids:
            export_data = {sid: self.carbon_tracking.get(sid) for sid in session_ids if sid in self.carbon_tracking}
        else:
            export_data = self.carbon_tracking.copy()
        
        # Add metadata
        export_metadata = {
            "export_timestamp": datetime.now().isoformat(),
            "total_sessions": len(export_data),
            "carbon_intensity_factors": self.carbon_intensity,
            "model_energy_consumption": self.model_energy_consumption,
            "agent_version": self.version
        }
        
        return {
            "metadata": export_metadata,
            "sessions": export_data
        }
    
    async def clear_old_sessions(self, days: int = 90) -> int:
        """Clear old session data to manage memory"""
        cutoff_date = datetime.now() - timedelta(days=days)
        sessions_to_remove = []
        
        for session_id, data in self.carbon_tracking.items():
            session_start = datetime.fromisoformat(data["start_time"])
            if session_start < cutoff_date:
                sessions_to_remove.append(session_id)
        
        for session_id in sessions_to_remove:
            del self.carbon_tracking[session_id]
        
        logger.info(f"Cleared {len(sessions_to_remove)} old sessions (older than {days} days)")
        return len(sessions_to_remove)
    
    async def get_status(self) -> Dict[str, Any]:
        """Get agent status"""
        active_sessions = len(self.carbon_tracking)
        total_operations = sum(len(session.get("operations", [])) for session in self.carbon_tracking.values())
        total_co2 = sum(session.get("total_co2_kg", 0) for session in self.carbon_tracking.values())
        
        return {
            "name": self.name,
            "version": self.version,
            "status": "active",
            "active_sessions": active_sessions,
            "total_operations_tracked": total_operations,
            "total_co2_tracked_kg": total_co2,
            "supported_regions": list(self.carbon_intensity.keys()),
            "supported_models": list(self.model_energy_consumption.keys()),
            "capabilities": [
                "Carbon footprint calculation",
                "Operation-level energy tracking",
                "Multi-region carbon intensity",
                "Model-specific energy consumption",
                "Environmental impact reporting",
                "Carbon optimization recommendations",
                "Trend analysis and efficiency tracking",
                "Data export and reporting"
            ]
        }