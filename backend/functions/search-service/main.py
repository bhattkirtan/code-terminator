from flask import jsonify, request
import functions_framework
import google.cloud.logging
from google.cloud import firestore
import numpy as np
import json
import logging

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
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
}

def cosine_similarity(vec1, vec2):
    """Calculate cosine similarity between two vectors."""
    vec1 = np.array(vec1)
    vec2 = np.array(vec2)
    
    dot_product = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    
    if norm1 == 0 or norm2 == 0:
        return 0.0
    
    return dot_product / (norm1 * norm2)

@functions_framework.http
def semantic_search(request):
    """Entry point for the snapit search service Google Cloud Function."""
    
    path = request.path
    method = request.method

    logger.info(f"Received request: {method} {path}")

    # Handle CORS preflight
    if method == 'OPTIONS':
        return '', 204, headers

    try:
        # Route handling
        if method == 'POST':
            if path == '/search' or path == '/semantic_search':
                return perform_semantic_search(request)
            elif path == '/search_assets':
                return search_assets(request)
            elif path == '/search_components':
                return search_components(request)
            elif path == '/search_analysis':
                return search_analysis_results(request)
            elif path == '/search_by_complexity':
                return search_by_complexity(request)
            elif path == '/search_ui_images':
                return search_ui_images(request)
            elif path == '/search_assets_by_type':
                return search_assets_by_type(request)
        elif method == 'GET':
            if path.startswith('/search_project/'):
                project_id = path.split('/')[-1]
                return get_project_search_data(project_id)
            elif path.startswith('/search_similar_components/'):
                component_id = path.split('/')[-1]
                project_id = request.args.get('projectId')
                return find_similar_components(component_id, project_id)
                
    except Exception as e:
        logger.error(f"Error processing request: {e}", exc_info=True)
        return jsonify({'error': 'An internal error occurred'}), 500, headers

    return jsonify({'error': 'Not found'}), 404, headers


def perform_semantic_search(request):
    """Perform semantic search using embeddings."""
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400, headers

    try:
        query_embedding = data.get('embedding')
        project_id = data.get('projectId')
        threshold = data.get('threshold', 0.7)
        limit = data.get('limit', 10)
        search_type = data.get('type', 'all')  # 'assets', 'components', 'all'
        
        if not query_embedding or not project_id:
            return jsonify({'error': 'Missing embedding or projectId'}), 400, headers
        
        results = []
        
        # Search in embeddings collection
        if search_type in ['all', 'embeddings']:
            embeddings_ref = db.collection('projects').document(project_id).collection('embeddings')
            embeddings_docs = embeddings_ref.stream()
            
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
                            'type': 'embedding',
                            'sourceType': embedding_data.get('type'),
                            'assetId': embedding_data.get('assetId'),
                            'createdAt': embedding_data.get('createdAt')
                        })
        
        # Search in components if they have embeddings
        if search_type in ['all', 'components']:
            components_ref = db.collection('projects').document(project_id).collection('components')
            components_docs = components_ref.stream()
            
            for doc in components_docs:
                component_data = doc.to_dict()
                component_embedding = component_data.get('embedding', [])
                
                if component_embedding:
                    similarity = cosine_similarity(query_embedding, component_embedding)
                    
                    if similarity >= threshold:
                        results.append({
                            'id': component_data.get('componentId', doc.id),
                            'content': component_data.get('description', f"{component_data.get('type', 'unknown')} component"),
                            'similarity': float(similarity),
                            'type': 'component',
                            'componentType': component_data.get('type'),  # Updated field name
                            'confidence': component_data.get('confidence'),
                            'bbox': component_data.get('bbox'),
                            'analysisId': component_data.get('analysisId'),
                            'assetId': component_data.get('assetId'),
                            'coordinates': component_data.get('coordinates'),
                            'createdAt': component_data.get('createdAt')
                        })
        
        # Sort by similarity (highest first)
        results.sort(key=lambda x: x['similarity'], reverse=True)
        
        # Limit results
        results = results[:limit]
        
        logger.info(f"Search completed. Found {len(results)} results for project {project_id}")
        
        return jsonify({
            'status': 'success',
            'results': results,
            'count': len(results),
            'threshold': threshold,
            'searchType': search_type
        }), 200, headers
        
    except Exception as e:
        logger.error(f"Error performing semantic search: {e}")
        return jsonify({'error': str(e)}), 500, headers


