#!/usr/bin/env python3
"""
Quick test of the accuracy validator without WebDriver
"""

import os
import sys
from pathlib import Path

# Add the current directory to path
sys.path.append('/Users/kirtanbhatt/hackathon-2025')

def quick_test():
    print("🧪 Quick AccuracyValidatorAgent Test")
    print("=" * 40)
    
    # Check if we can import the modules
    try:
        from skadoosh_agents import AccuracyValidatorAgent, AgentContext
        print("✅ Successfully imported AccuracyValidatorAgent")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return
    
    # Check for test images
    test_images_dir = Path("test_images")
    if not test_images_dir.exists():
        print("❌ test_images directory not found")
        return
    
    image_files = list(test_images_dir.glob("*.png")) + list(test_images_dir.glob("*.jpg"))
    if not image_files:
        print("❌ No test images found")
        return
    
    print(f"✅ Found {len(image_files)} test images")
    for img in image_files:
        print(f"   📸 {img.name}")
    
    # Check OpenAI API key status
    print("\n🔑 API Key Status:")
    if 'OPENAI_API_KEY' in os.environ:
        key = os.environ['OPENAI_API_KEY']
        print(f"✅ OpenAI API Key: {key[:10]}...{key[-4:] if len(key) > 14 else key}")
        print("🧠 LLM-Enhanced Mode available")
    else:
        print("❌ No OPENAI_API_KEY found")
        print("🖼️  Traditional CV Mode only")
    
    # Show available options
    print(f"\n🎯 Available Test Options:")
    print("1. 🖼️  Test Traditional CV Mode (No API key required)")
    
    if 'OPENAI_API_KEY' in os.environ:
        print("2. 🧠  Test LLM-Enhanced Mode")
        print("3. ⚔️  Compare CV vs LLM")
        print("4. 📋  Batch Test Multiple Images")
    else:
        print("2. 🧠  Test LLM-Enhanced Mode (Requires API key)")
        print("3. ⚔️  Compare CV vs LLM (Requires API key)")
        print("4. 📋  Batch Test Multiple Images")
    
    print("5. 🔧  Environment Check")
    print("6. ❌  Exit")
    
    print(f"\n✅ All test infrastructure is ready!")
    print(f"💡 Run 'python3 test_complete_accuracy_validator.py' to start testing")

if __name__ == "__main__":
    quick_test()
