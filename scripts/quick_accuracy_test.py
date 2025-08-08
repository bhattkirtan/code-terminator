"""
Quick test script for AccuracyValidatorAgent - simplified version
"""

from pathlib import Path

def quick_test():
    """Quick test with minimal setup"""
    
    print("⚡ Quick AccuracyValidatorAgent Test")
    print("-" * 35)
    
    # Check for images
    test_dir = Path("../../data/test_images")
    if not test_dir.exists():
        test_dir.mkdir()
        print("📁 Created test_images/ folder")
        print("   Add an image file and run again")
        return
    
    images = list(test_dir.glob("*.png")) + list(test_dir.glob("*.jpg"))
    if not images:
        print("❌ No images found in test_images/")
        print("   Add a PNG or JPG file and try again")
        return
    
    # Try to import after checking basic requirements
    try:
        from src.agents.skadoosh_agents import AccuracyValidatorAgent, AgentContext
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        print("   Make sure skadoosh_agents.py is in the same directory")
        return
    except SyntaxError as e:
        print(f"❌ Syntax error in skadoosh_agents.py: {e}")
        print("   Check for indentation or syntax issues")
        return
    
    # Use first image
    test_image = images[0]
    print(f"📸 Using: {test_image.name}")
    
    # Get URL (or use default)
    url = input("🌐 URL to test (Enter for example.com): ").strip()
    if not url:
        url = "https://example.com"
    elif not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    print(f"🔗 Testing: {url}")
    
    # Run test
    context = AgentContext(
        project_name="Quick Test",
        uploads={"screenshot": str(test_image)}
    )
    
    validator = AccuracyValidatorAgent(use_llm=False)  # CV mode for speed
    
    try:
        result = validator.execute(context, {"deployed_url": url})
        
        # Show key results
        accuracy = result.get('visual_accuracy_score', 0)
        passes = result.get('passes_accuracy_threshold', False)
        
        print(f"\n✅ Results:")
        print(f"   Accuracy: {accuracy:.1%}")
        print(f"   Pass/Fail: {'PASS' if passes else 'FAIL'}")
        print(f"   Files: {Path(result.get('live_screenshot_path', '')).parent}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    quick_test()
