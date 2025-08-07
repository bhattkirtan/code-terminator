#!/usr/bin/env python3
"""
Automated test of AccuracyValidatorAgent with predefined inputs
"""

import os
import sys
from pathlib import Path

# Add current directory to path
sys.path.append('/Users/kirtanbhatt/hackathon-2025')

# Load environment
try:
    from env_loader import load_env_file
    load_env_file()
except ImportError:
    print("⚠️  env_loader not found")

def test_traditional_cv():
    """Test traditional CV mode with predefined inputs"""
    print("🧪 Testing Traditional CV Mode")
    print("=" * 50)
    
    try:
        from skadoosh_agents import AccuracyValidatorAgent, AgentContext
        
        # Check for test images
        test_images_dir = Path("test_images")
        image_files = list(test_images_dir.glob("*.png")) + list(test_images_dir.glob("*.jpg"))
        
        if not image_files:
            print("❌ No test images found")
            return
        
        selected_image = image_files[0]
        deployed_url = "https://preview--frame-to-forge.lovable.app/"
        
        print(f"📸 Using image: {selected_image.name}")
        print(f"🔗 Testing URL: {deployed_url}")
        
        # Create context
        context = AgentContext(
            project_name="Automated CV Test",
            uploads={"screenshot": str(selected_image)}
        )
        
        # Create traditional CV validator
        validator = AccuracyValidatorAgent(use_llm=False)
        input_data = {"deployed_url": deployed_url}
        
        print("\n🚀 Running traditional CV analysis...")
        
        result = validator.execute(context, input_data)
        
        # Display results
        print(f"\n" + "="*60)
        print(f"🎯 TRADITIONAL CV RESULTS")
        print("="*60)
        
        if result.get("validation_failed"):
            print(f"❌ Validation failed: {result.get('error')}")
            return
        
        # Basic metrics
        accuracy = result.get('visual_accuracy_score', 0)
        ssim = result.get('structural_similarity', 0)
        color_acc = result.get('color_accuracy', {})
        if isinstance(color_acc, dict):
            color_accuracy = color_acc.get('overall_color_accuracy', 0)
        else:
            color_accuracy = 0
        
        pixel_diff = result.get('pixel_difference_percentage', 0)
        passes = result.get('passes_accuracy_threshold', False)
        
        print(f"📊 Overall Accuracy: {accuracy:.1%}")
        print(f"🏗️ Structural Similarity: {ssim:.1%}")
        print(f"🎨 Color Accuracy: {color_accuracy:.1%}")
        print(f"📏 Pixel Difference: {pixel_diff:.1f}%")
        print(f"✅ Passes Threshold: {passes}")
        print(f"⏱️ Processing Time: {result.get('processing_time_seconds', 0):.1f}s")
        
        # Component analysis
        component_analysis = result.get('component_detection', {})
        if component_analysis:
            print(f"\n🧩 Component Analysis:")
            comp_acc = component_analysis.get('component_accuracy', 0)
            print(f"   Component Accuracy: {comp_acc:.1f}%")
            print(f"   Analysis Method: {component_analysis.get('method', 'Traditional CV')}")
        
        # File locations
        print(f"\n📁 Generated Files:")
        print(f"   📸 Live Screenshot: {result.get('live_screenshot_path', 'N/A')}")
        print(f"   🔥 Difference Heatmap: {result.get('difference_heatmap_path', 'N/A')}")
        
        print(f"\n✅ Traditional CV test completed successfully! 🎉")
        
        return result
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    test_traditional_cv()
