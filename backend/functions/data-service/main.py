from flask import jsonify, request
import functions_framework
import google.cloud.logging
from google.cloud import firestore
import os
import json
import logging
import datetime

# Set up Google Cloud Logging
client = google.cloud.logging.Client()
client.setup_logging()

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# Initialize Firestore client
db = firestore.Client()

# CORS headers
headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
}

# Define Firestore collections for AI DevOps Agent Platform
COLLECTIONS = {
    # Core Project Collections
    "projects": "projects",
    "assets": "assets",
    "embeddings": "embeddings",
    "components": "components",
    "heatmaps": "heatmaps",
    "metadata": "metadata",
    
    # Agent Execution & Timeline Collections
    "agent_executions": "agent_executions",        # Time-stamped agent runs
    "agent_timeline": "agent_timeline",            # Execution traces with diffs
    "prompt_history": "prompt_history",            # Prompt lineage and versions
    "agent_performance": "agent_performance",      # Model latency and metrics
    
    # Version Management Collections
    "project_versions": "project_versions",        # Semantic project versions
    "version_snapshots": "version_snapshots",      # Version rollback data
    "prompt_lineage": "prompt_lineage",            # Prompt change tracking
    "code_diffs": "code_diffs",                   # Code change history
    
    # Carbon & Sustainability Collections
    "carbon_tracking": "carbon_tracking",          # CO2 emissions per model run
    "model_usage": "model_usage",                 # Model usage statistics
    "sustainability_metrics": "sustainability_metrics", # Green coding metrics
    "carbon_reports": "carbon_reports",           # Aggregated carbon reports
    
    # Quality & Validation Collections
    "validation_results": "validation_results",    # Build, test, lint results
    "code_reviews": "code_reviews",               # AI code review results
    "accuracy_validation": "accuracy_validation",  # Visual accuracy scores
    "test_results": "test_results",               # Unit/E2E test outcomes
    "accessibility_checks": "accessibility_checks", # WCAG compliance results
    
    # AI Analysis Collections
    "ui_analysis": "ui_analysis",                 # Vision agent results
    "layout_analysis": "layout_analysis",         # Layout detection data
    "complexity_analysis": "complexity_analysis", # Code complexity scores
    "pattern_detection": "pattern_detection",     # UI pattern recognition
    
    # Documentation & Export Collections
    "documentation": "documentation",             # Auto-generated docs
    "walkthroughs": "walkthroughs",              # AI walkthrough videos
    "export_history": "export_history",          # Export logs and artifacts
    "delivery_checklists": "delivery_checklists", # Project handoff data
    
    # User & Team Collections
    "users": "users",                           # User management
    "teams": "teams",                           # Team collaboration
    "user_preferences": "user_preferences",     # User settings
    "project_permissions": "project_permissions", # Access control
    
    # System & Analytics Collections
    "analytics": "analytics",                   # Usage analytics
    "system_logs": "system_logs",              # System monitoring
    "error_logs": "error_logs",                # Error tracking
    "performance_logs": "performance_logs",    # Performance monitoring
    
    # Test Data & Mock Collections
    "test_data": "test_data",                  # Generated test datasets
    "mock_apis": "mock_apis",                  # API stubs and responses
    "faker_schemas": "faker_schemas",          # Test data generation schemas
    
    # Pipeline & DevOps Collections
    "pipelines": "pipelines",                  # CI/CD pipeline configs
    "deployments": "deployments",             # Deployment history
    "environments": "environments",           # Environment configurations
    "secrets": "secrets",                     # Encrypted secrets storage
}