def search_assets(request):
    """Search assets by metadata and properties."""
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400, headers

    try:
        project_id = data.get('projectId')
        filters = data.get('filters', {})
        limit = data.get('limit', 20)
        
        if not project_id:
            return jsonify({'error': 'Missing projectId'}), 400, headers
        
        assets_ref = db.collection('projects').document(project_id).collection('assets')
        
        # Apply filters
        query = assets_ref
        
        if filters.get('type'):
            query = query.where('type', '==', filters['type'])
        
        if filters.get('contentType'):
            query = query.where('contentType', '==', filters['contentType'])
        
        # Execute query
        docs = query.limit(limit).stream()
        
        assets = []
        for doc in docs:
            asset_data = doc.to_dict()
            assets.append({
                'id': doc.id,
                **asset_data
            })
        
        return jsonify({
            'status': 'success',
            'assets': assets,
            'count': len(assets)
        }), 200, headers
        
    except Exception as e:
        logger.error(f"Error searching assets: {e}")
        return jsonify({'error': str(e)}), 500, headers


def search_components(request):
    """Search components by type and properties."""
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400, headers

    try:
        project_id = data.get('projectId')
        filters = data.get('filters', {})
        limit = data.get('limit', 20)
        
        if not project_id:
            return jsonify({'error': 'Missing projectId'}), 400, headers
        
        components_ref = db.collection('projects').document(project_id).collection('components')
        
        # Apply filters
        query = components_ref
        
        if filters.get('componentType'):
            query = query.where('type', '==', filters['componentType'])  # Updated field name
        
        if filters.get('analysisId'):
            query = query.where('analysisId', '==', filters['analysisId'])
        
        if filters.get('assetId'):
            query = query.where('assetId', '==', filters['assetId'])
        
        # Execute query
        docs = query.limit(limit).stream()
        
        components = []
        for doc in docs:
            component_data = doc.to_dict()
            components.append({
                'id': doc.id,
                **component_data
            })
        
        return jsonify({
            'status': 'success',
            'components': components,
            'count': len(components)
        }), 200, headers
        
    except Exception as e:
        logger.error(f"Error searching components: {e}")
        return jsonify({'error': str(e)}), 500, headers


def get_project_search_data(project_id):
    """Get search metadata for a project."""
    try:
        # Get counts of searchable items
        embeddings_count = len(list(db.collection('projects').document(project_id).collection('embeddings').stream()))
        components_count = len(list(db.collection('projects').document(project_id).collection('components').stream()))
        assets_count = len(list(db.collection('projects').document(project_id).collection('assets').stream()))
        analysis_count = len(list(db.collection('projects').document(project_id).collection('ui_analysis').stream()))
        
        # Get project metadata
        project_doc = db.collection('projects').document(project_id).get()
        project_data = project_doc.to_dict() if project_doc.exists else {}
        
        return jsonify({
            'status': 'success',
            'projectId': project_id,
            'searchStats': {
                'embeddings': embeddings_count,
                'components': components_count,
                'assets': assets_count,
                'analyses': analysis_count,
                'totalSearchable': embeddings_count + components_count
            },
            'projectMetadata': {
                'name': project_data.get('name', ''),
                'status': project_data.get('status', ''),
                'settings': project_data.get('settings', {})
            }
        }), 200, headers
        
    except Exception as e:
        logger.error(f"Error getting project search data: {e}")
        return jsonify({'error': str(e)}), 500, headers


def search_analysis_results(request):
    """Search through analysis results and reports."""
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400, headers

    try:
        project_id = data.get('projectId')
        analysis_type = data.get('analysisType')  # 'ui_analysis', 'complexity_analysis', 'heatmaps'
        filters = data.get('filters', {})
        limit = data.get('limit', 20)
        
        if not project_id:
            return jsonify({'error': 'Missing projectId'}), 400, headers
        
        # Determine collections to search
        collections_to_search = ['ui_analysis', 'complexity_analysis', 'heatmaps']
        if analysis_type:
            collections_to_search = [analysis_type] if analysis_type in collections_to_search else []
        
        all_results = []
        
        for collection_name in collections_to_search:
            try:
                query = db.collection('projects').document(project_id).collection(collection_name)
                
                # Apply filters
                if filters.get('analysisType'):
                    query = query.where('analysisType', '==', filters['analysisType'])
                
                if filters.get('status'):
                    query = query.where('status', '==', filters['status'])
                
                # Order by creation date (newest first)
                query = query.order_by('createdAt', direction=firestore.Query.DESCENDING)
                
                docs = query.limit(limit).stream()
                
                for doc in docs:
                    analysis_data = doc.to_dict()
                    all_results.append({
                        'id': doc.id,
                        'collectionType': collection_name,
                        **analysis_data
                    })
                    
            except Exception as e:
                logger.warning(f"Error searching {collection_name}: {e}")
                continue
        
        # Sort all results by creation date
        all_results.sort(key=lambda x: x.get('createdAt', ''), reverse=True)
        
        return jsonify({
            'status': 'success',
            'results': all_results[:limit],
            'count': len(all_results[:limit]),
            'collectionsSearched': collections_to_search
        }), 200, headers
        
    except Exception as e:
        logger.error(f"Error searching analysis results: {e}")
        return jsonify({'error': str(e)}), 500, headers


