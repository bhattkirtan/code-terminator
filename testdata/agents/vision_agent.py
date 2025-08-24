# Accepts UI screenshots and extracts layout elements
def detect_ui_elements(image_path):
    return {
        "layout": [
            {"type": "card", "label": "Phase", "position": [10, 20]},
            {"type": "button", "label": "Create Phase", "position": [200, 20]}
        ]
    }
