"""
LLM-powered Component Anomaly Detection
Uses vision-language models for intelligent UI component analysis
"""

import cv2
import numpy as np
import base64
import json
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
import openai
from PIL import Image
import io

@dataclass
class LLMComponentMatch:
    component_type: str
    description: str
    confidence: float
    bbox: Tuple[int, int, int, int]  # x, y, w, h
    functionality: str
    visual_attributes: Dict[str, Any]
    accessibility_notes: str
    match_status: str = "detected"

class LLMComponentDetector:
    """LLM-powered component detection and analysis"""
    
    def __init__(self, model: str = "gpt-4o"):
        self.model = model
        self.client = openai.OpenAI()
        
    def analyze_components(self, image: np.ndarray, image_type: str = "screenshot") -> List[LLMComponentMatch]:
        """Use LLM to analyze and detect UI components"""
        print(f"🧠 LLM analyzing {image_type} for UI components...")
        
        # Convert image to base64 for LLM
        image_b64 = self._image_to_base64(image)
        
        # Create analysis prompt
        prompt = self._create_analysis_prompt(image_type)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/png;base64,{image_b64}"}
                            }
                        ]
                    }
                ],
                max_tokens=2000,
                temperature=0.1
            )
            
            # Parse LLM response
            components = self._parse_llm_response(response.choices[0].message.content)
            
            print(f"✅ LLM detected {len(components)} components")
            return components
            
        except Exception as e:
            print(f"❌ LLM analysis failed: {e}")
            return []
    
    def _create_analysis_prompt(self, image_type: str) -> str:
        """Create detailed prompt for LLM component analysis"""
        
        return f"""
Analyze this {image_type} and identify all UI components with their exact locations and properties.

For each component you find, provide:
1. Component type (button, input, navigation, table, card, text, image, etc.)
2. Brief description of the component
3. Confidence score (0.0-1.0)
4. Bounding box coordinates (x, y, width, height) in pixels
5. Functionality description
6. Visual attributes (color, size, style)
7. Accessibility considerations

Return your analysis as a JSON array with this structure:
```json
[
  {{
    "component_type": "button",
    "description": "Primary action button with 'Submit' text",
    "confidence": 0.95,
    "bbox": [100, 200, 120, 40],
    "functionality": "Submits form data when clicked",
    "visual_attributes": {{
      "background_color": "blue",
      "text_color": "white",
      "border_radius": "rounded",
      "size": "medium"
    }},
    "accessibility_notes": "Has proper contrast ratio, needs aria-label"
  }}
]
```

Focus on:
- Interactive elements (buttons, links, inputs, dropdowns)
- Navigation components (menus, breadcrumbs, tabs)
- Data display (tables, lists, cards)
- Content sections (headers, sidebars, main content)
- Form elements (inputs, checkboxes, radio buttons)

Be precise with bounding box coordinates and comprehensive in your analysis.
"""
    
    def _image_to_base64(self, image: np.ndarray) -> str:
        """Convert OpenCV image to base64 string"""
        
        # Convert BGR to RGB
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Convert to PIL Image
        pil_image = Image.fromarray(image_rgb)
        
        # Convert to base64
        buffer = io.BytesIO()
        pil_image.save(buffer, format="PNG")
        image_b64 = base64.b64encode(buffer.getvalue()).decode()
        
        return image_b64
    
    def _parse_llm_response(self, response_text: str) -> List[LLMComponentMatch]:
        """Parse LLM response into component matches"""
        
        components = []
        
        try:
            # Extract JSON from response
            start_idx = response_text.find('[')
            end_idx = response_text.rfind(']') + 1
            
            if start_idx == -1 or end_idx == 0:
                print("❌ No valid JSON found in LLM response")
                return components
            
            json_str = response_text[start_idx:end_idx]
            component_data = json.loads(json_str)
            
            for comp in component_data:
                try:
                    component = LLMComponentMatch(
                        component_type=comp.get("component_type", "unknown"),
                        description=comp.get("description", ""),
                        confidence=float(comp.get("confidence", 0.0)),
                        bbox=tuple(comp.get("bbox", [0, 0, 0, 0])),
                        functionality=comp.get("functionality", ""),
                        visual_attributes=comp.get("visual_attributes", {}),
                        accessibility_notes=comp.get("accessibility_notes", "")
                    )
                    components.append(component)
                    
                except Exception as e:
                    print(f"⚠️ Failed to parse component: {e}")
                    continue
            
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse JSON from LLM response: {e}")
            
        return components
    
    def compare_components_llm(self, original_components: List[LLMComponentMatch], 
                              live_components: List[LLMComponentMatch]) -> Dict[str, Any]:
        """Use LLM to intelligently compare components between images"""
        
        print("🧠 LLM comparing components for anomalies...")
        
        # Create comparison prompt
        comparison_prompt = self._create_comparison_prompt(original_components, live_components)
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": comparison_prompt
                    }
                ],
                max_tokens=1500,
                temperature=0.1
            )
            
            # Parse comparison results
            analysis = self._parse_comparison_response(response.choices[0].message.content)
            
            print("✅ LLM component comparison completed")
            return analysis
            
        except Exception as e:
            print(f"❌ LLM comparison failed: {e}")
            return self._fallback_comparison(original_components, live_components)
    
    def _create_comparison_prompt(self, original_components: List[LLMComponentMatch], 
                                 live_components: List[LLMComponentMatch]) -> str:
        """Create prompt for LLM component comparison"""
        
        # Serialize components for LLM
        original_summary = []
        for comp in original_components:
            original_summary.append({
                "type": comp.component_type,
                "description": comp.description,
                "bbox": comp.bbox,
                "functionality": comp.functionality
            })
        
        live_summary = []
        for comp in live_components:
            live_summary.append({
                "type": comp.component_type,
                "description": comp.description,
                "bbox": comp.bbox,
                "functionality": comp.functionality
            })
        
        return f"""
Compare these two sets of UI components and identify anomalies:

ORIGINAL COMPONENTS:
{json.dumps(original_summary, indent=2)}

LIVE COMPONENTS:
{json.dumps(live_summary, indent=2)}

Analyze and return a JSON response with:
1. missing_components: Components in original but not in live
2. extra_components: Components in live but not in original  
3. modified_components: Components that exist in both but have changed
4. position_changes: Components that moved significantly
5. functionality_changes: Components with different behavior
6. accessibility_issues: New accessibility problems
7. overall_assessment: Summary of changes and their impact

For each anomaly, provide:
- component_type
- description of the change
- severity (low/medium/high)
- recommendation for fixing

Focus on:
- Functional equivalence (same purpose, different implementation)
- Layout preservation (components in similar positions)
- User experience impact (missing critical features)
- Accessibility compliance (proper labeling, contrast)

Return as valid JSON.
"""
    
    def _parse_comparison_response(self, response_text: str) -> Dict[str, Any]:
        """Parse LLM comparison response"""
        
        try:
            # Extract JSON from response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx == -1 or end_idx == 0:
                return {"error": "No valid JSON in response"}
            
            json_str = response_text[start_idx:end_idx]
            analysis = json.loads(json_str)
            
            return analysis
            
        except json.JSONDecodeError as e:
            return {"error": f"Failed to parse JSON: {e}"}
    
    def _fallback_comparison(self, original_components: List[LLMComponentMatch], 
                            live_components: List[LLMComponentMatch]) -> Dict[str, Any]:
        """Fallback comparison using simple logic"""
        
        return {
            "missing_components": [],
            "extra_components": [],
            "modified_components": [],
            "overall_assessment": "Fallback analysis - LLM comparison failed",
            "component_count_original": len(original_components),
            "component_count_live": len(live_components)
        }
    
    def generate_llm_report(self, components_original: List[LLMComponentMatch], 
                           components_live: List[LLMComponentMatch], 
                           comparison_result: Dict[str, Any]) -> str:
        """Generate comprehensive report using LLM"""
        
        print("📝 Generating LLM-powered analysis report...")
        
        report_prompt = f"""
Generate a comprehensive UI component analysis report based on this data:

COMPONENT ANALYSIS:
- Original components: {len(components_original)}
- Live components: {len(components_live)}

COMPARISON RESULTS:
{json.dumps(comparison_result, indent=2)}

Create a professional report with:

1. EXECUTIVE SUMMARY
   - Overall accuracy assessment
   - Key findings and impact
   
2. COMPONENT BREAKDOWN
   - Missing functionality
   - Added features
   - Modified elements
   
3. USER EXPERIENCE IMPACT
   - Critical issues affecting usability
   - Accessibility concerns
   - Performance implications
   
4. RECOMMENDATIONS
   - Priority fixes
   - Enhancement opportunities
   - Best practices

5. TECHNICAL DETAILS
   - Specific component changes
   - Implementation notes

Format as markdown with clear sections and actionable insights.
"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": report_prompt
                    }
                ],
                max_tokens=2000,
                temperature=0.2
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"# Component Analysis Report\n\nError generating report: {e}"

class LLMEnhancedAccuracyValidator:
    """Enhanced AccuracyValidator using LLM component detection"""
    
    def __init__(self):
        self.llm_detector = LLMComponentDetector()
        self.traditional_detector = None  # Keep traditional as fallback
        
    def analyze_with_llm(self, original_img: np.ndarray, live_img: np.ndarray) -> Dict[str, Any]:
        """Comprehensive analysis using LLM"""
        
        print("🧠 Starting LLM-enhanced component analysis...")
        
        try:
            # Analyze both images with LLM
            original_components = self.llm_detector.analyze_components(original_img, "original")
            live_components = self.llm_detector.analyze_components(live_img, "live")
            
            # LLM-powered comparison
            comparison_result = self.llm_detector.compare_components_llm(original_components, live_components)
            
            # Generate detailed report
            report = self.llm_detector.generate_llm_report(original_components, live_components, comparison_result)
            
            # Calculate metrics
            component_accuracy = self._calculate_llm_accuracy(comparison_result)
            
            return {
                "original_components": original_components or [],
                "live_components": live_components or [],
                "comparison_analysis": comparison_result or {},
                "component_accuracy": float(component_accuracy) if component_accuracy else 0.0,
                "detailed_report": report or "LLM analysis completed with limited data",
                "analysis_method": "LLM-powered",
                "model_used": self.llm_detector.model
            }
            
        except Exception as e:
            print(f"❌ LLM analysis failed completely: {e}")
            # Return safe fallback structure
            return {
                "original_components": [],
                "live_components": [],
                "comparison_analysis": {
                    "missing_components": [],
                    "extra_components": [],
                    "modified_components": [],
                    "analysis_failed": True,
                    "error": str(e)
                },
                "component_accuracy": 0.0,
                "detailed_report": f"LLM analysis failed: {e}",
                "analysis_method": "LLM-powered (failed)",
                "model_used": self.llm_detector.model
            }
    
    def _calculate_llm_accuracy(self, comparison_result: Dict[str, Any]) -> float:
        """Calculate accuracy score from LLM analysis"""
        
        try:
            missing = len(comparison_result.get("missing_components", []))
            extra = len(comparison_result.get("extra_components", []))
            modified = len(comparison_result.get("modified_components", []))
            
            # Simple scoring - can be enhanced
            total_issues = missing + extra + modified
            
            if total_issues == 0:
                return 100.0
            
            # Penalize missing components more than extra ones
            penalty = (missing * 10) + (extra * 5) + (modified * 7)
            accuracy = max(0, 100 - penalty)
            
            return float(accuracy)
            
        except Exception:
            return 0.0
