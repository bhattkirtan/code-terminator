import functions_framework
from google.cloud import firestore
import numpy as np
import json

# Initialize Firestore client
firestore_client = firestore.Client()

def cosine_similarity(vec1, vec2):
    """Calculate cosine similarity between two vectors."""
    vec1 = np.array(vec1)
    vec2 = np.array(vec2)
    
    dot_product = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    
    return dot_product / (norm1 * norm2)

@functions_framework.http
def semantic_search(request):
    """Cloud Function for semantic search using embeddings."""
    
    # Handle CORS
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '3600'
        }
        return ('', 204, headers)

    headers = {'Access-Control-Allow-Origin': '*'}
    
    try:
        request_json = request.get_json()
        
        query_embedding = request_json.get('embedding')
        project_id = request_json.get('projectId')
        threshold = request_json.get('threshold', 0.7)
        limit = request_json.get('limit', 10)
        
        if not query_embedding or not project_id:
            return json.dumps({'error': 'Missing embedding or projectId'}), 400, headers
        
        # Get all embeddings for the project
        embeddings_ref = firestore_client.collection('projects').document(project_id).collection('embeddings')
        embeddings_docs = embeddings_ref.stream()
        
        results = []
        
        for doc in embeddings_docs:
            embedding_data = doc.to_dict()
            stored_embedding = embedding_data.get('vector', [])
            
            if stored_embedding:
                similarity = cosine_similarity(query_embedding, stored_embedding)
                
                if similarity >= threshold:
                    results.append({
                        'id': embedding_data.get('id'),
                        'content': embedding_data.get('content'),
                        'similarity': float(similarity),
                        'type': embedding_data.get('type'),
                        'createdAt': embedding_data.get('createdAt')
                    })
        
        # Sort by similarity (highest first)
        results.sort(key=lambda x: x['similarity'], reverse=True)
        
        # Limit results
        results = results[:limit]
        
        return json.dumps({
            'status': 'success',
            'results': results,
            'count': len(results)
        }), 200, headers
        
    except Exception as e:
        return json.dumps({'error': str(e)}), 500, headers