def search_by_complexity(request):
    """Search components/analyses by complexity score ranges."""
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400, headers

    try:
        project_id = data.get('projectId')
        min_complexity = data.get('minComplexity', 0)
        max_complexity = data.get('maxComplexity', 100)
        limit = data.get('limit', 20)
        
        if not project_id:
            return jsonify({'error': 'Missing projectId'}), 400, headers
        
        results = []
        
        # Search in complexity analysis collection
        complexity_ref = db.collection('projects').document(project_id).collection('complexity_analysis')
        complexity_docs = complexity_ref.stream()
        
        for doc in complexity_docs:
            data_doc = doc.to_dict()
            complexity_metrics = data_doc.get('complexityMetrics', {})
            complexity_score = complexity_metrics.get('complexity_score', 0)
            
            if min_complexity <= complexity_score <= max_complexity:
                results.append({
                    'id': doc.id,
                    'type': 'complexity_analysis',
                    'complexityScore': complexity_score,
                    'complexityMetrics': complexity_metrics,
                    'analysisId': data_doc.get('analysisId'),
                    'componentCount': data_doc.get('componentCount', 0),
                    'createdAt': data_doc.get('createdAt')
                })
        
        # Sort by complexity score
        results.sort(key=lambda x: x['complexityScore'], reverse=True)
        
        return jsonify({
            'status': 'success',
            'results': results[:limit],
            'count': len(results[:limit]),
            'complexityRange': {
                'min': min_complexity,
                'max': max_complexity
            }
        }), 200, headers
        
    except Exception as e:
        logger.error(f"Error searching by complexity: {e}")
        return jsonify({'error': str(e)}), 500, headers


def find_similar_components(component_id, project_id):
    """Find components similar to the given component based on type and characteristics."""
    try:
        if not component_id or not project_id:
            return jsonify({'error': 'Missing componentId or projectId'}), 400, headers
        
        # Get the reference component
        ref_component_doc = db.collection('projects').document(project_id).collection('components').document(component_id).get()
        
        if not ref_component_doc.exists:
            return jsonify({'error': 'Component not found'}), 404, headers
        
        ref_component = ref_component_doc.to_dict()
        ref_type = ref_component.get('type')
        ref_confidence = ref_component.get('confidence', 0)
        ref_bbox = ref_component.get('bbox', [])
        
        # Calculate reference area and aspect ratio
        ref_area = ref_bbox[2] * ref_bbox[3] if len(ref_bbox) >= 4 else 0
        ref_aspect_ratio = ref_bbox[2] / ref_bbox[3] if len(ref_bbox) >= 4 and ref_bbox[3] > 0 else 0
        
        # Search for similar components
        components_ref = db.collection('projects').document(project_id).collection('components')
        all_components = components_ref.stream()
        
        similar_components = []
        
        for doc in all_components:
            if doc.id == component_id:  # Skip the reference component itself
                continue
                
            component_data = doc.to_dict()
            comp_type = component_data.get('type')
            comp_confidence = component_data.get('confidence', 0)
            comp_bbox = component_data.get('bbox', [])
            
            # Calculate similarity score
            similarity_score = 0.0
            
            # Type similarity (exact match gets high score)
            if comp_type == ref_type:
                similarity_score += 0.4
            
            # Confidence similarity
            confidence_diff = abs(comp_confidence - ref_confidence)
            confidence_similarity = max(0, 1 - confidence_diff)
            similarity_score += confidence_similarity * 0.2
            
            # Size and aspect ratio similarity
            if len(comp_bbox) >= 4 and ref_area > 0:
                comp_area = comp_bbox[2] * comp_bbox[3]
                comp_aspect_ratio = comp_bbox[2] / comp_bbox[3] if comp_bbox[3] > 0 else 0
                
                # Area similarity
                area_ratio = min(comp_area, ref_area) / max(comp_area, ref_area)
                similarity_score += area_ratio * 0.2
                
                # Aspect ratio similarity
                if ref_aspect_ratio > 0:
                    aspect_ratio_diff = abs(comp_aspect_ratio - ref_aspect_ratio) / ref_aspect_ratio
                    aspect_similarity = max(0, 1 - aspect_ratio_diff)
                    similarity_score += aspect_similarity * 0.2
            
            # Only include components with reasonable similarity
            if similarity_score >= 0.3:
                similar_components.append({
                    'id': doc.id,
                    'similarity': similarity_score,
                    'type': comp_type,
                    'confidence': comp_confidence,
                    'bbox': comp_bbox,
                    'analysisId': component_data.get('analysisId'),
                    'createdAt': component_data.get('createdAt')
                })
        
        # Sort by similarity score (highest first)
        similar_components.sort(key=lambda x: x['similarity'], reverse=True)
        
        return jsonify({
            'status': 'success',
            'referenceComponent': {
                'id': component_id,
                'type': ref_type,
                'confidence': ref_confidence,
                'bbox': ref_bbox
            },
            'similarComponents': similar_components[:10],  # Limit to top 10
            'count': len(similar_components[:10])
        }), 200, headers
        
    except Exception as e:
        logger.error(f"Error finding similar components: {e}")
        return jsonify({'error': str(e)}), 500, headers


