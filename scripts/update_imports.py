#!/usr/bin/env python3
"""
Script to update imports after project restructuring
"""

import os
import re
from pathlib import Path

def update_imports_in_file(file_path):
    """Update imports in a single file"""
    if not os.path.exists(file_path):
        return
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Store original content for comparison
    original_content = content
    
    # Update imports
    content = re.sub(r'from llm_carbon_calculator import', 'from src.carbon.llm_carbon_calculator import', content)
    content = re.sub(r'from skadoosh_agents import', 'from src.agents.skadoosh_agents import', content)
    content = re.sub(r'from carbon_monitoring_dashboard import', 'from src.carbon.carbon_monitoring_dashboard import', content)
    content = re.sub(r'from component_anomaly_detector import', 'from src.validation.component_anomaly_detector import', content)
    content = re.sub(r'from llm_component_detector import', 'from src.validation.llm_component_detector import', content)
    content = re.sub(r'from env_loader import', 'from src.utils.env_loader import', content)
    
    # Update path references
    content = re.sub(r'Path\("test_images"\)', 'Path("../../data/test_images")', content)
    content = re.sub(r'Path\("testdata"\)', 'Path("../../data/testdata")', content)
    
    # Only write if content changed
    if content != original_content:
        with open(file_path, 'w') as f:
            f.write(content)
        print(f"✅ Updated: {file_path}")
    else:
        print(f"ℹ️  No changes needed: {file_path}")

def main():
    """Update all test files"""
    test_files = [
        "tests/unit/test_automated.py",
        "tests/unit/test_accuracy_validator.py", 
        "tests/unit/test_carbon_calculator.py",
        "tests/unit/test_carbon_integration.py",
        "tests/unit/test_complete_accuracy_validator.py",
        "tests/unit/test_llm_accuracy_validator.py",
        "tests/unit/test_methods.py",
        "tests/unit/test_with_env.py"
    ]
    
    # Also update script files
    script_files = [
        "scripts/quick_setup.py",
        "scripts/quick_accuracy_test.py",
        "scripts/debug_test.py",
        "scripts/simple_test.py",
        "scripts/setup_accuracy_test.py"
    ]
    
    all_files = test_files + script_files
    
    for file_path in all_files:
        update_imports_in_file(file_path)

if __name__ == "__main__":
    main()
