"""
Advanced Component Anomaly Detection for AccuracyValidatorAgent
Detects missing, misplaced, or incorrectly implemented UI components
"""

import cv2
import numpy as np
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass

@dataclass
class ComponentMatch:
    component_type: str
    confidence: float
    original_bbox: Tuple[int, int, int, int]  # x, y, w, h
    live_bbox: Tuple[int, int, int, int] = None
    match_status: str = "missing"  # missing, found, misplaced, different
    similarity_score: float = 0.0
    anomalies: List[str] = None

    def __post_init__(self):
        if self.anomalies is None:
            self.anomalies = []

class ComponentAnomalyDetector:
    """Advanced component detection and anomaly analysis"""
    
    def __init__(self):
        self.similarity_threshold = 0.6
        self.position_tolerance = 100
        
    def detect_components(self, image: np.ndarray, image_type: str = "original") -> List[ComponentMatch]:
        """Detect UI components using multiple detection methods"""
        print(f"🔍 Detecting components in {image_type} image...")
        
        components = []
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Method 1: Button detection
        components.extend(self._detect_buttons(image, gray))
        
        # Method 2: Input field detection
        components.extend(self._detect_input_fields(image, gray))
        
        # Method 3: Navigation detection
        components.extend(self._detect_navigation(image, gray))
        
        # Method 4: Card/container detection
        components.extend(self._detect_cards(image, gray))
        
        # Method 5: Table detection
        components.extend(self._detect_tables(image, gray))
        
        # Method 6: Text/label detection
        components.extend(self._detect_text_elements(image, gray))
        
        # Remove duplicates and merge overlapping detections
        components = self._merge_overlapping_components(components)
        
        print(f"✅ Detected {len(components)} components in {image_type} image")
        return components
    
    def _detect_buttons(self, image: np.ndarray, gray: np.ndarray) -> List[ComponentMatch]:
        """Detect button components"""
        components = []
        
        # Use edge detection and morphological operations
        edges = cv2.Canny(gray, 50, 150)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        processed = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
        
        contours, _ = cv2.findContours(processed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            area = w * h
            aspect_ratio = w / h if h > 0 else 0
            
            # Button characteristics: moderate size, rectangular shape
            if (800 <= area <= 20000 and 
                0.5 <= aspect_ratio <= 8.0 and
                w >= 40 and h >= 20):
                
                roi = gray[y:y+h, x:x+w]
                
                # Check for button-like characteristics
                if self._has_button_characteristics(roi):
                    components.append(ComponentMatch(
                        component_type="button",
                        confidence=0.8,
                        original_bbox=(x, y, w, h),
                        match_status="detected"
                    ))
        
        return components
    
    def _has_button_characteristics(self, roi: np.ndarray) -> bool:
        """Check if region has button-like visual characteristics"""
        if roi.size == 0:
            return False
            
        # Check color uniformity (buttons often have solid backgrounds)
        color_variance = np.var(roi)
        
        # Check for moderate edge density
        edges = cv2.Canny(roi, 50, 150)
        edge_density = np.sum(edges > 0) / max(edges.size, 1)
        
        return (color_variance < 4000 and  # Relatively uniform
                0.02 < edge_density < 0.5)      # Some edges but not too many
    
    def _detect_input_fields(self, image: np.ndarray, gray: np.ndarray) -> List[ComponentMatch]:
        """Detect input field components"""
        components = []
        
        # Look for rectangular regions with clear borders
        edges = cv2.Canny(gray, 30, 100)
        
        # Dilate to connect broken lines
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
        edges = cv2.dilate(edges, kernel, iterations=1)
        
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            area = w * h
            aspect_ratio = w / h if h > 0 else 0
            
            # Input field characteristics: rectangular, wider than tall
            if (1500 <= area <= 40000 and 
                3.0 <= aspect_ratio <= 20.0 and
                w >= 80 and h >= 25):
                
                components.append(ComponentMatch(
                    component_type="input_field",
                    confidence=0.7,
                    original_bbox=(x, y, w, h),
                    match_status="detected"
                ))
        
        return components
    
    def _detect_navigation(self, image: np.ndarray, gray: np.ndarray) -> List[ComponentMatch]:
        """Detect navigation components"""
        components = []
        h, w = gray.shape
        
        # Scan horizontal strips for navigation patterns
        strip_height = 100
        for y in range(0, min(h//3, 300), 50):  # Look in top portion
            strip = gray[y:y+strip_height, :]
            
            # Look for horizontal text arrangements
            edges = cv2.Canny(strip, 50, 150)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            horizontal_elements = []
            for contour in contours:
                x_rel, y_rel, w_rel, h_rel = cv2.boundingRect(contour)
                area = w_rel * h_rel
                aspect_ratio = w_rel / h_rel if h_rel > 0 else 0
                
                # Look for text-like elements
                if (200 <= area <= 5000 and 
                    1.0 <= aspect_ratio <= 10.0):
                    horizontal_elements.append((x_rel, y_rel, w_rel, h_rel))
            
            # If we have multiple horizontal elements, it might be navigation
            if len(horizontal_elements) >= 2:
                # Calculate bounding box for the entire navigation
                all_x = [x for x, y, w, h in horizontal_elements]
                all_y = [y for x, y, w, h in horizontal_elements]
                all_right = [x + w for x, y, w, h in horizontal_elements]
                all_bottom = [y + h for x, y, w, h in horizontal_elements]
                
                nav_x = min(all_x)
                nav_y = y + min(all_y)
                nav_w = max(all_right) - min(all_x)
                nav_h = max(all_bottom) - min(all_y)
                
                components.append(ComponentMatch(
                    component_type="navigation",
                    confidence=0.6,
                    original_bbox=(nav_x, nav_y, nav_w, nav_h),
                    match_status="detected"
                ))
        
        return components
    
    def _detect_cards(self, image: np.ndarray, gray: np.ndarray) -> List[ComponentMatch]:
        """Detect card/container components"""
        components = []
        
        # Look for rectangular regions with potential shadows/borders
        edges = cv2.Canny(gray, 30, 100)
        
        # Use larger kernel to capture card boundaries
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        processed = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
        
        contours, _ = cv2.findContours(processed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            area = w * h
            aspect_ratio = w / h if h > 0 else 0
            
            # Card characteristics: larger rectangular areas
            if (5000 <= area <= 200000 and 
                0.3 <= aspect_ratio <= 5.0 and
                w >= 100 and h >= 100):
                
                components.append(ComponentMatch(
                    component_type="card",
                    confidence=0.5,
                    original_bbox=(x, y, w, h),
                    match_status="detected"
                ))
        
        return components
    
    def _detect_tables(self, image: np.ndarray, gray: np.ndarray) -> List[ComponentMatch]:
        """Detect table components"""
        components = []
        
        # Look for grid patterns
        edges = cv2.Canny(gray, 50, 150)
        
        # Detect horizontal and vertical lines
        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
        vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 40))
        
        horizontal_lines = cv2.morphologyEx(edges, cv2.MORPH_OPEN, horizontal_kernel)
        vertical_lines = cv2.morphologyEx(edges, cv2.MORPH_OPEN, vertical_kernel)
        
        # Combine lines to find table structure
        table_structure = cv2.bitwise_or(horizontal_lines, vertical_lines)
        
        contours, _ = cv2.findContours(table_structure, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            area = w * h
            
            if area >= 15000:  # Large enough to be a table
                components.append(ComponentMatch(
                    component_type="table",
                    confidence=0.7,
                    original_bbox=(x, y, w, h),
                    match_status="detected"
                ))
        
        return components
    
    def _detect_text_elements(self, image: np.ndarray, gray: np.ndarray) -> List[ComponentMatch]:
        """Detect text/label components"""
        components = []
        
        # Use adaptive threshold for text detection
        adaptive_thresh = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
        
        # Invert if needed (text should be black on white)
        if np.mean(adaptive_thresh) > 127:
            adaptive_thresh = cv2.bitwise_not(adaptive_thresh)
        
        # Find contours
        contours, _ = cv2.findContours(adaptive_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            area = w * h
            aspect_ratio = w / h if h > 0 else 0
            
            # Text characteristics: moderate size, not too square
            if (100 <= area <= 8000 and 
                1.5 <= aspect_ratio <= 15.0 and
                w >= 20 and h >= 8):
                
                components.append(ComponentMatch(
                    component_type="text",
                    confidence=0.4,
                    original_bbox=(x, y, w, h),
                    match_status="detected"
                ))
        
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
            
            bbox1 = comp1.original_bbox or comp1.live_bbox
            if not bbox1:
                continue
            
            # Find overlapping components of the same type
            overlapping = [comp1]
            used.add(i)
            
            for j, comp2 in enumerate(components[i+1:], i+1):
                if j in used or comp2.component_type != comp1.component_type:
                    continue
                
                bbox2 = comp2.original_bbox or comp2.live_bbox
                if not bbox2:
                    continue
                
                if self._boxes_overlap(bbox1, bbox2, threshold=0.3):
                    overlapping.append(comp2)
                    used.add(j)
            
            # Keep the component with highest confidence
            best_component = max(overlapping, key=lambda c: c.confidence)
            merged.append(best_component)
        
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
        
        if left < right and top < bottom:
            intersection_area = (right - left) * (bottom - top)
            area1 = w1 * h1
            area2 = w2 * h2
            
            # Calculate IoU (Intersection over Union)
            union_area = area1 + area2 - intersection_area
            iou = intersection_area / union_area if union_area > 0 else 0
            
            return iou >= threshold
        
        return False
    
    def compare_components(self, original_components: List[ComponentMatch], live_components: List[ComponentMatch]) -> Dict[str, Any]:
        """Compare components between original and live images to detect anomalies"""
        print("🔍 Analyzing component anomalies...")
        
        anomalies = {
            "missing_components": [],
            "extra_components": [],
            "misplaced_components": [],
            "modified_components": [],
            "component_breakdown": {},
            "summary": {}
        }
        
        # Count components by type
        original_counts = {}
        live_counts = {}
        
        for comp in original_components:
            original_counts[comp.component_type] = original_counts.get(comp.component_type, 0) + 1
        
        for comp in live_components:
            live_counts[comp.component_type] = live_counts.get(comp.component_type, 0) + 1
        
        # Find matches between original and live components
        matched_pairs = []
        used_live = set()
        
        for orig_comp in original_components:
            best_match = None
            best_score = 0
            best_idx = -1
            
            orig_bbox = orig_comp.original_bbox
            
            for i, live_comp in enumerate(live_components):
                if i in used_live or live_comp.component_type != orig_comp.component_type:
                    continue
                
                live_bbox = live_comp.live_bbox or live_comp.original_bbox
                
                # Calculate similarity score
                position_score = self._calculate_position_similarity(orig_bbox, live_bbox)
                size_score = self._calculate_size_similarity(orig_bbox, live_bbox)
                
                total_score = (position_score * 0.7 + size_score * 0.3)
                
                if total_score > best_score and total_score > self.similarity_threshold:
                    best_match = live_comp
                    best_score = total_score
                    best_idx = i
            
            if best_match:
                # Component found
                orig_comp.live_bbox = best_match.live_bbox or best_match.original_bbox
                orig_comp.match_status = "found"
                orig_comp.similarity_score = best_score
                
                if best_score < 0.8:
                    orig_comp.match_status = "modified"
                    anomalies["modified_components"].append(orig_comp)
                
                matched_pairs.append((orig_comp, best_match))
                used_live.add(best_idx)
            else:
                # Component missing
                orig_comp.match_status = "missing"
                anomalies["missing_components"].append(orig_comp)
        
        # Find extra components in live image
        for i, live_comp in enumerate(live_components):
            if i not in used_live:
                live_comp.match_status = "extra"
                anomalies["extra_components"].append(live_comp)
        
        # Generate component breakdown
        all_types = set(original_counts.keys()) | set(live_counts.keys())
        for comp_type in all_types:
            orig_count = original_counts.get(comp_type, 0)
            live_count = live_counts.get(comp_type, 0)
            
            anomalies["component_breakdown"][comp_type] = {
                "original_count": orig_count,
                "live_count": live_count,
                "difference": live_count - orig_count,
                "accuracy": min(orig_count, live_count) / max(orig_count, live_count, 1) * 100
            }
        
        # Generate summary
        total_original = len(original_components)
        total_live = len(live_components)
        total_matched = len(matched_pairs)
        
        anomalies["summary"] = {
            "total_original_components": total_original,
            "total_live_components": total_live,
            "matched_components": total_matched,
            "missing_count": len(anomalies["missing_components"]),
            "extra_count": len(anomalies["extra_components"]),
            "modified_count": len(anomalies["modified_components"]),
            "component_accuracy": total_matched / max(total_original, 1) * 100,
            "component_types_detected": len(all_types)
        }
        
        print(f"✅ Component analysis complete:")
        print(f"   📊 Component Accuracy: {anomalies['summary']['component_accuracy']:.1f}%")
        print(f"   ❌ Missing: {anomalies['summary']['missing_count']}")
        print(f"   ➕ Extra: {anomalies['summary']['extra_count']}")
        print(f"   🔄 Modified: {anomalies['summary']['modified_count']}")
        
        return anomalies
    
    def _calculate_position_similarity(self, bbox1: Tuple[int, int, int, int], bbox2: Tuple[int, int, int, int]) -> float:
        """Calculate position similarity between two bounding boxes"""
        x1, y1, w1, h1 = bbox1
        x2, y2, w2, h2 = bbox2
        
        # Calculate center points
        center1 = (x1 + w1/2, y1 + h1/2)
        center2 = (x2 + w2/2, y2 + h2/2)
        
        # Calculate distance between centers
        distance = np.sqrt((center1[0] - center2[0])**2 + (center1[1] - center2[1])**2)
        
        # Normalize distance
        max_distance = self.position_tolerance * 2
        position_score = max(0, 1 - (distance / max_distance))
        
        return position_score
    
    def _calculate_size_similarity(self, bbox1: Tuple[int, int, int, int], bbox2: Tuple[int, int, int, int]) -> float:
        """Calculate size similarity between two bounding boxes"""
        x1, y1, w1, h1 = bbox1
        x2, y2, w2, h2 = bbox2
        
        area1 = w1 * h1
        area2 = w2 * h2
        
        if area1 == 0 or area2 == 0:
            return 0
        
        # Calculate size ratio
        size_ratio = min(area1, area2) / max(area1, area2)
        
        return size_ratio
    
    def generate_anomaly_report(self, anomalies: Dict[str, Any]) -> str:
        """Generate a detailed anomaly report"""
        report = []
        
        report.append("🔍 COMPONENT ANOMALY DETECTION REPORT")
        report.append("=" * 50)
        
        summary = anomalies["summary"]
        report.append(f"\n📊 Summary:")
        report.append(f"   Original Components: {summary['total_original_components']}")
        report.append(f"   Live Components: {summary['total_live_components']}")
        report.append(f"   Component Accuracy: {summary['component_accuracy']:.1f}%")
        report.append(f"   Component Types: {summary['component_types_detected']}")
        
        # Component breakdown
        if anomalies["component_breakdown"]:
            report.append(f"\n📋 Component Breakdown:")
            for comp_type, data in anomalies["component_breakdown"].items():
                report.append(f"   {comp_type.title()}:")
                report.append(f"     Original: {data['original_count']}, Live: {data['live_count']}")
                report.append(f"     Difference: {data['difference']:+d}, Accuracy: {data['accuracy']:.1f}%")
        
        # Detailed anomalies
        if anomalies["missing_components"]:
            report.append(f"\n❌ Missing Components ({len(anomalies['missing_components'])}):")
            for comp in anomalies["missing_components"]:
                bbox = comp.original_bbox
                report.append(f"   • {comp.component_type.title()} at ({bbox[0]}, {bbox[1]}) - {bbox[2]}x{bbox[3]}")
        
        if anomalies["extra_components"]:
            report.append(f"\n➕ Extra Components ({len(anomalies['extra_components'])}):")
            for comp in anomalies["extra_components"]:
                bbox = comp.live_bbox or comp.original_bbox
                report.append(f"   • {comp.component_type.title()} at ({bbox[0]}, {bbox[1]}) - {bbox[2]}x{bbox[3]}")
        
        if anomalies["modified_components"]:
            report.append(f"\n🔄 Modified Components ({len(anomalies['modified_components'])}):")
            for comp in anomalies["modified_components"]:
                orig_bbox = comp.original_bbox
                live_bbox = comp.live_bbox
                report.append(f"   • {comp.component_type.title()} - Similarity: {comp.similarity_score:.1%}")
                report.append(f"     Original: ({orig_bbox[0]}, {orig_bbox[1]}) - {orig_bbox[2]}x{orig_bbox[3]}")
                if live_bbox:
                    report.append(f"     Live: ({live_bbox[0]}, {live_bbox[1]}) - {live_bbox[2]}x{live_bbox[3]}")
        
        return "\n".join(report)
