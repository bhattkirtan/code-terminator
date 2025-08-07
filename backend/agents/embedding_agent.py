"""
EmbeddingAgent - Ingests all uploaded screenshots and generated artifacts early in the flow.
Enables semantic memory across agents for UI, code reuse, and layout consistency.
"""
import logging
import base64
import hashlib
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class EmbeddingAgent:
    def __init__(self):
        self.name = "EmbeddingAgent"
        self.version = "1.0.0"
        self.embeddings_cache = {}
        self.semantic_memory = {}
    
    async def process_screenshot(self, content: bytes, filename: str) -> Dict[str, Any]:
        """
        Process a screenshot and create embeddings for semantic search
        """
        logger.info(f"Processing screenshot: {filename}")
        
        # Create a hash for the content
        content_hash = hashlib.md5(content).hexdigest()
        
        # Check if already processed
        if content_hash in self.embeddings_cache:
            logger.info(f"Screenshot {filename} already processed, returning cached result")
            return self.embeddings_cache[content_hash]
        
        # Encode content to base64 for storage
        encoded_content = base64.b64encode(content).decode('utf-8')
        
        # Extract basic metadata
        metadata = {
            "filename": filename,
            "size": len(content),
            "hash": content_hash,
            "timestamp": datetime.now().isoformat(),
            "format": self._detect_image_format(content)
        }
        
        # Create semantic features (simplified version)
        semantic_features = await self._extract_semantic_features(content, metadata)
        
        # Store in cache and memory
        result = {
            "content": encoded_content,
            "metadata": metadata,
            "semantic_features": semantic_features,
            "embedding_vector": self._create_embedding_vector(semantic_features)
        }
        
        self.embeddings_cache[content_hash] = result
        self._update_semantic_memory(result)
        
        logger.info(f"Screenshot processing completed for {filename}")
        return result
    
    async def find_similar_components(self, query_features: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Find similar UI components based on semantic features
        """
        logger.info("Searching for similar components")
        
        query_vector = self._create_embedding_vector(query_features)
        similarities = []
        
        for content_hash, embedding_data in self.embeddings_cache.items():
            similarity = self._calculate_similarity(query_vector, embedding_data["embedding_vector"])
            if similarity > 0.7:  # Threshold for similarity
                similarities.append({
                    "content_hash": content_hash,
                    "similarity": similarity,
                    "metadata": embedding_data["metadata"],
                    "semantic_features": embedding_data["semantic_features"]
                })
        
        # Sort by similarity score
        similarities.sort(key=lambda x: x["similarity"], reverse=True)
        return similarities[:5]  # Return top 5 matches
    
    async def get_layout_patterns(self) -> List[Dict[str, Any]]:
        """
        Extract common layout patterns from processed screenshots
        """
        patterns = []
        
        for content_hash, data in self.embeddings_cache.items():
            features = data["semantic_features"]
            if features.get("layout_type"):
                patterns.append({
                    "layout_type": features["layout_type"],
                    "components": features.get("ui_components", []),
                    "hierarchy": features.get("hierarchy_depth", 1),
                    "content_hash": content_hash
                })
        
        return patterns
    
    async def store_generated_artifact(self, artifact_type: str, content: Any, metadata: Dict[str, Any]) -> str:
        """
        Store generated artifacts (code, documentation, etc.) for future reference
        """
        logger.info(f"Storing artifact: {artifact_type}")
        
        artifact_id = f"{artifact_type}_{datetime.now().timestamp()}"
        
        artifact_data = {
            "id": artifact_id,
            "type": artifact_type,
            "content": content,
            "metadata": metadata,
            "timestamp": datetime.now().isoformat()
        }
        
        self.semantic_memory[artifact_id] = artifact_data
        return artifact_id
    
    def _detect_image_format(self, content: bytes) -> str:
        """Detect image format from content"""
        if content.startswith(b'\x89PNG'):
            return "PNG"
        elif content.startswith(b'\xff\xd8\xff'):
            return "JPEG"
        elif content.startswith(b'GIF8'):
            return "GIF"
        elif content.startswith(b'RIFF') and b'WEBP' in content[:12]:
            return "WEBP"
        else:
            return "UNKNOWN"
    
    async def _extract_semantic_features(self, content: bytes, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract semantic features from image content
        This is a simplified version - in production, you'd use actual computer vision models
        """
        features = {
            "layout_type": self._infer_layout_type(metadata),
            "ui_components": self._detect_ui_components(content),
            "color_scheme": self._analyze_color_scheme(content),
            "hierarchy_depth": self._estimate_hierarchy_depth(content),
            "text_density": self._estimate_text_density(content),
            "interactive_elements": self._detect_interactive_elements(content)
        }
        
        return features
    
    def _infer_layout_type(self, metadata: Dict[str, Any]) -> str:
        """Infer layout type from filename and other metadata"""
        filename = metadata.get("filename", "").lower()
        
        if "dashboard" in filename:
            return "dashboard"
        elif "form" in filename:
            return "form"
        elif "table" in filename or "list" in filename:
            return "data_table"
        elif "portal" in filename or "home" in filename:
            return "portal"
        elif "detail" in filename or "view" in filename:
            return "detail_view"
        else:
            return "general"
    
    def _detect_ui_components(self, content: bytes) -> List[str]:
        """
        Detect UI components in the image
        Simplified version - would use actual computer vision in production
        """
        # This is a mock implementation
        # In reality, you'd use computer vision to detect actual UI elements
        components = ["header", "navigation", "content_area", "footer"]
        
        # Add random components based on content size (mock logic)
        if len(content) > 100000:  # Larger images might have more components
            components.extend(["sidebar", "cards", "buttons", "forms"])
        
        return components
    
    def _analyze_color_scheme(self, content: bytes) -> Dict[str, Any]:
        """
        Analyze color scheme of the image
        Simplified version - would use actual image processing in production
        """
        return {
            "primary_colors": ["#2196F3", "#FFC107", "#4CAF50"],  # Mock colors
            "scheme_type": "material_design",
            "contrast_ratio": "high"
        }
    
    def _estimate_hierarchy_depth(self, content: bytes) -> int:
        """Estimate UI hierarchy depth"""
        # Mock implementation
        return min(len(content) // 50000 + 2, 5)  # Between 2-5 levels
    
    def _estimate_text_density(self, content: bytes) -> str:
        """Estimate text density in the UI"""
        # Mock implementation
        density_ratio = len(content) % 3
        if density_ratio == 0:
            return "low"
        elif density_ratio == 1:
            return "medium"
        else:
            return "high"
    
    def _detect_interactive_elements(self, content: bytes) -> List[str]:
        """Detect interactive elements in the UI"""
        # Mock implementation
        elements = ["buttons", "links"]
        
        if len(content) > 80000:
            elements.extend(["forms", "dropdowns", "modals"])
        
        return elements
    
    def _create_embedding_vector(self, features: Dict[str, Any]) -> List[float]:
        """
        Create a simple embedding vector from semantic features
        In production, this would use actual embedding models
        """
        vector = []
        
        # Layout type encoding
        layout_types = ["dashboard", "form", "data_table", "portal", "detail_view", "general"]
        layout_vector = [1.0 if features.get("layout_type") == lt else 0.0 for lt in layout_types]
        vector.extend(layout_vector)
        
        # Component encoding
        all_components = ["header", "navigation", "content_area", "footer", "sidebar", "cards", "buttons", "forms"]
        component_vector = [1.0 if comp in features.get("ui_components", []) else 0.0 for comp in all_components]
        vector.extend(component_vector)
        
        # Hierarchy depth (normalized)
        hierarchy = features.get("hierarchy_depth", 1)
        vector.append(hierarchy / 5.0)  # Normalize to 0-1
        
        # Text density encoding
        density_map = {"low": 0.2, "medium": 0.5, "high": 0.8}
        vector.append(density_map.get(features.get("text_density", "medium"), 0.5))
        
        return vector
    
    def _calculate_similarity(self, vector1: List[float], vector2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        if len(vector1) != len(vector2):
            return 0.0
        
        dot_product = sum(a * b for a, b in zip(vector1, vector2))
        magnitude1 = sum(a * a for a in vector1) ** 0.5
        magnitude2 = sum(b * b for b in vector2) ** 0.5
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)
    
    def _update_semantic_memory(self, embedding_data: Dict[str, Any]) -> None:
        """Update semantic memory with new embedding data"""
        content_hash = embedding_data["metadata"]["hash"]
        self.semantic_memory[f"screenshot_{content_hash}"] = {
            "type": "screenshot",
            "data": embedding_data,
            "timestamp": datetime.now().isoformat()
        }
    
    async def get_status(self) -> Dict[str, Any]:
        """Get agent status"""
        return {
            "name": self.name,
            "version": self.version,
            "status": "active",
            "cached_embeddings": len(self.embeddings_cache),
            "memory_entries": len(self.semantic_memory),
            "capabilities": [
                "Screenshot processing",
                "Semantic feature extraction",
                "Component similarity search",
                "Layout pattern analysis",
                "Artifact storage"
            ]
        }