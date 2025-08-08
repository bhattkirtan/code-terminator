#!/usr/bin/env python3
"""
Carbon Monitoring Dashboard
Real-time monitoring and optimization for LLM carbon footprints
"""

import os
import json
import time
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

try:
    from .llm_carbon_calculator import LLMCarbonCalculator
    CARBON_TRACKING_AVAILABLE = True
except ImportError:
    print("⚠️  LLM Carbon Calculator not available")
    CARBON_TRACKING_AVAILABLE = False

class CarbonDashboard:
    """Real-time carbon monitoring dashboard for LLM operations"""
    
    def __init__(self):
        self.calculator = LLMCarbonCalculator() if CARBON_TRACKING_AVAILABLE else None
        self.carbon_history = []
        self.alerts = []
        self.budgets = {
            "daily_kg": 0.1,
            "hourly_kg": 0.02,
            "per_operation_kg": 0.01,
            "model_limits": {
                "gpt-4o": 0.005,
                "gpt-4": 0.004,
                "gpt-3.5-turbo": 0.001
            }
        }
        self.current_session = {
            "start_time": datetime.now(),
            "operations": 0,
            "total_carbon_kg": 0.0,
            "models_used": set()
        }
        
    def log_operation(self, model: str, input_tokens: int, output_tokens: int, 
                     operation_type: str, processing_time: float) -> Dict[str, Any]:
        """Log an LLM operation and update dashboard metrics"""
        
        if not self.calculator:
            return {"error": "Carbon calculator not available"}
        
        # Log to calculator
        usage_id = self.calculator.log_llm_usage(
            model, input_tokens, output_tokens, processing_time, operation_type
        )
        
        # Calculate emissions
        emissions = self.calculator.calculate_request_emissions(
            model, input_tokens, output_tokens, operation_type
        )
        
        # Update session metrics
        self.current_session["operations"] += 1
        self.current_session["total_carbon_kg"] += emissions["total_kg_co2"]
        self.current_session["models_used"].add(model)
        
        # Add to history
        operation_record = {
            "timestamp": datetime.now().isoformat(),
            "usage_id": usage_id,
            "model": model,
            "tokens": {"input": input_tokens, "output": output_tokens},
            "operation_type": operation_type,
            "processing_time": processing_time,
            "emissions": emissions,
            "session_total_kg": self.current_session["total_carbon_kg"]
        }
        
        self.carbon_history.append(operation_record)
        
        # Check for budget alerts
        self._check_budget_alerts(operation_record)
        
        return operation_record
    
    def _check_budget_alerts(self, operation: Dict[str, Any]):
        """Check for budget violations and generate alerts"""
        
        emissions_kg = operation["emissions"]["total_kg_co2"]
        model = operation["model"]
        
        # Check per-operation limit
        if emissions_kg > self.budgets["per_operation_kg"]:
            self.alerts.append({
                "timestamp": datetime.now().isoformat(),
                "type": "per_operation_limit",
                "severity": "warning",
                "message": f"Operation exceeded per-operation limit: {emissions_kg:.6f} kg > {self.budgets['per_operation_kg']:.6f} kg",
                "model": model,
                "emissions": emissions_kg
            })
        
        # Check model-specific limits
        model_limit = self.budgets["model_limits"].get(model, self.budgets["model_limits"]["gpt-4o"])
        if emissions_kg > model_limit:
            self.alerts.append({
                "timestamp": datetime.now().isoformat(),
                "type": "model_limit",
                "severity": "warning",
                "message": f"Model {model} exceeded limit: {emissions_kg:.6f} kg > {model_limit:.6f} kg",
                "model": model,
                "emissions": emissions_kg
            })
        
        # Check session accumulation against daily budget
        if self.current_session["total_carbon_kg"] > self.budgets["daily_kg"]:
            self.alerts.append({
                "timestamp": datetime.now().isoformat(),
                "type": "daily_budget",
                "severity": "critical",
                "message": f"Daily budget exceeded: {self.current_session['total_carbon_kg']:.6f} kg > {self.budgets['daily_kg']:.6f} kg",
                "session_total": self.current_session["total_carbon_kg"]
            })
        
        # Check hourly rate
        session_duration_hours = (datetime.now() - self.current_session["start_time"]).total_seconds() / 3600
        if session_duration_hours > 0:
            hourly_rate = self.current_session["total_carbon_kg"] / session_duration_hours
            if hourly_rate > self.budgets["hourly_kg"]:
                self.alerts.append({
                    "timestamp": datetime.now().isoformat(),
                    "type": "hourly_rate",
                    "severity": "warning",
                    "message": f"Hourly carbon rate exceeded: {hourly_rate:.6f} kg/h > {self.budgets['hourly_kg']:.6f} kg/h",
                    "hourly_rate": hourly_rate
                })
    
    def get_real_time_status(self) -> Dict[str, Any]:
        """Get current dashboard status"""
        
        session_duration = datetime.now() - self.current_session["start_time"]
        duration_hours = session_duration.total_seconds() / 3600
        
        # Calculate rates
        operations_per_hour = self.current_session["operations"] / duration_hours if duration_hours > 0 else 0
        carbon_per_hour = self.current_session["total_carbon_kg"] / duration_hours if duration_hours > 0 else 0
        carbon_per_operation = self.current_session["total_carbon_kg"] / self.current_session["operations"] if self.current_session["operations"] > 0 else 0
        
        # Budget utilization
        daily_utilization = (self.current_session["total_carbon_kg"] / self.budgets["daily_kg"]) * 100
        hourly_utilization = (carbon_per_hour / self.budgets["hourly_kg"]) * 100 if carbon_per_hour > 0 else 0
        
        # Recent alerts
        recent_alerts = [a for a in self.alerts if 
                        (datetime.now() - datetime.fromisoformat(a["timestamp"])).total_seconds() < 3600]
        
        return {
            "session_info": {
                "start_time": self.current_session["start_time"].isoformat(),
                "duration_hours": round(duration_hours, 2),
                "total_operations": self.current_session["operations"],
                "models_used": list(self.current_session["models_used"]),
                "total_carbon_kg": self.current_session["total_carbon_kg"]
            },
            "rates": {
                "operations_per_hour": round(operations_per_hour, 1),
                "carbon_per_hour_kg": round(carbon_per_hour, 6),
                "carbon_per_operation_kg": round(carbon_per_operation, 6)
            },
            "budget_status": {
                "daily_utilization_percent": min(100, round(daily_utilization, 1)),
                "hourly_utilization_percent": min(100, round(hourly_utilization, 1)),
                "remaining_daily_budget_kg": max(0, self.budgets["daily_kg"] - self.current_session["total_carbon_kg"]),
                "status": self._get_status_color(daily_utilization)
            },
            "alerts": {
                "total_alerts": len(self.alerts),
                "recent_alerts": len(recent_alerts),
                "critical_alerts": len([a for a in recent_alerts if a["severity"] == "critical"]),
                "latest_alerts": recent_alerts[-5:] if recent_alerts else []
            },
            "recommendations": self._get_current_recommendations()
        }
    
    def _get_status_color(self, utilization: float) -> str:
        """Get status color based on utilization"""
        if utilization < 30:
            return "🟢 Good"
        elif utilization < 70:
            return "🟡 Warning"
        else:
            return "🔴 Critical"
    
    def _get_current_recommendations(self) -> List[str]:
        """Get current optimization recommendations"""
        
        recommendations = []
        
        if not self.current_session["operations"]:
            return ["Start operations to get recommendations"]
        
        # Calculate carbon per operation
        carbon_per_op = self.current_session["total_carbon_kg"] / self.current_session["operations"]
        
        if carbon_per_op > 0.005:
            recommendations.append("🔄 High carbon per operation - consider smaller models")
        
        if "gpt-4o" in self.current_session["models_used"] and "gpt-3.5-turbo" not in self.current_session["models_used"]:
            recommendations.append("💡 Try GPT-3.5-turbo for simpler tasks")
        
        if self.current_session["operations"] > 10:
            recommendations.append("💾 Consider caching results to reduce duplicate calls")
        
        # Check for high frequency operations
        session_duration_hours = (datetime.now() - self.current_session["start_time"]).total_seconds() / 3600
        ops_per_hour = self.current_session["operations"] / session_duration_hours if session_duration_hours > 0 else 0
        
        if ops_per_hour > 50:
            recommendations.append("⚡ High operation frequency - implement rate limiting")
        
        recent_alerts = [a for a in self.alerts if 
                        (datetime.now() - datetime.fromisoformat(a["timestamp"])).total_seconds() < 1800]
        
        if recent_alerts:
            recommendations.append("⚠️  Recent budget alerts - review operation efficiency")
        
        return recommendations[:5]  # Limit to top 5
    
    def print_dashboard(self):
        """Print real-time dashboard to console"""
        
        status = self.get_real_time_status()
        
        # Clear screen (works on most terminals)
        os.system('clear' if os.name == 'posix' else 'cls')
        
        print("🌍 LLM Carbon Monitoring Dashboard")
        print("=" * 60)
        print(f"⏰ Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Session info
        session = status["session_info"]
        print(f"\n📊 Session Overview:")
        print(f"   Duration: {session['duration_hours']} hours")
        print(f"   Operations: {session['total_operations']}")
        print(f"   Models Used: {', '.join(session['models_used']) if session['models_used'] else 'None'}")
        print(f"   Total Carbon: {session['total_carbon_kg']:.6f} kg CO2e")
        
        # Rates
        rates = status["rates"]
        print(f"\n📈 Current Rates:")
        print(f"   Operations/Hour: {rates['operations_per_hour']}")
        print(f"   Carbon/Hour: {rates['carbon_per_hour_kg']:.6f} kg CO2e")
        print(f"   Carbon/Operation: {rates['carbon_per_operation_kg']:.6f} kg CO2e")
        
        # Budget status
        budget = status["budget_status"]
        print(f"\n💰 Budget Status: {budget['status']}")
        print(f"   Daily Utilization: {budget['daily_utilization_percent']:.1f}%")
        print(f"   Hourly Utilization: {budget['hourly_utilization_percent']:.1f}%")
        print(f"   Remaining Budget: {budget['remaining_daily_budget_kg']:.6f} kg CO2e")
        
        # Alerts
        alerts = status["alerts"]
        print(f"\n🚨 Alerts:")
        print(f"   Total: {alerts['total_alerts']} | Recent: {alerts['recent_alerts']} | Critical: {alerts['critical_alerts']}")
        
        if alerts["latest_alerts"]:
            print(f"   Latest Alerts:")
            for alert in alerts["latest_alerts"][-3:]:  # Show last 3
                time_str = datetime.fromisoformat(alert["timestamp"]).strftime('%H:%M:%S')
                severity_icon = "🔴" if alert["severity"] == "critical" else "🟡"
                print(f"      {severity_icon} {time_str}: {alert['message'][:50]}...")
        
        # Recommendations
        print(f"\n💡 Recommendations:")
        for rec in status["recommendations"]:
            print(f"   {rec}")
        
        # Progress bars for budget utilization
        daily_progress = min(100, budget['daily_utilization_percent'])
        daily_bar = "█" * int(daily_progress / 5) + "░" * (20 - int(daily_progress / 5))
        print(f"\n📊 Daily Budget: [{daily_bar}] {daily_progress:.1f}%")
        
        hourly_progress = min(100, budget['hourly_utilization_percent'])
        hourly_bar = "█" * int(hourly_progress / 5) + "░" * (20 - int(hourly_progress / 5))
        print(f"⏰ Hourly Rate:  [{hourly_bar}] {hourly_progress:.1f}%")
    
    def export_session_report(self) -> str:
        """Export detailed session report"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"carbon_session_report_{timestamp}.json"
        
        # Custom JSON serializer for complex objects
        def json_serializer(obj):
            """Custom JSON serializer for complex objects"""
            if isinstance(obj, datetime):
                return obj.isoformat()
            elif isinstance(obj, set):
                return list(obj)
            elif hasattr(obj, '__dict__'):
                return obj.__dict__
            elif isinstance(obj, (bytes, bytearray)):
                return obj.decode('utf-8', errors='ignore')
            else:
                return str(obj)
        
        # Get session emissions from calculator if available
        session_emissions = {}
        if self.calculator:
            try:
                session_emissions = self.calculator.calculate_session_emissions()
            except Exception as e:
                session_emissions = {"error": f"Failed to get session emissions: {e}"}
        
        # Prepare session summary (convert set to list for JSON)
        session_summary = dict(self.current_session)
        if "models_used" in session_summary and isinstance(session_summary["models_used"], set):
            session_summary["models_used"] = list(session_summary["models_used"])
        
        report = {
            "report_metadata": {
                "timestamp": datetime.now().isoformat(),
                "session_start": self.current_session["start_time"].isoformat(),
                "report_type": "session_carbon_monitoring",
                "version": "1.1"
            },
            "session_summary": session_summary,
            "detailed_operations": self.carbon_history,
            "all_alerts": self.alerts,
            "calculator_session": session_emissions,
            "budget_configuration": self.budgets,
            "final_recommendations": self._get_comprehensive_recommendations()
        }
        
        try:
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2, default=json_serializer, ensure_ascii=False)
            
            print(f"📊 Session report exported: {report_file}")
            return report_file
            
        except Exception as e:
            print(f"❌ Failed to export report: {e}")
            print(f"🔍 Error type: {type(e).__name__}")
            
            # Try to export a simplified version
            try:
                simplified_report = {
                    "report_metadata": {
                        "timestamp": datetime.now().isoformat(),
                        "report_type": "session_carbon_monitoring_simplified",
                        "error": f"Full export failed: {e}"
                    },
                    "session_summary": {
                        "operations": self.current_session["operations"],
                        "total_carbon_kg": self.current_session["total_carbon_kg"],
                        "models_used": list(self.current_session["models_used"]) if self.current_session["models_used"] else []
                    },
                    "alerts_count": len(self.alerts),
                    "recommendations": self._get_comprehensive_recommendations()[:3]  # Top 3 only
                }
                
                simple_file = f"carbon_session_report_simplified_{timestamp}.json"
                with open(simple_file, 'w') as f:
                    json.dump(simplified_report, f, indent=2, default=str)
                
                print(f"💾 Simplified report saved: {simple_file}")
                return simple_file
                
            except Exception as e2:
                print(f"❌ Even simplified report failed: {e2}")
                return ""
    
    def _get_comprehensive_recommendations(self) -> List[str]:
        """Get comprehensive recommendations for the session"""
        
        if not self.current_session["operations"]:
            return ["No operations recorded for analysis"]
        
        recommendations = []
        
        # Calculate session metrics
        total_carbon = self.current_session["total_carbon_kg"]
        operations = self.current_session["operations"]
        carbon_per_op = total_carbon / operations
        
        # Efficiency analysis
        if carbon_per_op > 0.01:
            recommendations.append("🔴 High carbon per operation - consider model optimization")
        elif carbon_per_op > 0.005:
            recommendations.append("🟡 Moderate carbon usage - room for improvement")
        else:
            recommendations.append("🟢 Efficient carbon usage - good job!")
        
        # Model recommendations
        models_used = self.current_session["models_used"]
        if "gpt-4o" in models_used:
            recommendations.append("💡 GPT-4o detected - consider GPT-3.5-turbo for simpler tasks")
        
        if len(models_used) == 1 and "gpt-4" in list(models_used)[0]:
            recommendations.append("🔄 Single large model used - diversify with smaller models")
        
        # Alert analysis
        critical_alerts = [a for a in self.alerts if a["severity"] == "critical"]
        if critical_alerts:
            recommendations.append("🚨 Critical budget violations occurred - review operation strategy")
        
        # Frequency analysis
        duration_hours = (datetime.now() - self.current_session["start_time"]).total_seconds() / 3600
        if duration_hours > 0:
            ops_per_hour = operations / duration_hours
            if ops_per_hour > 100:
                recommendations.append("⚡ Very high operation frequency - implement batching")
        
        return recommendations

def simulate_dashboard_demo():
    """Simulate dashboard with sample operations"""
    
    print("🚀 Starting Carbon Monitoring Dashboard Demo")
    print("=" * 60)
    
    dashboard = CarbonDashboard()
    
    if not CARBON_TRACKING_AVAILABLE:
        print("⚠️  Carbon calculator not available - demo will be limited")
        return
    
    # Simulate some operations
    sample_operations = [
        {"model": "gpt-4o", "input": 1200, "output": 600, "type": "vision", "time": 3.2},
        {"model": "gpt-3.5-turbo", "input": 800, "output": 400, "type": "text", "time": 1.5},
        {"model": "gpt-4", "input": 1000, "output": 800, "type": "text", "time": 2.8},
        {"model": "gpt-3.5-turbo", "input": 600, "output": 300, "type": "text", "time": 1.2},
        {"model": "gpt-4o", "input": 1500, "output": 700, "type": "vision", "time": 3.8},
    ]
    
    print("📊 Simulating LLM operations with carbon tracking...")
    
    for i, op in enumerate(sample_operations, 1):
        print(f"\n🔄 Operation {i}: {op['model']} ({op['type']})")
        
        # Log operation
        result = dashboard.log_operation(
            op["model"], op["input"], op["output"], op["type"], op["time"]
        )
        
        if "error" not in result:
            emissions = result["emissions"]["total_kg_co2"]
            print(f"   📊 Emissions: {emissions:.6f} kg CO2e")
            print(f"   🔄 Session Total: {result['session_total_kg']:.6f} kg CO2e")
        
        # Print dashboard every few operations
        if i % 2 == 0:
            print(f"\n" + "="*60)
            print(f"🌍 Dashboard Update (after {i} operations)")
            print("="*60)
            dashboard.print_dashboard()
            
            # Pause for demo effect (remove in real usage)
            time.sleep(1)
    
    # Final dashboard
    print(f"\n" + "="*60)
    print(f"🎯 Final Dashboard State")
    print("="*60)
    dashboard.print_dashboard()
    
    # Export report
    print(f"\n📤 Exporting session report...")
    report_file = dashboard.export_session_report()
    
    # Final summary
    status = dashboard.get_real_time_status()
    print(f"\n🎉 Demo Complete!")
    print(f"   Operations: {status['session_info']['total_operations']}")
    print(f"   Total Carbon: {status['session_info']['total_carbon_kg']:.6f} kg CO2e")
    print(f"   Budget Status: {status['budget_status']['status']}")
    print(f"   Report: {report_file}")

def main():
    """Main dashboard application"""
    
    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        simulate_dashboard_demo()
    else:
        print("🌍 LLM Carbon Monitoring Dashboard")
        print("=" * 40)
        print("Usage:")
        print("  python3 carbon_monitoring_dashboard.py demo  # Run demo")
        print("  python3 carbon_monitoring_dashboard.py       # Show usage")
        print("")
        print("To integrate into your code:")
        print("  from carbon_monitoring_dashboard import CarbonDashboard")
        print("  dashboard = CarbonDashboard()")
        print("  dashboard.log_operation(model, input_tokens, output_tokens, op_type, time)")
        print("  dashboard.print_dashboard()")

if __name__ == "__main__":
    main()
