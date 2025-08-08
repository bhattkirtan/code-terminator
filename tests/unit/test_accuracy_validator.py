"""
Standalone test script for AccuracyValidatorAgent
Place your test images in the 'test_images' folder and run this script
"""

import os
import sys
from pathlib import Path
from src.agents.skadoosh_agents import AccuracyValidatorAgent, AgentContext

def test_accuracy_validator():
    """Test the AccuracyValidatorAgent with local image and deployed URL"""
    
    # Configuration
    TEST_IMAGES_DIR = Path(__file__).parent / "test_images"
    
    print("🧪 AccuracyValidatorAgent Test Script")
    print("=" * 50)
    
    # Check if test_images directory exists
    if not TEST_IMAGES_DIR.exists():
        TEST_IMAGES_DIR.mkdir()
        print(f"📁 Created test_images directory: {TEST_IMAGES_DIR}")
        print("   Please place your test images in this folder and run again.")
        return
    
    # List available images
    image_files = list(TEST_IMAGES_DIR.glob("*.png")) + list(TEST_IMAGES_DIR.glob("*.jpg")) + list(TEST_IMAGES_DIR.glob("*.jpeg"))
    
    if not image_files:
        print(f"❌ No images found in {TEST_IMAGES_DIR}")
        print("   Supported formats: .png, .jpg, .jpeg")
        print("   Please add test images and run again.")
        return
    
    print(f"📸 Found {len(image_files)} test images:")
    for i, img_file in enumerate(image_files):
        print(f"   {i + 1}. {img_file.name}")
    
    # Select image
    try:
        choice = input(f"\nSelect image (1-{len(image_files)}): ").strip()
        selected_image = image_files[int(choice) - 1]
        print(f"✅ Selected: {selected_image.name}")
    except (ValueError, IndexError):
        print("❌ Invalid selection")
        return
    
    # Get URL from user
    deployed_url = input("\n🌐 Enter deployed URL to test: ").strip()
    if not deployed_url:
        print("❌ URL is required")
        return
    
    if not deployed_url.startswith(('http://', 'https://')):
        deployed_url = 'https://' + deployed_url
    
    print(f"🔗 Testing URL: {deployed_url}")
    
    # Create context and test
    context = AgentContext(
        project_name="Accuracy Validation Test",
        uploads={"screenshot": str(selected_image)}
    )
    
    validator = AccuracyValidatorAgent()
    
    input_data = {
        "deployed_url": deployed_url
    }
    
    print("\n🚀 Starting validation test...")
    print("-" * 30)
    
    try:
        result = validator.execute(context, input_data)
        
        # Display results
        print("\n" + "="*60)
        print("🎯 VISUAL ACCURACY VALIDATION RESULTS")
        print("="*60)
        
        if result.get("validation_failed"):
            print(f"❌ Validation failed: {result.get('error', 'Unknown error')}")
            return
        
        print(f"📊 Overall Accuracy Score: {result.get('visual_accuracy_score', 0):.1%}")
        print(f"🏗️ Structural Similarity (SSIM): {result.get('structural_similarity', 0):.1%}")
        print(f"🎨 Color Accuracy: {result.get('color_accuracy', {}).get('overall_color_accuracy', 0):.1%}")
        print(f"📏 Pixel Difference: {result.get('pixel_difference_percentage', 0):.1f}%")
        print(f"✅ Passes Threshold (85%): {result.get('passes_accuracy_threshold', False)}")
        print(f"⏱️ Processing Time: {result.get('processing_time_seconds', 0):.1f} seconds")
        
        # File paths
        print(f"\n📁 Generated Files:")
        print(f"   📸 Live Screenshot: {result.get('live_screenshot_path', 'N/A')}")
        print(f"   🔥 Difference Heatmap: {result.get('difference_heatmap_path', 'N/A')}")
        
        # Layout analysis
        layout_match = result.get('layout_structure_match', {})
        if layout_match:
            print(f"\n🏗️ Layout Analysis:")
            print(f"   Edge Similarity: {layout_match.get('edge_similarity', 0):.1%}")
            print(f"   Contour Similarity: {layout_match.get('contour_similarity', 0):.1%}")
            print(f"   Layout Preserved: {layout_match.get('layout_preserved', False)}")
            print(f"   Original Components: {layout_match.get('original_components', 0)}")
            print(f"   Live Components: {layout_match.get('live_components', 0)}")
        
        # Color analysis
        color_accuracy = result.get('color_accuracy', {})
        if color_accuracy:
            print(f"\n🎨 Color Analysis:")
            channels = color_accuracy.get('channel_correlations', {})
            print(f"   Blue Channel: {channels.get('blue', 0):.1%}")
            print(f"   Green Channel: {channels.get('green', 0):.1%}")
            print(f"   Red Channel: {channels.get('red', 0):.1%}")
            print(f"   Theme Preserved: {color_accuracy.get('color_theme_preserved', False)}")
        
        # Recommendations
        recommendations = result.get('accuracy_recommendations', [])
        if recommendations:
            print(f"\n💡 Recommendations:")
            for i, rec in enumerate(recommendations, 1):
                print(f"   {i}. {rec}")
        
        # Component analysis
        component_analysis = result.get('component_detection', {})
        if component_analysis:
            print(f"\n🔍 Component Analysis:")
            print(f"   Layout Structure: {component_analysis.get('layout_structure', 'N/A')}")
            print(f"   Color Theme: {component_analysis.get('color_theme', 'N/A')}")
            print(f"   Overall Fidelity: {component_analysis.get('overall_fidelity', 'N/A')}")
        
        print("\n" + "="*60)
        
        # Open results folder
        temp_dir = Path(result.get('live_screenshot_path', '')).parent
        if temp_dir.exists():
            print(f"📂 Results saved to: {temp_dir}")
            
            # Ask if user wants to open folder (optional)
            try:
                open_folder = input("\nOpen results folder? (y/n): ").strip().lower()
                if open_folder == 'y':
                    import subprocess
                    import platform
                    
                    if platform.system() == "Darwin":  # macOS
                        subprocess.run(["open", str(temp_dir)])
                    elif platform.system() == "Windows":
                        subprocess.run(["explorer", str(temp_dir)])
                    elif platform.system() == "Linux":
                        subprocess.run(["xdg-open", str(temp_dir)])
            except:
                pass
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        print("\n🔍 Full error trace:")
        traceback.print_exc()

