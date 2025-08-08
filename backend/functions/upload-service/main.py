import functions_framework
import google.cloud.logging
from google.cloud import firestore, storage
from flask import jsonify
import logging
import uuid
import datetime
import json

# Set up Google Cloud Logging
client = google.cloud.logging.Client()
client.setup_logging()

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# Initialize Firestore client
db = firestore.Client()

# Initialize Cloud Storage client
storage_client = storage.Client()

# CORS headers
headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, DELETE, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
}

@functions_framework.http
def upload_file(request):
    """
    A Google Cloud Function handling file uploads with folder structure:
      - POST /upload - Upload files according to snapit folder structure
    """
    path = request.path
    method = request.method

    logger.info(f"Received request: {method} {path}")

    # Handle CORS preflight
    if method == 'OPTIONS':
        return '', 204, headers

    try:
        if method == 'POST':
            return add_file(request)
        else:
            return jsonify({'error': 'Method not allowed'}), 405, headers

    except Exception as e:
        logger.error(f"Error processing request: {e}", exc_info=True)
        return jsonify({'error': 'An internal error occurred'}), 500, headers

def get_file_storage_path(project_id, file_type, filename):
    """
    Determine storage path based on file type according to snapit folder structure:
    /{projectId}/dist 
    /{projectId}/context/ui-images
    /{projectId}/context/assets/css
    /{projectId}/context/assets/images
    /{projectId}/context/assets/docs
    """
    if file_type.startswith('image/'):
        return f"{project_id}/context/ui-images/{filename}"
    elif 'css' in file_type.lower() or file_type == 'text/css':
        return f"{project_id}/context/assets/css/{filename}"
    elif file_type.startswith('image/') and not file_type.startswith('image/'):
        # Static images (non-UI screenshots)
        return f"{project_id}/context/assets/images/{filename}"
    elif file_type.startswith('application/') or file_type.startswith('text/'):
        return f"{project_id}/context/assets/docs/{filename}"
    else:
        # Default to docs folder
        return f"{project_id}/context/assets/docs/{filename}"

def add_file(request):
    """
    Expects multipart/form-data:
      - 'file': the uploaded file (required)
      - 'projectId': project identifier (required)
      - 'metadata': JSON string with extra info (optional)
    Uploads the file to GCS following snapit folder structure, stores metadata in Firestore.
    """
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400, headers

    upload_file = request.files['file']
    if upload_file.filename == '':
        return jsonify({"error": "No file selected"}), 400, headers

    # Get project ID (required)
    project_id = request.form.get('projectId')
    if not project_id:
        return jsonify({"error": "projectId is required"}), 400, headers

    # Optional: get additional metadata
    raw_metadata = request.form.get('metadata')
    custom_metadata = {}
    if raw_metadata:
        try:
            custom_metadata = json.loads(raw_metadata)
        except json.JSONDecodeError:
            return jsonify({"error": "Invalid JSON in 'metadata' field"}), 400, headers

    original_filename = upload_file.filename
    file_ext = original_filename.split('.')[-1] if '.' in original_filename else ''
    unique_id = str(uuid.uuid4())
    gcs_filename = f"{unique_id}.{file_ext}" if file_ext else unique_id

    # Determine storage path based on file type and snapit structure
    storage_path = get_file_storage_path(project_id, upload_file.content_type, gcs_filename)

    # Get project-specific bucket
    bucket_name = f"snapit-{project_id}"
    bucket = storage_client.bucket(bucket_name)

    # Upload to GCS
    blob = bucket.blob(storage_path)
    blob.upload_from_string(upload_file.read(), content_type=upload_file.content_type)

    # Make file publicly accessible
    blob.make_public()

    # Determine asset type for Firestore
    if upload_file.content_type.startswith('image/'):
        asset_type = 'image'
    elif 'css' in upload_file.content_type.lower():
        asset_type = 'css'
    else:
        asset_type = 'document'

    # Firestore document in projects/{projectId}/assets/{assetId} structure
    asset_data = {
        "id": unique_id,
        "projectId": project_id,
        "type": asset_type,
        "originalName": original_filename,
        "fileName": gcs_filename,
        "storagePath": storage_path,
        "url": blob.public_url,
        "contentType": upload_file.content_type,
        "size": len(upload_file.read()),
        "createdAt": datetime.datetime.utcnow(),
        "updatedAt": datetime.datetime.utcnow(),
        "metadata": custom_metadata,
    }

    # Save to Firestore in the correct collection structure
    doc_ref = db.collection("projects").document(project_id).collection("assets").document(unique_id)
    doc_ref.set(asset_data)

    logger.info(f"File uploaded successfully: {storage_path}")

    return jsonify({
        "status": "success",
        "uploadedFiles": [asset_data],
        "storageUrls": [blob.public_url],
        "count": 1
    }), 200, headers
