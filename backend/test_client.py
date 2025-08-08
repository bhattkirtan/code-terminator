#!/usr/bin/env python3
"""
Simple test client for local cloud functions
"""

import requests
import json
import os

# Local service URLs
UPLOAD_URL = "http://localhost:8080"
EMBEDDING_URL = "http://localhost:8081"
DATA_URL = "http://localhost:8082"
SEARCH_URL = "http://localhost:8083"

def test_upload_service():
    """Test the upload service"""
    print("📤 Testing Upload Service...")
    
    # Create a test file
    test_content = b"This is a test file content"
    files = {'file': ('test.txt', test_content, 'text/plain')}
    data = {'projectId': 'test-project-123', 'metadata': '{"description": "test file"}'}
    
    try:
        response = requests.post(UPLOAD_URL, files=files, data=data)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        return response.json()
    except Exception as e:
        print(f"   Error: {e}")
        return None

def test_embedding_service():
    """Test the embedding service"""
    print("🧠 Testing Embedding Service...")
    
    payload = {
        "content": "This is a test text for embedding generation",
        "type": "text",
        "projectId": "test-project-123"
    }
    
    try:
        response = requests.post(EMBEDDING_URL, json=payload)
        print(f"   Status: {response.status_code}")
        result = response.json()
        if 'embeddings' in result:
            print(f"   Embeddings length: {len(result['embeddings'])}")
            print(f"   Model: {result.get('model')}")
        else:
            print(f"   Response: {result}")
        return result
    except Exception as e:
        print(f"   Error: {e}")
        return None

def test_data_service():
    """Test the data service"""
    print("💾 Testing Data Service...")
    
    # Test creating a project
    payload = {
        "name": "Test Project",
        "owner": "test-user",
        "metadata": {"description": "A test project"}
    }
    
    try:
        response = requests.post(DATA_URL, json=payload)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        return response.json()
    except Exception as e:
        print(f"   Error: {e}")
        return None

def test_search_service():
    """Test the search service"""
    print("🔍 Testing Search Service...")
    
    # Use dummy embedding for testing
    dummy_embedding = [0.1] * 1536  # OpenAI embedding size
    
    payload = {
        "embedding": dummy_embedding,
        "projectId": "test-project-123",
        "threshold": 0.5,
        "limit": 5
    }
    
    try:
        response = requests.post(SEARCH_URL, json=payload)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        return response.json()
    except Exception as e:
        print(f"   Error: {e}")
        return None

def test_health_checks():
    """Test health endpoints"""
    print("🚦 Testing Health Checks...")
    
    services = [
        ("Upload", UPLOAD_URL),
        ("Embedding", EMBEDDING_URL),
        ("Data", DATA_URL),
        ("Search", SEARCH_URL)
    ]
    
    for name, url in services:
        try:
            response = requests.get(f"{url}/health")
            if response.status_code == 404:
                print(f"   {name}: Service running (no health endpoint)")
            else:
                print(f"   {name}: {response.status_code} - {response.text[:50]}")
        except requests.exceptions.ConnectionError:
            print(f"   {name}: ❌ Not running")
        except Exception as e:
            print(f"   {name}: Error - {e}")

if __name__ == "__main__":
    print("🧪 Starting Cloud Functions Local Test Suite\n")
    
    # Check if services are running
    test_health_checks()
    print()
    
    # Test each service
    test_upload_service()
    print()
    
    test_embedding_service()
    print()
    
    test_data_service()
    print()
    
    test_search_service()
    print()
    
    print("✅ Testing complete!")