@functions_framework.http
def data_service(request):
    """Entry point for the snapit data service Google Cloud Function."""
    
    path = request.path
    method = request.method

    logger.info(f"Received request: {method} {path}")

    # Handle CORS preflight
    if method == 'OPTIONS':
        return '', 204, headers

    try:
        # Route handling
        if method == 'GET':
            if path.startswith('/get_data/'):
                parts = path.split('/')
                if len(parts) >= 3:
                    collection_name = parts[2]
                    project_id = parts[3] if len(parts) > 3 else None
                    return get_data(collection_name, project_id)
            elif path.startswith('/get_project/'):
                project_id = path.split('/')[-1]
                return get_project_data(project_id)
                
        elif method == 'POST':
            if path.startswith('/add_data/'):
                collection_name = path.split('/')[-1]
                return add_data(collection_name, request)
            elif path == '/create_project':
                return create_project(request)
            elif path == '/load_data':
                return load_data(request)
                
        elif method == 'DELETE' and path.startswith('/delete_data/'):
            parts = path.split('/')
            collection_name, doc_id = parts[-2], parts[-1]
            project_id = request.args.get('projectId')
            return delete_data(collection_name, doc_id, project_id)
            
        elif method == 'PUT' and path.startswith('/update_data/'):
            parts = path.split('/')
            collection_name, doc_id = parts[-2], parts[-1]
            project_id = request.args.get('projectId')
            return update_data(collection_name, doc_id, request, project_id)
            
    except Exception as e:
        logger.error(f"Error processing request: {e}", exc_info=True)
        return jsonify({'error': 'An internal error occurred'}), 500, headers

    return jsonify({'error': 'Not found'}), 404, headers


def get_data(collection_name, project_id=None):
    """Fetch data from a Firestore collection."""
    if collection_name not in COLLECTIONS.values():
        return jsonify({"error": "Invalid collection name"}), 400, headers

    try:
        # Define which collections are project subcollections
        project_subcollections = [
            'assets', 'embeddings', 'metadata', 'components', 'heatmaps',
            'agent_executions', 'agent_timeline', 'prompt_history', 'agent_performance',
            'project_versions', 'version_snapshots', 'prompt_lineage', 'code_diffs',
            'validation_results', 'code_reviews', 'accuracy_validation',
            'ui_analysis', 'layout_analysis', 'complexity_analysis',
            'documentation', 'walkthroughs', 'export_history',
            'test_data', 'mock_apis'
        ]
        
        if project_id and collection_name in project_subcollections:
            # For subcollections under projects
            docs = db.collection('projects').document(project_id).collection(collection_name).stream()
        else:
            # For top-level collections
            docs = db.collection(collection_name).stream()
            
        data = [{"id": doc.id, **doc.to_dict()} for doc in docs if doc.id != '_metadata']
        
        # Add collection metadata if available
        metadata = None
        if project_id and collection_name in project_subcollections:
            try:
                metadata_doc = db.collection('projects').document(project_id).collection(collection_name).document('_metadata').get()
                if metadata_doc.exists:
                    metadata = metadata_doc.to_dict()
            except:
                pass
        
        response = {
            "collection": collection_name,
            "projectId": project_id,
            "data": data,
            "count": len(data),
            "metadata": metadata,
            "timestamp": datetime.datetime.utcnow().isoformat()
        }
        
        return jsonify(response), 200, headers
        
    except Exception as e:
        logger.error(f"Failed to fetch data from {collection_name}: {e}")
        return jsonify({"error": str(e)}), 500, headers