def search_ui_images(request):
    """Search UI images and their analysis results."""
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400, headers

    try:
        project_id = data.get('projectId')
        filters = data.get('filters', {})
        limit = data.get('limit', 20)
        
        if not project_id:
            return jsonify({'error': 'Missing projectId'}), 400, headers
        
        # Search in UI analysis collection for image-based results
        ui_analysis_ref = db.collection('projects').document(project_id).collection('ui_analysis')
        query = ui_analysis_ref
        
        # Apply filters
        if filters.get('imageId'):
            query = query.where('imageId', '==', filters['imageId'])
        
        if filters.get('analysisType'):
            query = query.where('analysisType', '==', filters['analysisType'])
        
        if filters.get('status'):
            query = query.where('status', '==', filters['status'])
        
        # Order by creation date (newest first)
        query = query.order_by('createdAt', direction=firestore.Query.DESCENDING)
        
        docs = query.limit(limit).stream()
        
        ui_images = []
        for doc in docs:
            analysis_data = doc.to_dict()
            ui_images.append({
                'id': doc.id,
                'imageId': analysis_data.get('imageId'),
                'imagePath': f"context/ui-images/{analysis_data.get('imageId')}/image.png",
                'analysisPath': f"context/ui-images/{analysis_data.get('imageId')}/analysis/",
                'analysisResults': analysis_data,
                'componentCount': analysis_data.get('componentCount', 0),
                'complexityScore': analysis_data.get('complexityScore', 0),
                'createdAt': analysis_data.get('createdAt')
            })
        
        return jsonify({
            'status': 'success',
            'uiImages': ui_images,
            'count': len(ui_images),
            'structure': 'Individual folders per UI image with analysis results'
        }), 200, headers
        
    except Exception as e:
        logger.error(f"Error searching UI images: {e}")
        return jsonify({'error': str(e)}), 500, headers


def search_assets_by_type(request):
    """Search assets organized by type in the assets folder."""
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400, headers

    try:
        project_id = data.get('projectId')
        asset_type = data.get('assetType')  # 'css', 'images', 'docs', 'raw'
        filters = data.get('filters', {})
        limit = data.get('limit', 20)
        
        if not project_id:
            return jsonify({'error': 'Missing projectId'}), 400, headers
        
        assets_ref = db.collection('projects').document(project_id).collection('assets')
        
        # Apply filters
        query = assets_ref
        
        if asset_type:
            query = query.where('type', '==', asset_type)
        
        if filters.get('contentType'):
            query = query.where('contentType', '==', filters['contentType'])
        
        if filters.get('size_min'):
            query = query.where('size', '>=', filters['size_min'])
        
        if filters.get('size_max'):
            query = query.where('size', '<=', filters['size_max'])
        
        # Execute query
        docs = query.limit(limit).stream()
        
        assets_by_type = {}
        total_assets = []
        
        for doc in docs:
            asset_data = doc.to_dict()
            asset_type_key = asset_data.get('type', 'unknown')
            asset_path = f"context/assets/{asset_type_key}/{doc.id}"
            
            asset_info = {
                'id': doc.id,
                'assetPath': asset_path,
                'metadata': asset_data,
                'createdAt': asset_data.get('createdAt')
            }
            
            if asset_type_key not in assets_by_type:
                assets_by_type[asset_type_key] = []
            
            assets_by_type[asset_type_key].append(asset_info)
            total_assets.append(asset_info)
        
        return jsonify({
            'status': 'success',
            'assetsByType': assets_by_type,
            'allAssets': total_assets,
            'count': len(total_assets),
            'structure': 'Type-based asset organization in assets folder'
        }), 200, headers
        
    except Exception as e:
        logger.error(f"Error searching assets by type: {e}")
        return jsonify({'error': str(e)}), 500, headers
