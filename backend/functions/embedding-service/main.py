from flask import jsonify, request
import functions_framework
import google.cloud.logging
from google.cloud import firestore, storage
import numpy as np
import cv2
import os
import json
import logging
import datetime
import uuid
import base64
import io
from PIL import Image
from typing import Dict, List, Any, Tuple
import openai

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

# GCS Folder Structure:
# {projectId}/
# ├── dist/                    # Production builds & deployments  
# └── context/                 # Analysis context and results
#     └── {analysisId}/
#         ├── analysis/        # Basic analysis results
#         ├── heatmaps/        # Complexity heatmaps
#         └── comprehensive/   # Comprehensive analysis reports

# Component Detection Classes (Simplified versions from existing code)
class ComponentMatch:
    def __init__(self, component_type: str, confidence: float, bbox: Tuple[int, int, int, int], 
                 match_status: str = "detected"):
        self.component_type = component_type
        self.confidence = confidence
        self.original_bbox = bbox
        self.live_bbox = None
        self.match_status = match_status
        self.similarity_score = 0.0

class AIVisionAnalyzer:
    """AI-powered image analysis for UI components and embeddings"""
    
    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
    
    def detect_ui_components(self, image: np.ndarray) -> List[ComponentMatch]:
        """Detect UI components using computer vision techniques"""
        components = []
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Button detection
        components.extend(self._detect_buttons(image, gray))
        
        # Input field detection
        components.extend(self._detect_input_fields(image, gray))
        
        # Navigation detection
        components.extend(self._detect_navigation(image, gray))
        
        # Card/container detection
        components.extend(self._detect_cards(image, gray))
        
        # Table detection
        components.extend(self._detect_tables(image, gray))
        
        # Text element detection
        components.extend(self._detect_text_elements(image, gray))
        
        return self._merge_overlapping_components(components)
    
    def _detect_buttons(self, image: np.ndarray, gray: np.ndarray) -> List[ComponentMatch]:
        """Detect button components"""
        components = []
        edges = cv2.Canny(gray, 50, 150)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        processed = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
        
        contours, _ = cv2.findContours(processed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            area = w * h
            aspect_ratio = w / h if h > 0 else 0
            
            if (800 <= area <= 20000 and 0.5 <= aspect_ratio <= 8.0 and w >= 40 and h >= 20):
                roi = gray[y:y+h, x:x+w]
                if self._has_button_characteristics(roi):
                    components.append(ComponentMatch("button", 0.8, (x, y, w, h)))
        
        return components
    
    def _has_button_characteristics(self, roi: np.ndarray) -> bool:
        """Check if region has button-like visual characteristics"""
        if roi.size == 0:
            return False
        
        color_variance = np.var(roi)
        edges = cv2.Canny(roi, 50, 150)
        edge_density = np.sum(edges > 0) / max(edges.size, 1)
        
        return (color_variance < 4000 and 0.02 < edge_density < 0.5)
    
    def _detect_input_fields(self, image: np.ndarray, gray: np.ndarray) -> List[ComponentMatch]:
        """Detect input field components"""
        components = []
        edges = cv2.Canny(gray, 30, 100)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
        edges = cv2.dilate(edges, kernel, iterations=1)
        
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            area = w * h
            aspect_ratio = w / h if h > 0 else 0
            
            if (1500 <= area <= 40000 and 3.0 <= aspect_ratio <= 20.0 and w >= 80 and h >= 25):
                components.append(ComponentMatch("input_field", 0.7, (x, y, w, h)))
        
        return components
    
    def _detect_navigation(self, image: np.ndarray, gray: np.ndarray) -> List[ComponentMatch]:
        """Detect navigation components"""
        components = []
        h, w = gray.shape
        
        for y in range(0, min(h//3, 300), 50):
            strip = gray[y:y+100, :]
            edges = cv2.Canny(strip, 50, 150)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            horizontal_elements = []
            for contour in contours:
                x_rel, y_rel, w_rel, h_rel = cv2.boundingRect(contour)
                area = w_rel * h_rel
                aspect_ratio = w_rel / h_rel if h_rel > 0 else 0
                
                if (200 <= area <= 5000 and 1.0 <= aspect_ratio <= 10.0):
                    horizontal_elements.append((x_rel, y_rel, w_rel, h_rel))
            
            if len(horizontal_elements) >= 2:
                all_x = [x for x, y, w, h in horizontal_elements]
                all_y = [y for x, y, w, h in horizontal_elements]
                all_right = [x + w for x, y, w, h in horizontal_elements]
                all_bottom = [y + h for x, y, w, h in horizontal_elements]
                
                nav_x = min(all_x)
                nav_y = y + min(all_y)
                nav_w = max(all_right) - min(all_x)
                nav_h = max(all_bottom) - min(all_y)
                
                components.append(ComponentMatch("navigation", 0.6, (nav_x, nav_y, nav_w, nav_h)))
        
        return components
    
    def _detect_cards(self, image: np.ndarray, gray: np.ndarray) -> List[ComponentMatch]:
        """Detect card/container components"""
        components = []
        edges = cv2.Canny(gray, 30, 100)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        processed = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
        
        contours, _ = cv2.findContours(processed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            area = w * h
            aspect_ratio = w / h if h > 0 else 0
            
            if (5000 <= area <= 200000 and 0.3 <= aspect_ratio <= 5.0 and w >= 100 and h >= 100):
                components.append(ComponentMatch("card", 0.5, (x, y, w, h)))
        
        return components
    
    def _detect_tables(self, image: np.ndarray, gray: np.ndarray) -> List[ComponentMatch]:
        """Detect table components"""
        components = []
        edges = cv2.Canny(gray, 50, 150)
        
        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
        vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 40))
        
        horizontal_lines = cv2.morphologyEx(edges, cv2.MORPH_OPEN, horizontal_kernel)
        vertical_lines = cv2.morphologyEx(edges, cv2.MORPH_OPEN, vertical_kernel)
        table_structure = cv2.bitwise_or(horizontal_lines, vertical_lines)
        
        contours, _ = cv2.findContours(table_structure, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            area = w * h
            
            if area >= 15000:
                components.append(ComponentMatch("table", 0.7, (x, y, w, h)))
        
        return components
    
    def _detect_text_elements(self, image: np.ndarray, gray: np.ndarray) -> List[ComponentMatch]:
        """Detect text/label components"""
        components = []
        adaptive_thresh = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
        
        if np.mean(adaptive_thresh) > 127:
            adaptive_thresh = cv2.bitwise_not(adaptive_thresh)
        
        contours, _ = cv2.findContours(adaptive_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            area = w * h
            aspect_ratio = w / h if h > 0 else 0
            
            if (100 <= area <= 8000 and 1.5 <= aspect_ratio <= 15.0 and w >= 20 and h >= 8):
                components.append(ComponentMatch("text", 0.4, (x, y, w, h)))
        
        return components
    
    def _merge_overlapping_components(self, components: List[ComponentMatch]) -> List[ComponentMatch]:
        """Merge overlapping component detections"""
        if not components:
            return components
        
        merged = []
        used = set()
        
        for i, comp1 in enumerate(components):
            if i in used:
                continue
            
            current_group = [comp1]
            used.add(i)
            
            for j, comp2 in enumerate(components[i+1:], i+1):
                if j in used:
                    continue
                
                if (comp1.component_type == comp2.component_type and 
                    self._boxes_overlap(comp1.original_bbox, comp2.original_bbox)):
                    current_group.append(comp2)
                    used.add(j)
            
            # Merge the group into a single component
            if len(current_group) == 1:
                merged.append(current_group[0])
            else:
                # Merge bounding boxes
                all_x = [comp.original_bbox[0] for comp in current_group]
                all_y = [comp.original_bbox[1] for comp in current_group]
                all_right = [comp.original_bbox[0] + comp.original_bbox[2] for comp in current_group]
                all_bottom = [comp.original_bbox[1] + comp.original_bbox[3] for comp in current_group]
                
                merged_bbox = (
                    min(all_x),
                    min(all_y),
                    max(all_right) - min(all_x),
                    max(all_bottom) - min(all_y)
                )
                
                # Use highest confidence
                best_confidence = max(comp.confidence for comp in current_group)
                
                merged.append(ComponentMatch(
                    current_group[0].component_type,
                    best_confidence,
                    merged_bbox
                ))
        
        return merged
    
    def _boxes_overlap(self, bbox1: Tuple[int, int, int, int], bbox2: Tuple[int, int, int, int], threshold: float = 0.3) -> bool:
        """Check if two bounding boxes overlap significantly"""
        x1, y1, w1, h1 = bbox1
        x2, y2, w2, h2 = bbox2
        
        # Calculate intersection
        left = max(x1, x2)
        top = max(y1, y2)
        right = min(x1 + w1, x2 + w2)
        bottom = min(y1 + h1, y2 + h2)
        
        if left >= right or top >= bottom:
            return False
        
        intersection_area = (right - left) * (bottom - top)
        area1 = w1 * h1
        area2 = w2 * h2
        union_area = area1 + area2 - intersection_area
        
        overlap_ratio = intersection_area / min(area1, area2) if min(area1, area2) > 0 else 0
        return overlap_ratio > threshold
    
    def generate_complexity_heatmap(self, image: np.ndarray) -> Tuple[np.ndarray, Dict[str, Any]]:
        """Generate complexity heatmap for UI analysis"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Edge density analysis
        edges = cv2.Canny(gray, 50, 150)
        kernel = np.ones((15, 15), np.uint8)
        edge_density = cv2.filter2D(edges.astype(np.float32), -1, kernel)
        
        # Texture analysis
        texture = cv2.Laplacian(gray, cv2.CV_64F)
        texture = np.abs(texture)
        texture_density = cv2.filter2D(texture.astype(np.float32), -1, kernel)
        
        # Color variance analysis
        color_var = np.var(image, axis=2)
        color_density = cv2.filter2D(color_var.astype(np.float32), -1, kernel)
        
        # Combine metrics
        complexity_map = (edge_density * 0.4 + texture_density * 0.3 + color_density * 0.3)
        complexity_map = cv2.normalize(complexity_map, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
        
        # Apply colormap for visualization
        heatmap = cv2.applyColorMap(complexity_map, cv2.COLORMAP_JET)
        
        # Calculate complexity metrics
        total_complexity = np.sum(complexity_map)
        avg_complexity = np.mean(complexity_map)
        max_complexity = np.max(complexity_map)
        
        # Find high complexity regions
        high_complexity_threshold = np.percentile(complexity_map, 85)
        high_complexity_regions = np.where(complexity_map > high_complexity_threshold)
        
        metrics = {
            "total_complexity": float(total_complexity),
            "average_complexity": float(avg_complexity),
            "max_complexity": float(max_complexity),
            "high_complexity_pixel_count": len(high_complexity_regions[0]),
            "complexity_score": min(100, (avg_complexity / 255) * 100)
        }
        
        return heatmap, metrics
    
    def generate_embeddings(self, content: str, content_type: str = "text") -> Tuple[List[float], Dict[str, Any]]:
        """Generate embeddings using OpenAI"""
        try:
            if content_type == "text":
                response = self.openai_client.embeddings.create(
                    model="text-embedding-3-small",
                    input=content
                )
                embeddings = response.data[0].embedding
                
                return embeddings, {
                    "model": "text-embedding-3-small",
                    "dimensions": len(embeddings),
                    "tokens_used": response.usage.total_tokens if hasattr(response, 'usage') else 0
                }
            else:
                return [], {"error": "Only text embeddings supported currently"}
                
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            return [], {"error": str(e)}


@functions_framework.http
def embedding_service(request):
    """Entry point for the AI embedding and analysis service."""
    
    path = request.path
    method = request.method

    logger.info(f"Received request: {method} {path}")

    # Handle CORS preflight
    if method == 'OPTIONS':
        return '', 204, headers

    try:
        # Route handling
        if method == 'POST':
            if path == '/analyze_image':
                return analyze_image(request)
            elif path == '/generate_embeddings':
                return generate_embeddings_endpoint(request)
            elif path == '/detect_components':
                return detect_components_endpoint(request)
            elif path == '/generate_heatmap':
                return generate_heatmap_endpoint(request)
            elif path == '/comprehensive_analysis':
                return comprehensive_analysis_endpoint(request)
                
        elif method == 'GET':
            if path.startswith('/get_analysis/'):
                analysis_id = path.split('/')[-1]
                return get_analysis_results(analysis_id)
                
    except Exception as e:
        logger.error(f"Error processing request: {e}", exc_info=True)
        return jsonify({'error': 'An internal error occurred'}), 500, headers

    return jsonify({'error': 'Not found'}), 404, headers


def analyze_image(request):
    """Comprehensive image analysis with component detection and heatmaps"""
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400, headers

    try:
        project_id = data.get('projectId')
        image_url = data.get('imageUrl')
        image_base64 = data.get('imageBase64')
        
        if not project_id:
            return jsonify({"error": "projectId is required"}), 400, headers
        
        if not image_url and not image_base64:
            return jsonify({"error": "Either imageUrl or imageBase64 is required"}), 400, headers
        
        # Load image
        if image_base64:
            # Decode base64 image
            image_data = base64.b64decode(image_base64.split(',')[-1])
            image = Image.open(io.BytesIO(image_data))
            image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        else:
            # Download from URL (implement if needed)
            return jsonify({"error": "URL loading not implemented yet"}), 400, headers
        
        analyzer = AIVisionAnalyzer()
        analysis_id = str(uuid.uuid4())
        
        # Detect components
        components = analyzer.detect_ui_components(image)
        
        # Generate heatmap
        heatmap, complexity_metrics = analyzer.generate_complexity_heatmap(image)
        
        # Save analysis results to GCS
        bucket_name = f"snapit-{project_id}"
        results = save_analysis_to_gcs(bucket_name, analysis_id, image, heatmap, components, complexity_metrics, project_id)
        
        # Store metadata in Firestore
        analysis_data = {
            "analysisId": analysis_id,
            "projectId": project_id,
            "analysisType": "comprehensive_image_analysis",
            "componentCount": len(components),
            "complexityMetrics": complexity_metrics,
            "gcsResults": results,
            "createdAt": datetime.datetime.utcnow(),
            "status": "completed"
        }
        
        # Save to multiple collections
        db.collection('projects').document(project_id).collection('ui_analysis').document(analysis_id).set(analysis_data)
        db.collection('projects').document(project_id).collection('complexity_analysis').document(analysis_id).set({
            **analysis_data,
            "complexityScore": complexity_metrics["complexity_score"]
        })
        
        # Save individual components
        for i, component in enumerate(components):
            component_data = {
                "analysisId": analysis_id,
                "componentId": f"{analysis_id}_comp_{i}",
                "type": component.component_type,
                "confidence": component.confidence,
                "bbox": component.original_bbox,
                "createdAt": datetime.datetime.utcnow()
            }
            db.collection('projects').document(project_id).collection('components').document(component_data["componentId"]).set(component_data)
        
        return jsonify({
            "status": "success",
            "analysisId": analysis_id,
            "componentCount": len(components),
            "complexityScore": complexity_metrics["complexity_score"],
            "gcsResults": results,
            "components": [
                {
                    "type": comp.component_type,
                    "confidence": comp.confidence,
                    "bbox": comp.original_bbox
                } for comp in components
            ]
        }), 200, headers
        
    except Exception as e:
        logger.error(f"Image analysis failed: {e}")
        return jsonify({"error": str(e)}), 500, headers


def generate_embeddings_endpoint(request):
    """Generate embeddings for text content"""
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400, headers

    try:
        content = data.get('content')
        content_type = data.get('type', 'text')
        project_id = data.get('projectId')
        
        if not content or not project_id:
            return jsonify({'error': 'Missing content or projectId'}), 400, headers
        
        analyzer = AIVisionAnalyzer()
        embeddings, metadata = analyzer.generate_embeddings(content, content_type)
        
        if 'error' in metadata:
            return jsonify(metadata), 400, headers
        
        # Save to Firestore
        embedding_id = str(uuid.uuid4())
        embedding_data = {
            'id': embedding_id,
            'content': content,
            'type': content_type,
            'vector': embeddings,
            'dimensions': metadata['dimensions'],
            'model': metadata['model'],
            'tokensUsed': metadata.get('tokens_used', 0),
            'createdAt': datetime.datetime.utcnow()
        }
        
        db.collection('projects').document(project_id).collection('embeddings').document(embedding_id).set(embedding_data)
        
        return jsonify({
            'status': 'success',
            'embeddings': embeddings,
            'dimensions': metadata['dimensions'],
            'model': metadata['model'],
            'embeddingId': embedding_id
        }), 200, headers
        
    except Exception as e:
        logger.error(f"Embedding generation failed: {e}")
        return jsonify({'error': str(e)}), 500, headers


def detect_components_endpoint(request):
    """Detect UI components in an image"""
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400, headers

    try:
        project_id = data.get('projectId')
        image_base64 = data.get('imageBase64')
        
        if not project_id or not image_base64:
            return jsonify({"error": "projectId and imageBase64 are required"}), 400, headers
        
        # Decode image
        image_data = base64.b64decode(image_base64.split(',')[-1])
        image = Image.open(io.BytesIO(image_data))
        image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        analyzer = AIVisionAnalyzer()
        components = analyzer.detect_ui_components(image)
        
        # Create analysis entry
        analysis_id = str(uuid.uuid4())
        analysis_data = {
            "analysisId": analysis_id,
            "projectId": project_id,
            "analysisType": "component_detection",
            "componentCount": len(components),
            "components": [
                {
                    "type": comp.component_type,
                    "confidence": comp.confidence,
                    "bbox": comp.original_bbox
                } for comp in components
            ],
            "createdAt": datetime.datetime.utcnow()
        }
        
        db.collection('projects').document(project_id).collection('ui_analysis').document(analysis_id).set(analysis_data)
        
        return jsonify({
            "status": "success",
            "analysisId": analysis_id,
            "componentCount": len(components),
            "components": analysis_data["components"]
        }), 200, headers
        
    except Exception as e:
        logger.error(f"Component detection failed: {e}")
        return jsonify({"error": str(e)}), 500, headers


def generate_heatmap_endpoint(request):
    """Generate complexity heatmap for an image"""
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400, headers

    try:
        project_id = data.get('projectId')
        image_base64 = data.get('imageBase64')
        
        if not project_id or not image_base64:
            return jsonify({"error": "projectId and imageBase64 are required"}), 400, headers
        
        # Decode image
        image_data = base64.b64decode(image_base64.split(',')[-1])
        image = Image.open(io.BytesIO(image_data))
        image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        analyzer = AIVisionAnalyzer()
        heatmap, complexity_metrics = analyzer.generate_complexity_heatmap(image)
        
        # Save heatmap to GCS
        bucket_name = f"snapit-{project_id}"
        analysis_id = str(uuid.uuid4())
        
        heatmap_url = save_heatmap_to_gcs(bucket_name, analysis_id, heatmap, project_id)
        
        # Save analysis
        heatmap_data = {
            "analysisId": analysis_id,
            "projectId": project_id,
            "analysisType": "complexity_heatmap",
            "complexityMetrics": complexity_metrics,
            "heatmapUrl": heatmap_url,
            "createdAt": datetime.datetime.utcnow()
        }
        
        db.collection('projects').document(project_id).collection('heatmaps').document(analysis_id).set(heatmap_data)
        
        return jsonify({
            "status": "success",
            "analysisId": analysis_id,
            "complexityScore": complexity_metrics["complexity_score"],
            "heatmapUrl": heatmap_url,
            "metrics": complexity_metrics
        }), 200, headers
        
    except Exception as e:
        logger.error(f"Heatmap generation failed: {e}")
        return jsonify({"error": str(e)}), 500, headers


def comprehensive_analysis_endpoint(request):
    """Perform comprehensive analysis including components, embeddings, and heatmaps"""
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400, headers

    try:
        project_id = data.get('projectId')
        image_base64 = data.get('imageBase64')
        description = data.get('description', '')
        
        if not project_id or not image_base64:
            return jsonify({"error": "projectId and imageBase64 are required"}), 400, headers
        
        # Decode image
        image_data = base64.b64decode(image_base64.split(',')[-1])
        image = Image.open(io.BytesIO(image_data))
        image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        analyzer = AIVisionAnalyzer()
        analysis_id = str(uuid.uuid4())
        
        # 1. Component Detection
        components = analyzer.detect_ui_components(image)
        
        # 2. Complexity Heatmap
        heatmap, complexity_metrics = analyzer.generate_complexity_heatmap(image)
        
        # 3. Text Embeddings (if description provided)
        embeddings = []
        embedding_metadata = {}
        if description:
            embeddings, embedding_metadata = analyzer.generate_embeddings(description, "text")
        
        # 4. Save all results to GCS
        bucket_name = f"snapit-{project_id}"
        gcs_results = save_comprehensive_analysis_to_gcs(
            bucket_name, analysis_id, image, heatmap, components, complexity_metrics, description, project_id
        )
        
        # 5. Save to Firestore collections
        comprehensive_data = {
            "analysisId": analysis_id,
            "projectId": project_id,
            "analysisType": "comprehensive_analysis",
            "componentCount": len(components),
            "complexityMetrics": complexity_metrics,
            "embeddingMetadata": embedding_metadata,
            "gcsResults": gcs_results,
            "description": description,
            "createdAt": datetime.datetime.utcnow(),
            "status": "completed"
        }
        
        # Save to multiple collections for different queries
        db.collection('projects').document(project_id).collection('ui_analysis').document(analysis_id).set(comprehensive_data)
        db.collection('projects').document(project_id).collection('complexity_analysis').document(analysis_id).set(comprehensive_data)
        
        if embeddings:
            embedding_doc = {
                "analysisId": analysis_id,
                "content": description,
                "vector": embeddings,
                "dimensions": embedding_metadata.get('dimensions', 0),
                "model": embedding_metadata.get('model', ''),
                "createdAt": datetime.datetime.utcnow()
            }
            db.collection('projects').document(project_id).collection('embeddings').document(analysis_id).set(embedding_doc)
        
        return jsonify({
            "status": "success",
            "analysisId": analysis_id,
            "results": {
                "componentCount": len(components),
                "complexityScore": complexity_metrics["complexity_score"],
                "embeddingDimensions": embedding_metadata.get('dimensions', 0),
                "gcsResults": gcs_results
            },
            "components": [
                {
                    "type": comp.component_type,
                    "confidence": comp.confidence,
                    "bbox": comp.original_bbox
                } for comp in components
            ]
        }), 200, headers
        
    except Exception as e:
        logger.error(f"Comprehensive analysis failed: {e}")
        return jsonify({"error": str(e)}), 500, headers


def get_analysis_results(analysis_id):
    """Retrieve analysis results by ID"""
    try:
        # Search across multiple collections
        collections_to_search = ['ui_analysis', 'complexity_analysis', 'heatmaps']
        
        for collection_name in collections_to_search:
            # Search across all projects (for now)
            docs = db.collection_group(collection_name).where('analysisId', '==', analysis_id).stream()
            
            for doc in docs:
                data = doc.to_dict()
                return jsonify({
                    "status": "success",
                    "analysisId": analysis_id,
                    "data": data
                }), 200, headers
        
        return jsonify({"error": "Analysis not found"}), 404, headers
        
    except Exception as e:
        logger.error(f"Failed to get analysis results: {e}")
        return jsonify({"error": str(e)}), 500, headers


def save_analysis_to_gcs(bucket_name: str, analysis_id: str, original_image: np.ndarray, 
                        heatmap: np.ndarray, components: List[ComponentMatch], 
                        complexity_metrics: Dict[str, Any], project_id: str = None) -> Dict[str, str]:
    """Save analysis results to Google Cloud Storage under context/ folder"""
    try:
        bucket = storage_client.bucket(bucket_name)
        
        results = {}
        
        # Use context folder structure: {projectId}/context/{analysisId}/analysis/
        if project_id:
            base_path = f"{project_id}/context/{analysis_id}/analysis"
        else:
            base_path = f"context/{analysis_id}/analysis"
        
        # Save original image
        _, original_encoded = cv2.imencode('.png', original_image)
        original_blob = bucket.blob(f"{base_path}/original_image.png")
        original_blob.upload_from_string(original_encoded.tobytes(), content_type='image/png')
        results["original_image_url"] = f"gs://{bucket_name}/{original_blob.name}"
        
        # Save heatmap
        _, heatmap_encoded = cv2.imencode('.png', heatmap)
        heatmap_blob = bucket.blob(f"{base_path}/complexity_heatmap.png")
        heatmap_blob.upload_from_string(heatmap_encoded.tobytes(), content_type='image/png')
        results["heatmap_url"] = f"gs://{bucket_name}/{heatmap_blob.name}"
        
        # Save component visualization
        component_vis = create_component_visualization(original_image, components)
        _, comp_encoded = cv2.imencode('.png', component_vis)
        comp_blob = bucket.blob(f"{base_path}/component_visualization.png")
        comp_blob.upload_from_string(comp_encoded.tobytes(), content_type='image/png')
        results["component_visualization_url"] = f"gs://{bucket_name}/{comp_blob.name}"
        
        # Save analysis metadata as JSON
        metadata = {
            "analysis_id": analysis_id,
            "project_id": project_id,
            "component_count": len(components),
            "complexity_metrics": complexity_metrics,
            "components": [
                {
                    "type": comp.component_type,
                    "confidence": comp.confidence,
                    "bbox": comp.original_bbox
                } for comp in components
            ],
            "gcs_folder_structure": f"{project_id}/context/{analysis_id}/",
            "timestamp": datetime.datetime.utcnow().isoformat()
        }
        
        metadata_blob = bucket.blob(f"{base_path}/metadata.json")
        metadata_blob.upload_from_string(json.dumps(metadata, indent=2), content_type='application/json')
        results["metadata_url"] = f"gs://{bucket_name}/{metadata_blob.name}"
        
        return results
        
    except Exception as e:
        logger.error(f"Failed to save analysis to GCS: {e}")
        return {"error": str(e)}


def save_heatmap_to_gcs(bucket_name: str, analysis_id: str, heatmap: np.ndarray, project_id: str = None) -> str:
    """Save heatmap to Google Cloud Storage under context/ folder"""
    try:
        bucket = storage_client.bucket(bucket_name)
        
        # Use context folder structure: {projectId}/context/{analysisId}/heatmaps/
        if project_id:
            base_path = f"{project_id}/context/{analysis_id}/heatmaps"
        else:
            base_path = f"context/{analysis_id}/heatmaps"
        
        _, heatmap_encoded = cv2.imencode('.png', heatmap)
        heatmap_blob = bucket.blob(f"{base_path}/complexity_heatmap.png")
        heatmap_blob.upload_from_string(heatmap_encoded.tobytes(), content_type='image/png')
        
        return f"gs://{bucket_name}/{heatmap_blob.name}"
        
    except Exception as e:
        logger.error(f"Failed to save heatmap to GCS: {e}")
        return ""


def save_comprehensive_analysis_to_gcs(bucket_name: str, analysis_id: str, original_image: np.ndarray,
                                     heatmap: np.ndarray, components: List[ComponentMatch],
                                     complexity_metrics: Dict[str, Any], description: str, project_id: str = None) -> Dict[str, str]:
    """Save comprehensive analysis results to GCS under context/ folder"""
    try:
        bucket = storage_client.bucket(bucket_name)
        results = {}
        
        # Create analysis folder structure under context: {projectId}/context/{analysisId}/comprehensive/
        if project_id:
            base_path = f"{project_id}/context/{analysis_id}/comprehensive"
        else:
            base_path = f"context/{analysis_id}/comprehensive"
        
        # Save original image
        _, original_encoded = cv2.imencode('.png', original_image)
        original_blob = bucket.blob(f"{base_path}/original_image.png")
        original_blob.upload_from_string(original_encoded.tobytes(), content_type='image/png')
        results["original_image"] = f"gs://{bucket_name}/{original_blob.name}"
        
        # Save heatmap
        _, heatmap_encoded = cv2.imencode('.png', heatmap)
        heatmap_blob = bucket.blob(f"{base_path}/complexity_heatmap.png")
        heatmap_blob.upload_from_string(heatmap_encoded.tobytes(), content_type='image/png')
        results["heatmap"] = f"gs://{bucket_name}/{heatmap_blob.name}"
        
        # Save component visualization
        component_vis = create_component_visualization(original_image, components)
        _, comp_encoded = cv2.imencode('.png', component_vis)
        comp_blob = bucket.blob(f"{base_path}/component_detection.png")
        comp_blob.upload_from_string(comp_encoded.tobytes(), content_type='image/png')
        results["component_visualization"] = f"gs://{bucket_name}/{comp_blob.name}"
        
        # Save comprehensive report
        report = {
            "analysis_id": analysis_id,
            "project_id": project_id,
            "description": description,
            "gcs_folder_structure": f"{project_id}/context/{analysis_id}/",
            "component_analysis": {
                "total_components": len(components),
                "component_types": list(set(comp.component_type for comp in components)),
                "components_detail": [
                    {
                        "type": comp.component_type,
                        "confidence": comp.confidence,
                        "bbox": comp.original_bbox,
                        "area": comp.original_bbox[2] * comp.original_bbox[3]
                    } for comp in components
                ]
            },
            "complexity_analysis": complexity_metrics,
            "recommendations": generate_analysis_recommendations(components, complexity_metrics),
            "timestamp": datetime.datetime.utcnow().isoformat()
        }
        
        report_blob = bucket.blob(f"{base_path}/comprehensive_report.json")
        report_blob.upload_from_string(json.dumps(report, indent=2), content_type='application/json')
        results["comprehensive_report"] = f"gs://{bucket_name}/{report_blob.name}"
        
        return results
        
    except Exception as e:
        logger.error(f"Failed to save comprehensive analysis to GCS: {e}")
        return {"error": str(e)}


def create_component_visualization(image: np.ndarray, components: List[ComponentMatch]) -> np.ndarray:
    """Create visualization of detected components"""
    vis_image = image.copy()
    
    colors = {
        "button": (0, 255, 0),        # Green
        "input_field": (255, 0, 0),   # Blue
        "navigation": (0, 0, 255),    # Red
        "table": (255, 255, 0),       # Cyan
        "card": (255, 0, 255),        # Magenta
        "text": (128, 128, 128),      # Gray
        "unknown": (255, 255, 255)    # White
    }
    
    for comp in components:
        x, y, w, h = comp.original_bbox
        color = colors.get(comp.component_type, colors["unknown"])
        
        # Draw bounding box
        cv2.rectangle(vis_image, (x, y), (x + w, y + h), color, 2)
        
        # Add label
        label = f"{comp.component_type} ({comp.confidence:.2f})"
        cv2.putText(vis_image, label, (x, y - 10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
    
    return vis_image


def generate_analysis_recommendations(components: List[ComponentMatch], 
                                    complexity_metrics: Dict[str, Any]) -> List[str]:
    """Generate recommendations based on analysis results"""
    recommendations = []
    
    # Component-based recommendations
    component_types = [comp.component_type for comp in components]
    component_counts = {comp_type: component_types.count(comp_type) for comp_type in set(component_types)}
    
    if component_counts.get('button', 0) > 10:
        recommendations.append("Consider consolidating buttons or using progressive disclosure")
    
    if component_counts.get('input_field', 0) > 8:
        recommendations.append("Form might be too complex - consider breaking into multiple steps")
    
    if 'navigation' not in component_types:
        recommendations.append("No navigation detected - ensure clear navigation structure")
    
    # Complexity-based recommendations
    complexity_score = complexity_metrics.get('complexity_score', 0)
    
    if complexity_score > 80:
        recommendations.append("High visual complexity detected - consider simplifying design")
    elif complexity_score < 20:
        recommendations.append("Low visual complexity - might need more visual hierarchy")
    
    if not recommendations:
        recommendations.append("Analysis looks good - no major issues detected")
    
    return recommendations
