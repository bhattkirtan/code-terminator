"""
EnhancementAgent - Recommends improvements and re-generates code if necessary
"""
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class EnhancementAgent:
    def __init__(self):
        self.name = "EnhancementAgent"
        self.version = "1.0.0"
    
    async def enhance_code(self, code_files: Dict[str, Any], review_suggestions: List[str]) -> Dict[str, Any]:
        """
        Enhance code based on review suggestions and best practices
        """
        logger.info("Enhancing code based on review feedback")
        
        enhanced_code = code_files.copy()
        enhancement_log = []
        
        try:
            # Apply enhancements based on suggestions
            enhanced_code = await self._apply_suggested_improvements(enhanced_code, review_suggestions, enhancement_log)
            
            # Apply additional best practice enhancements
            enhanced_code = await self._apply_best_practices(enhanced_code, enhancement_log)
            
            # Optimize performance
            enhanced_code = await self._optimize_performance(enhanced_code, enhancement_log)
            
            # Improve accessibility
            enhanced_code = await self._improve_accessibility(enhanced_code, enhancement_log)
            
        except Exception as e:
            logger.error(f"Code enhancement failed: {e}")
            enhancement_log.append(f"Enhancement failed: {str(e)}")
        
        logger.info(f"Code enhancement completed with {len(enhancement_log)} improvements")
        
        return {
            "enhanced_code": enhanced_code,
            "enhancement_log": enhancement_log,
            "improvements_applied": len(enhancement_log)
        }
    
    async def _apply_suggested_improvements(self, code_files: Dict[str, Any], suggestions: List[str], log: List[str]) -> Dict[str, Any]:
        """Apply specific improvements based on review suggestions"""
        enhanced_code = code_files.copy()
        
        for suggestion in suggestions:
            if "console.log" in suggestion.lower():
                enhanced_code = await self._remove_console_logs(enhanced_code, log)
            elif "responsive" in suggestion.lower():
                enhanced_code = await self._add_responsive_design(enhanced_code, log)
            elif "accessibility" in suggestion.lower():
                enhanced_code = await self._enhance_accessibility(enhanced_code, log)
            elif "performance" in suggestion.lower():
                enhanced_code = await self._enhance_performance(enhanced_code, log)
            elif "validation" in suggestion.lower():
                enhanced_code = await self._add_form_validation(enhanced_code, log)
        
        return enhanced_code
    
    async def _remove_console_logs(self, code_files: Dict[str, Any], log: List[str]) -> Dict[str, Any]:
        """Remove console.log statements from code"""
        enhanced_code = code_files.copy()
        
        if "components" in enhanced_code:
            for comp_name, comp_files in enhanced_code["components"].items():
                if "component.ts" in comp_files:
                    original_content = comp_files["component.ts"]
                    
                    # Remove console.log statements
                    import re
                    cleaned_content = re.sub(r'console\.log\([^)]*\);\s*', '', original_content)
                    
                    if cleaned_content != original_content:
                        enhanced_code["components"][comp_name]["component.ts"] = cleaned_content
                        log.append(f"Removed console.log statements from {comp_name}.component.ts")
        
        return enhanced_code
    
    async def _add_responsive_design(self, code_files: Dict[str, Any], log: List[str]) -> Dict[str, Any]:
        """Add responsive design patterns"""
        enhanced_code = code_files.copy()
        
        if "components" in enhanced_code:
            for comp_name, comp_files in enhanced_code["components"].items():
                if "component.scss" in comp_files:
                    original_scss = comp_files["component.scss"]
                    
                    # Add responsive mixins if not present
                    if "@media" not in original_scss and "respond-to" not in original_scss:
                        responsive_scss = self._add_responsive_styles(original_scss, comp_name)
                        enhanced_code["components"][comp_name]["component.scss"] = responsive_scss
                        log.append(f"Added responsive design to {comp_name}.component.scss")
        
        return enhanced_code
    
    def _add_responsive_styles(self, original_scss: str, comp_name: str) -> str:
        """Add responsive styles to SCSS"""
        responsive_addition = f'''
/* Responsive Design Enhancements */
.{comp_name}-container {{
  // Mobile first approach
  @media (max-width: 767px) {{
    padding: 0.5rem;
    
    .mat-card {{
      margin: 0.5rem 0;
    }}
    
    .mat-table {{
      font-size: 0.8rem;
    }}
  }}
  
  // Tablet
  @media (min-width: 768px) and (max-width: 1023px) {{
    padding: 1rem;
    
    .mat-card {{
      margin: 1rem 0;
    }}
  }}
  
  // Desktop
  @media (min-width: 1024px) {{
    padding: 1.5rem;
    
    .mat-card {{
      margin: 1.5rem 0;
    }}
  }}
}}
'''
        return original_scss + responsive_addition
    
    async def _enhance_accessibility(self, code_files: Dict[str, Any], log: List[str]) -> Dict[str, Any]:
        """Enhance accessibility features"""
        enhanced_code = code_files.copy()
        
        if "components" in enhanced_code:
            for comp_name, comp_files in enhanced_code["components"].items():
                if "component.html" in comp_files:
                    original_html = comp_files["component.html"]
                    enhanced_html = self._add_accessibility_features(original_html)
                    
                    if enhanced_html != original_html:
                        enhanced_code["components"][comp_name]["component.html"] = enhanced_html
                        log.append(f"Enhanced accessibility in {comp_name}.component.html")
        
        return enhanced_code
    
    def _add_accessibility_features(self, html_content: str) -> str:
        """Add accessibility features to HTML"""
        import re
        
        enhanced_html = html_content
        
        # Add aria-label to buttons without text
        button_pattern = r'<button([^>]*?)>(\s*<mat-icon[^>]*>[^<]*</mat-icon>\s*)</button>'
        
        def add_aria_label(match):
            button_attrs = match.group(1)
            icon_content = match.group(2)
            
            if 'aria-label=' not in button_attrs:
                # Extract icon name for aria-label
                icon_match = re.search(r'<mat-icon[^>]*>([^<]*)</mat-icon>', icon_content)
                if icon_match:
                    icon_name = icon_match.group(1).strip()
                    aria_label = f' aria-label="{icon_name.title()} button"'
                    button_attrs += aria_label
            
            return f'<button{button_attrs}>{icon_content}</button>'
        
        enhanced_html = re.sub(button_pattern, add_aria_label, enhanced_html)
        
        # Add role attributes where appropriate
        enhanced_html = re.sub(
            r'<div class="([^"]*(?:header|navigation|main|footer)[^"]*)"',
            lambda m: f'<div class="{m.group(1)}" role="{self._get_semantic_role(m.group(1))}"',
            enhanced_html
        )
        
        return enhanced_html
    
    def _get_semantic_role(self, class_name: str) -> str:
        """Get semantic role based on class name"""
        if "header" in class_name:
            return "banner"
        elif "navigation" in class_name:
            return "navigation"
        elif "main" in class_name:
            return "main"
        elif "footer" in class_name:
            return "contentinfo"
        else:
            return "region"
    
    async def _enhance_performance(self, code_files: Dict[str, Any], log: List[str]) -> Dict[str, Any]:
        """Enhance performance features"""
        enhanced_code = code_files.copy()
        
        if "components" in enhanced_code:
            for comp_name, comp_files in enhanced_code["components"].items():
                if "component.ts" in comp_files:
                    original_ts = comp_files["component.ts"]
                    enhanced_ts = self._add_performance_optimizations(original_ts)
                    
                    if enhanced_ts != original_ts:
                        enhanced_code["components"][comp_name]["component.ts"] = enhanced_ts
                        log.append(f"Added performance optimizations to {comp_name}.component.ts")
                
                if "component.html" in comp_files:
                    original_html = comp_files["component.html"]
                    enhanced_html = self._add_template_optimizations(original_html)
                    
                    if enhanced_html != original_html:
                        enhanced_code["components"][comp_name]["component.html"] = enhanced_html
                        log.append(f"Added template optimizations to {comp_name}.component.html")
        
        return enhanced_code
    
    def _add_performance_optimizations(self, ts_content: str) -> str:
        """Add performance optimizations to TypeScript"""
        import re
        
        enhanced_ts = ts_content
        
        # Add OnPush change detection if not present
        if "@Component" in enhanced_ts and "changeDetection" not in enhanced_ts:
            # Import ChangeDetectionStrategy if not imported
            if "ChangeDetectionStrategy" not in enhanced_ts:
                enhanced_ts = enhanced_ts.replace(
                    "import { Component",
                    "import { Component, ChangeDetectionStrategy"
                )
            
            # Add changeDetection to component decorator
            enhanced_ts = re.sub(
                r'(@Component\({[^}]*)(}\))',
                r'\1,\n  changeDetection: ChangeDetectionStrategy.OnPush\2',
                enhanced_ts
            )
        
        # Add subscription cleanup if subscriptions are present
        if "subscribe(" in enhanced_ts and "ngOnDestroy" not in enhanced_ts:
            # Add OnDestroy import
            enhanced_ts = enhanced_ts.replace(
                "import { Component",
                "import { Component, OnDestroy"
            )
            
            # Add implements OnDestroy
            enhanced_ts = re.sub(
                r'(export class \w+Component)( implements \w+)?',
                r'\1 implements OnDestroy',
                enhanced_ts
            )
            
            # Add destroy subject and ngOnDestroy method
            destroy_pattern = '''
  private destroy$ = new Subject<void>();

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }
}'''
            enhanced_ts = enhanced_ts.replace('}', destroy_pattern)
            
            # Add takeUntil to imports
            enhanced_ts = enhanced_ts.replace(
                "import { Observable",
                "import { Observable, Subject"
            )
            enhanced_ts = enhanced_ts.replace(
                "import { map, shareReplay",
                "import { map, shareReplay, takeUntil"
            )
        
        return enhanced_ts
    
    def _add_template_optimizations(self, html_content: str) -> str:
        """Add template optimizations to HTML"""
        import re
        
        enhanced_html = html_content
        
        # Add trackBy to *ngFor directives
        ngfor_pattern = r'\*ngFor="let (\w+) of (\w+)"'
        
        def add_trackby(match):
            item_name = match.group(1)
            array_name = match.group(2)
            return f'*ngFor="let {item_name} of {array_name}; trackBy: track{item_name.title()}By"'
        
        enhanced_html = re.sub(ngfor_pattern, add_trackby, enhanced_html)
        
        return enhanced_html
    
    async def _add_form_validation(self, code_files: Dict[str, Any], log: List[str]) -> Dict[str, Any]:
        """Add form validation features"""
        enhanced_code = code_files.copy()
        
        if "components" in enhanced_code:
            for comp_name, comp_files in enhanced_code["components"].items():
                if "component.html" in comp_files and "<form" in comp_files["component.html"]:
                    original_html = comp_files["component.html"]
                    enhanced_html = self._add_validation_to_forms(original_html)
                    
                    if enhanced_html != original_html:
                        enhanced_code["components"][comp_name]["component.html"] = enhanced_html
                        log.append(f"Added form validation to {comp_name}.component.html")
        
        return enhanced_code
    
    def _add_validation_to_forms(self, html_content: str) -> str:
        """Add validation to form elements"""
        import re
        
        enhanced_html = html_content
        
        # Add mat-error elements to form fields
        form_field_pattern = r'(<mat-form-field[^>]*>.*?</mat-form-field>)'
        
        def add_validation_messages(match):
            field_content = match.group(1)
            
            if "mat-error" not in field_content:
                # Add mat-error before closing tag
                validation_html = '''
    <mat-error *ngIf="form.get('fieldName')?.hasError('required')">
      This field is required
    </mat-error>
    <mat-error *ngIf="form.get('fieldName')?.hasError('email')">
      Please enter a valid email
    </mat-error>'''
                
                field_content = field_content.replace('</mat-form-field>', validation_html + '\n  </mat-form-field>')
            
            return field_content
        
        enhanced_html = re.sub(form_field_pattern, add_validation_messages, enhanced_html, flags=re.DOTALL)
        
        return enhanced_html
    
    async def _apply_best_practices(self, code_files: Dict[str, Any], log: List[str]) -> Dict[str, Any]:
        """Apply Angular best practices"""
        enhanced_code = code_files.copy()
        
        # Add loading states
        enhanced_code = await self._add_loading_states(enhanced_code, log)
        
        # Add error handling
        enhanced_code = await self._add_error_handling(enhanced_code, log)
        
        # Add empty states
        enhanced_code = await self._add_empty_states(enhanced_code, log)
        
        return enhanced_code
    
    async def _add_loading_states(self, code_files: Dict[str, Any], log: List[str]) -> Dict[str, Any]:
        """Add loading states to components"""
        enhanced_code = code_files.copy()
        
        if "components" in enhanced_code:
            for comp_name, comp_files in enhanced_code["components"].items():
                if "mat-table" in comp_files.get("component.html", ""):
                    # Add loading state to tables
                    original_html = comp_files["component.html"]
                    loading_html = self._add_table_loading_state(original_html)
                    
                    if loading_html != original_html:
                        enhanced_code["components"][comp_name]["component.html"] = loading_html
                        
                        # Add loading property to component
                        original_ts = comp_files.get("component.ts", "")
                        enhanced_ts = self._add_loading_property(original_ts)
                        enhanced_code["components"][comp_name]["component.ts"] = enhanced_ts
                        
                        log.append(f"Added loading state to {comp_name}")
        
        return enhanced_code
    
    def _add_table_loading_state(self, html_content: str) -> str:
        """Add loading state to table"""
        loading_row = '''
  <!-- Loading state -->
  <mat-row *ngIf="loading" class="loading-row">
    <mat-cell [attr.colspan]="displayedColumns.length">
      <div class="loading-container">
        <mat-spinner diameter="30"></mat-spinner>
        <span>Loading...</span>
      </div>
    </mat-cell>
  </mat-row>'''
        
        # Insert loading row before regular rows
        enhanced_html = html_content.replace(
            '<mat-row *matRowDef="let row; columns: displayedColumns;"></mat-row>',
            loading_row + '\n  <mat-row *matRowDef="let row; columns: displayedColumns;"></mat-row>'
        )
        
        return enhanced_html
    
    def _add_loading_property(self, ts_content: str) -> str:
        """Add loading property to component"""
        # Add loading property
        class_match = ts_content.find("export class")
        if class_match != -1:
            brace_pos = ts_content.find("{", class_match)
            if brace_pos != -1:
                enhanced_ts = (ts_content[:brace_pos + 1] + 
                             "\n  loading = false;\n" + 
                             ts_content[brace_pos + 1:])
                return enhanced_ts
        
        return ts_content
    
    async def _add_error_handling(self, code_files: Dict[str, Any], log: List[str]) -> Dict[str, Any]:
        """Add error handling to components"""
        enhanced_code = code_files.copy()
        
        if "components" in enhanced_code:
            for comp_name, comp_files in enhanced_code["components"].items():
                if "component.ts" in comp_files and "subscribe(" in comp_files["component.ts"]:
                    original_ts = comp_files["component.ts"]
                    enhanced_ts = self._add_error_handling_to_subscriptions(original_ts)
                    
                    if enhanced_ts != original_ts:
                        enhanced_code["components"][comp_name]["component.ts"] = enhanced_ts
                        log.append(f"Added error handling to {comp_name}")
        
        return enhanced_code
    
    def _add_error_handling_to_subscriptions(self, ts_content: str) -> str:
        """Add error handling to RxJS subscriptions"""
        import re
        
        # Add catchError import
        enhanced_ts = ts_content
        if "catchError" not in enhanced_ts:
            enhanced_ts = enhanced_ts.replace(
                "import { map, shareReplay",
                "import { map, shareReplay, catchError"
            )
            enhanced_ts = enhanced_ts.replace(
                "import { Observable",
                "import { Observable, throwError"
            )
        
        # Add error handling to subscribe calls
        subscribe_pattern = r'\.subscribe\(\s*([^)]+)\s*\)'
        
        def add_error_handler(match):
            original_handler = match.group(1).strip()
            if "error:" not in original_handler:
                if original_handler.endswith(','):
                    original_handler = original_handler[:-1]
                
                error_handler = f'''{{
    next: {original_handler},
    error: (error) => {{
      console.error('Error occurred:', error);
      // Handle error appropriately
    }}
  }}'''
                return f'.subscribe({error_handler})'
            return match.group(0)
        
        enhanced_ts = re.sub(subscribe_pattern, add_error_handler, enhanced_ts)
        
        return enhanced_ts
    
    async def _add_empty_states(self, code_files: Dict[str, Any], log: List[str]) -> Dict[str, Any]:
        """Add empty states to components"""
        enhanced_code = code_files.copy()
        
        if "components" in enhanced_code:
            for comp_name, comp_files in enhanced_code["components"].items():
                if "*ngFor" in comp_files.get("component.html", ""):
                    original_html = comp_files["component.html"]
                    enhanced_html = self._add_empty_state_to_lists(original_html)
                    
                    if enhanced_html != original_html:
                        enhanced_code["components"][comp_name]["component.html"] = enhanced_html
                        log.append(f"Added empty state to {comp_name}")
        
        return enhanced_code
    
    def _add_empty_state_to_lists(self, html_content: str) -> str:
        """Add empty state to lists"""
        import re
        
        # Find *ngFor directives and add empty states
        ngfor_pattern = r'\*ngFor="let \w+ of (\w+)"'
        matches = re.findall(ngfor_pattern, html_content)
        
        for array_name in matches:
            empty_state = f'''
<!-- Empty state -->
<div *ngIf="{array_name}.length === 0" class="empty-state">
  <mat-icon>inbox</mat-icon>
  <h3>No items found</h3>
  <p>There are no items to display at the moment.</p>
</div>'''
            
            # Insert empty state before the *ngFor element
            ngfor_full_pattern = f'<[^>]*\\*ngFor="let \\w+ of {array_name}"[^>]*>'
            html_content = re.sub(ngfor_full_pattern, empty_state + '\n\n' + r'\g<0>', html_content, count=1)
        
        return html_content
    
    async def _optimize_performance(self, code_files: Dict[str, Any], log: List[str]) -> Dict[str, Any]:
        """Apply performance optimizations"""
        enhanced_code = code_files.copy()
        
        # Add lazy loading for routes
        enhanced_code = await self._add_lazy_loading(enhanced_code, log)
        
        # Optimize bundle size
        enhanced_code = await self._optimize_imports(enhanced_code, log)
        
        return enhanced_code
    
    async def _add_lazy_loading(self, code_files: Dict[str, Any], log: List[str]) -> Dict[str, Any]:
        """Add lazy loading to routes"""
        enhanced_code = code_files.copy()
        
        if "routing" in enhanced_code:
            for route_file, content in enhanced_code["routing"].items():
                if "loadChildren" not in content and "component:" in content:
                    enhanced_routing = self._convert_to_lazy_routes(content)
                    enhanced_code["routing"][route_file] = enhanced_routing
                    log.append("Converted routes to lazy loading")
        
        return enhanced_code
    
    def _convert_to_lazy_routes(self, routing_content: str) -> str:
        """Convert regular routes to lazy routes"""
        import re
        
        # Convert component routes to loadChildren
        route_pattern = r"{ path: '([^']+)', component: (\w+) }"
        
        def convert_route(match):
            path = match.group(1)
            component = match.group(2)
            module_name = component.replace('Component', 'Module')
            return f"{{ path: '{path}', loadChildren: () => import('./{path}/{path}.module').then(m => m.{module_name}) }}"
        
        enhanced_routing = re.sub(route_pattern, convert_route, routing_content)
        
        return enhanced_routing
    
    async def _optimize_imports(self, code_files: Dict[str, Any], log: List[str]) -> Dict[str, Any]:
        """Optimize imports for better tree shaking"""
        enhanced_code = code_files.copy()
        
        if "components" in enhanced_code:
            for comp_name, comp_files in enhanced_code["components"].items():
                if "component.ts" in comp_files:
                    original_ts = comp_files["component.ts"]
                    optimized_ts = self._optimize_rxjs_imports(original_ts)
                    
                    if optimized_ts != original_ts:
                        enhanced_code["components"][comp_name]["component.ts"] = optimized_ts
                        log.append(f"Optimized imports in {comp_name}")
        
        return enhanced_code
    
    def _optimize_rxjs_imports(self, ts_content: str) -> str:
        """Optimize RxJS imports for better tree shaking"""
        import re
        
        # Replace barrel imports with specific imports
        barrel_import_pattern = r"import { ([^}]+) } from 'rxjs';"
        
        def replace_barrel_import(match):
            imports = [imp.strip() for imp in match.group(1).split(',')]
            specific_imports = []
            
            for imp in imports:
                if imp in ['Observable', 'Subject', 'BehaviorSubject']:
                    specific_imports.append(f"import {{ {imp} }} from 'rxjs';")
                elif imp in ['map', 'filter', 'switchMap', 'catchError', 'takeUntil']:
                    specific_imports.append(f"import {{ {imp} }} from 'rxjs/operators';")
            
            return '\n'.join(specific_imports)
        
        optimized_ts = re.sub(barrel_import_pattern, replace_barrel_import, ts_content)
        
        return optimized_ts
    
    async def _improve_accessibility(self, code_files: Dict[str, Any], log: List[str]) -> Dict[str, Any]:
        """Improve accessibility features"""
        enhanced_code = code_files.copy()
        
        # Add ARIA attributes
        enhanced_code = await self._add_aria_attributes(enhanced_code, log)
        
        # Add keyboard navigation
        enhanced_code = await self._add_keyboard_navigation(enhanced_code, log)
        
        return enhanced_code
    
    async def _add_aria_attributes(self, code_files: Dict[str, Any], log: List[str]) -> Dict[str, Any]:
        """Add ARIA attributes for better accessibility"""
        enhanced_code = code_files.copy()
        
        if "components" in enhanced_code:
            for comp_name, comp_files in enhanced_code["components"].items():
                if "component.html" in comp_files:
                    original_html = comp_files["component.html"]
                    enhanced_html = self._add_comprehensive_aria_attributes(original_html)
                    
                    if enhanced_html != original_html:
                        enhanced_code["components"][comp_name]["component.html"] = enhanced_html
                        log.append(f"Added ARIA attributes to {comp_name}")
        
        return enhanced_code
    
    def _add_comprehensive_aria_attributes(self, html_content: str) -> str:
        """Add comprehensive ARIA attributes"""
        import re
        
        enhanced_html = html_content
        
        # Add aria-describedby to form controls
        form_control_pattern = r'<(input|select|textarea)([^>]*?)>'
        
        def add_describedby(match):
            tag = match.group(1)
            attrs = match.group(2)
            
            if 'aria-describedby=' not in attrs and 'formControlName=' in attrs:
                control_match = re.search(r'formControlName="([^"]*)"', attrs)
                if control_match:
                    control_name = control_match.group(1)
                    attrs += f' aria-describedby="{control_name}-hint {control_name}-error"'
            
            return f'<{tag}{attrs}>'
        
        enhanced_html = re.sub(form_control_pattern, add_describedby, enhanced_html)
        
        # Add live regions for dynamic content
        if "loading" in enhanced_html.lower():
            enhanced_html = enhanced_html.replace(
                '<div class="loading-container">',
                '<div class="loading-container" aria-live="polite" aria-label="Loading content">'
            )
        
        return enhanced_html
    
    async def _add_keyboard_navigation(self, code_files: Dict[str, Any], log: List[str]) -> Dict[str, Any]:
        """Add keyboard navigation support"""
        enhanced_code = code_files.copy()
        
        if "components" in enhanced_code:
            for comp_name, comp_files in enhanced_code["components"].items():
                if "component.ts" in comp_files:
                    original_ts = comp_files["component.ts"]
                    enhanced_ts = self._add_keyboard_handlers(original_ts)
                    
                    if enhanced_ts != original_ts:
                        enhanced_code["components"][comp_name]["component.ts"] = enhanced_ts
                        log.append(f"Added keyboard navigation to {comp_name}")
        
        return enhanced_code
    
    def _add_keyboard_handlers(self, ts_content: str) -> str:
        """Add keyboard event handlers"""
        # Add HostListener import
        if "HostListener" not in ts_content:
            ts_content = ts_content.replace(
                "import { Component",
                "import { Component, HostListener"
            )
        
        # Add keyboard handler method
        keyboard_handler = '''
  @HostListener('keydown', ['$event'])
  onKeyDown(event: KeyboardEvent): void {
    // Handle keyboard navigation
    if (event.key === 'Escape') {
      // Close modals, dropdowns, etc.
      this.handleEscape();
    } else if (event.key === 'Enter' && event.target) {
      // Activate focused element
      this.handleEnter(event);
    }
  }

  private handleEscape(): void {
    // Implementation for escape key
  }

  private handleEnter(event: KeyboardEvent): void {
    // Implementation for enter key
    const target = event.target as HTMLElement;
    if (target.tagName === 'BUTTON') {
      target.click();
    }
  }'''
        
        # Insert before the closing brace
        ts_content = ts_content.replace('}', keyboard_handler + '\n}')
        
        return ts_content
    
    async def get_status(self) -> Dict[str, Any]:
        """Get agent status"""
        return {
            "name": self.name,
            "version": self.version,
            "status": "active",
            "capabilities": [
                "Code improvement suggestions",
                "Performance optimization",
                "Accessibility enhancement",
                "Responsive design improvement",
                "Form validation enhancement",
                "Error handling improvement",
                "Loading state addition",
                "Empty state handling",
                "Keyboard navigation support",
                "ARIA attributes enhancement"
            ]
        }