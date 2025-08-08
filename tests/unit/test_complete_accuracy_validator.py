"""
Complete test suite for AccuracyValidatorAgent with both CV and LLM modes
"""

import os
import sys
from pathlib import Path
from src.agents.skadoosh_agents import AccuracyValidatorAgent, AgentContext
import json

# Load environment variables from .env file
try:
    from src.utils.env_loader import load_env_file
    load_env_file()
except ImportError:
    print("⚠️  env_loader not found, using system environment variables")

def setup_test_environment():
    """Setup test environment and check dependencies"""
    print("🧪 Setting up AccuracyValidatorAgent Test Environment")
    print("=" * 60)
    
    # Check dependencies
    required_packages = [
        ("cv2", "opencv-python"),
        ("selenium", "selenium"), 
        ("skimage", "scikit-image"),
        ("numpy", "numpy"),
        ("PIL", "pillow")
    ]
    
    missing_packages = []
    for module, package in required_packages:
        try:
            __import__(module)
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} - MISSING")
    
    if missing_packages:
        print(f"\n📦 Install missing packages:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    # Create test directories
    test_images_dir = Path("../../data/test_images")
    test_images_dir.mkdir(exist_ok=True)
    
    # Check for Chrome WebDriver
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
        return False
    
    return True

def test_traditional_cv_mode():
    """Test AccuracyValidatorAgent with traditional computer vision"""
    print("\n🖼️ Testing Traditional Computer Vision Mode")
    print("-" * 50)
    
    # Find test images
    test_images_dir = Path("../../data/test_images")
    image_files = list(test_images_dir.glob("*.png")) + list(test_images_dir.glob("*.jpg"))
    
    if not image_files:
        print("❌ No test images found in test_images/")
        print("   Add an image file (PNG/JPG) and try again")
        return None
    
    # Select image
    selected_image = image_files[0]
    print(f"📸 Using image: {selected_image.name}")
    
    # Get URL
    deployed_url = input("🌐 Enter URL to test (or press Enter for demo): ").strip()
    if not deployed_url:
        deployed_url = "https://example.com"  # Demo URL
    
    if not deployed_url.startswith(('http://', 'https://')):
        deployed_url = 'https://' + deployed_url
    
    print(f"🔗 Testing URL: {deployed_url}")
    
    # Create context
    context = AgentContext(
        project_name="CV Mode Test",
        uploads={"screenshot": str(selected_image)}
    )
    
    # Create validator with CV mode
    validator = AccuracyValidatorAgent(use_llm=False)
    input_data = {"deployed_url": deployed_url}
    
    print("\n🚀 Running traditional CV analysis...")
    
    try:
        result = validator.execute(context, input_data)
        display_results(result, "Traditional Computer Vision")
        return result
        
    except Exception as e:
        print(f"❌ CV test failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def display_results(result: dict, mode: str):
    """Display test results in a formatted way"""
    
    print(f"\n" + "="*60)
    print(f"🎯 {mode.upper()} RESULTS")
    print("="*60)
    
    if result.get("validation_failed"):
        print(f"❌ Validation failed: {result.get('error')}")
        return
    
    # Basic metrics
    accuracy = result.get('visual_accuracy_score', 0)
    ssim = result.get('structural_similarity', 0)
    color_acc = result.get('color_accuracy', {}).get('overall_color_accuracy', 0)
    pixel_diff = result.get('pixel_difference_percentage', 0)
    passes = result.get('passes_accuracy_threshold', False)
    
    print(f"📊 Overall Accuracy: {accuracy:.1%}")
    print(f"🏗️ Structural Similarity: {ssim:.1%}")
    print(f"🎨 Color Accuracy: {color_acc:.1%}")
    print(f"📏 Pixel Difference: {pixel_diff:.1f}%")
    print(f"✅ Passes Threshold: {passes}")
    print(f"⏱️ Processing Time: {result.get('processing_time_seconds', 0):.1f}s")
    
    # Component analysis
    component_analysis = result.get('component_detection', {})
    if component_analysis:
        print(f"\n🧩 Component Analysis:")
        for key, value in component_analysis.items():
            if isinstance(value, str):
                print(f"   {key}: {value}")
    
    # Enhanced LLM results
    detailed_analysis = result.get('detailed_analysis', {})
    if detailed_analysis:
        detailed_report = detailed_analysis.get('detailed_report', {})
        if 'llm_analysis' in detailed_report:
            llm_data = detailed_report['llm_analysis']
            print(f"\n🧠 LLM Analysis:")
            print(f"   Component Accuracy: {llm_data.get('component_accuracy', 0):.1f}%")
            print(f"   Model Used: {llm_data.get('model_used', 'Unknown')}")
    
    # Recommendations
    recommendations = result.get('accuracy_recommendations', [])
    if recommendations:
        print(f"\n💡 Recommendations:")
        for i, rec in enumerate(recommendations[:5], 1):  # Show first 5
            print(f"   {i}. {rec}")
    
    # File locations
    print(f"\n📁 Generated Files:")
    print(f"   📸 Live Screenshot: {result.get('live_screenshot_path', 'N/A')}")
    print(f"   🔥 Difference Heatmap: {result.get('difference_heatmap_path', 'N/A')}")
    
    # Component visualizations
    temp_dir = Path(result.get('live_screenshot_path', '')).parent
    if temp_dir.exists():
        component_files = list(temp_dir.glob("*components*.png"))
        if component_files:
            print(f"   🧩 Component Visualizations:")
            for comp_file in component_files:
                print(f"      {comp_file.name}")

def main():
    """Main test function with menu"""
    
    if not setup_test_environment():
        print("❌ Environment setup failed")
        return
    

        
        input("\nPress Enter to continue...")

def test_llm_enhanced_mode():
    """Test AccuracyValidatorAgent with LLM enhancement"""
    print("\n🧠 Testing LLM-Enhanced Mode")
    print("-" * 50)
    
    # Find test images
    test_images_dir = Path("../../data/test_images")
    image_files = list(test_images_dir.glob("*.png")) + list(test_images_dir.glob("*.jpg"))
    
    if not image_files:
        print("❌ No test images found in test_images/")
        print("   Add an image file (PNG/JPG) and try again")
        return None
    
    # Select image
    selected_image = image_files[0]
    print(f"📸 Using image: {selected_image.name}")
    
    # Get URL
    deployed_url = input("🌐 Enter URL to test (or press Enter for demo): ").strip()
    if not deployed_url:
        deployed_url = "https://example.com"  # Demo URL
    
    if not deployed_url.startswith(('http://', 'https://')):
        deployed_url = 'https://' + deployed_url
    
    print(f"🔗 Testing URL: {deployed_url}")
    
    # Create context
    context = AgentContext(
        project_name="LLM Mode Test",
        uploads={"screenshot": str(selected_image)}
    )
    
    # Create validator with LLM mode
    validator = AccuracyValidatorAgent(use_llm=True)
    input_data = {"deployed_url": deployed_url}
    
    print("\n� Running LLM-enhanced analysis...")
    
    try:
        result = validator.execute(context, input_data)
        display_results(result, "LLM-Enhanced")
        return result
        
    except Exception as e:
        print(f"❌ LLM test failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def compare_cv_vs_llm():
    """Run both modes and compare results"""
    print("\n⚔️ Comparing CV vs LLM Modes")
    print("=" * 50)
    
    # Find test images
    test_images_dir = Path("../../data/test_images")
    image_files = list(test_images_dir.glob("*.png")) + list(test_images_dir.glob("*.jpg"))
    
    if not image_files:
        print("❌ No test images found")
        return
    
    selected_image = image_files[0]
    deployed_url = input("🌐 Enter URL for comparison test: ").strip()
    
    if not deployed_url.startswith(('http://', 'https://')):
        deployed_url = 'https://' + deployed_url
    
    print(f"🔗 Testing both modes against: {deployed_url}")
    
    # Test CV mode
    print("\n🖼️ Running CV mode...")
    context_cv = AgentContext(
        project_name="CV Comparison",
        uploads={"screenshot": str(selected_image)}
    )
    
    validator_cv = AccuracyValidatorAgent(use_llm=False)
    result_cv = validator_cv.execute(context_cv, {"deployed_url": deployed_url})
    
    # Test LLM mode
    print("\n🧠 Running LLM mode...")
    context_llm = AgentContext(
        project_name="LLM Comparison",
        uploads={"screenshot": str(selected_image)}
    )
    
    validator_llm = AccuracyValidatorAgent(use_llm=True)
    result_llm = validator_llm.execute(context_llm, {"deployed_url": deployed_url})
    
    # Compare results
    print(f"\n📊 Comparison Results:")
    print(f"{'Metric':<25} {'CV Mode':<15} {'LLM Mode':<15} {'Difference':<15}")
    print("-" * 70)
    
    metrics = [
        ("Accuracy Score", "visual_accuracy_score"),
        ("Structural Similarity", "structural_similarity"),
        ("Processing Time", "processing_time_seconds")
    ]
    
    for label, key in metrics:
        cv_val = result_cv.get(key, 0)
        llm_val = result_llm.get(key, 0)
        diff = llm_val - cv_val
        
        if key == "processing_time_seconds":
            print(f"{label:<25} {cv_val:<15.1f}s {llm_val:<15.1f}s {diff:<15.1f}s")
        else:
            print(f"{label:<25} {cv_val:<15.1%} {llm_val:<15.1%} {diff:<15.1%}")

def run_batch_tests():
    """Run tests on multiple images if available"""
    print("\n📋 Batch Testing Mode")
    print("-" * 30)
    
    test_images_dir = Path("../../data/test_images")
    image_files = list(test_images_dir.glob("*.png")) + list(test_images_dir.glob("*.jpg"))
    
    if len(image_files) < 2:
        print("❌ Need at least 2 images for batch testing")
        return
    
    deployed_url = input("🌐 Enter URL for batch testing: ").strip()
    if not deployed_url.startswith(('http://', 'https://')):
        deployed_url = 'https://' + deployed_url
    
    print(f"🔗 Testing {len(image_files)} images against: {deployed_url}")
    
    results = []
    
    for i, image_file in enumerate(image_files[:3]):  # Test first 3
        print(f"\n📸 Testing {i+1}/{min(3, len(image_files))}: {image_file.name}")
        
        context = AgentContext(
            project_name=f"Batch Test {i+1}",
            uploads={"screenshot": str(image_file)}
        )
        
        validator = AccuracyValidatorAgent(use_llm=False)  # Use CV for speed
        result = validator.execute(context, {"deployed_url": deployed_url})
        
        results.append({
            "image": image_file.name,
            "accuracy": result.get('visual_accuracy_score', 0),
            "passes": result.get('passes_accuracy_threshold', False)
        })
    
    # Summary
    print(f"\n📊 Batch Test Summary:")
    print(f"{'Image':<20} {'Accuracy':<12} {'Pass/Fail':<10}")
    print("-" * 42)
    
    for result in results:
        status = "PASS" if result["passes"] else "FAIL"
        print(f"{result['image']:<20} {result['accuracy']:<12.1%} {status:<10}")

def main():
    """Main test function with menu"""
    
    if not setup_test_environment():
        print("❌ Environment setup failed")
        return
    
    while True:
        print("\n🧪 AccuracyValidatorAgent Test Menu")
        print("=" * 40)
        print("1. 🖼️  Test Traditional CV Mode")
        print("2. 🧠  Test LLM-Enhanced Mode") 
        print("3. ⚔️  Compare CV vs LLM")
        print("4. 📋  Batch Test Multiple Images")
        print("5. 🔧  Environment Check")
        print("6. ❌  Exit")
        
        choice = input("\nSelect option (1-6): ").strip()
        
        if choice == "1":
            test_traditional_cv_mode()
        elif choice == "2":
            test_llm_enhanced_mode()
        elif choice == "3":
            compare_cv_vs_llm()
        elif choice == "4":
            run_batch_tests()
        elif choice == "5":
            setup_test_environment()
        elif choice == "6":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice, try again")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()
