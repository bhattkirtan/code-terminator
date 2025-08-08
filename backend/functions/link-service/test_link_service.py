#!/usr/bin/env python3
"""
Local test script for link-service functionality
"""

import os
import json
import time
import requests
from datetime import datetime

# Configuration
LINK_SERVICE_URL = "http://localhost:8084"
TEST_PROJECT_ID = "test-project"

# Test URLs with different content types
TEST_LINKS = [
    {
        "url": "https://docs.python.org/3/tutorial/",
        "contentType": "documentation",
        "title": "Python Tutorial",
        "tags": ["python", "tutorial", "programming"]
    },
    {
        "url": "https://github.com/microsoft/vscode",
        "contentType": "frameworks",
        "title": "VS Code GitHub",
        "tags": ["vscode", "editor", "microsoft"]
    },
    {
        "url": "https://openai.com/blog/chatgpt/",
        "contentType": "blog",
        "title": "ChatGPT Blog Post",
        "tags": ["ai", "chatgpt", "openai"]
    }
]

def test_add_links():
    """Test adding multiple links with different content types."""
    print("🔗 Testing link addition...")
    
    link_ids = []
    for link_data in TEST_LINKS:
        payload = {
            "projectId": TEST_PROJECT_ID,
            **link_data
        }
        
        response = requests.post(f"{LINK_SERVICE_URL}/api/links/add", json=payload)
        
        if response.status_code == 200:
            result = response.json()
            link_id = result.get('linkId')
            link_ids.append(link_id)
            print(f"✅ Added link: {link_id} ({link_data['contentType']}) - TTL: {result.get('ttlHours', 'N/A')}h")
        else:
            print(f"❌ Failed to add link: {link_data['url']} - {response.text}")
    
    return link_ids

def test_fetch_content(link_ids):
    """Test fetching content for added links."""
    print("\n📄 Testing content fetching...")
    
    for link_id in link_ids:
        try:
            response = requests.get(
                f"{LINK_SERVICE_URL}/api/fetch/{link_id}",
                params={
                    "projectId": TEST_PROJECT_ID,
                    "generateEmbeddings": "true"
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                content_length = len(result.get('content', ''))
                embeddings_length = len(result.get('embeddings', []))
                freshness = result.get('freshness', 'unknown')
                
                print(f"✅ Fetched content for {link_id}:")
                print(f"   - Content: {content_length} characters")
                print(f"   - Embeddings: {embeddings_length} dimensions")
                print(f"   - Freshness: {freshness}")
                print(f"   - Cached: {result.get('cached', False)}")
                
            else:
                print(f"❌ Failed to fetch content for {link_id}: {response.text}")
                
        except Exception as e:
            print(f"❌ Error fetching {link_id}: {e}")

def test_link_status(link_ids):
    """Test checking link cache status."""
    print("\n📊 Testing link status...")
    
    for link_id in link_ids:
        try:
            response = requests.get(
                f"{LINK_SERVICE_URL}/api/status/{link_id}",
                params={"projectId": TEST_PROJECT_ID}
            )
            
            if response.status_code == 200:
                result = response.json()
                cache_status = result.get('cacheStatus', 'unknown')
                freshness = result.get('freshness', 'unknown')
                time_until_expiry = result.get('timeUntilExpiryHours', 0)
                
                print(f"✅ Status for {link_id}:")
                print(f"   - Cache Status: {cache_status}")
                print(f"   - Freshness: {freshness}")
                print(f"   - Expires in: {time_until_expiry:.1f} hours")
                
            else:
                print(f"❌ Failed to get status for {link_id}: {response.text}")
                
        except Exception as e:
            print(f"❌ Error getting status for {link_id}: {e}")

def test_search_links():
    """Test searching across cached link content."""
    print("\n🔍 Testing link search...")
    
    search_queries = [
        {"query": "python", "searchType": "keyword"},
        {"query": "tutorial", "searchType": "keyword"},
        {"query": "programming language", "searchType": "keyword"}
    ]
    
    for search in search_queries:
        try:
            payload = {
                "projectId": TEST_PROJECT_ID,
                "limit": 5,
                **search
            }
            
            response = requests.post(f"{LINK_SERVICE_URL}/api/links/search", json=payload)
            
            if response.status_code == 200:
                result = response.json()
                links = result.get('links', [])
                
                print(f"✅ Search '{search['query']}' ({search['searchType']}):")
                print(f"   - Found: {len(links)} results")
                
                for link in links[:2]:  # Show top 2 results
                    title = link.get('title', 'No title')
                    score = link.get('relevanceScore', 0)
                    print(f"   - {title} (score: {score:.2f})")
                    
            else:
                print(f"❌ Failed to search for '{search['query']}': {response.text}")
                
        except Exception as e:
            print(f"❌ Error searching for '{search['query']}': {e}")

def test_refresh_link(link_ids):
    """Test force refreshing a cached link."""
    if not link_ids:
        return
        
    print("\n🔄 Testing link refresh...")
    
    link_id = link_ids[0]  # Test with first link
    try:
        payload = {"projectId": TEST_PROJECT_ID}
        response = requests.post(f"{LINK_SERVICE_URL}/api/refresh/{link_id}", json=payload)
        
        if response.status_code == 200:
            result = response.json()
            freshness = result.get('freshness', 'unknown')
            cached = result.get('cached', False)
            
            print(f"✅ Refreshed {link_id}:")
            print(f"   - Freshness: {freshness}")
            print(f"   - Cached: {cached}")
            
        else:
            print(f"❌ Failed to refresh {link_id}: {response.text}")
            
    except Exception as e:
        print(f"❌ Error refreshing {link_id}: {e}")

def main():
    """Run all link service tests."""
    print("🚀 Starting Link Service Tests")
    print(f"Service URL: {LINK_SERVICE_URL}")
    print(f"Test Project: {TEST_PROJECT_ID}")
    print("=" * 50)
    
    # Check if service is running
    try:
        response = requests.get(f"{LINK_SERVICE_URL}/api/status/test?projectId={TEST_PROJECT_ID}")
        print("✅ Link service is accessible")
    except requests.exceptions.ConnectionError:
        print("❌ Link service is not running!")
        print("Start it with: cd link-service && functions-framework --target=link_processor --port=8084")
        return
    
    # Run tests
    link_ids = test_add_links()
    time.sleep(2)  # Wait for processing
    
    test_fetch_content(link_ids)
    time.sleep(1)
    
    test_link_status(link_ids)
    time.sleep(1)
    
    test_search_links()
    time.sleep(1)
    
    test_refresh_link(link_ids)
    
    print("\n" + "=" * 50)
    print("🎉 Link Service Tests Complete!")
    print("\nNext Steps:")
    print("- Check GCS bucket for cached content")
    print("- Verify Firestore link collections")
    print("- Test TTL expiration behavior")
    print("- Integrate with frontend application")

if __name__ == "__main__":
    main()
