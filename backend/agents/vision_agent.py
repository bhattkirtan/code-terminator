"""Vision Agent for analyzing UI screenshots using AI vision models."""

import base64
import json
from typing import Any, Dict, List

import openai
from anthropic import Anthropic
from PIL import Image

from config.settings import settings
from shared.models import AgentResult, UIElement, UIElementType, LayoutStructure
from shared.utils import estimate_tokens
from .base_agent import BaseAgent


class VisionAgent(BaseAgent):
    """Agent that analyzes screenshots to extract UI elements and layout."""
    
    def __init__(self):
        super().__init__("VisionAgent")
        self.openai_client = None
        self.anthropic_client = None
        
        if settings.openai_api_key:
            self.openai_client = openai.OpenAI(api_key=settings.openai_api_key)
        if settings.anthropic_api_key:
            self.anthropic_client = Anthropic(api_key=settings.anthropic_api_key)
    
    async def process(self, input_data: Dict[str, Any]) -> AgentResult:
        """Process screenshot to extract UI elements."""
        image_path = input_data.get("image_path")
        if not image_path:
            return AgentResult(
                agent_name=self.name,
                success=False,
                error="No image_path provided"
            )
        
        try:
            # Analyze the image
            layout_structure = await self._analyze_screenshot(image_path)
            
            return AgentResult(
                agent_name=self.name,
                success=True,
                output={
                    "layout_structure": layout_structure.dict(),
                    "elements_count": len(layout_structure.elements)
                },
                tokens_used=self._estimate_analysis_tokens(layout_structure),
                carbon_emission=self._calculate_carbon_emission(
                    self._estimate_analysis_tokens(layout_structure),
                    settings.default_vision_model
                )
            )
            
        except Exception as e:
            return AgentResult(
                agent_name=self.name,
                success=False,
                error=f"Vision analysis failed: {str(e)}"
            )
    
    async def _analyze_screenshot(self, image_path: str) -> LayoutStructure:
        """Analyze screenshot using AI vision model."""
        # Convert image to base64
        with open(image_path, "rb") as image_file:
            image_data = base64.b64encode(image_file.read()).decode()
        
        # Create analysis prompt
        prompt = self._create_analysis_prompt()
        
        # Use OpenAI GPT-4 Vision if available
        if self.openai_client and "gpt-4" in settings.default_vision_model:
            response = await self._analyze_with_openai(image_data, prompt)
        elif self.anthropic_client and "claude" in settings.default_vision_model:
            response = await self._analyze_with_anthropic(image_data, prompt)
        else:
            # Fallback to basic analysis
            response = await self._basic_analysis(image_path)
        
        return self._parse_analysis_response(response)
    
    def _create_analysis_prompt(self) -> str:
        """Create prompt for UI analysis."""
        return """
        Analyze this screenshot of a legacy application interface and extract all UI elements.
        
        For each UI element you identify, provide:
        1. Type (button, input, card, table, navigation, header, footer, sidebar, modal, form, list, chart, image, text)
        2. Label/text content (if visible)
        3. Position (approximate x, y, width, height in pixels)
        4. Properties (color, size, style, etc.)
        5. Confidence level (0.0 to 1.0)
        
        Also determine:
        - Overall layout type (grid, flex, absolute)
        - Whether the design is responsive
        - Accessibility considerations
        
        Return the analysis as a JSON object with this structure:
        {
            "elements": [
                {
                    "type": "button",
                    "label": "Create Phase", 
                    "position": [x, y, width, height],
                    "properties": {"color": "#blue", "size": "medium"},
                    "confidence": 0.95
                }
            ],
            "layout_type": "grid",
            "responsive": true,
            "accessibility": {"has_alt_text": false, "color_contrast": "good"}
        }
        
        Focus on identifying functional elements that would need to be recreated in Angular.
        """
    
    async def _analyze_with_openai(self, image_data: str, prompt: str) -> str:
        """Analyze image using OpenAI GPT-4 Vision."""
        response = self.openai_client.chat.completions.create(
            model=settings.default_vision_model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}
                        }
                    ]
                }
            ],
            max_tokens=2000
        )
        
        return response.choices[0].message.content
    
    async def _analyze_with_anthropic(self, image_data: str, prompt: str) -> str:
        """Analyze image using Anthropic Claude Vision."""
        message = self.anthropic_client.messages.create(
            model=settings.default_vision_model,
            max_tokens=2000,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": image_data
                            }
                        }
                    ]
                }
            ]
        )
        
        return message.content[0].text
    
    async def _basic_analysis(self, image_path: str) -> str:
        """Basic analysis when no AI models are available."""
        # Get image dimensions
        with Image.open(image_path) as img:
            width, height = img.size
        
        # Create a basic mock analysis
        mock_analysis = {
            "elements": [
                {
                    "type": "header",
                    "label": "Application Header",
                    "position": [0, 0, width, 60],
                    "properties": {"background": "#333"},
                    "confidence": 0.8
                },
                {
                    "type": "card",
                    "label": "Main Content Area",
                    "position": [50, 80, width-100, height-150],
                    "properties": {"background": "#fff"},
                    "confidence": 0.7
                },
                {
                    "type": "button",
                    "label": "Action Button",
                    "position": [width-150, height-80, 120, 40],
                    "properties": {"color": "primary"},
                    "confidence": 0.6
                }
            ],
            "layout_type": "grid",
            "responsive": True,
            "accessibility": {"has_alt_text": False, "color_contrast": "unknown"}
        }
        
        return json.dumps(mock_analysis)
    
    def _parse_analysis_response(self, response: str) -> LayoutStructure:
        """Parse the AI response into a LayoutStructure."""
        try:
            # Extract JSON from response
            if "```json" in response:
                json_start = response.find("```json") + 7
                json_end = response.find("```", json_start)
                json_str = response[json_start:json_end]
            elif "{" in response:
                json_start = response.find("{")
                json_end = response.rfind("}") + 1
                json_str = response[json_start:json_end]
            else:
                json_str = response
            
            data = json.loads(json_str)
            
            # Convert to UIElement objects
            elements = []
            for elem_data in data.get("elements", []):
                try:
                    element = UIElement(
                        type=UIElementType(elem_data.get("type", "text")),
                        label=elem_data.get("label", ""),
                        position=elem_data.get("position", [0, 0, 100, 100]),
                        properties=elem_data.get("properties", {}),
                        confidence=elem_data.get("confidence", 0.5)
                    )
                    elements.append(element)
                except ValueError:
                    # Skip invalid element types
                    continue
            
            return LayoutStructure(
                elements=elements,
                layout_type=data.get("layout_type", "grid"),
                responsive=data.get("responsive", True),
                accessibility=data.get("accessibility", {})
            )
            
        except json.JSONDecodeError:
            # Fallback for invalid JSON
            return LayoutStructure(
                elements=[
                    UIElement(
                        type=UIElementType.TEXT,
                        label="Analysis failed - using fallback",
                        position=[0, 0, 100, 100]
                    )
                ]
            )
    
    def _estimate_analysis_tokens(self, layout: LayoutStructure) -> int:
        """Estimate tokens used for analysis."""
        base_tokens = 500  # Base prompt tokens
        elements_tokens = len(layout.elements) * 50  # Approximate tokens per element
        return base_tokens + elements_tokens