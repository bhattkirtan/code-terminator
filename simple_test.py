"""
Simple test runner for AccuracyValidatorAgent
Run this after adding a test image to test_images/ folder
"""

import os
import sys
from pathlib import Path

def find_test_images():
    """Find available test images"""
    test_dir = Path("test_images")
    if not test_dir.exists():
        return []
    
    extensions = [".png", ".jpg", ".jpeg"]
    images = []
    for ext in extensions:
        images.extend(test_dir.glob(f"*{ext}"))
    
    return images

def simple_test():
    """Run a simple test"""
    print("🧪 Simple AccuracyValidatorAgent Test")
    print("=" * 40)
    
    # Check for test images
    images = find_test_images()
    if not images:
        print("❌ No test images found!")
        print("📝 Please add an image to test_images/ folder first")
        print("   Supported: .png, .jpg, .jpeg")
        print("\n💡 Example:")
        print("   cp ~/Desktop/screenshot.png test_images/")
        return
    
    print(f"📸 Found {len(images)} test images:")
    for i, img in enumerate(images):
        print(f"   {i+1}. {img.name}")
    
    # Simple selection
    if len(images) == 1:
        selected = images[0]
        print(f"✅ Auto-selected: {selected.name}")
    else:
        try:
            choice = int(input(f"\nSelect image (1-{len(images)}): ")) - 1
            selected = images[choice]
            print(f"✅ Selected: {selected.name}")
        except (ValueError, IndexError):
            print("❌ Invalid selection")
            return
    
    # Get URL
    print("\n🌐 Enter a URL to test against:")
    print("   Examples:")
    print("   - https://example.com")
    print("   - http://localhost:3000")
    print("   - https://your-app.vercel.app")
    
    url = input("\nURL: ").strip()
    if not url:
        print("❌ URL required")
        return
    
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    print(f"🔗 Will test: {url}")
    print(f"📸 Against image: {selected}")
    
    # Import and run the actual test
    try:
        from skadoosh_agents import AccuracyValidatorAgent, AgentContext
        
        print("\n🚀 Starting test...")
        
        # Create context
        context = AgentContext(
            project_name="Simple Test",
            uploads={"screenshot": str(selected)}
        )
        
        # Create validator
        validator = AccuracyValidatorAgent()
        
        # Run test
        result = validator.execute(context, {"deployed_url": url})
        
        # Show results
        print("\n" + "="*50)
        print("🎯 TEST RESULTS")
        print("="*50)
        
        if result.get("validation_failed"):
            print(f"❌ Test failed: {result.get('error')}")
        else:
            accuracy = result.get('visual_accuracy_score', 0)
            passed = result.get('passes_accuracy_threshold', False)
            
            print(f"📊 Accuracy Score: {accuracy:.1%}")
            print(f"✅ Pass/Fail: {'PASS' if passed else 'FAIL'}")
            print(f"📸 Screenshot: {result.get('live_screenshot_path', 'N/A')}")
            print(f"🔥 Heatmap: {result.get('difference_heatmap_path', 'N/A')}")
            
            recommendations = result.get('accuracy_recommendations', [])
            if recommendations:
                print(f"\n💡 Recommendations:")
                for rec in recommendations:
                    print(f"   • {rec}")
        
    except ImportError:
        print("❌ Cannot import AccuracyValidatorAgent")
        print("   Make sure skadoosh_agents.py is in the same directory")
    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    simple_test()
