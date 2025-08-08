import functions_framework
from google.cloud import firestore
import openai
import json
import os
from datetime import datetime

# Initialize clients
firestore_client = firestore.Client()
openai.api_key = os.environ.get('OPENAI_API_KEY')

@functions_framework.http
def generate_embeddings(request):
    """Cloud Function to generate embeddings for content."""
    
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
        
        content = request_json.get('content')
        content_type = request_json.get('type', 'text')
        project_id = request_json.get('projectId')
        
        if not content or not project_id:
            return json.dumps({'error': 'Missing content or projectId'}), 400, headers
        
        # Generate embeddings using OpenAI
        if content_type == 'text':
            response = openai.embeddings.create(
                model="text-embedding-3-small",
                input=content
            )
            embeddings = response.data[0].embedding
            dimensions = len(embeddings)
            model_used = "text-embedding-3-small"
        else:
            return json.dumps({'error': 'Only text embeddings supported currently'}), 400, headers
        
        # Save to Firestore
        embedding_id = firestore_client.collection('projects').document(project_id).collection('embeddings').document().id
        
        firestore_client.collection('projects').document(project_id).collection('embeddings').document(embedding_id).set({
            'id': embedding_id,
            'content': content,
            'type': content_type,
            'vector': embeddings,
            'dimensions': dimensions,
            'model': model_used,
            'createdAt': datetime.now()
        })
        
        return json.dumps({
            'status': 'success',
            'embeddings': embeddings,
            'dimensions': dimensions,
            'model': model_used,
            'embeddingId': embedding_id
        }), 200, headers
        
    except Exception as e:
        return json.dumps({'error': str(e)}), 500, headers
