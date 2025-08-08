import functions_framework
from google.cloud import firestore
import json
from datetime import datetime

# Initialize Firestore client
firestore_client = firestore.Client()

@functions_framework.http
def data_service(request):
    """Cloud Function for CRUD operations on project data."""
    
    # Handle CORS
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '3600'
        }
        return ('', 204, headers)

    headers = {'Access-Control-Allow-Origin': '*'}
    
    try:
        method = request.method
        path = request.path.strip('/')
        
        if method == 'GET':
            # GET /api/data/{projectId}
            if 'api/data/' in path:
                project_id = path.split('/')[-1]
                
                # Get project data
                project_doc = firestore_client.collection('projects').document(project_id).get()
                if not project_doc.exists:
                    return json.dumps({'error': 'Project not found'}), 404, headers
                
                project_data = project_doc.to_dict()
                
                # Get assets
                assets = []
                assets_ref = firestore_client.collection('projects').document(project_id).collection('assets')
                for asset_doc in assets_ref.stream():
                    assets.append(asset_doc.to_dict())
                
                return json.dumps({
                    'project': project_data,
                    'assets': assets
                }), 200, headers
        
        elif method == 'POST':
            # POST /api/data - Create new project
            request_json = request.get_json()
            
            project_id = request_json.get('id') or firestore_client.collection('projects').document().id
            project_data = {
                'id': project_id,
                'name': request_json.get('name', 'Untitled Project'),
                'metadata': request_json.get('metadata', {}),
                'owner': request_json.get('owner'),
                'createdAt': datetime.now(),
                'updatedAt': datetime.now()
            }
            
            firestore_client.collection('projects').document(project_id).set(project_data)
            
            return json.dumps({
                'status': 'success',
                'project': project_data
            }), 201, headers
        
        elif method == 'PUT':
            # PUT /api/data/{id} - Update project
            project_id = path.split('/')[-1]
            request_json = request.get_json()
            
            update_data = {
                'name': request_json.get('name'),
                'metadata': request_json.get('metadata'),
                'updatedAt': datetime.now()
            }
            
            # Remove None values
            update_data = {k: v for k, v in update_data.items() if v is not None}
            
            firestore_client.collection('projects').document(project_id).update(update_data)
            
            return json.dumps({'status': 'success'}), 200, headers
        
        elif method == 'DELETE':
            # DELETE /api/data/{id} - Delete project
            project_id = path.split('/')[-1]
            
            # Delete project and all subcollections
            firestore_client.collection('projects').document(project_id).delete()
            
            return json.dumps({'status': 'success'}), 200, headers
        
        else:
            return json.dumps({'error': 'Method not allowed'}), 405, headers
            
    except Exception as e:
        return json.dumps({'error': str(e)}), 500, headers
