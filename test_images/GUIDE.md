# Quick Test Guide

## Step 1: Add a test image
1. Find any screenshot or image (PNG, JPG)
2. Copy it to the test_images/ folder
3. Name it something descriptive like 'original_design.png'

## Step 2: Find a test URL
- Use any live website (e.g., https://example.com)
- Or use a localhost URL if you have a local server
- Or use a deployed app (Vercel, Netlify, etc.)

## Step 3: Run the test
```bash
python test_accuracy_validator.py
```

## Example Test:
- Image: A screenshot of a dashboard
- URL: https://dashboard.example.com
- Expected: Visual comparison with similarity score