def get_project_data(project_id):
    """Fetch complete project data including all subcollections."""
    try:
        # Get project document
        project_doc = db.collection('projects').document(project_id).get()
        if not project_doc.exists:
            return jsonify({"error": "Project not found"}), 404, headers
        
        project_data = {"id": project_doc.id, **project_doc.to_dict()}
        
        # Get all subcollections - organized by category
        core_subcollections = ['assets', 'embeddings', 'metadata', 'components', 'heatmaps']
        agent_subcollections = ['agent_executions', 'agent_timeline', 'prompt_history', 'agent_performance']
        version_subcollections = ['project_versions', 'version_snapshots', 'prompt_lineage', 'code_diffs']
        quality_subcollections = ['validation_results', 'code_reviews', 'accuracy_validation']
        analysis_subcollections = ['ui_analysis', 'layout_analysis', 'complexity_analysis']
        carbon_subcollections = ['carbon_tracking']
        export_subcollections = ['documentation', 'walkthroughs', 'export_history']
        test_subcollections = ['test_data', 'mock_apis']
        
        all_subcollections = (core_subcollections + agent_subcollections + 
                            version_subcollections + quality_subcollections + 
                            analysis_subcollections + carbon_subcollections + 
                            export_subcollections + test_subcollections)
        
        # Organize data by categories
        project_data['core'] = {}
        project_data['agents'] = {}
        project_data['versions'] = {}
        project_data['quality'] = {}
        project_data['analysis'] = {}
        project_data['carbon'] = {}
        project_data['exports'] = {}
        project_data['testing'] = {}
        
        # Fetch data for each subcollection
        for subcoll in all_subcollections:
            try:
                docs = db.collection('projects').document(project_id).collection(subcoll).stream()
                # Exclude metadata documents
                data = [{"id": doc.id, **doc.to_dict()} for doc in docs if doc.id != '_metadata']
                
                # Categorize the data
                if subcoll in core_subcollections:
                    project_data['core'][subcoll] = data
                elif subcoll in agent_subcollections:
                    project_data['agents'][subcoll] = data
                elif subcoll in version_subcollections:
                    project_data['versions'][subcoll] = data
                elif subcoll in quality_subcollections:
                    project_data['quality'][subcoll] = data
                elif subcoll in analysis_subcollections:
                    project_data['analysis'][subcoll] = data
                elif subcoll in carbon_subcollections:
                    project_data['carbon'][subcoll] = data
                elif subcoll in export_subcollections:
                    project_data['exports'][subcoll] = data
                elif subcoll in test_subcollections:
                    project_data['testing'][subcoll] = data
                    
            except Exception as e:
                logger.warning(f"Failed to fetch {subcoll} for project {project_id}: {e}")
                # Initialize empty arrays for missing collections
                if subcoll in core_subcollections:
                    project_data['core'][subcoll] = []
                elif subcoll in agent_subcollections:
                    project_data['agents'][subcoll] = []
                elif subcoll in version_subcollections:
                    project_data['versions'][subcoll] = []
                elif subcoll in quality_subcollections:
                    project_data['quality'][subcoll] = []
                elif subcoll in analysis_subcollections:
                    project_data['analysis'][subcoll] = []
                elif subcoll in carbon_subcollections:
                    project_data['carbon'][subcoll] = []
                elif subcoll in export_subcollections:
                    project_data['exports'][subcoll] = []
                elif subcoll in test_subcollections:
                    project_data['testing'][subcoll] = []
        
        # Add summary statistics
        project_data['stats'] = {
            "totalAssets": len(project_data['core'].get('assets', [])),
            "totalExecutions": len(project_data['agents'].get('agent_executions', [])),
            "totalVersions": len(project_data['versions'].get('project_versions', [])),
            "totalCarbonEntries": len(project_data['carbon'].get('carbon_tracking', [])),
            "lastActivity": project_data.get('updatedAt'),
            "qualityScore": calculate_quality_score(project_data['quality']),
            "carbonFootprint": calculate_carbon_footprint(project_data['carbon'])
        }
        
        return jsonify(project_data), 200, headers
        
    except Exception as e:
        logger.error(f"Failed to fetch project data for {project_id}: {e}")
        return jsonify({"error": str(e)}), 500, headers


def calculate_quality_score(quality_data):
    """Calculate overall quality score from validation results."""
    try:
        validation_results = quality_data.get('validation_results', [])
        if not validation_results:
            return 0.0
        
        scores = [result.get('score', 0) for result in validation_results if 'score' in result]
        return sum(scores) / len(scores) if scores else 0.0
    except:
        return 0.0


def calculate_carbon_footprint(carbon_data):
    """Calculate total carbon footprint from tracking data."""
    try:
        carbon_tracking = carbon_data.get('carbon_tracking', [])
        total_emissions = sum(entry.get('carbonEmitted', 0) for entry in carbon_tracking)
        return round(total_emissions, 6)
    except:
        return 0.0


