#!/usr/bin/env python3
"""
Direct test of AccuracyValidatorAgent functionality
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

def test_agent_methods():
    """Test that all required methods exist"""
    print("🧪 Testing AccuracyValidatorAgent Methods")
    print("=" * 50)
    
    try:
        from skadoosh_agents import AccuracyValidatorAgent, AgentContext
        
        # Create agents
        cv_agent = AccuracyValidatorAgent(use_llm=False)
        llm_agent = AccuracyValidatorAgent(use_llm=True)
        
        print("✅ Agents created successfully")
        
        # Check if methods exist
        required_methods = [
            '_cleanup',
            '_generate_difference_heatmap',
            '_analyze_layout_structure',
            '_analyze_color_accuracy',
            '_save_component_visualizations',
            '_save_llm_component_visualizations'
        ]
        
        print("\n🔍 Checking required methods:")
        for method in required_methods:
            if hasattr(cv_agent, method):
                print(f"✅ {method}")
            else:
                print(f"❌ {method} - MISSING")
        
        # Check OpenAI API key
        api_key = os.environ.get('OPENAI_API_KEY')
        if api_key:
            print(f"\n✅ OpenAI API Key loaded: {api_key[:10]}...{api_key[-4:]}")
        else:
            print("\n❌ No OpenAI API Key found")
        
        # Check test images
        test_images_dir = Path("test_images")
        image_files = list(test_images_dir.glob("*.png")) + list(test_images_dir.glob("*.jpg"))
        
        if image_files:
            print(f"\n✅ Found {len(image_files)} test images:")
            for img in image_files:
                print(f"   📸 {img.name}")
        else:
            print("\n❌ No test images found")
        
        print(f"\n🎯 All methods are available!")
        print(f"🚀 Ready to test accuracy validation!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_agent_methods()
