from flask import jsonify, request
import functions_framework
import google.cloud.logging
from google.cloud import firestore, storage
import requests
from bs4 import BeautifulSoup
import openai
import os
import json
import logging
from datetime import datetime, timedelta
import hashlib
import time
import math

# Set up Google Cloud Logging
client = google.cloud.logging.Client()
client.setup_logging()

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# Initialize clients
db = firestore.Client()
storage_client = storage.Client()

# Initialize OpenAI
openai.api_key = os.environ.get('OPENAI_API_KEY')

# CORS headers
headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
}

# Content type TTL policies (in hours)
CONTENT_TYPE_TTL = {
    'api-docs': 2,
    'news': 1,
    'blog': 1,
    'release-notes': 6,
    'tutorials': 12,
    'documentation': 6,
    'frameworks': 24,
    'specifications': 72,  # 3 days
    'standards': 168,     # 7 days
    'static-content': 336, # 14 days
    'default': 24
}

def cosine_similarity(vec1, vec2):
    """Calculate cosine similarity between two vectors."""
    if not vec1 or not vec2 or len(vec1) != len(vec2):
        return 0.0
    
    # Calculate dot product
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    
    # Calculate magnitudes
    magnitude1 = math.sqrt(sum(a * a for a in vec1))
    magnitude2 = math.sqrt(sum(a * a for a in vec2))
    
    # Avoid division by zero
    if magnitude1 == 0 or magnitude2 == 0:
        return 0.0
    
    return dot_product / (magnitude1 * magnitude2)

@functions_framework.http
def link_processor(request):
    """Entry point for the snapit link processing service Google Cloud Function."""
    
    path = request.path
    method = request.method

    logger.info(f"Received request: {method} {path}")

    # Handle CORS preflight
    if method == 'OPTIONS':
        return '', 204, headers

    try:
        # Route handling
        if method == 'POST':
            if path == '/add' or path == '/links/add':
                return add_link(request)
            elif path.startswith('/refresh/'):
                link_id = path.split('/')[-1]
                return refresh_link(link_id, request)
            elif path == '/search' or path == '/links/search':
                return search_links(request)
        elif method == 'GET':
            if path.startswith('/fetch/'):
                link_id = path.split('/')[-1]
                return fetch_link(link_id, request)
            elif path.startswith('/status/'):
                link_id = path.split('/')[-1]
                return get_link_status(link_id, request)
                
    except Exception as e:
        logger.error(f"Error processing request: {e}", exc_info=True)
        return jsonify({'error': 'An internal error occurred'}), 500, headers

    return jsonify({'error': 'Not found'}), 404, headers


def add_link(request):
    """Add external link reference with smart caching configuration."""
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400, headers

    try:
        project_id = data.get('projectId')
        url = data.get('url')
        content_type = data.get('contentType', 'default')
        priority = data.get('priority', 'medium')
        title = data.get('title', '')
        tags = data.get('tags', [])
        
        if not project_id or not url:
            return jsonify({'error': 'Missing projectId or url'}), 400, headers
        
        # Generate link ID from URL hash
        link_id = hashlib.md5(url.encode()).hexdigest()[:12]
        
        # Determine TTL based on content type
        ttl_hours = CONTENT_TYPE_TTL.get(content_type, CONTENT_TYPE_TTL['default'])
        
        # Create link metadata
        link_metadata = {
            'linkId': link_id,
            'url': url,
            'contentType': content_type,
            'priority': priority,
            'title': title,
            'tags': tags,
            'ttlHours': ttl_hours,
            'createdAt': datetime.utcnow().isoformat(),
            'lastFetched': None,
            'fetchCount': 0,
            'status': 'pending',
            'projectId': project_id
        }
        
        # Store in Firestore
        links_ref = db.collection('projects').document(project_id).collection('links')
        links_ref.document(link_id).set(link_metadata)
        
        # Create GCS folder structure
        bucket_name = f"snapit-{project_id}"
        try:
            bucket = storage_client.bucket(bucket_name)
            
            # Create link.json file in GCS
            link_blob_path = f"{project_id}/context/links/{link_id}/link.json"
            link_blob = bucket.blob(link_blob_path)
            link_blob.upload_from_string(
                json.dumps(link_metadata, indent=2),
                content_type='application/json'
            )
            
            logger.info(f"Added link {link_id} for project {project_id}")
            
        except Exception as storage_error:
            logger.warning(f"Storage operation failed: {storage_error}")
            # Continue even if storage fails
        
        return jsonify({
            'status': 'success',
            'linkId': link_id,
            'metadata': link_metadata,
            'folderPath': f"context/links/{link_id}/",
            'ttlHours': ttl_hours
        }), 200, headers
        
    except Exception as e:
        logger.error(f"Error adding link: {e}")
        return jsonify({'error': str(e)}), 500, headers


