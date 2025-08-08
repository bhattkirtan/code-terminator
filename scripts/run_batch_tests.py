#!/usr/bin/env python3
"""
Sample test script with predefined test cases
Modify this script to add your own test scenarios
"""

from test_accuracy_validator import test_accuracy_validator
from src.agents.skadoosh_agents import AccuracyValidatorAgent, AgentContext
from pathlib import Path
import json

def run_batch_tests():
    """Run multiple test cases from configuration"""
    
    config_path = Path(__file__).parent / "test_images" / "test_config.json"
    
    if not config_path.exists():
        print("❌ Test configuration not found. Run setup_accuracy_test.py first.")
        return
    
    with open(config_path) as f:
        config = json.load(f)
    
    test_cases = config.get("test_cases", [])
    
    if not test_cases:
        print("❌ No test cases found in configuration")
        return
    
    print(f"🧪 Running {len(test_cases)} test cases...")
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test Case {i}: {test_case['name']}")
        print(f"   Image: {test_case['image']}")
        print(f"   URL: {test_case['url']}")
        
        image_path = Path(__file__).parent / "test_images" / test_case['image']
        
        if not image_path.exists():
            print(f"   ❌ Image not found: {image_path}")
            continue
        
        # Create context and run test
        context = AgentContext(
            project_name=f"Test Case {i}",
            uploads={"screenshot": str(image_path)}
        )
        
        validator = AccuracyValidatorAgent()
        input_data = {"deployed_url": test_case['url']}
        
        try:
            result = validator.execute(context, input_data)
            
            accuracy = result.get('visual_accuracy_score', 0)
            passed = result.get('passes_accuracy_threshold', False)
            
            print(f"   📊 Accuracy: {accuracy:.1%}")
            print(f"   ✅ Result: {'PASS' if passed else 'FAIL'}")
            
        except Exception as e:
            print(f"   ❌ Test failed: {str(e)}")

if __name__ == "__main__":
    run_batch_tests()
