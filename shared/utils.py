"""Shared utilities for AI DevOps Agent Platform."""

import hashlib
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import aiofiles
from PIL import Image
import cv2
import numpy as np


def generate_task_id() -> str:
    """Generate a unique task ID."""
    return str(uuid.uuid4())


def generate_timestamp() -> str:
    """Generate a timestamp string."""
    return datetime.utcnow().isoformat()


def calculate_file_hash(file_path: str) -> str:
    """Calculate SHA-256 hash of a file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


async def save_uploaded_file(file_content: bytes, filename: str, upload_dir: str) -> str:
    """Save uploaded file and return the path."""
    upload_path = Path(upload_dir)
    upload_path.mkdir(parents=True, exist_ok=True)
    
    # Generate unique filename
    timestamp = int(time.time())
    name, ext = Path(filename).stem, Path(filename).suffix
    unique_filename = f"{name}_{timestamp}{ext}"
    file_path = upload_path / unique_filename
    
    async with aiofiles.open(file_path, 'wb') as f:
        await f.write(file_content)
    
    return str(file_path)


def validate_image(file_path: str) -> bool:
    """Validate if file is a valid image."""
    try:
        with Image.open(file_path) as img:
            img.verify()
        return True
    except Exception:
        return False


def resize_image(file_path: str, max_size: tuple = (1920, 1080)) -> str:
    """Resize image if it's too large."""
    with Image.open(file_path) as img:
        if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            img.save(file_path, optimize=True)
    return file_path


def extract_colors_from_image(image_path: str, num_colors: int = 5) -> List[str]:
    """Extract dominant colors from an image."""
    try:
        image = cv2.imread(image_path)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Reshape the image to be a list of pixels
        pixels = image.reshape((-1, 3))
        
        # Use k-means clustering to find dominant colors
        try:
            from sklearn.cluster import KMeans
            kmeans = KMeans(n_clusters=num_colors, random_state=42, n_init=10)
            kmeans.fit(pixels)
            
            colors = []
            for color in kmeans.cluster_centers_:
                hex_color = "#{:02x}{:02x}{:02x}".format(int(color[0]), int(color[1]), int(color[2]))
                colors.append(hex_color)
            
            return colors
        except ImportError:
            # Fallback if sklearn is not available
            return ["#1976d2", "#ffc107", "#f44336", "#4caf50", "#ff9800"]
    except Exception:
        # Return default colors if image processing fails
        return ["#1976d2", "#ffc107", "#f44336", "#4caf50", "#ff9800"]


def sanitize_component_name(name: str) -> str:
    """Sanitize a string to be a valid Angular component name."""
    # Remove special characters and spaces, convert to kebab-case
    import re
    name = re.sub(r'[^a-zA-Z0-9\s-]', '', name)
    name = re.sub(r'\s+', '-', name.strip())
    name = name.lower()
    
    # Ensure it doesn't start with a number or hyphen
    if name and (name[0].isdigit() or name[0] == '-'):
        name = 'component-' + name
        
    return name or 'generated-component'


def estimate_tokens(text: str) -> int:
    """Estimate token count for text (rough approximation)."""
    # Rough estimation: 1 token ≈ 4 characters
    return len(text) // 4


def format_angular_code(code: str, file_type: str) -> str:
    """Format Angular code according to best practices."""
    if file_type == 'typescript':
        # Basic TypeScript formatting
        lines = code.split('\n')
        formatted_lines = []
        indent_level = 0
        
        for line in lines:
            stripped = line.strip()
            if stripped.endswith('{'):
                formatted_lines.append('  ' * indent_level + stripped)
                indent_level += 1
            elif stripped.startswith('}'):
                indent_level = max(0, indent_level - 1)
                formatted_lines.append('  ' * indent_level + stripped)
            else:
                formatted_lines.append('  ' * indent_level + stripped)
        
        return '\n'.join(formatted_lines)
    
    return code


def create_project_structure(project_name: str, output_dir: str) -> Dict[str, str]:
    """Create Angular project directory structure."""
    project_path = Path(output_dir) / project_name
    
    # Create directory structure
    directories = [
        'src/app/components',
        'src/app/services',
        'src/app/models',
        'src/app/shared',
        'src/assets/styles',
        'src/assets/images',
        'src/environments'
    ]
    
    for directory in directories:
        (project_path / directory).mkdir(parents=True, exist_ok=True)
    
    # Return paths
    return {
        'project_root': str(project_path),
        'src': str(project_path / 'src'),
        'app': str(project_path / 'src/app'),
        'components': str(project_path / 'src/app/components'),
        'services': str(project_path / 'src/app/services'),
        'assets': str(project_path / 'src/assets')
    }