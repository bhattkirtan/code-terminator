"""Debug helper for AccuracyValidatorAgent testing"""

def debug_environment():
    """Check if environment is ready for testing"""
    print("🔧 Environment Debug Check")
    print("=" * 30)
    
    import sys
    print(f"Python: {sys.version}")
    
    # Check packages
    packages = {
        "cv2": "opencv-python",
        "selenium": "selenium", 
        "skimage": "scikit-image",
        "numpy": "numpy",
        "PIL": "pillow"
    }
    
    for module, package in packages.items():
        try:
            __import__(module)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - run: pip install {package}")
    
    # Check Chrome
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        
        driver = webdriver.Chrome(options=options)
        driver.quit()
        print("✅ Chrome WebDriver")
    except Exception as e:
        print(f"❌ Chrome WebDriver: {e}")
        print("   Install Chrome browser and run: pip install webdriver-manager")
    
    # Check files
    from pathlib import Path
    
    required_files = [
        "skadoosh_agents.py",
        "test_images/"
    ]
    
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - missing")

if __name__ == "__main__":
    debug_environment()
