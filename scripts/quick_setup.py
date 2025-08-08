"""
Quick setup script to get AccuracyValidatorAgent testing ready
"""

import os
import sys
from pathlib import Path
import subprocess

def quick_setup():
    """Quick setup for testing"""
    print("🚀 Quick Setup for AccuracyValidatorAgent Testing")
    print("=" * 50)
    
    # Create test directories
    test_images_dir = Path("../../data/test_images")
    test_images_dir.mkdir(exist_ok=True)
    print(f"✅ Created directory: {test_images_dir}")
    
    # Check Python dependencies
    required_packages = [
        "opencv-python",
        "selenium", 
        "scikit-image",
        "webdriver-manager",
        "numpy",
        "pillow"
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"✅ {package} - available")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} - missing")
    
    if missing_packages:
        print(f"\n📦 Installing missing packages...")
        for package in missing_packages:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                print(f"✅ Installed {package}")
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to install {package}: {e}")
    
    # Create sample test guide
    guide_content = """# Quick Test Guide

## Step 1: Add a test image
1. Find any screenshot or image (PNG, JPG)
2. Copy it to the test_images/ folder
3. Name it something descriptive like 'original_design.png'

## Step 2: Find a test URL
- Use any live website (e.g., https://example.com)
- Or use a localhost URL if you have a local server
- Or use a deployed app (Vercel, Netlify, etc.)

## Step 3: Run the test
```bash
python test_accuracy_validator.py
```

## Example Test:
- Image: A screenshot of a dashboard
- URL: https://dashboard.example.com
- Expected: Visual comparison with similarity score
"""
    
    with open(test_images_dir / "GUIDE.md", "w") as f:
        f.write(guide_content)
    
    print(f"✅ Created test guide: {test_images_dir}/GUIDE.md")
    print("\n🎯 Next steps:")
    print("1. Add a test image to test_images/ folder")
    print("2. Run: python test_accuracy_validator.py")
    print("3. Enter a URL when prompted")

if __name__ == "__main__":
    quick_setup()
