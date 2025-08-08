import functions_framework
from google.cloud import storage, firestore
from PIL import Image
import io
import uuid
import json
from datetime import datetime

# Initialize clients
storage_client = storage.Client()
firestore_client = firestore.Client()
bucket = storage_client.bucket('snapit')

@functions_framework.http
def upload_file(request):
    """Cloud Function to handle file uploads."""
    
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
        # Get project ID from request
        project_id = request.form.get('projectId')
        if not project_id:
            return json.dumps({'error': 'Missing projectId'}), 400, headers
        
        uploaded_files = []
        
        # Process uploaded files
        for file_key in request.files:
            file = request.files[file_key]
            if file.filename == '':
                continue
                
            # Generate unique filename
            file_id = str(uuid.uuid4())
            file_extension = file.filename.split('.')[-1]
            filename = f"{file_id}.{file_extension}"
            
            # Determine storage path
            if file.content_type.startswith('image/'):
                storage_path = f"{project_id}/context/ui-images/{filename}"
            elif 'css' in file.content_type:
                storage_path = f"{project_id}/context/assets/css/{filename}"
            else:
                storage_path = f"{project_id}/context/assets/docs/{filename}"
            
            # Upload to Cloud Storage
            blob = bucket.blob(storage_path)
            blob.upload_from_file(file, content_type=file.content_type)
            blob.make_public()
            
            # Get public URL
            public_url = blob.public_url
            
            # Save metadata to Firestore
            doc_ref = firestore_client.collection('projects').document(project_id).collection('assets').document(file_id)
            doc_ref.set({
                'id': file_id,
                'projectId': project_id,
                'type': 'image' if file.content_type.startswith('image/') else 'document',
                'originalName': file.filename,
                'fileName': filename,
                'url': public_url,
                'contentType': file.content_type,
                'createdAt': datetime.now()
            })
            
            uploaded_files.append({
                'id': file_id,
                'url': public_url,
                'name': file.filename
            })
        
        return json.dumps({
            'status': 'success',
            'uploadedFiles': uploaded_files
        }), 200, headers
        
    except Exception as e:
        return json.dumps({'error': str(e)}), 500, headers
