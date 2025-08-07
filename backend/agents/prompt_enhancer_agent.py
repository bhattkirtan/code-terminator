"""
PromptEnhancerAgent - Enriches vague prompts with context (design goals, UX intent, architecture hints)
"""
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class PromptEnhancerAgent:
    def __init__(self):
        self.name = "PromptEnhancerAgent"
        self.version = "1.0.0"
    
    async def enhance_prompt(
        self, 
        user_prompt: str, 
        design_goals: Optional[str] = None,
        ux_intent: Optional[str] = None,
        architecture_hints: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Enhance a user's vague prompt with detailed context and specifications
        """
        logger.info(f"Enhancing prompt: {user_prompt[:100]}...")
        
        enhanced_prompt = {
            "original_prompt": user_prompt,
            "enhanced_description": "",
            "design_goals": design_goals or self._infer_design_goals(user_prompt),
            "ux_intent": ux_intent or self._infer_ux_intent(user_prompt),
            "architecture_hints": architecture_hints or self._infer_architecture_hints(user_prompt),
            "technical_requirements": self._extract_technical_requirements(user_prompt),
            "ui_patterns": self._identify_ui_patterns(user_prompt),
            "accessibility_requirements": self._identify_accessibility_requirements(user_prompt)
        }
        
        # Create enhanced description
        enhanced_prompt["enhanced_description"] = self._create_enhanced_description(enhanced_prompt)
        
        logger.info("Prompt enhancement completed")
        return enhanced_prompt
    
    def _infer_design_goals(self, prompt: str) -> str:
        """Infer design goals from the user prompt"""
        keywords_to_goals = {
            "modern": "Create a modern, clean interface with contemporary design principles",
            "responsive": "Ensure responsive design that works across all device sizes",
            "accessible": "Implement WCAG 2.1 AA compliance for accessibility",
            "professional": "Design a professional, business-appropriate interface",
            "user-friendly": "Focus on intuitive user experience and ease of use",
            "angular": "Follow Angular Material design guidelines and best practices"
        }
        
        goals = []
        prompt_lower = prompt.lower()
        
        for keyword, goal in keywords_to_goals.items():
            if keyword in prompt_lower:
                goals.append(goal)
        
        if not goals:
            goals.append("Create a clean, modern, and user-friendly interface")
        
        return "; ".join(goals)
    
    def _infer_ux_intent(self, prompt: str) -> str:
        """Infer UX intent from the user prompt"""
        if "dashboard" in prompt.lower():
            return "Dashboard interface for data visualization and monitoring"
        elif "form" in prompt.lower():
            return "Form-based interface for data input and validation"
        elif "portal" in prompt.lower():
            return "Portal interface for user management and workflows"
        elif "e-commerce" in prompt.lower() or "shop" in prompt.lower():
            return "E-commerce interface for product browsing and purchasing"
        else:
            return "General-purpose web application interface"
    
    def _infer_architecture_hints(self, prompt: str) -> str:
        """Infer architecture hints from the user prompt"""
        hints = []
        prompt_lower = prompt.lower()
        
        if "angular" in prompt_lower:
            hints.append("Use Angular framework with TypeScript")
        if "component" in prompt_lower:
            hints.append("Implement modular component architecture")
        if "service" in prompt_lower:
            hints.append("Use Angular services for data management")
        if "routing" in prompt_lower:
            hints.append("Implement Angular Router for navigation")
        if "material" in prompt_lower:
            hints.append("Use Angular Material for UI components")
        
        if not hints:
            hints.append("Use Angular best practices with component-based architecture")
        
        return "; ".join(hints)
    
    def _extract_technical_requirements(self, prompt: str) -> list:
        """Extract technical requirements from the prompt"""
        requirements = []
        prompt_lower = prompt.lower()
        
        if "angular" in prompt_lower:
            requirements.append("Angular framework")
        if "typescript" in prompt_lower:
            requirements.append("TypeScript")
        if "scss" in prompt_lower or "sass" in prompt_lower:
            requirements.append("SCSS styling")
        if "material" in prompt_lower:
            requirements.append("Angular Material")
        if "responsive" in prompt_lower:
            requirements.append("Responsive design")
        if "api" in prompt_lower or "rest" in prompt_lower:
            requirements.append("REST API integration")
        
        return requirements
    
    def _identify_ui_patterns(self, prompt: str) -> list:
        """Identify UI patterns mentioned in the prompt"""
        patterns = []
        prompt_lower = prompt.lower()
        
        pattern_keywords = {
            "card": "Card layout pattern",
            "table": "Data table pattern",
            "form": "Form input pattern",
            "navigation": "Navigation pattern",
            "sidebar": "Sidebar navigation pattern",
            "header": "Header/toolbar pattern",
            "footer": "Footer pattern",
            "modal": "Modal dialog pattern",
            "dropdown": "Dropdown menu pattern",
            "tab": "Tab navigation pattern"
        }
        
        for keyword, pattern in pattern_keywords.items():
            if keyword in prompt_lower:
                patterns.append(pattern)
        
        return patterns
    
    def _identify_accessibility_requirements(self, prompt: str) -> list:
        """Identify accessibility requirements"""
        requirements = []
        prompt_lower = prompt.lower()
        
        if "accessible" in prompt_lower or "accessibility" in prompt_lower:
            requirements.extend([
                "WCAG 2.1 AA compliance",
                "Keyboard navigation support",
                "Screen reader compatibility",
                "High contrast support",
                "Focus management"
            ])
        elif "keyboard" in prompt_lower:
            requirements.append("Keyboard navigation support")
        elif "screen reader" in prompt_lower:
            requirements.append("Screen reader compatibility")
        
        return requirements
    
    def _create_enhanced_description(self, enhanced_prompt: Dict[str, Any]) -> str:
        """Create a comprehensive enhanced description"""
        description_parts = [
            f"Enhanced Request: {enhanced_prompt['original_prompt']}",
            f"Design Goals: {enhanced_prompt['design_goals']}",
            f"UX Intent: {enhanced_prompt['ux_intent']}",
            f"Architecture: {enhanced_prompt['architecture_hints']}"
        ]
        
        if enhanced_prompt['technical_requirements']:
            description_parts.append(f"Technical Requirements: {', '.join(enhanced_prompt['technical_requirements'])}")
        
        if enhanced_prompt['ui_patterns']:
            description_parts.append(f"UI Patterns: {', '.join(enhanced_prompt['ui_patterns'])}")
        
        if enhanced_prompt['accessibility_requirements']:
            description_parts.append(f"Accessibility: {', '.join(enhanced_prompt['accessibility_requirements'])}")
        
        return "\n".join(description_parts)
    
    async def get_status(self) -> Dict[str, Any]:
        """Get agent status"""
        return {
            "name": self.name,
            "version": self.version,
            "status": "active",
            "capabilities": [
                "Prompt enhancement",
                "Design goal inference",
                "UX intent analysis",
                "Architecture recommendation",
                "Technical requirement extraction"
            ]
        }