def fetch_link(link_id, request):
    """Runtime content fetch with intelligent caching."""
    try:
        project_id = request.args.get('projectId')
        force_refresh = request.args.get('forceRefresh', 'false').lower() == 'true'
        generate_embeddings = request.args.get('generateEmbeddings', 'true').lower() == 'true'
        
        if not project_id:
            return jsonify({'error': 'Missing projectId'}), 400, headers
        
        # Get link metadata from Firestore
        link_doc = db.collection('projects').document(project_id).collection('links').document(link_id).get()
        
        if not link_doc.exists:
            return jsonify({'error': 'Link not found'}), 404, headers
        
        link_data = link_doc.to_dict()
        url = link_data.get('url')
        ttl_hours = link_data.get('ttlHours', 24)
        
        # Check cache freshness
        cache_valid = False
        cached_content = None
        
        if not force_refresh:
            cached_content, cache_valid = check_cache_validity(project_id, link_id, ttl_hours)
        
        if cache_valid and cached_content:
            logger.info(f"Using cached content for link {link_id}")
            
            # Return cached content
            return jsonify({
                'status': 'success',
                'linkId': link_id,
                'url': url,
                'content': cached_content.get('content', ''),
                'embeddings': cached_content.get('embeddings', []),
                'cached': True,
                'fetchedAt': cached_content.get('fetchedAt'),
                'expiresAt': cached_content.get('expiresAt'),
                'freshness': 'fresh'
            }), 200, headers
        
        # Fetch fresh content
        logger.info(f"Fetching fresh content for link {link_id}: {url}")
        
        try:
            # Fetch URL content
            response = requests.get(url, timeout=30, headers={
                'User-Agent': 'Mozilla/5.0 (compatible; SnapitBot/1.0)'
            })
            response.raise_for_status()
            
            # Extract text content
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get text content
            text_content = soup.get_text()
            
            # Clean up text
            lines = (line.strip() for line in text_content.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            clean_text = ' '.join(chunk for chunk in chunks if chunk)
            
            # Limit content size (first 10000 characters)
            if len(clean_text) > 10000:
                clean_text = clean_text[:10000] + "..."
            
            # Generate embeddings if requested
            embeddings = []
            if generate_embeddings and clean_text:
                try:
                    embedding_response = openai.embeddings.create(
                        model="text-embedding-3-small",
                        input=clean_text[:8000]  # Limit for OpenAI
                    )
                    embeddings = embedding_response.data[0].embedding
                except Exception as embed_error:
                    logger.warning(f"Failed to generate embeddings: {embed_error}")
            
            # Prepare cached content
            now = datetime.utcnow()
            expires_at = now + timedelta(hours=ttl_hours)
            
            fresh_content = {
                'content': clean_text,
                'embeddings': embeddings,
                'fetchedAt': now.isoformat(),
                'expiresAt': expires_at.isoformat(),
                'contentType': link_data.get('contentType', 'default'),
                'title': soup.title.string if soup.title else link_data.get('title', ''),
                'wordCount': len(clean_text.split()),
                'status': 'fresh'
            }
            
            # Store in cache
            store_in_cache(project_id, link_id, fresh_content)
            
            # Update Firestore metadata
            update_data = {
                'lastFetched': now.isoformat(),
                'fetchCount': firestore.Increment(1),
                'status': 'active'
            }
            link_doc.reference.update(update_data)
            
            return jsonify({
                'status': 'success',
                'linkId': link_id,
                'url': url,
                'content': clean_text,
                'embeddings': embeddings,
                'cached': False,
                'fetchedAt': now.isoformat(),
                'expiresAt': expires_at.isoformat(),
                'freshness': 'fresh',
                'wordCount': len(clean_text.split())
            }), 200, headers
            
        except requests.RequestException as req_error:
            logger.error(f"Failed to fetch URL {url}: {req_error}")
            
            # Try to use stale cache as fallback
            if cached_content:
                logger.info(f"Using stale cache as fallback for link {link_id}")
                return jsonify({
                    'status': 'success',
                    'linkId': link_id,
                    'url': url,
                    'content': cached_content.get('content', ''),
                    'embeddings': cached_content.get('embeddings', []),
                    'cached': True,
                    'fetchedAt': cached_content.get('fetchedAt'),
                    'expiresAt': cached_content.get('expiresAt'),
                    'freshness': 'stale',
                    'warning': 'Fresh fetch failed, using stale cache'
                }), 200, headers
            
            return jsonify({
                'error': f'Failed to fetch content: {str(req_error)}'
            }), 502, headers
        
    except Exception as e:
        logger.error(f"Error fetching link: {e}")
        return jsonify({'error': str(e)}), 500, headers


def check_cache_validity(project_id, link_id, ttl_hours):
    """Check if cached content is still valid."""
    try:
        bucket_name = f"snapit-{project_id}"
        bucket = storage_client.bucket(bucket_name)
        
        # Check for cached content
        cache_blob_path = f"{project_id}/context/links/{link_id}/cache/content.json"
        cache_blob = bucket.blob(cache_blob_path)
        
        if not cache_blob.exists():
            return None, False
        
        # Download and parse cached content
        cached_data = json.loads(cache_blob.download_as_text())
        
        # Check expiry
        expires_at = datetime.fromisoformat(cached_data.get('expiresAt', ''))
        now = datetime.utcnow()
        
        is_valid = now < expires_at
        
        return cached_data, is_valid
        
    except Exception as e:
        logger.warning(f"Error checking cache validity: {e}")
        return None, False


def store_in_cache(project_id, link_id, content_data):
    """Store fresh content in GCS cache."""
    try:
        bucket_name = f"snapit-{project_id}"
        bucket = storage_client.bucket(bucket_name)
        
        # Store content in cache
        cache_blob_path = f"{project_id}/context/links/{link_id}/cache/content.json"
        cache_blob = bucket.blob(cache_blob_path)
        cache_blob.upload_from_string(
            json.dumps(content_data, indent=2),
            content_type='application/json'
        )
        
        # Store HTML content separately if available
        if 'content' in content_data:
            html_blob_path = f"{project_id}/context/links/{link_id}/cache/content.html"
            html_blob = bucket.blob(html_blob_path)
            html_blob.upload_from_string(
                content_data['content'],
                content_type='text/html'
            )
        
        logger.info(f"Stored fresh content in cache for link {link_id}")
        
    except Exception as e:
        logger.warning(f"Failed to store in cache: {e}")


def refresh_link(link_id, request):
    """Force refresh cached content."""
    try:
        project_id = request.json.get('projectId') if request.json else request.args.get('projectId')
        
        if not project_id:
            return jsonify({'error': 'Missing projectId'}), 400, headers
        
        # Force refresh by setting forceRefresh=true
        request.args = {'projectId': project_id, 'forceRefresh': 'true'}
        
        return fetch_link(link_id, request)
        
    except Exception as e:
        logger.error(f"Error refreshing link: {e}")
        return jsonify({'error': str(e)}), 500, headers


def get_link_status(link_id, request):
    """Check cache status and freshness."""
    try:
        project_id = request.args.get('projectId')
        
        if not project_id:
            return jsonify({'error': 'Missing projectId'}), 400, headers
        
        # Get link metadata
        link_doc = db.collection('projects').document(project_id).collection('links').document(link_id).get()
        
        if not link_doc.exists:
            return jsonify({'error': 'Link not found'}), 404, headers
        
        link_data = link_doc.to_dict()
        ttl_hours = link_data.get('ttlHours', 24)
        
        # Check cache status
        cached_content, is_valid = check_cache_validity(project_id, link_id, ttl_hours)
        
        if cached_content:
            expires_at = datetime.fromisoformat(cached_content.get('expiresAt', ''))
            now = datetime.utcnow()
            
            if is_valid:
                freshness = 'fresh'
                status = 'cached_fresh'
            else:
                freshness = 'stale'
                status = 'cached_stale'
            
            time_until_expiry = (expires_at - now).total_seconds() / 3600  # hours
            
        else:
            freshness = 'not_cached'
            status = 'not_cached'
            time_until_expiry = 0
        
        return jsonify({
            'status': 'success',
            'linkId': link_id,
            'cacheStatus': status,
            'freshness': freshness,
            'timeUntilExpiryHours': max(0, time_until_expiry),
            'metadata': link_data,
            'lastFetched': link_data.get('lastFetched'),
            'fetchCount': link_data.get('fetchCount', 0)
        }), 200, headers
        
    except Exception as e:
        logger.error(f"Error getting link status: {e}")
        return jsonify({'error': str(e)}), 500, headers


def search_links(request):
    """Search across cached link content."""
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400, headers

    try:
        project_id = data.get('projectId')
        query = data.get('query', '')
        query_embedding = data.get('embedding')
        search_type = data.get('searchType', 'keyword')  # 'semantic', 'keyword', 'metadata'
        threshold = data.get('threshold', 0.7)
        limit = data.get('limit', 10)
        
        if not project_id:
            return jsonify({'error': 'Missing projectId'}), 400, headers
        
        results = []
        
        # Get all links for the project
        links_ref = db.collection('projects').document(project_id).collection('links')
        links_docs = links_ref.stream()
        
        for link_doc in links_docs:
            link_data = link_doc.to_dict()
            link_id = link_doc.id
            
            # Get cached content
            cached_content, _ = check_cache_validity(project_id, link_id, link_data.get('ttlHours', 24))
            
            if not cached_content:
                continue
            
            relevance_score = 0.0
            
            # Keyword search
            if search_type in ['keyword', 'all'] and query:
                content = cached_content.get('content', '').lower()
                title = cached_content.get('title', '').lower()
                query_lower = query.lower()
                
                if query_lower in content:
                    relevance_score += 0.6
                if query_lower in title:
                    relevance_score += 0.4
                
                # Check tags
                tags = link_data.get('tags', [])
                tag_match = any(query_lower in tag.lower() for tag in tags)
                if tag_match:
                    relevance_score += 0.3
            
            # Semantic search
            if search_type in ['semantic', 'all'] and query_embedding:
                stored_embeddings = cached_content.get('embeddings', [])
                if stored_embeddings:
                    # Calculate cosine similarity
                    similarity = cosine_similarity(query_embedding, stored_embeddings)
                    if similarity >= threshold:
                        relevance_score = max(relevance_score, similarity)
            
            # Include result if relevant
            if relevance_score > 0.1:  # Minimum relevance threshold
                results.append({
                    'linkId': link_id,
                    'url': link_data.get('url'),
                    'title': cached_content.get('title', link_data.get('title', '')),
                    'content': cached_content.get('content', '')[:300],  # First 300 chars
                    'relevanceScore': relevance_score,
                    'contentType': link_data.get('contentType'),
                    'tags': link_data.get('tags', []),
                    'lastFetched': link_data.get('lastFetched'),
                    'freshness': 'fresh' if cached_content else 'stale',
                    'wordCount': cached_content.get('wordCount', 0)
                })
        
        # Sort by relevance score
        results.sort(key=lambda x: x['relevanceScore'], reverse=True)
        
        return jsonify({
            'status': 'success',
            'links': results[:limit],
            'count': len(results[:limit]),
            'searchType': search_type,
            'query': query,
            'threshold': threshold
        }), 200, headers
        
    except Exception as e:
        logger.error(f"Error searching links: {e}")
        return jsonify({'error': str(e)}), 500, headers
