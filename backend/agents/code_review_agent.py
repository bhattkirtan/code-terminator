"""
CodeReviewAgent - Flags UI/UX violations, Angular antipatterns, accessibility issues
"""
import logging
from typing import Dict, Any, List, Optional
import re

logger = logging.getLogger(__name__)

class CodeReviewAgent:
    def __init__(self):
        self.name = "CodeReviewAgent"
        self.version = "1.0.0"
        self.review_categories = [
            "angular_patterns",
            "ui_ux_guidelines", 
            "accessibility",
            "performance",
            "security",
            "maintainability"
        ]
    
    async def review_code(self, code_files: Dict[str, Any], enhanced_prompt: Dict[str, Any]) -> Dict[str, Any]:
        """
        Review generated code for Angular antipatterns, UI/UX violations, and accessibility issues
        """
        logger.info("Starting comprehensive code review")
        
        review_result = {
            "needs_improvement": False,
            "overall_score": 0,
            "suggestions": [],
            "violations": [],
            "categories": {}
        }
        
        try:
            # Perform different types of reviews
            angular_review = await self._review_angular_patterns(code_files)
            ui_ux_review = await self._review_ui_ux_guidelines(code_files, enhanced_prompt)
            accessibility_review = await self._review_accessibility(code_files)
            performance_review = await self._review_performance(code_files)
            security_review = await self._review_security(code_files)
            maintainability_review = await self._review_maintainability(code_files)
            
            # Aggregate all reviews
            all_reviews = [
                angular_review, ui_ux_review, accessibility_review,
                performance_review, security_review, maintainability_review
            ]
            
            review_result = self._aggregate_review_results(all_reviews)
            
        except Exception as e:
            logger.error(f"Code review failed: {e}")
            review_result["violations"].append({
                "category": "system",
                "severity": "high",
                "message": f"Code review failed: {str(e)}",
                "file": "system",
                "line": 0
            })
        
        logger.info(f"Code review completed. Overall score: {review_result['overall_score']}/100")
        return review_result
    
    async def _review_angular_patterns(self, code_files: Dict[str, Any]) -> Dict[str, Any]:
        """Review Angular-specific patterns and antipatterns"""
        logger.info("Reviewing Angular patterns")
        
        review = {
            "category": "angular_patterns",
            "score": 100,
            "violations": [],
            "suggestions": []
        }
        
        # Review component files
        if "components" in code_files:
            for comp_name, comp_files in code_files["components"].items():
                violations = await self._check_component_patterns(comp_name, comp_files)
                review["violations"].extend(violations)
        
        # Review service files
        if "services" in code_files:
            for service_name, service_files in code_files["services"].items():
                violations = await self._check_service_patterns(service_name, service_files)
                review["violations"].extend(violations)
        
        # Review module files
        if "modules" in code_files:
            for module_name, content in code_files["modules"].items():
                violations = await self._check_module_patterns(module_name, content)
                review["violations"].extend(violations)
        
        # Calculate score based on violations
        review["score"] = max(0, 100 - len(review["violations"]) * 5)
        
        # Generate suggestions
        review["suggestions"] = self._generate_angular_suggestions(review["violations"])
        
        return review
    
    async def _check_component_patterns(self, comp_name: str, comp_files: Dict[str, str]) -> List[Dict[str, Any]]:
        """Check component for Angular antipatterns"""
        violations = []
        
        # Check TypeScript file
        if "component.ts" in comp_files:
            ts_content = comp_files["component.ts"]
            
            # Check for proper component decorator
            if "@Component" not in ts_content:
                violations.append({
                    "severity": "high",
                    "message": "Missing @Component decorator",
                    "file": f"{comp_name}.component.ts",
                    "line": 1,
                    "rule": "component-decorator-required"
                })
            
            # Check for OnInit implementation
            if "implements OnInit" in ts_content and "ngOnInit" not in ts_content:
                violations.append({
                    "severity": "medium",
                    "message": "Component implements OnInit but missing ngOnInit method",
                    "file": f"{comp_name}.component.ts",
                    "line": 1,
                    "rule": "implement-lifecycle-methods"
                })
            
            # Check for proper naming convention
            expected_class_name = f"{comp_name.title().replace('-', '')}Component"
            if f"export class {expected_class_name}" not in ts_content:
                violations.append({
                    "severity": "low",
                    "message": f"Component class should be named {expected_class_name}",
                    "file": f"{comp_name}.component.ts",
                    "line": 1,
                    "rule": "component-naming-convention"
                })
            
            # Check for console.log statements
            if "console.log" in ts_content:
                violations.append({
                    "severity": "low",
                    "message": "Remove console.log statements from production code",
                    "file": f"{comp_name}.component.ts",
                    "line": ts_content.find("console.log"),
                    "rule": "no-console-logs"
                })
            
            # Check for proper dependency injection
            if "constructor(" in ts_content:
                constructor_match = re.search(r'constructor\((.*?)\)', ts_content, re.DOTALL)
                if constructor_match:
                    constructor_params = constructor_match.group(1).strip()
                    if constructor_params and "private" not in constructor_params and "public" not in constructor_params:
                        violations.append({
                            "severity": "medium",
                            "message": "Constructor parameters should use access modifiers (private/public)",
                            "file": f"{comp_name}.component.ts",
                            "line": ts_content.find("constructor("),
                            "rule": "constructor-access-modifiers"
                        })
        
        # Check HTML template
        if "component.html" in comp_files:
            html_content = comp_files["component.html"]
            
            # Check for Angular template syntax
            if "{{" in html_content or "*ng" in html_content or "[" in html_content or "(" in html_content:
                # Good - using Angular template syntax
                pass
            else:
                violations.append({
                    "severity": "low",
                    "message": "Template appears to be static HTML without Angular bindings",
                    "file": f"{comp_name}.component.html",
                    "line": 1,
                    "rule": "use-angular-template-syntax"
                })
            
            # Check for proper event binding
            onclick_matches = re.findall(r'onclick=', html_content)
            if onclick_matches:
                violations.append({
                    "severity": "medium",
                    "message": "Use Angular event binding (click) instead of onclick",
                    "file": f"{comp_name}.component.html",
                    "line": 1,
                    "rule": "use-angular-event-binding"
                })
        
        return violations
    
    async def _check_service_patterns(self, service_name: str, service_files: Dict[str, str]) -> List[Dict[str, Any]]:
        """Check service for Angular antipatterns"""
        violations = []
        
        if "service.ts" in service_files:
            service_content = service_files["service.ts"]
            
            # Check for @Injectable decorator
            if "@Injectable" not in service_content:
                violations.append({
                    "severity": "high",
                    "message": "Service missing @Injectable decorator",
                    "file": f"{service_name}.service.ts",
                    "line": 1,
                    "rule": "service-injectable-decorator"
                })
            
            # Check for providedIn: 'root'
            if "providedIn: 'root'" not in service_content:
                violations.append({
                    "severity": "medium",
                    "message": "Consider using providedIn: 'root' for tree-shakable services",
                    "file": f"{service_name}.service.ts",
                    "line": 1,
                    "rule": "service-provided-in-root"
                })
            
            # Check for proper Observable usage
            if "Observable" in service_content and "import" in service_content:
                if "from 'rxjs'" not in service_content:
                    violations.append({
                        "severity": "medium",
                        "message": "Import Observable from 'rxjs' for consistency",
                        "file": f"{service_name}.service.ts",
                        "line": 1,
                        "rule": "import-observable-from-rxjs"
                    })
        
        return violations
    
    async def _check_module_patterns(self, module_name: str, content: str) -> List[Dict[str, Any]]:
        """Check module for Angular antipatterns"""
        violations = []
        
        # Check for @NgModule decorator
        if "@NgModule" not in content:
            violations.append({
                "severity": "high",
                "message": "Module missing @NgModule decorator",
                "file": module_name,
                "line": 1,
                "rule": "module-ng-module-decorator"
            })
        
        return violations
    
    def _generate_angular_suggestions(self, violations: List[Dict[str, Any]]) -> List[str]:
        """Generate Angular-specific improvement suggestions"""
        suggestions = []
        
        violation_counts = {}
        for violation in violations:
            rule = violation.get("rule", "unknown")
            violation_counts[rule] = violation_counts.get(rule, 0) + 1
        
        if violation_counts.get("component-decorator-required", 0) > 0:
            suggestions.append("Ensure all components have the @Component decorator")
        
        if violation_counts.get("no-console-logs", 0) > 0:
            suggestions.append("Remove console.log statements and use proper logging service")
        
        if violation_counts.get("use-angular-event-binding", 0) > 0:
            suggestions.append("Use Angular event binding syntax (click) instead of native onclick")
        
        return suggestions
    
    async def _review_ui_ux_guidelines(self, code_files: Dict[str, Any], enhanced_prompt: Dict[str, Any]) -> Dict[str, Any]:
        """Review UI/UX guidelines compliance"""
        logger.info("Reviewing UI/UX guidelines")
        
        review = {
            "category": "ui_ux_guidelines",
            "score": 100,
            "violations": [],
            "suggestions": []
        }
        
        # Check component templates for UI/UX issues
        if "components" in code_files:
            for comp_name, comp_files in code_files["components"].items():
                if "component.html" in comp_files:
                    violations = await self._check_ui_ux_patterns(comp_name, comp_files["component.html"])
                    review["violations"].extend(violations)
                
                if "component.scss" in comp_files:
                    violations = await self._check_ui_ux_styles(comp_name, comp_files["component.scss"])
                    review["violations"].extend(violations)
        
        # Calculate score
        review["score"] = max(0, 100 - len(review["violations"]) * 3)
        review["suggestions"] = self._generate_ui_ux_suggestions(review["violations"])
        
        return review
    
    async def _check_ui_ux_patterns(self, comp_name: str, html_content: str) -> List[Dict[str, Any]]:
        """Check HTML for UI/UX violations"""
        violations = []
        
        # Check for proper button labeling
        button_matches = re.findall(r'<button[^>]*>(.*?)</button>', html_content, re.DOTALL)
        for i, button_content in enumerate(button_matches):
            if not button_content.strip() or button_content.strip() == "{{}}":
                violations.append({
                    "severity": "medium",
                    "message": "Button should have descriptive text content",
                    "file": f"{comp_name}.component.html",
                    "line": 1,
                    "rule": "button-descriptive-text"
                })
        
        # Check for form validation feedback
        if "<form" in html_content and "mat-error" not in html_content:
            violations.append({
                "severity": "low",
                "message": "Forms should provide validation feedback to users",
                "file": f"{comp_name}.component.html",
                "line": 1,
                "rule": "form-validation-feedback"
            })
        
        # Check for loading states
        if "mat-table" in html_content and "loading" not in html_content.lower():
            violations.append({
                "severity": "low",
                "message": "Data tables should show loading states",
                "file": f"{comp_name}.component.html",
                "line": 1,
                "rule": "data-loading-states"
            })
        
        # Check for empty states
        if "*ngFor" in html_content and "empty" not in html_content.lower():
            violations.append({
                "severity": "low",
                "message": "Lists should handle empty states gracefully",
                "file": f"{comp_name}.component.html",
                "line": 1,
                "rule": "handle-empty-states"
            })
        
        return violations
    
    async def _check_ui_ux_styles(self, comp_name: str, scss_content: str) -> List[Dict[str, Any]]:
        """Check SCSS for UI/UX violations"""
        violations = []
        
        # Check for responsive design
        if "@media" not in scss_content and "respond-to" not in scss_content:
            violations.append({
                "severity": "medium",
                "message": "Component should include responsive design considerations",
                "file": f"{comp_name}.component.scss",
                "line": 1,
                "rule": "responsive-design"
            })
        
        # Check for hardcoded colors
        color_pattern = r'#[0-9a-fA-F]{3,6}'
        hardcoded_colors = re.findall(color_pattern, scss_content)
        if hardcoded_colors:
            violations.append({
                "severity": "low",
                "message": "Use CSS custom properties or SCSS variables instead of hardcoded colors",
                "file": f"{comp_name}.component.scss",
                "line": 1,
                "rule": "avoid-hardcoded-colors"
            })
        
        # Check for z-index management
        z_index_matches = re.findall(r'z-index:\s*(\d+)', scss_content)
        for z_index in z_index_matches:
            if int(z_index) > 1000:
                violations.append({
                    "severity": "low",
                    "message": f"High z-index value ({z_index}) may cause stacking issues",
                    "file": f"{comp_name}.component.scss",
                    "line": 1,
                    "rule": "z-index-management"
                })
        
        return violations
    
    def _generate_ui_ux_suggestions(self, violations: List[Dict[str, Any]]) -> List[str]:
        """Generate UI/UX improvement suggestions"""
        suggestions = []
        
        rules = [v.get("rule") for v in violations]
        
        if "button-descriptive-text" in rules:
            suggestions.append("Ensure all buttons have clear, descriptive text")
        
        if "responsive-design" in rules:
            suggestions.append("Implement responsive design patterns for better mobile experience")
        
        if "form-validation-feedback" in rules:
            suggestions.append("Add proper form validation with user-friendly error messages")
        
        return suggestions
    
    async def _review_accessibility(self, code_files: Dict[str, Any]) -> Dict[str, Any]:
        """Review accessibility compliance"""
        logger.info("Reviewing accessibility compliance")
        
        review = {
            "category": "accessibility",
            "score": 100,
            "violations": [],
            "suggestions": []
        }
        
        # Check components for accessibility issues
        if "components" in code_files:
            for comp_name, comp_files in code_files["components"].items():
                if "component.html" in comp_files:
                    violations = await self._check_accessibility_issues(comp_name, comp_files["component.html"])
                    review["violations"].extend(violations)
        
        # Calculate score
        review["score"] = max(0, 100 - len(review["violations"]) * 4)
        review["suggestions"] = self._generate_accessibility_suggestions(review["violations"])
        
        return review
    
    async def _check_accessibility_issues(self, comp_name: str, html_content: str) -> List[Dict[str, Any]]:
        """Check for accessibility violations"""
        violations = []
        
        # Check for missing alt attributes on images
        img_matches = re.findall(r'<img[^>]*>', html_content)
        for img_tag in img_matches:
            if 'alt=' not in img_tag:
                violations.append({
                    "severity": "high",
                    "message": "Images must have alt attributes for screen readers",
                    "file": f"{comp_name}.component.html",
                    "line": 1,
                    "rule": "img-alt-required"
                })
        
        # Check for proper heading hierarchy
        headings = re.findall(r'<h([1-6])', html_content)
        if headings:
            heading_levels = [int(h) for h in headings]
            for i in range(1, len(heading_levels)):
                if heading_levels[i] > heading_levels[i-1] + 1:
                    violations.append({
                        "severity": "medium",
                        "message": "Heading levels should not skip (e.g., h1 to h3)",
                        "file": f"{comp_name}.component.html",
                        "line": 1,
                        "rule": "heading-hierarchy"
                    })
        
        # Check for form labels
        input_matches = re.findall(r'<input[^>]*>', html_content)
        for input_tag in input_matches:
            if 'aria-label=' not in input_tag and 'id=' not in input_tag:
                violations.append({
                    "severity": "high",
                    "message": "Form inputs should have labels or aria-label attributes",
                    "file": f"{comp_name}.component.html",
                    "line": 1,
                    "rule": "form-input-labels"
                })
        
        # Check for button accessibility
        button_matches = re.findall(r'<button[^>]*>(.*?)</button>', html_content, re.DOTALL)
        for button_content in button_matches:
            if not button_content.strip() and 'aria-label=' not in button_content:
                violations.append({
                    "severity": "high",
                    "message": "Buttons need accessible names (text content or aria-label)",
                    "file": f"{comp_name}.component.html",
                    "line": 1,
                    "rule": "button-accessible-name"
                })
        
        # Check for focus management
        if "tabindex=" in html_content:
            tabindex_matches = re.findall(r'tabindex="(-?\d+)"', html_content)
            for tabindex in tabindex_matches:
                if int(tabindex) > 0:
                    violations.append({
                        "severity": "medium",
                        "message": "Avoid positive tabindex values, use 0 or -1",
                        "file": f"{comp_name}.component.html",
                        "line": 1,
                        "rule": "tabindex-values"
                    })
        
        # Check for color contrast (basic check)
        if "color:" in html_content and "background" in html_content:
            violations.append({
                "severity": "low",
                "message": "Verify color contrast meets WCAG AA standards (4.5:1 ratio)",
                "file": f"{comp_name}.component.html",
                "line": 1,
                "rule": "color-contrast"
            })
        
        return violations
    
    def _generate_accessibility_suggestions(self, violations: List[Dict[str, Any]]) -> List[str]:
        """Generate accessibility improvement suggestions"""
        suggestions = []
        
        rules = [v.get("rule") for v in violations]
        
        if "img-alt-required" in rules:
            suggestions.append("Add descriptive alt text to all images")
        
        if "form-input-labels" in rules:
            suggestions.append("Associate all form inputs with proper labels")
        
        if "heading-hierarchy" in rules:
            suggestions.append("Maintain proper heading hierarchy (h1, h2, h3, etc.)")
        
        if "button-accessible-name" in rules:
            suggestions.append("Ensure all buttons have accessible names")
        
        return suggestions
    
    async def _review_performance(self, code_files: Dict[str, Any]) -> Dict[str, Any]:
        """Review performance considerations"""
        logger.info("Reviewing performance considerations")
        
        review = {
            "category": "performance",
            "score": 100,
            "violations": [],
            "suggestions": []
        }
        
        # Check for performance antipatterns
        if "components" in code_files:
            for comp_name, comp_files in code_files["components"].items():
                violations = await self._check_performance_issues(comp_name, comp_files)
                review["violations"].extend(violations)
        
        review["score"] = max(0, 100 - len(review["violations"]) * 3)
        review["suggestions"] = self._generate_performance_suggestions(review["violations"])
        
        return review
    
    async def _check_performance_issues(self, comp_name: str, comp_files: Dict[str, str]) -> List[Dict[str, Any]]:
        """Check for performance issues"""
        violations = []
        
        # Check TypeScript file
        if "component.ts" in comp_files:
            ts_content = comp_files["component.ts"]
            
            # Check for proper OnPush change detection
            if "@Component" in ts_content and "changeDetection" not in ts_content:
                violations.append({
                    "severity": "low",
                    "message": "Consider using OnPush change detection for better performance",
                    "file": f"{comp_name}.component.ts",
                    "line": 1,
                    "rule": "change-detection-strategy"
                })
            
            # Check for memory leaks (basic check)
            if "subscribe(" in ts_content and "unsubscribe" not in ts_content and "takeUntil" not in ts_content:
                violations.append({
                    "severity": "medium",
                    "message": "Subscriptions should be properly unsubscribed to prevent memory leaks",
                    "file": f"{comp_name}.component.ts",
                    "line": 1,
                    "rule": "subscription-cleanup"
                })
        
        # Check template file
        if "component.html" in comp_files:
            html_content = comp_files["component.html"]
            
            # Check for trackBy in *ngFor
            ngfor_matches = re.findall(r'\*ngFor="[^"]*"', html_content)
            for ngfor in ngfor_matches:
                if "trackBy" not in ngfor:
                    violations.append({
                        "severity": "low",
                        "message": "Use trackBy function in *ngFor for better performance",
                        "file": f"{comp_name}.component.html",
                        "line": 1,
                        "rule": "ngfor-trackby"
                    })
        
        return violations
    
    def _generate_performance_suggestions(self, violations: List[Dict[str, Any]]) -> List[str]:
        """Generate performance improvement suggestions"""
        suggestions = []
        
        rules = [v.get("rule") for v in violations]
        
        if "change-detection-strategy" in rules:
            suggestions.append("Use OnPush change detection strategy where appropriate")
        
        if "subscription-cleanup" in rules:
            suggestions.append("Implement proper subscription cleanup in components")
        
        if "ngfor-trackby" in rules:
            suggestions.append("Add trackBy functions to *ngFor directives for better rendering performance")
        
        return suggestions
    
    async def _review_security(self, code_files: Dict[str, Any]) -> Dict[str, Any]:
        """Review security considerations"""
        logger.info("Reviewing security considerations")
        
        review = {
            "category": "security",
            "score": 100,
            "violations": [],
            "suggestions": []
        }
        
        # Basic security checks
        if "components" in code_files:
            for comp_name, comp_files in code_files["components"].items():
                violations = await self._check_security_issues(comp_name, comp_files)
                review["violations"].extend(violations)
        
        review["score"] = max(0, 100 - len(review["violations"]) * 5)
        review["suggestions"] = self._generate_security_suggestions(review["violations"])
        
        return review
    
    async def _check_security_issues(self, comp_name: str, comp_files: Dict[str, str]) -> List[Dict[str, Any]]:
        """Check for security issues"""
        violations = []
        
        # Check template for innerHTML usage
        if "component.html" in comp_files:
            html_content = comp_files["component.html"]
            
            if "[innerHTML]" in html_content:
                violations.append({
                    "severity": "high",
                    "message": "innerHTML binding can be dangerous - ensure content is sanitized",
                    "file": f"{comp_name}.component.html",
                    "line": 1,
                    "rule": "innerHTML-safety"
                })
        
        # Check TypeScript for sensitive data handling
        if "component.ts" in comp_files:
            ts_content = comp_files["component.ts"]
            
            # Check for hardcoded secrets (basic patterns)
            secret_patterns = [
                r'password\s*=\s*["\'][^"\']+["\']',
                r'api[_-]?key\s*=\s*["\'][^"\']+["\']',
                r'secret\s*=\s*["\'][^"\']+["\']'
            ]
            
            for pattern in secret_patterns:
                if re.search(pattern, ts_content, re.IGNORECASE):
                    violations.append({
                        "severity": "high",
                        "message": "Avoid hardcoding sensitive information in source code",
                        "file": f"{comp_name}.component.ts",
                        "line": 1,
                        "rule": "no-hardcoded-secrets"
                    })
        
        return violations
    
    def _generate_security_suggestions(self, violations: List[Dict[str, Any]]) -> List[str]:
        """Generate security improvement suggestions"""
        suggestions = []
        
        rules = [v.get("rule") for v in violations]
        
        if "innerHTML-safety" in rules:
            suggestions.append("Use Angular's DomSanitizer for safe HTML content")
        
        if "no-hardcoded-secrets" in rules:
            suggestions.append("Move sensitive configuration to environment files")
        
        return suggestions
    
    async def _review_maintainability(self, code_files: Dict[str, Any]) -> Dict[str, Any]:
        """Review code maintainability"""
        logger.info("Reviewing code maintainability")
        
        review = {
            "category": "maintainability",
            "score": 100,
            "violations": [],
            "suggestions": []
        }
        
        # Check for maintainability issues
        if "components" in code_files:
            for comp_name, comp_files in code_files["components"].items():
                violations = await self._check_maintainability_issues(comp_name, comp_files)
                review["violations"].extend(violations)
        
        review["score"] = max(0, 100 - len(review["violations"]) * 2)
        review["suggestions"] = self._generate_maintainability_suggestions(review["violations"])
        
        return review
    
    async def _check_maintainability_issues(self, comp_name: str, comp_files: Dict[str, str]) -> List[Dict[str, Any]]:
        """Check for maintainability issues"""
        violations = []
        
        if "component.ts" in comp_files:
            ts_content = comp_files["component.ts"]
            
            # Check for overly complex methods
            methods = re.findall(r'(\w+)\s*\([^)]*\)\s*{', ts_content)
            for method in methods:
                method_content = self._extract_method_content(ts_content, method)
                if method_content and len(method_content.split('\n')) > 20:
                    violations.append({
                        "severity": "low",
                        "message": f"Method '{method}' is too long - consider breaking it down",
                        "file": f"{comp_name}.component.ts",
                        "line": 1,
                        "rule": "method-complexity"
                    })
            
            # Check for magic numbers
            number_matches = re.findall(r'\b\d{2,}\b', ts_content)
            if number_matches:
                violations.append({
                    "severity": "low",
                    "message": "Consider using named constants instead of magic numbers",
                    "file": f"{comp_name}.component.ts",
                    "line": 1,
                    "rule": "avoid-magic-numbers"
                })
        
        return violations
    
    def _extract_method_content(self, content: str, method_name: str) -> str:
        """Extract method content for analysis"""
        # Simplified method extraction
        method_start = content.find(f"{method_name}(")
        if method_start == -1:
            return ""
        
        brace_start = content.find("{", method_start)
        if brace_start == -1:
            return ""
        
        # Find matching closing brace
        brace_count = 1
        pos = brace_start + 1
        while pos < len(content) and brace_count > 0:
            if content[pos] == '{':
                brace_count += 1
            elif content[pos] == '}':
                brace_count -= 1
            pos += 1
        
        return content[brace_start:pos]
    
    def _generate_maintainability_suggestions(self, violations: List[Dict[str, Any]]) -> List[str]:
        """Generate maintainability improvement suggestions"""
        suggestions = []
        
        rules = [v.get("rule") for v in violations]
        
        if "method-complexity" in rules:
            suggestions.append("Break down complex methods into smaller, focused functions")
        
        if "avoid-magic-numbers" in rules:
            suggestions.append("Use named constants for numeric values to improve readability")
        
        return suggestions
    
    def _aggregate_review_results(self, reviews: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate all review results"""
        aggregated = {
            "needs_improvement": False,
            "overall_score": 0,
            "suggestions": [],
            "violations": [],
            "categories": {}
        }
        
        total_score = 0
        violation_count = 0
        
        for review in reviews:
            category = review["category"]
            score = review["score"]
            violations = review["violations"]
            suggestions = review["suggestions"]
            
            # Add to aggregated results
            aggregated["categories"][category] = {
                "score": score,
                "violation_count": len(violations),
                "suggestions": suggestions
            }
            
            # Add violations with category info
            for violation in violations:
                violation["category"] = category
                aggregated["violations"].append(violation)
            
            # Add suggestions
            aggregated["suggestions"].extend(suggestions)
            
            total_score += score
            violation_count += len(violations)
        
        # Calculate overall score
        aggregated["overall_score"] = total_score // len(reviews) if reviews else 0
        
        # Determine if improvement is needed
        aggregated["needs_improvement"] = aggregated["overall_score"] < 80 or violation_count > 10
        
        return aggregated
    
    async def get_status(self) -> Dict[str, Any]:
        """Get agent status"""
        return {
            "name": self.name,
            "version": self.version,
            "status": "active",
            "review_categories": self.review_categories,
            "capabilities": [
                "Angular pattern analysis",
                "UI/UX guideline compliance",
                "Accessibility compliance checking",
                "Performance optimization review",
                "Security vulnerability detection",
                "Code maintainability analysis",
                "Best practices enforcement",
                "Automated suggestion generation"
            ]
        }