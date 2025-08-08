"""
Setup script for AccuracyValidatorAgent testing environment
This script will help you get started with testing visual accuracy validation
"""

import os
import sys
from pathlib import Path
import subprocess

def install_dependencies():
    """Install required Python packages"""
    print("📦 Installing dependencies...")
    
    packages = [
        "opencv-python>=4.8.0",
        "selenium>=4.15.0", 
        "scikit-image>=0.21.0",
        "webdriver-manager>=4.0.0",
        "numpy>=1.24.0",
        "pillow>=10.0.0",
        "requests>=2.31.0",
        "pyyaml>=6.0"
    ]
    
    for package in packages:
        try:
            print(f"   Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        except subprocess.CalledProcessError as e:
            print(f"   ❌ Failed to install {package}: {e}")
            return False
    
    print("✅ All dependencies installed successfully!")
    return True

def setup_chrome_driver():
    """Setup Chrome WebDriver for Selenium"""
    print("🌐 Setting up Chrome WebDriver...")
    
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from webdriver_manager.chrome import ChromeDriverManager
        from selenium.webdriver.chrome.service import Service
        
        # Test Chrome driver installation
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.quit()
        
        print("✅ Chrome WebDriver setup successful!")
        return True
        
    except Exception as e:
        print(f"❌ Chrome WebDriver setup failed: {e}")
        print("   Please install Google Chrome browser and try again")
        return False

def create_test_structure():
    """Create the test directory structure"""
    print("📁 Creating test directory structure...")
    
    base_dir = Path(__file__).parent
    test_images_dir = base_dir / "test_images"
    test_results_dir = base_dir / "test_results"
    
    # Create directories
    test_images_dir.mkdir(exist_ok=True)
    test_results_dir.mkdir(exist_ok=True)
    
    # Create sample test configuration
    test_config = test_images_dir / "test_config.json"
    sample_config = {
        "test_cases": [
            {
                "name": "Sample Test Case",
                "image": "place_your_image_here.png",
                "url": "https://example.com",
                "description": "Sample test case - replace with your actual test data"
            }
        ],
        "thresholds": {
            "accuracy_threshold": 0.85,
            "layout_threshold": 0.7,
            "color_threshold": 0.8
        }
    }
    
    import json
    with open(test_config, 'w') as f:
        json.dump(sample_config, f, indent=2)
    
    print(f"✅ Test structure created:")
    print(f"   📸 Test images: {test_images_dir}")
    print(f"   📊 Test results: {test_results_dir}")
    print(f"   ⚙️ Test config: {test_config}")
    
    return True

def create_sample_test_script():
    """Create a sample test script with predefined test cases"""
    
    sample_script_content = '''#!/usr/bin/env python3
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
        print(f"\\n📋 Test Case {i}: {test_case['name']}")
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
'''
    
    script_path = Path(__file__).parent / "run_batch_tests.py"
    with open(script_path, 'w') as f:
        f.write(sample_script_content)
    
    # Make it executable
    os.chmod(script_path, 0o755)
    
    print(f"✅ Sample batch test script created: {script_path}")
    return True

def main():
    """Main setup function"""
    print("🚀 AccuracyValidatorAgent Test Environment Setup")
    print("=" * 50)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    
    print(f"✅ Python {sys.version.split()[0]} detected")
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Dependency installation failed")
        sys.exit(1)
    
    # Setup Chrome driver
    if not setup_chrome_driver():
        print("❌ Chrome WebDriver setup failed")
        sys.exit(1)
    
    # Create test structure
    if not create_test_structure():
        print("❌ Test structure creation failed")
        sys.exit(1)
    
    # Create sample test script
    if not create_sample_test_script():
        print("❌ Sample script creation failed")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Place your test images in the 'test_images/' folder")
    print("2. Run: python test_accuracy_validator.py")
    print("3. Or modify and run: python run_batch_tests.py")
    print("\n💡 For help: check test_images/README.md")

if __name__ == "__main__":
    main()