def setup_test_environment():
    """Setup test environment with sample images and instructions"""
    
    TEST_IMAGES_DIR = Path(__file__).parent / "test_images"
    
    if not TEST_IMAGES_DIR.exists():
        TEST_IMAGES_DIR.mkdir()
    
    # Create a README in test_images folder
    readme_content = """# Test Images for AccuracyValidatorAgent

## Instructions:
1. Place your test images in this folder
2. Supported formats: .png, .jpg, .jpeg
3. Run: python test_accuracy_validator.py
4. Enter the deployed URL when prompted

## Example Test Scenarios:
- Original UI screenshot vs modernized deployed app
- Legacy dashboard vs new Angular implementation
- Figma design vs live website

## Tips:
- Use clear, high-resolution images for better accuracy
- Ensure the deployed URL is accessible and fully loaded
- The tool will capture a full-page screenshot automatically
"""
    
    readme_path = TEST_IMAGES_DIR / "README.md"
    with open(readme_path, 'w') as f:
        f.write(readme_content)
    
    print(f"📁 Test environment setup complete!")
    print(f"   Test images folder: {TEST_IMAGES_DIR}")
    print(f"   Instructions: {readme_path}")

if __name__ == "__main__":
    print("🧪 AccuracyValidatorAgent Test Suite")
    print("=" * 40)
    
    # Check dependencies
    try:
        import cv2
        import selenium
        import skimage
        print("✅ All dependencies available")
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("\nInstall required packages:")
        print("pip install opencv-python selenium scikit-image webdriver-manager")
        sys.exit(1)
    
    # Setup test environment if needed
    setup_test_environment()
    
    # Run test
    test_accuracy_validator()
