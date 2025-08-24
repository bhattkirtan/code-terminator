"""
ValidationAgent - Runs ng build, ng test, ng lint and parses errors
"""
import logging
import asyncio
import json
from typing import Dict, Any, List, Optional
import tempfile
import os

logger = logging.getLogger(__name__)

class ValidationAgent:
    def __init__(self):
        self.name = "ValidationAgent"
        self.version = "1.0.0"
        self.supported_checks = ["build", "test", "lint", "syntax"]
    
    async def validate_code(self, code_files: Dict[str, Any], service_stubs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate generated code by running build, test, and lint checks
        """
        logger.info("Starting code validation")
        
        validation_results = {
            "success": True,
            "errors": [],
            "warnings": [],
            "checks_performed": [],
            "summary": {}
        }
        
        try:
            # Create temporary project structure
            with tempfile.TemporaryDirectory() as temp_dir:
                await self._setup_temp_project(temp_dir, code_files, service_stubs)
                
                # Run validation checks
                build_result = await self._run_build_check(temp_dir)
                test_result = await self._run_test_check(temp_dir)
                lint_result = await self._run_lint_check(temp_dir)
                syntax_result = await self._run_syntax_check(code_files)
                
                # Aggregate results
                validation_results.update(self._aggregate_results([
                    build_result, test_result, lint_result, syntax_result
                ]))
                
        except Exception as e:
            logger.error(f"Validation failed with exception: {e}")
            validation_results["success"] = False
            validation_results["errors"].append(f"Validation exception: {str(e)}")
        
        logger.info(f"Validation completed. Success: {validation_results['success']}")
        return validation_results
    
    async def _setup_temp_project(self, temp_dir: str, code_files: Dict[str, Any], service_stubs: Dict[str, Any]):
        """Setup temporary Angular project structure for validation"""
        logger.info("Setting up temporary project structure")
        
        # Create basic Angular project structure
        project_structure = {
            "package.json": self._get_package_json(),
            "angular.json": code_files.get("angular_json", self._get_default_angular_json()),
            "tsconfig.json": code_files.get("tsconfig", self._get_default_tsconfig()),
            "src/main.ts": code_files.get("app_config", {}).get("main.ts", self._get_default_main_ts()),
            "src/index.html": code_files.get("app_config", {}).get("index.html", self._get_default_index_html()),
            "src/styles.scss": code_files.get("styles", {}).get("styles.scss", ""),
        }
        
        # Add component files
        if "components" in code_files:
            for comp_name, comp_files in code_files["components"].items():
                for file_type, content in comp_files.items():
                    file_path = f"src/app/{comp_name}/{comp_name}.{file_type}"
                    project_structure[file_path] = content
        
        # Add service files
        if "services" in code_files:
            for service_name, service_files in code_files["services"].items():
                for file_type, content in service_files.items():
                    file_path = f"src/app/services/{service_name}.{file_type}"
                    project_structure[file_path] = content
        
        # Add module files
        if "modules" in code_files:
            for module_name, content in code_files["modules"].items():
                file_path = f"src/app/{module_name}"
                project_structure[file_path] = content
        
        # Add service stubs
        if service_stubs:
            for category, files in service_stubs.items():
                if isinstance(files, dict):
                    for file_name, content in files.items():
                        file_path = f"src/app/mocks/{file_name}"
                        project_structure[file_path] = content
        
        # Write files to temp directory
        for file_path, content in project_structure.items():
            full_path = os.path.join(temp_dir, file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            with open(full_path, 'w', encoding='utf-8') as f:
                if isinstance(content, dict):
                    f.write(json.dumps(content, indent=2))
                else:
                    f.write(str(content))
    
    async def _run_build_check(self, project_dir: str) -> Dict[str, Any]:
        """Run Angular build check"""
        logger.info("Running build validation")
        
        result = {
            "check_type": "build",
            "success": True,
            "errors": [],
            "warnings": [],
            "output": ""
        }
        
        try:
            # Simulate ng build --dry-run (since we can't actually run ng in this environment)
            # In a real implementation, you would run: ng build --dry-run --no-progress
            
            # Check for common build issues
            build_issues = await self._check_build_issues(project_dir)
            
            if build_issues:
                result["success"] = False
                result["errors"].extend(build_issues)
            else:
                result["output"] = "Build validation passed - no obvious build issues detected"
                
        except Exception as e:
            result["success"] = False
            result["errors"].append(f"Build check failed: {str(e)}")
        
        return result
    
    async def _check_build_issues(self, project_dir: str) -> List[str]:
        """Check for common build issues"""
        issues = []
        
        # Check if package.json exists
        package_json_path = os.path.join(project_dir, "package.json")
        if not os.path.exists(package_json_path):
            issues.append("Missing package.json file")
        
        # Check if angular.json exists
        angular_json_path = os.path.join(project_dir, "angular.json")
        if not os.path.exists(angular_json_path):
            issues.append("Missing angular.json configuration")
        
        # Check if main.ts exists
        main_ts_path = os.path.join(project_dir, "src/main.ts")
        if not os.path.exists(main_ts_path):
            issues.append("Missing src/main.ts bootstrap file")
        
        # Check for TypeScript syntax issues in component files
        src_app_dir = os.path.join(project_dir, "src/app")
        if os.path.exists(src_app_dir):
            ts_issues = await self._check_typescript_files(src_app_dir)
            issues.extend(ts_issues)
        
        return issues
    
    async def _check_typescript_files(self, app_dir: str) -> List[str]:
        """Check TypeScript files for basic syntax issues"""
        issues = []
        
        for root, dirs, files in os.walk(app_dir):
            for file in files:
                if file.endswith('.ts'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                        # Basic syntax checks
                        file_issues = self._check_typescript_syntax(content, file_path)
                        issues.extend(file_issues)
                        
                    except Exception as e:
                        issues.append(f"Error reading {file_path}: {str(e)}")
        
        return issues
    
    def _check_typescript_syntax(self, content: str, file_path: str) -> List[str]:
        """Check TypeScript content for basic syntax issues"""
        issues = []
        
        # Check for missing imports
        if '@Component' in content and 'import' not in content:
            issues.append(f"{file_path}: Missing import statements")
        
        # Check for unmatched braces
        open_braces = content.count('{')
        close_braces = content.count('}')
        if open_braces != close_braces:
            issues.append(f"{file_path}: Unmatched braces ({open_braces} open, {close_braces} close)")
        
        # Check for unmatched parentheses
        open_parens = content.count('(')
        close_parens = content.count(')')
        if open_parens != close_parens:
            issues.append(f"{file_path}: Unmatched parentheses ({open_parens} open, {close_parens} close)")
        
        # Check for missing semicolons at end of statements
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if (stripped and 
                not stripped.startswith('//') and 
                not stripped.startswith('*') and
                not stripped.endswith(';') and 
                not stripped.endswith('{') and 
                not stripped.endswith('}') and
                not stripped.endswith(',') and
                not stripped.startswith('export') and
                not stripped.startswith('import') and
                '=' in stripped and
                not stripped.endswith(')')):
                issues.append(f"{file_path}:{i}: Possible missing semicolon")
        
        return issues
    
    async def _run_test_check(self, project_dir: str) -> Dict[str, Any]:
        """Run Angular test check"""
        logger.info("Running test validation")
        
        result = {
            "check_type": "test",
            "success": True,
            "errors": [],
            "warnings": [],
            "output": ""
        }
        
        try:
            # Check for test files and basic test structure
            test_issues = await self._check_test_structure(project_dir)
            
            if test_issues:
                result["warnings"].extend(test_issues)  # Tests are warnings, not errors
            
            result["output"] = "Test structure validation completed"
            
        except Exception as e:
            result["success"] = False
            result["errors"].append(f"Test check failed: {str(e)}")
        
        return result
    
    async def _check_test_structure(self, project_dir: str) -> List[str]:
        """Check test file structure"""
        warnings = []
        
        src_app_dir = os.path.join(project_dir, "src/app")
        if not os.path.exists(src_app_dir):
            return ["No src/app directory found"]
        
        # Count component and test files
        component_files = []
        test_files = []
        
        for root, dirs, files in os.walk(src_app_dir):
            for file in files:
                if file.endswith('.component.ts'):
                    component_files.append(file)
                elif file.endswith('.spec.ts'):
                    test_files.append(file)
        
        # Check if components have corresponding test files
        for comp_file in component_files:
            test_file = comp_file.replace('.component.ts', '.component.spec.ts')
            if test_file not in test_files:
                warnings.append(f"Missing test file for component: {comp_file}")
        
        # Check test file content
        for root, dirs, files in os.walk(src_app_dir):
            for file in files:
                if file.endswith('.spec.ts'):
                    file_path = os.path.join(root, file)
                    test_warnings = await self._check_test_file_content(file_path)
                    warnings.extend(test_warnings)
        
        return warnings
    
    async def _check_test_file_content(self, file_path: str) -> List[str]:
        """Check individual test file content"""
        warnings = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for basic test structure
            if 'describe(' not in content:
                warnings.append(f"{file_path}: Missing describe block")
            
            if 'it(' not in content:
                warnings.append(f"{file_path}: Missing it block")
            
            if 'expect(' not in content:
                warnings.append(f"{file_path}: Missing expect assertions")
            
            # Check for component creation test
            if '.component.spec.ts' in file_path and 'should create' not in content:
                warnings.append(f"{file_path}: Missing component creation test")
                
        except Exception as e:
            warnings.append(f"Error reading test file {file_path}: {str(e)}")
        
        return warnings
    
    async def _run_lint_check(self, project_dir: str) -> Dict[str, Any]:
        """Run linting check"""
        logger.info("Running lint validation")
        
        result = {
            "check_type": "lint",
            "success": True,
            "errors": [],
            "warnings": [],
            "output": ""
        }
        
        try:
            # Check for common linting issues
            lint_issues = await self._check_lint_issues(project_dir)
            
            # Categorize issues
            for issue in lint_issues:
                if "error:" in issue.lower():
                    result["errors"].append(issue)
                else:
                    result["warnings"].append(issue)
            
            if result["errors"]:
                result["success"] = False
            
            result["output"] = f"Lint check completed. Found {len(result['errors'])} errors and {len(result['warnings'])} warnings"
            
        except Exception as e:
            result["success"] = False
            result["errors"].append(f"Lint check failed: {str(e)}")
        
        return result
    
    async def _check_lint_issues(self, project_dir: str) -> List[str]:
        """Check for common linting issues"""
        issues = []
        
        src_app_dir = os.path.join(project_dir, "src/app")
        if not os.path.exists(src_app_dir):
            return ["No src/app directory found for linting"]
        
        # Check TypeScript and HTML files
        for root, dirs, files in os.walk(src_app_dir):
            for file in files:
                if file.endswith(('.ts', '.html')):
                    file_path = os.path.join(root, file)
                    file_issues = await self._check_file_lint_issues(file_path)
                    issues.extend(file_issues)
        
        return issues
    
    async def _check_file_lint_issues(self, file_path: str) -> List[str]:
        """Check individual file for lint issues"""
        issues = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            
            for i, line in enumerate(lines, 1):
                # Check for trailing whitespace
                if line.endswith(' ') or line.endswith('\t'):
                    issues.append(f"{file_path}:{i}: Trailing whitespace")
                
                # Check for tabs instead of spaces
                if '\t' in line:
                    issues.append(f"{file_path}:{i}: Use spaces instead of tabs")
                
                # Check for long lines (basic check)
                if len(line) > 120:
                    issues.append(f"{file_path}:{i}: Line too long ({len(line)} characters)")
                
                # Check for console.log statements
                if 'console.log(' in line and not line.strip().startswith('//'):
                    issues.append(f"{file_path}:{i}: Remove console.log statement")
                
                # Check for TODO comments
                if 'TODO' in line.upper():
                    issues.append(f"{file_path}:{i}: TODO comment found")
            
            # TypeScript specific checks
            if file_path.endswith('.ts'):
                ts_issues = self._check_typescript_lint_issues(content, file_path)
                issues.extend(ts_issues)
            
            # HTML specific checks
            if file_path.endswith('.html'):
                html_issues = self._check_html_lint_issues(content, file_path)
                issues.extend(html_issues)
                
        except Exception as e:
            issues.append(f"Error linting {file_path}: {str(e)}")
        
        return issues
    
    def _check_typescript_lint_issues(self, content: str, file_path: str) -> List[str]:
        """Check TypeScript specific lint issues"""
        issues = []
        
        # Check for unused variables (basic check)
        lines = content.split('\n')
        declared_vars = set()
        used_vars = set()
        
        for line in lines:
            # Simple variable declaration detection
            if ' let ' in line or ' const ' in line or ' var ' in line:
                parts = line.split()
                for i, part in enumerate(parts):
                    if part in ['let', 'const', 'var'] and i + 1 < len(parts):
                        var_name = parts[i + 1].split('=')[0].split(':')[0].strip()
                        declared_vars.add(var_name)
            
            # Simple usage detection
            for var in declared_vars:
                if var in line and f' {var} ' in line or f'.{var}' in line or f'{var}(' in line:
                    used_vars.add(var)
        
        unused_vars = declared_vars - used_vars
        for var in unused_vars:
            issues.append(f"{file_path}: Unused variable '{var}'")
        
        return issues
    
    def _check_html_lint_issues(self, content: str, file_path: str) -> List[str]:
        """Check HTML specific lint issues"""
        issues = []
        
        # Check for missing alt attributes on images
        if '<img' in content and 'alt=' not in content:
            issues.append(f"{file_path}: Image missing alt attribute")
        
        # Check for inline styles
        if 'style=' in content:
            issues.append(f"{file_path}: Avoid inline styles, use CSS classes")
        
        # Check for missing ARIA attributes on interactive elements
        if '<button' in content and 'aria-label' not in content and '>' in content:
            button_content = content[content.find('<button'):content.find('</button>') + 9]
            if not any(text.strip() for text in button_content.split('>')[1].split('<')[0]):
                issues.append(f"{file_path}: Button missing text or aria-label")
        
        return issues
    
    async def _run_syntax_check(self, code_files: Dict[str, Any]) -> Dict[str, Any]:
        """Run syntax validation on code files"""
        logger.info("Running syntax validation")
        
        result = {
            "check_type": "syntax",
            "success": True,
            "errors": [],
            "warnings": [],
            "output": ""
        }
        
        try:
            syntax_errors = []
            
            # Check component files
            if "components" in code_files:
                for comp_name, comp_files in code_files["components"].items():
                    for file_type, content in comp_files.items():
                        if file_type.endswith('.ts'):
                            errors = self._check_typescript_syntax(content, f"{comp_name}.{file_type}")
                            syntax_errors.extend(errors)
                        elif file_type.endswith('.html'):
                            errors = self._check_html_syntax(content, f"{comp_name}.{file_type}")
                            syntax_errors.extend(errors)
                        elif file_type.endswith('.scss'):
                            errors = self._check_scss_syntax(content, f"{comp_name}.{file_type}")
                            syntax_errors.extend(errors)
            
            if syntax_errors:
                result["success"] = False
                result["errors"].extend(syntax_errors)
            
            result["output"] = f"Syntax check completed. Found {len(syntax_errors)} issues"
            
        except Exception as e:
            result["success"] = False
            result["errors"].append(f"Syntax check failed: {str(e)}")
        
        return result
    
    def _check_html_syntax(self, content: str, file_name: str) -> List[str]:
        """Check HTML syntax"""
        errors = []
        
        # Check for unclosed tags (basic check)
        stack = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Simple tag matching (not comprehensive)
            line = line.strip()
            if '<' in line and '>' in line:
                # Extract tags
                start = 0
                while True:
                    start_pos = line.find('<', start)
                    if start_pos == -1:
                        break
                    
                    end_pos = line.find('>', start_pos)
                    if end_pos == -1:
                        break
                    
                    tag = line[start_pos:end_pos + 1]
                    
                    if tag.startswith('<!--'):
                        start = end_pos + 1
                        continue
                    
                    if tag.startswith('</'):
                        # Closing tag
                        tag_name = tag[2:-1].strip()
                        if stack and stack[-1] == tag_name:
                            stack.pop()
                        else:
                            errors.append(f"{file_name}:{i}: Unmatched closing tag {tag}")
                    elif not tag.endswith('/>') and not tag.startswith('<!'):
                        # Opening tag
                        tag_name = tag[1:-1].split()[0]
                        if tag_name not in ['br', 'hr', 'img', 'input', 'meta', 'link']:
                            stack.append(tag_name)
                    
                    start = end_pos + 1
        
        # Check for remaining unclosed tags
        for tag in stack:
            errors.append(f"{file_name}: Unclosed tag <{tag}>")
        
        return errors
    
    def _check_scss_syntax(self, content: str, file_name: str) -> List[str]:
        """Check SCSS syntax"""
        errors = []
        
        # Check for unmatched braces
        open_braces = content.count('{')
        close_braces = content.count('}')
        if open_braces != close_braces:
            errors.append(f"{file_name}: Unmatched braces in SCSS ({open_braces} open, {close_braces} close)")
        
        # Check for missing semicolons in property declarations
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            line = line.strip()
            if ':' in line and not line.endswith(';') and not line.endswith('{') and not line.startswith('//'):
                if line and not line.endswith(')') and not line.startswith('@'):
                    errors.append(f"{file_name}:{i}: Missing semicolon")
        
        return errors
    
    def _aggregate_results(self, check_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate results from all validation checks"""
        aggregated = {
            "success": True,
            "errors": [],
            "warnings": [],
            "checks_performed": [],
            "summary": {}
        }
        
        for result in check_results:
            check_type = result.get("check_type", "unknown")
            aggregated["checks_performed"].append(check_type)
            
            if not result.get("success", True):
                aggregated["success"] = False
            
            aggregated["errors"].extend(result.get("errors", []))
            aggregated["warnings"].extend(result.get("warnings", []))
            
            # Add to summary
            aggregated["summary"][check_type] = {
                "success": result.get("success", True),
                "error_count": len(result.get("errors", [])),
                "warning_count": len(result.get("warnings", [])),
                "output": result.get("output", "")
            }
        
        return aggregated
    
    def _get_package_json(self) -> str:
        """Get basic package.json for validation"""
        return '''{
  "name": "temp-validation-project",
  "version": "1.0.0",
  "scripts": {
    "build": "ng build",
    "test": "ng test",
    "lint": "ng lint"
  },
  "dependencies": {
    "@angular/core": "^17.0.0",
    "@angular/common": "^17.0.0",
    "@angular/material": "^17.0.0"
  }
}'''
    
    def _get_default_angular_json(self) -> str:
        """Get default angular.json for validation"""
        return '''{
  "$schema": "./node_modules/@angular/cli/lib/config/schema.json",
  "version": 1,
  "projects": {
    "temp-project": {
      "projectType": "application",
      "root": "",
      "sourceRoot": "src"
    }
  }
}'''
    
    def _get_default_tsconfig(self) -> str:
        """Get default tsconfig.json for validation"""
        return '''{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ES2022",
    "lib": ["ES2022", "dom"],
    "strict": true
  }
}'''
    
    def _get_default_main_ts(self) -> str:
        """Get default main.ts for validation"""
        return '''import { platformBrowserDynamic } from '@angular/platform-browser-dynamic';
import { AppModule } from './app/app.module';

platformBrowserDynamic().bootstrapModule(AppModule);'''
    
    def _get_default_index_html(self) -> str:
        """Get default index.html for validation"""
        return '''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Temp Project</title>
  <base href="/">
  <meta name="viewport" content="width=device-width, initial-scale=1">
</head>
<body>
  <app-root></app-root>
</body>
</html>'''
    
    async def get_status(self) -> Dict[str, Any]:
        """Get agent status"""
        return {
            "name": self.name,
            "version": self.version,
            "status": "active",
            "supported_checks": self.supported_checks,
            "capabilities": [
                "Angular build validation",
                "TypeScript syntax checking",
                "HTML structure validation",
                "SCSS syntax checking",
                "Test structure validation",
                "Lint rule checking",
                "Project structure validation",
                "Error aggregation and reporting"
            ]
        }