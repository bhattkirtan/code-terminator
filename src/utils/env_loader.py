#!/usr/bin/env python3
"""
Simple .env file loader for the accuracy validator
"""

import os
from pathlib import Path

def load_env_file(env_path='.env'):
    """Load environment variables from .env file"""
    env_file = Path(env_path)
    
    if not env_file.exists():
        print(f"❌ No .env file found at {env_file}")
        return False
    
    print(f"📄 Loading environment from {env_file}")
    
    try:
        with open(env_file, 'r') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                
                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue
                
                # Parse KEY=VALUE format
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # Remove quotes if present
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]
                    
                    # Set environment variable
                    os.environ[key] = value
                    print(f"✅ Loaded {key}")
                else:
                    print(f"⚠️  Skipping invalid line {line_num}: {line}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error loading .env file: {e}")
        return False

if __name__ == "__main__":
    load_env_file()
