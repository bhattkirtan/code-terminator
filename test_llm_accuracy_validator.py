"""
Test script for LLM-enhanced AccuracyValidatorAgent
"""

import os
from pathlib import Path
from skadoosh_agents import AccuracyValidatorAgent, AgentContext

def test_llm_accuracy_validator():
    """Test the LLM-enhanced AccuracyValidatorAgent"""
    
    print("🧠 Testing LLM-Enhanced AccuracyValidatorAgent")
    print("=" * 50)
    
    # Check for test images
    test_images_dir = Path("test_images")
    if not test_images_dir.exists():
        print("❌ test_images directory not found")
        return
    
    image_files = list(test_images_dir.glob("*.png")) + list(test_images_dir.glob("*.jpg"))
    
    if not image_files:
        print("❌ No test images found")
        return
    
    print(f"📸 Found {len(image_files)} test images")
    
    # Select image
    selected_image = image_files[0]
    print(f"✅ Using: {selected_image.name}")
    
    # Get URL
    deployed_url = input("\n🌐 Enter deployed URL to test: ").strip()
    if not deployed_url.startswith(('http://', 'https://')):
        deployed_url = 'https://' + deployed_url
    
    # Test with LLM enabled
    print("\n🧠 Testing with LLM-powered analysis...")
    
    context = AgentContext(
        project_name="LLM Accuracy Test",
        uploads={"screenshot": str(selected_image)}
    )
    
    # Create LLM-enabled validator
    validator = AccuracyValidatorAgent(use_llm=True)
    
    input_data = {"deployed_url": deployed_url}
    
    try:
        result = validator.execute(context, input_data)
        
        print("\n" + "="*60)
        print("🧠 LLM-ENHANCED ACCURACY VALIDATION RESULTS")
        print("="*60)
        
        if result.get("validation_failed"):
            print(f"❌ Validation failed: {result.get('error')}")
            return
        
        # Display enhanced results
        print(f"📊 Overall Accuracy Score: {result.get('visual_accuracy_score', 0):.1%}")
        print(f"🏗️ Structural Similarity: {result.get('structural_similarity', 0):.1%}")
        print(f"🎨 Color Accuracy: {result.get('color_accuracy', {}).get('overall_color_accuracy', 0):.1%}")
        print(f"✅ Passes Threshold (85%): {result.get('passes_accuracy_threshold', False)}")
        
        # LLM-specific results
        component_anomalies = result.get('detailed_analysis', {}).get('detailed_report', {})
        if 'llm_analysis' in component_anomalies:
            llm_data = component_anomalies['llm_analysis']
            print(f"\n🧠 LLM Analysis:")
            print(f"   🎯 Component Accuracy: {llm_data.get('component_accuracy', 0):.1f}%")
            print(f"   🤖 Model Used: {llm_data.get('model_used', 'Unknown')}")
        
        # Enhanced recommendations
        recommendations = result.get('accuracy_recommendations', [])
        if recommendations:
            print(f"\n💡 AI-Powered Recommendations:")
            for i, rec in enumerate(recommendations, 1):
                print(f"   {i}. {rec}")
        
        # Component analysis method
        analysis_method = component_anomalies.get('analysis_method', 'Unknown')
        print(f"\n🔬 Analysis Method: {analysis_method}")
        
        # File paths
        print(f"\n📁 Generated Files:")
        print(f"   📸 Live Screenshot: {result.get('live_screenshot_path', 'N/A')}")
        print(f"   🔥 Difference Heatmap: {result.get('difference_heatmap_path', 'N/A')}")
        
        # Show component report if available
        component_report = result.get('detailed_analysis', {}).get('component_anomaly_report', '')
        if component_report and len(component_report) > 100:
            print(f"\n📋 Detailed Component Analysis:")
            print(component_report[:500] + "..." if len(component_report) > 500 else component_report)
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_llm_accuracy_validator()
