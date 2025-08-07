#!/bin/bash

echo "🧪 Let's Test AccuracyValidatorAgent Together!"
echo "============================================="

# Step 1: Setup
echo "📦 Step 1: Setting up environment..."
python3 quick_setup.py

echo ""
echo "📸 Step 2: Check for test images..."
if [ "$(ls -A test_images/*.png test_images/*.jpg test_images/*.jpeg 2>/dev/null | wc -l)" -eq 0 ]; then
    echo "❌ No test images found!"
    echo ""
    echo "🔧 Please add a test image now:"
    echo "   1. Find any screenshot or image file"
    echo "   2. Copy it to the test_images/ folder"
    echo "   3. Example: cp ~/Desktop/screenshot.png test_images/"
    echo ""
    echo "⏸️  Press Enter when you've added an image..."
    read
fi

echo ""
echo "🚀 Step 3: Running the test..."
python3 simple_test.py

echo ""
echo "✅ Test completed! Check the results above."