def create_project(request):
    """Create a new project with metadata."""
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400, headers

    try:
        project_id = data.get('id') or db.collection('projects').document().id
        project_data = {
            "id": project_id,
            "name": data.get('name', 'Untitled Project'),
            "description": data.get('description', ''),
            "owner": data.get('owner', ''),
            "status": "initialized",
            "bucketName": f"snapit-{project_id}",
            "createdAt": datetime.datetime.utcnow(),
            "updatedAt": datetime.datetime.utcnow(),
            "metadata": data.get('metadata', {}),
            "settings": {
                "enableEmbeddings": True,
                "enableComponentDetection": True,
                "enableHeatmapGeneration": True,
                "enableCarbonTracking": True,
                "enableVersionControl": True,
                "enableAccuracyValidation": True,
                "autoAnalysis": True,
                "qualityGates": {
                    "accessibilityCheck": True,
                    "performanceCheck": True,
                    "codeReview": True,
                    "testCoverage": 80
                }
            },
            "agentConfig": {
                "enabledAgents": [
                    "PromptEnhancerAgent",
                    "VisionAgent",
                    "LayoutAgent",
                    "StyleAgent",
                    "CodeAgent",
                    "ValidationAgent",
                    "CarbonAgent",
                    "DocumentationAgent"
                ],
                "modelPreferences": {
                    "visionModel": "phi-3-vision",
                    "codeModel": "orca-2-7b",
                    "reviewModel": "phi-3-mini"
                }
            },
            "versionInfo": {
                "currentVersion": "1.0.0",
                "versionCount": 1,
                "lastPromptChange": datetime.datetime.utcnow()
            },
            "carbonMetrics": {
                "totalEmissions": 0.0,
                "modelUsageCount": 0,
                "lastCarbonCalculation": datetime.datetime.utcnow()
            }
        }
        
        doc_ref = db.collection('projects').document(project_id)
        doc_ref.set(project_data)
        
        # Initialize all subcollections with metadata
        subcollections = [
            'assets', 'embeddings', 'metadata', 'components', 'heatmaps',
            'agent_executions', 'agent_timeline', 'prompt_history', 'agent_performance',
            'project_versions', 'version_snapshots', 'prompt_lineage', 'code_diffs',
            'carbon_tracking', 'validation_results', 'code_reviews', 'accuracy_validation',
            'ui_analysis', 'layout_analysis', 'complexity_analysis', 'documentation',
            'walkthroughs', 'export_history', 'test_data', 'mock_apis'
        ]
        
        for subcoll in subcollections:
            metadata_doc = {
                "collectionType": subcoll,
                "projectId": project_id,
                "createdAt": datetime.datetime.utcnow(),
                "count": 0,
                "lastUpdated": datetime.datetime.utcnow(),
                "schema": get_collection_schema(subcoll)
            }
            
            db.collection('projects').document(project_id).collection(subcoll).document('_metadata').set(metadata_doc)
            logger.info(f"Initialized {subcoll} subcollection")
        
        logger.info(f"Project created successfully: {project_id}")
        
        return jsonify({
            "message": "Project created successfully",
            "project": project_data
        }), 201, headers
        
    except Exception as e:
        logger.error(f"Failed to create project: {e}")
        return jsonify({"error": str(e)}), 500, headers


def get_collection_schema(collection_name):
    """Return schema definition for each collection type."""
    schemas = {
        "agent_executions": {
            "agentName": "string",
            "executionId": "string", 
            "startTime": "timestamp",
            "endTime": "timestamp",
            "duration": "number",
            "status": "string",
            "input": "object",
            "output": "object",
            "modelUsed": "string",
            "tokensUsed": "number",
            "carbonEmitted": "number"
        },
        "carbon_tracking": {
            "executionId": "string",
            "agentName": "string",
            "modelName": "string",
            "tokensUsed": "number",
            "energyUsed": "number",
            "carbonEmitted": "number",
            "timestamp": "timestamp",
            "region": "string"
        },
        "project_versions": {
            "version": "string",
            "description": "string",
            "changes": "array",
            "createdBy": "string",
            "createdAt": "timestamp",
            "isStable": "boolean",
            "rollbackData": "object"
        },
        "validation_results": {
            "validationType": "string",
            "status": "string",
            "score": "number",
            "issues": "array",
            "suggestions": "array",
            "timestamp": "timestamp",
            "executionId": "string"
        },
        # Add more schemas as needed
        "default": {
            "id": "string",
            "createdAt": "timestamp",
            "updatedAt": "timestamp"
        }
    }
    
    return schemas.get(collection_name, schemas["default"])


