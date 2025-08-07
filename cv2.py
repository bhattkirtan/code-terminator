"""Mock cv2 for testing."""

import numpy as np


def imread(path):
    """Mock imread function."""
    # Return a dummy image array
    return np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)


def cvtColor(image, conversion):
    """Mock cvtColor function."""
    return image


COLOR_BGR2RGB = "BGR2RGB"