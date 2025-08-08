#!/usr/bin/env python3
"""
Post-restructure verification script
"""

import os
import sys
from pathlib import Path

def check_structure():
    """Check that all directories exist"""
    expected_dirs = [
        'src',
        'src/agents',
        'src/carbon', 
        'src/validation',
        'src/utils',
        'tests',
        'tests/unit',
        'tests/integration',
        'tests/e2e',
        'config',
        'data',
        'data/test_images',
        'data/testdata',
        'docs',
        'reports',
        'scripts'
    ]
    
    missing = []
    for dir_path in expected_dirs:
        if not os.path.exists(dir_path):
            missing.append(dir_path)
    
    if missing:
        print(f"❌ Missing directories: {missing}")
        return False
    else:
        print("✅ All expected directories exist")
        return True

def check_key_files():
    """Check that key files are in the right places"""
    expected_files = {
        'src/agents/skadoosh_agents.py': 'Main agents module',
        'src/carbon/llm_carbon_calculator.py': 'Carbon calculator',
        'src/carbon/carbon_monitoring_dashboard.py': 'Carbon dashboard',
        'src/validation/component_anomaly_detector.py': 'Component detector',
        'src/validation/llm_component_detector.py': 'LLM component detector',
        'src/utils/env_loader.py': 'Environment loader',
        'config/requirements.txt': 'Dependencies',
        'config/skadoosh_agents_workflow.json': 'Workflow config',
        'README.md': 'Main documentation'
    }
    
    missing = []
    for file_path, description in expected_files.items():
        if not os.path.exists(file_path):
            missing.append(f"{file_path} ({description})")
    
    if missing:
        print(f"❌ Missing files: {missing}")
        return False
    else:
        print("✅ All key files are in place")
        return True

def check_imports():
    """Try importing key modules"""
    sys.path.append(os.getcwd())
    
    try:
        from src.carbon.llm_carbon_calculator import LLMCarbonCalculator
        print("✅ Carbon calculator import successful")
    except ImportError as e:
        print(f"❌ Carbon calculator import failed: {e}")
        return False
    
    try:
        from src.agents.skadoosh_agents import AccuracyValidatorAgent
        print("✅ Agents module import successful")
    except ImportError as e:
        print(f"❌ Agents module import failed: {e}")
        return False
    
    return True

def main():
    """Run all checks"""
    print("🔍 Running post-restructure verification...\n")
    
    structure_ok = check_structure()
    files_ok = check_key_files()
    imports_ok = check_imports()
    
    print(f"\n📊 Summary:")
    print(f"   Directory structure: {'✅' if structure_ok else '❌'}")
    print(f"   Key files: {'✅' if files_ok else '❌'}")
    print(f"   Imports: {'✅' if imports_ok else '❌'}")
    
    if structure_ok and files_ok and imports_ok:
        print(f"\n🎉 Project restructure completed successfully!")
        print(f"   You can now run tests with: python3 -m pytest tests/")
        print(f"   Or run scripts from: python3 scripts/quick_setup.py")
    else:
        print(f"\n⚠️  Some issues found - please review above")

if __name__ == "__main__":
    main()