def add_data(collection_name, request):
    """Add data to a Firestore collection."""
    if collection_name not in COLLECTIONS.values():
        return jsonify({"error": "Invalid collection name"}), 400, headers

    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400, headers

    try:
        project_id = data.get('projectId')
        
        # Define which collections are project subcollections
        project_subcollections = [
            'assets', 'embeddings', 'metadata', 'components', 'heatmaps',
            'agent_executions', 'agent_timeline', 'prompt_history', 'agent_performance',
            'project_versions', 'version_snapshots', 'prompt_lineage', 'code_diffs',
            'validation_results', 'code_reviews', 'accuracy_validation',
            'ui_analysis', 'layout_analysis', 'complexity_analysis',
            'documentation', 'walkthroughs', 'export_history',
            'test_data', 'mock_apis'
        ]
        
        if project_id and collection_name in project_subcollections:
            # Add to subcollection under project
            doc_ref = db.collection('projects').document(project_id).collection(collection_name).document()
        else:
            # Add to top-level collection
            doc_ref = db.collection(collection_name).document()
        
        # Add timestamps and metadata
        data['createdAt'] = datetime.datetime.utcnow()
        data['updatedAt'] = datetime.datetime.utcnow()
        
        # Add collection-specific metadata
        if collection_name == 'agent_executions':
            data['executionId'] = data.get('executionId', doc_ref.id)
        elif collection_name == 'carbon_tracking':
            data['trackingId'] = data.get('trackingId', doc_ref.id)
        elif collection_name == 'project_versions':
            data['versionId'] = data.get('versionId', doc_ref.id)
        
        doc_ref.set(data)
        
        # Update collection metadata count
        if project_id and collection_name in project_subcollections:
            try:
                metadata_ref = db.collection('projects').document(project_id).collection(collection_name).document('_metadata')
                metadata_ref.update({
                    'count': firestore.Increment(1),
                    'lastUpdated': datetime.datetime.utcnow()
                })
            except:
                # Create metadata if it doesn't exist
                metadata_ref.set({
                    'collectionType': collection_name,
                    'projectId': project_id,
                    'createdAt': datetime.datetime.utcnow(),
                    'count': 1,
                    'lastUpdated': datetime.datetime.utcnow(),
                    'schema': get_collection_schema(collection_name)
                })
        
        return jsonify({
            "message": f"Data added to {collection_name} successfully",
            "id": doc_ref.id,
            "collection": collection_name,
            "projectId": project_id
        }), 201, headers
        
    except Exception as e:
        logger.error(f"Failed to add data to {collection_name}: {e}")
        return jsonify({"error": str(e)}), 500, headers


def delete_data(collection_name, doc_id, project_id=None):
    """Delete a document from a Firestore collection."""
    if collection_name not in COLLECTIONS.values():
        return jsonify({"error": "Invalid collection name"}), 400, headers

    try:
        if project_id and collection_name in ['assets', 'embeddings', 'metadata', 'components', 'heatmaps']:
            doc_ref = db.collection('projects').document(project_id).collection(collection_name).document(doc_id)
        else:
            doc_ref = db.collection(collection_name).document(doc_id)
        
        doc = doc_ref.get()
        
        if doc.exists:
            doc_ref.delete()
            logger.info(f"Document {doc_id} successfully deleted from {collection_name}")
            return jsonify({"message": f"Document {doc_id} deleted from {collection_name}"}), 200, headers
        else:
            return jsonify({"error": f"Document {doc_id} not found"}), 404, headers
            
    except Exception as e:
        logger.error(f"Error deleting document {doc_id} from {collection_name}: {e}")
        return jsonify({"error": str(e)}), 500, headers


def update_data(collection_name, doc_id, request, project_id=None):
    """Update a document in a Firestore collection."""
    if collection_name not in COLLECTIONS.values():
        return jsonify({"error": "Invalid collection name"}), 400, headers

    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400, headers

    try:
        if project_id and collection_name in ['assets', 'embeddings', 'metadata', 'components', 'heatmaps']:
            doc_ref = db.collection('projects').document(project_id).collection(collection_name).document(doc_id)
        else:
            doc_ref = db.collection(collection_name).document(doc_id)
        
        # Add update timestamp
        data['updatedAt'] = datetime.datetime.utcnow()
        
        doc_ref.update(data)
        
        return jsonify({"message": f"Document {doc_id} updated in {collection_name}"}), 200, headers
        
    except Exception as e:
        logger.error(f"Failed to update data in {collection_name}: {e}")
        return jsonify({"error": str(e)}), 500, headers


def load_data(request):
    """Batch load data into Firestore."""
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400, headers

    try:
        project_id = data.get('projectId')
        
        for collection_name, items in data.items():
            if collection_name not in COLLECTIONS.values() or collection_name == 'projectId':
                continue
                
            for item in items:
                if project_id and collection_name in ['assets', 'embeddings', 'metadata', 'components', 'heatmaps']:
                    db.collection('projects').document(project_id).collection(collection_name).document().set(item)
                else:
                    db.collection(collection_name).document().set(item)
                    
        return jsonify({"message": "Data loaded successfully"}), 201, headers
        
    except Exception as e:
        logger.error(f"Failed to load data: {e}")
        return jsonify({"error": str(e)}), 500, headers
