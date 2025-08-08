from flask import jsonify, request
import functions_framework
import google.cloud.logging
from google.cloud import firestore, storage
import logging
import datetime
import uuid

# Set up Google Cloud Logging
client = google.cloud.logging.Client()
client.setup_logging()

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# Initialize clients
db = firestore.Client()
storage_client = storage.Client()

# CORS headers
headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
}

@functions_framework.http
def project_init_service(request):
    """Entry point for the snapit project initialization service."""
    
    path = request.path
    method = request.method

    logger.info(f"Received request: {method} {path}")

    # Handle CORS preflight
    if method == 'OPTIONS':
        return '', 204, headers

    try:
        # Route handling
        if method == 'POST':
            if path == '/start_project' or path == '/init_project':
                return initialize_project(request)
            elif path == '/setup_bucket':
                return setup_project_bucket(request)
        elif method == 'GET':
            if path.startswith('/project_status/'):
                project_id = path.split('/')[-1]
                return get_project_status(project_id)
                
    except Exception as e:
        logger.error(f"Error processing request: {e}", exc_info=True)
        return jsonify({'error': 'An internal error occurred'}), 500, headers

    return jsonify({'error': 'Not found'}), 404, headers


def initialize_project(request):
    """Initialize a new snapit project with bucket and firestore setup."""
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400, headers

    try:
        # Generate project ID if not provided
        project_id = data.get('id') or str(uuid.uuid4())
        project_name = data.get('name', 'Untitled Project')
        user_id = data.get('userId', 'anonymous')
        
        # Create bucket name
        bucket_name = f"snapit-{project_id}"
        
        logger.info(f"Initializing project {project_id} with bucket {bucket_name}")
        
        # Step 1: Create Cloud Storage bucket
        try:
            bucket = storage_client.bucket(bucket_name)
            if not bucket.exists():
                bucket = storage_client.create_bucket(bucket_name)
                logger.info(f"Created bucket: {bucket_name}")
            else:
                logger.info(f"Bucket already exists: {bucket_name}")
        except Exception as e:
            logger.error(f"Failed to create bucket: {e}")
            return jsonify({"error": f"Failed to create bucket: {str(e)}"}), 500, headers
        
        # Step 2: Create folder structure in bucket
        folder_structure = [
            f"{project_id}/dist/",
            f"{project_id}/context/ui-images/",
            f"{project_id}/context/docs/",
            f"{project_id}/context/links/",
            f"{project_id}/context/assets/css/",
            f"{project_id}/context/assets/images/",
            f"{project_id}/context/assets/docs/"
        ]
        
        for folder_path in folder_structure:
            # Create empty placeholder files to establish folder structure
            placeholder_blob = bucket.blob(f"{folder_path}.placeholder")
            placeholder_blob.upload_from_string("", content_type='text/plain')
            logger.info(f"Created folder: {folder_path}")
        
        # Step 3: Create project document in Firestore
        project_data = {
            "id": project_id,
            "name": project_name,
            "description": data.get('description', ''),
            "owner": user_id,
            "status": "initialized",
            "bucketName": bucket_name,
            "createdAt": datetime.datetime.utcnow(),
            "updatedAt": datetime.datetime.utcnow(),
            "metadata": data.get('metadata', {}),
            "settings": {
                "enableEmbeddings": True,
                "enableComponentDetection": True,
                "enableHeatmapGeneration": True,
                "autoAnalysis": True,
                "analysisThreshold": 0.7
            },
            "stats": {
                "totalAssets": 0,
                "processedAssets": 0,
                "embeddings": 0,
                "components": 0,
                "heatmaps": 0
            },
            "folderStructure": folder_structure
        }
        
        # Save to Firestore
        doc_ref = db.collection('projects').document(project_id)
        doc_ref.set(project_data)
        
        # Step 4: Initialize empty subcollections with metadata
        subcollections = ['assets', 'embeddings', 'components', 'heatmaps', 'metadata']
        
        for subcoll in subcollections:
            # Create initial metadata document
            metadata_doc = {
                "collectionType": subcoll,
                "projectId": project_id,
                "createdAt": datetime.datetime.utcnow(),
                "count": 0,
                "lastUpdated": datetime.datetime.utcnow()
            }
            
            db.collection('projects').document(project_id).collection(subcoll).document('_metadata').set(metadata_doc)
            logger.info(f"Initialized {subcoll} subcollection")
        
        # Step 5: Log project creation
        logger.info(f"Project {project_id} initialized successfully")
        
        return jsonify({
            "status": "success",
            "message": "Project initialized successfully",
            "project": project_data,
            "bucketUrl": f"gs://{bucket_name}",
            "nextSteps": [
                "Upload images using the upload service",
                "Trigger embedding generation",
                "Enable component detection",
                "Generate heatmaps"
            ]
        }), 201, headers
        
    except Exception as e:
        logger.error(f"Failed to initialize project: {e}")
        return jsonify({"error": str(e)}), 500, headers


