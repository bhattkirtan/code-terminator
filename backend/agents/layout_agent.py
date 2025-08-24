"""
LayoutAgent - Translates UI trees into Angular-compatible layout (HTML)
"""
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class LayoutAgent:
    def __init__(self):
        self.name = "LayoutAgent"
        self.version = "1.0.0"
    
    async def generate_layout(self, ui_elements: List[Dict[str, Any]], enhanced_prompt: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate Angular-compatible layout from UI elements
        """
        logger.info("Generating Angular layout from UI elements")
        
        # Sort elements by position (top to bottom, left to right)
        sorted_elements = self._sort_elements_by_position(ui_elements)
        
        # Create layout hierarchy
        layout_tree = self._create_layout_hierarchy(sorted_elements)
        
        # Generate Angular template structure
        template_structure = self._generate_template_structure(layout_tree, enhanced_prompt)
        
        # Generate layout metadata
        layout_metadata = self._generate_layout_metadata(sorted_elements, enhanced_prompt)
        
        result = {
            "layout_tree": layout_tree,
            "template_structure": template_structure,
            "metadata": layout_metadata,
            "breakpoints": self._define_responsive_breakpoints(),
            "grid_system": self._define_grid_system(sorted_elements)
        }
        
        logger.info("Layout generation completed")
        return result
    
    def _sort_elements_by_position(self, elements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Sort elements by their position for logical layout order"""
        def get_sort_key(element):
            pos = element.get("position", {})
            return (pos.get("y", 0), pos.get("x", 0))
        
        return sorted(elements, key=get_sort_key)
    
    def _create_layout_hierarchy(self, elements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create a hierarchical layout tree"""
        # Define typical layout structure
        layout_tree = {
            "type": "app-root",
            "children": []
        }
        
        # Categorize elements by their typical positions
        header_elements = []
        navigation_elements = []
        sidebar_elements = []
        content_elements = []
        footer_elements = []
        
        for element in elements:
            element_type = element.get("type", "")
            pos = element.get("position", {})
            
            if element_type == "header" or pos.get("y", 0) < 100:
                header_elements.append(element)
            elif element_type == "navigation":
                navigation_elements.append(element)
            elif element_type == "sidebar" or pos.get("x", 0) < 250:
                sidebar_elements.append(element)
            elif element_type == "footer" or pos.get("y", 0) > 700:
                footer_elements.append(element)
            else:
                content_elements.append(element)
        
        # Build layout structure
        if header_elements:
            layout_tree["children"].append({
                "type": "header-container",
                "elements": header_elements,
                "angular_component": "app-header"
            })
        
        # Main container
        main_container = {
            "type": "main-container",
            "children": [],
            "angular_component": "app-main"
        }
        
        if navigation_elements:
            main_container["children"].append({
                "type": "navigation-container",
                "elements": navigation_elements,
                "angular_component": "app-navigation"
            })
        
        # Content area with optional sidebar
        content_area = {
            "type": "content-area",
            "children": [],
            "angular_component": "app-content"
        }
        
        if sidebar_elements:
            content_area["children"].append({
                "type": "sidebar-container",
                "elements": sidebar_elements,
                "angular_component": "app-sidebar"
            })
        
        if content_elements:
            content_area["children"].append({
                "type": "main-content",
                "elements": content_elements,
                "angular_component": "app-main-content"
            })
        
        main_container["children"].append(content_area)
        layout_tree["children"].append(main_container)
        
        if footer_elements:
            layout_tree["children"].append({
                "type": "footer-container",
                "elements": footer_elements,
                "angular_component": "app-footer"
            })
        
        return layout_tree
    
    def _generate_template_structure(self, layout_tree: Dict[str, Any], enhanced_prompt: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Angular template structure"""
        
        def generate_template_node(node):
            if "elements" in node:
                # Leaf node with actual UI elements
                return self._generate_element_templates(node["elements"], node.get("angular_component", "div"))
            elif "children" in node:
                # Container node
                children_templates = [generate_template_node(child) for child in node["children"]]
                return {
                    "tag": "div",
                    "class": f"{node['type']} {node.get('angular_component', '')}-container",
                    "children": children_templates,
                    "angular_component": node.get("angular_component")
                }
            else:
                return {"tag": "div", "class": node.get("type", "container")}
        
        return generate_template_node(layout_tree)
    
    def _generate_element_templates(self, elements: List[Dict[str, Any]], container_component: str) -> Dict[str, Any]:
        """Generate template structure for UI elements"""
        templates = []
        
        for element in elements:
            element_type = element.get("type", "div")
            angular_info = element.get("angular_component", {})
            
            template = {
                "tag": angular_info.get("component", "div"),
                "class": f"app-{element_type} {element_type}-element",
                "attributes": self._generate_element_attributes(element),
                "content": element.get("text", ""),
                "angular_directives": self._generate_angular_directives(element),
                "events": self._generate_event_bindings(element)
            }
            
            # Add specific template features based on element type
            if element_type == "table":
                template.update(self._generate_table_template(element))
            elif element_type == "form":
                template.update(self._generate_form_template(element))
            elif element_type == "card":
                template.update(self._generate_card_template(element))
            
            templates.append(template)
        
        return {
            "tag": "div",
            "class": f"{container_component}-container",
            "children": templates,
            "angular_component": container_component
        }
    
    def _generate_element_attributes(self, element: Dict[str, Any]) -> Dict[str, str]:
        """Generate HTML attributes for an element"""
        attributes = {}
        
        # Accessibility attributes
        accessibility = element.get("accessibility", {})
        if accessibility.get("role"):
            attributes["role"] = accessibility["role"]
        if accessibility.get("aria_label"):
            attributes["aria-label"] = accessibility["aria_label"]
        if accessibility.get("aria_modal"):
            attributes["aria-modal"] = "true"
        
        # Add responsive attributes
        responsive = element.get("responsive", {})
        if responsive:
            attributes["[class.mobile]"] = "isMobile"
            attributes["[class.tablet]"] = "isTablet"
            attributes["[class.desktop]"] = "isDesktop"
        
        return attributes
    
    def _generate_angular_directives(self, element: Dict[str, Any]) -> List[str]:
        """Generate Angular directives for an element"""
        directives = []
        element_type = element.get("type", "")
        
        # Add common Angular directives
        if element_type in ["table", "card", "list"]:
            directives.append("*ngFor")
        
        if element_type in ["modal", "sidebar"]:
            directives.append("*ngIf")
        
        # Add Material Design directives
        angular_info = element.get("angular_component", {})
        component = angular_info.get("component", "")
        
        if component.startswith("mat-"):
            if component == "mat-button":
                directives.append("mat-raised-button")
            elif component == "mat-table":
                directives.append("matSort")
            elif component == "mat-paginator":
                directives.append("[length]=\"totalItems\"")
        
        return directives
    
    def _generate_event_bindings(self, element: Dict[str, Any]) -> Dict[str, str]:
        """Generate Angular event bindings"""
        events = {}
        interactions = element.get("interactions", [])
        
        for interaction in interactions:
            angular_event = self._map_to_angular_event(interaction["event"])
            events[angular_event] = interaction["action"] + "()"
        
        return events
    
    def _map_to_angular_event(self, event: str) -> str:
        """Map generic events to Angular event syntax"""
        event_map = {
            "click": "(click)",
            "submit": "(ngSubmit)",
            "change": "(change)",
            "input": "(input)",
            "focus": "(focus)",
            "blur": "(blur)",
            "sort": "(matSortChange)",
            "page": "(page)"
        }
        return event_map.get(event, f"({event})")
    
    def _generate_table_template(self, element: Dict[str, Any]) -> Dict[str, Any]:
        """Generate specific template for table elements"""
        attributes = element.get("attributes", {})
        
        return {
            "datasource": "dataSource",
            "columns": self._generate_table_columns(attributes),
            "pagination": attributes.get("rows", 10) > 10,
            "sorting": attributes.get("sortable", False),
            "filtering": attributes.get("filterable", False)
        }
    
    def _generate_table_columns(self, attributes: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate table column definitions"""
        column_count = attributes.get("columns", 4)
        columns = []
        
        column_names = ["id", "name", "status", "date", "actions", "description"]
        
        for i in range(min(column_count, len(column_names))):
            columns.append({
                "name": column_names[i],
                "header": column_names[i].title(),
                "sortable": True if attributes.get("sortable") else False,
                "type": "string"
            })
        
        return columns
    
    def _generate_form_template(self, element: Dict[str, Any]) -> Dict[str, Any]:
        """Generate specific template for form elements"""
        return {
            "form_group": "formGroup",
            "validation": True,
            "submit_handler": "onSubmit()",
            "fields": self._generate_form_fields(element)
        }
    
    def _generate_form_fields(self, element: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate form field definitions"""
        return [
            {"name": "name", "type": "text", "label": "Name", "required": True},
            {"name": "email", "type": "email", "label": "Email", "required": True},
            {"name": "description", "type": "textarea", "label": "Description", "required": False}
        ]
    
    def _generate_card_template(self, element: Dict[str, Any]) -> Dict[str, Any]:
        """Generate specific template for card elements"""
        return {
            "header": True,
            "content": True,
            "actions": element.get("attributes", {}).get("has_actions", False),
            "elevation": element.get("attributes", {}).get("elevation", 1)
        }
    
    def _generate_layout_metadata(self, elements: List[Dict[str, Any]], enhanced_prompt: Dict[str, Any]) -> Dict[str, Any]:
        """Generate metadata about the layout"""
        return {
            "total_elements": len(elements),
            "layout_type": self._determine_layout_type(elements),
            "responsive_breakpoints": ["mobile", "tablet", "desktop"],
            "material_design": True,
            "accessibility_compliant": True,
            "theme_support": True,
            "components_count": len(set(e.get("type") for e in elements)),
            "complexity_score": self._calculate_complexity_score(elements)
        }
    
    def _determine_layout_type(self, elements: List[Dict[str, Any]]) -> str:
        """Determine the overall layout pattern"""
        element_types = [e.get("type") for e in elements]
        
        if "sidebar" in element_types and "table" in element_types:
            return "dashboard"
        elif "form" in element_types:
            return "form-based"
        elif "card" in element_types and len([e for e in element_types if e == "card"]) > 2:
            return "card-grid"
        elif "table" in element_types:
            return "data-centric"
        else:
            return "general"
    
    def _calculate_complexity_score(self, elements: List[Dict[str, Any]]) -> int:
        """Calculate layout complexity score (1-10)"""
        base_score = min(len(elements), 5)  # Base on element count
        
        # Add complexity for interactive elements
        interactive_elements = ["button", "form", "table", "modal"]
        interactive_count = len([e for e in elements if e.get("type") in interactive_elements])
        
        complexity_bonus = min(interactive_count * 0.5, 3)
        
        # Add complexity for responsive design
        responsive_bonus = 1 if any(e.get("responsive") for e in elements) else 0
        
        return min(int(base_score + complexity_bonus + responsive_bonus), 10)
    
    def _define_responsive_breakpoints(self) -> Dict[str, str]:
        """Define responsive breakpoints"""
        return {
            "mobile": "(max-width: 768px)",
            "tablet": "(min-width: 769px) and (max-width: 1024px)",
            "desktop": "(min-width: 1025px)"
        }
    
    def _define_grid_system(self, elements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Define grid system for the layout"""
        return {
            "type": "css-grid",
            "columns": 12,
            "gap": "1rem",
            "container_max_width": "1200px",
            "breakpoint_columns": {
                "mobile": 1,
                "tablet": 2,
                "desktop": 3
            }
        }
    
    async def get_status(self) -> Dict[str, Any]:
        """Get agent status"""
        return {
            "name": self.name,
            "version": self.version,
            "status": "active",
            "capabilities": [
                "UI element hierarchy creation",
                "Angular template generation",
                "Responsive layout design",
                "Material Design integration",
                "Accessibility compliance",
                "Grid system definition"
            ]
        }