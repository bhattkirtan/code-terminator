#!/usr/bin/env python3
"""
Quick test runner with environment loading
"""

import os
import sys
from pathlib import Path

# Add current directory to path
sys.path.append('/Users/kirtanbhatt/hackathon-2025')

# Load environment variables
try:
    from env_loader import load_env_file
    load_env_file()
except ImportError:
    print("⚠️  env_loader not found")

def quick_test_with_env():
    print("🧪 AccuracyValidatorAgent Test (with .env)")
    print("=" * 50)
    
    # Check API key
    api_key = os.environ.get('OPENAI_API_KEY')
    if api_key:
        print(f"✅ OpenAI API Key loaded: {api_key[:10]}...{api_key[-4:]}")
        llm_available = True
    else:
        print("❌ No OpenAI API Key found")
        llm_available = False
    
    # Check test images
    test_images_dir = Path("test_images")
    image_files = list(test_images_dir.glob("*.png")) + list(test_images_dir.glob("*.jpg"))
    
    if image_files:
        print(f"✅ Found {len(image_files)} test images:")
        for img in image_files[:3]:  # Show first 3
            print(f"   📸 {img.name}")
    else:
        print("❌ No test images found")
    
    # Check if we can import the agent
    try:
        from skadoosh_agents import AccuracyValidatorAgent, AgentContext
        print("✅ AccuracyValidatorAgent imported successfully")
        
        # Try to create both agents
        print("\n🔧 Testing Agent Creation:")
        
        # CV Agent (no API key needed)
        try:
            cv_agent = AccuracyValidatorAgent(use_llm=False)
            print("✅ Traditional CV Agent created")
        except Exception as e:
            print(f"❌ CV Agent creation failed: {e}")
        
        # LLM Agent (needs API key)
        if llm_available:
            try:
                llm_agent = AccuracyValidatorAgent(use_llm=True)
                print("✅ LLM-Enhanced Agent created")
            except Exception as e:
                print(f"❌ LLM Agent creation failed: {e}")
        else:
            print("⏸️  LLM Agent skipped (no API key)")
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
    
    print(f"\n🎯 Available Options:")
    print("1. 🖼️  Traditional CV Mode ✅")
    if llm_available:
        print("2. 🧠  LLM-Enhanced Mode ✅")
        print("3. ⚔️  Compare CV vs LLM ✅")
    else:
        print("2. 🧠  LLM-Enhanced Mode ❌ (Need API key)")
        print("3. ⚔️  Compare CV vs LLM ❌ (Need API key)")
    print("4. 📋  Batch Testing ✅")
    
    print(f"\n🚀 Ready to test! Run the main script:")
    print("   python3 test_complete_accuracy_validator.py")

if __name__ == "__main__":
    quick_test_with_env()