def setup_project_bucket(request):
    """Setup or verify bucket for existing project."""
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400, headers

    try:
        project_id = data.get('projectId')
        if not project_id:
            return jsonify({"error": "projectId is required"}), 400, headers
        
        # Get project from Firestore
        project_doc = db.collection('projects').document(project_id).get()
        if not project_doc.exists:
            return jsonify({"error": "Project not found"}), 404, headers
        
        project_data = project_doc.to_dict()
        bucket_name = project_data.get('bucketName', f"snapit-{project_id}")
        
        # Verify/create bucket
        bucket = storage_client.bucket(bucket_name)
        if not bucket.exists():
            bucket = storage_client.create_bucket(bucket_name)
            logger.info(f"Created missing bucket: {bucket_name}")
        
        # Update project status
        db.collection('projects').document(project_id).update({
            'status': 'bucket_ready',
            'updatedAt': datetime.datetime.utcnow()
        })
        
        return jsonify({
            "status": "success",
            "bucketName": bucket_name,
            "bucketUrl": f"gs://{bucket_name}",
            "message": "Bucket setup completed"
        }), 200, headers
        
    except Exception as e:
        logger.error(f"Failed to setup bucket: {e}")
        return jsonify({"error": str(e)}), 500, headers


def get_project_status(project_id):
    """Get the current status of a project."""
    try:
        # Get project document
        project_doc = db.collection('projects').document(project_id).get()
        if not project_doc.exists:
            return jsonify({"error": "Project not found"}), 404, headers
        
        project_data = project_doc.to_dict()
        
        # Check bucket status
        bucket_name = project_data.get('bucketName')
        bucket_exists = False
        bucket_files_count = 0
        
        if bucket_name:
            try:
                bucket = storage_client.bucket(bucket_name)
                bucket_exists = bucket.exists()
                if bucket_exists:
                    blobs = list(bucket.list_blobs())
                    bucket_files_count = len([b for b in blobs if not b.name.endswith('.placeholder')])
            except Exception as e:
                logger.warning(f"Could not check bucket status: {e}")
        
        # Get subcollection counts
        subcollection_stats = {}
        subcollections = ['assets', 'embeddings', 'components', 'heatmaps']
        
        for subcoll in subcollections:
            try:
                docs = list(db.collection('projects').document(project_id).collection(subcoll).stream())
                # Exclude metadata documents
                count = len([d for d in docs if d.id != '_metadata'])
                subcollection_stats[subcoll] = count
            except Exception as e:
                logger.warning(f"Could not get {subcoll} count: {e}")
                subcollection_stats[subcoll] = 0
        
        status_info = {
            "projectId": project_id,
            "name": project_data.get('name'),
            "status": project_data.get('status'),
            "owner": project_data.get('owner'),
            "createdAt": project_data.get('createdAt'),
            "updatedAt": project_data.get('updatedAt'),
            "bucketStatus": {
                "name": bucket_name,
                "exists": bucket_exists,
                "filesCount": bucket_files_count
            },
            "collections": subcollection_stats,
            "settings": project_data.get('settings', {}),
            "readyForUpload": bucket_exists,
            "readyForAnalysis": subcollection_stats.get('assets', 0) > 0
        }
        
        return jsonify({
            "status": "success",
            "project": status_info
        }), 200, headers
        
    except Exception as e:
        logger.error(f"Failed to get project status: {e}")
        return jsonify({"error": str(e)}), 500, headers
