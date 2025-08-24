"""
CodeAgent - Generates Angular TS/HTML/SCSS following best practices
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class CodeAgent:
    def __init__(self):
        self.name = "CodeAgent"
        self.version = "1.0.0"
        self.angular_version = "17.0.0"
    
    async def generate_code(self, layout: Dict[str, Any], enhanced_prompt: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate complete Angular application code from layout and requirements
        """
        logger.info("Generating Angular application code")
        
        # Extract requirements from enhanced prompt
        requirements = self._extract_requirements(enhanced_prompt)
        
        # Generate component files
        components = await self._generate_components(layout, requirements)
        
        # Generate service files
        services = await self._generate_services(layout, requirements)
        
        # Generate module files
        modules = await self._generate_modules(components, services)
        
        # Generate app configuration
        app_config = await self._generate_app_config(requirements)
        
        # Generate routing
        routing = await self._generate_routing(components)
        
        result = {
            "components": components,
            "services": services,
            "modules": modules,
            "app_config": app_config,
            "routing": routing,
            "package_json": self._generate_package_json(requirements),
            "angular_json": self._generate_angular_json(),
            "tsconfig": self._generate_tsconfig()
        }
        
        logger.info(f"Generated {len(components)} components and {len(services)} services")
        return result
    
    async def fix_validation_errors(self, code_files: Dict[str, Any], errors: List[str]) -> Dict[str, Any]:
        """
        Fix validation errors in the generated code
        """
        logger.info(f"Fixing {len(errors)} validation errors")
        
        # Analyze errors and apply fixes
        fixed_code = code_files.copy()
        
        for error in errors:
            if "compilation" in error.lower():
                fixed_code = await self._fix_compilation_errors(fixed_code, error)
            elif "lint" in error.lower():
                fixed_code = await self._fix_lint_errors(fixed_code, error)
            elif "test" in error.lower():
                fixed_code = await self._fix_test_errors(fixed_code, error)
        
        return fixed_code
    
    def _extract_requirements(self, enhanced_prompt: Dict[str, Any]) -> Dict[str, Any]:
        """Extract technical requirements from enhanced prompt"""
        return {
            "framework": "Angular",
            "version": self.angular_version,
            "ui_library": "Angular Material",
            "styling": "SCSS",
            "typescript": True,
            "responsive": True,
            "accessibility": enhanced_prompt.get("accessibility_requirements", []),
            "features": enhanced_prompt.get("ui_patterns", []),
            "technical_stack": enhanced_prompt.get("technical_requirements", [])
        }
    
    async def _generate_components(self, layout: Dict[str, Any], requirements: Dict[str, Any]) -> Dict[str, Dict[str, str]]:
        """Generate Angular component files"""
        components = {}
        
        # Generate components based on layout hierarchy
        layout_tree = layout.get("layout_tree", {})
        components.update(await self._generate_components_from_tree(layout_tree))
        
        # Generate main app component
        components["app"] = {
            "component.ts": self._generate_app_component_ts(),
            "component.html": self._generate_app_component_html(layout),
            "component.scss": self._generate_app_component_scss(),
            "component.spec.ts": self._generate_component_spec("AppComponent")
        }
        
        return components
    
    async def _generate_components_from_tree(self, tree_node: Dict[str, Any], parent_path: str = "") -> Dict[str, Dict[str, str]]:
        """Recursively generate components from layout tree"""
        components = {}
        
        if tree_node.get("angular_component"):
            component_name = tree_node["angular_component"].replace("app-", "")
            component_path = f"{parent_path}/{component_name}" if parent_path else component_name
            
            components[component_path] = {
                "component.ts": self._generate_component_ts(component_name, tree_node),
                "component.html": self._generate_component_html(component_name, tree_node),
                "component.scss": self._generate_component_scss(component_name, tree_node),
                "component.spec.ts": self._generate_component_spec(f"{component_name.title()}Component")
            }
        
        # Process children
        if "children" in tree_node:
            for child in tree_node["children"]:
                child_components = await self._generate_components_from_tree(child, parent_path)
                components.update(child_components)
        
        return components
    
    def _generate_app_component_ts(self) -> str:
        """Generate main app component TypeScript file"""
        return '''import { Component, OnInit } from '@angular/core';
import { BreakpointObserver, Breakpoints } from '@angular/cdk/layout';
import { Observable } from 'rxjs';
import { map, shareReplay } from 'rxjs/operators';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent implements OnInit {
  title = 'ai-generated-app';
  
  isHandset$: Observable<boolean> = this.breakpointObserver.observe(Breakpoints.Handset)
    .pipe(
      map(result => result.matches),
      shareReplay()
    );

  constructor(private breakpointObserver: BreakpointObserver) {}

  ngOnInit(): void {
    console.log('AI Generated Angular Application initialized');
  }
}'''

    def _generate_app_component_html(self, layout: Dict[str, Any]) -> str:
        """Generate main app component HTML template"""
        return '''<div class="app-container">
  <mat-toolbar color="primary" class="app-header">
    <mat-toolbar-row>
      <span>{{ title }}</span>
      <span class="spacer"></span>
      <button mat-icon-button>
        <mat-icon>menu</mat-icon>
      </button>
    </mat-toolbar-row>
  </mat-toolbar>

  <mat-sidenav-container class="sidenav-container">
    <mat-sidenav #drawer class="sidenav" fixedInViewport
        [attr.role]="(isHandset$ | async) ? 'dialog' : 'navigation'"
        [mode]="(isHandset$ | async) ? 'over' : 'side'"
        [opened]="(isHandset$ | async) === false">
      <app-navigation></app-navigation>
    </mat-sidenav>
    
    <mat-sidenav-content>
      <main class="main-content">
        <router-outlet></router-outlet>
      </main>
    </mat-sidenav-content>
  </mat-sidenav-container>
</div>'''

    def _generate_app_component_scss(self) -> str:
        """Generate main app component SCSS file"""
        return '''.app-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-header {
  position: sticky;
  top: 0;
  z-index: 1000;
}

.spacer {
  flex: 1 1 auto;
}

.sidenav-container {
  flex: 1;
}

.sidenav {
  width: 250px;
}

.main-content {
  padding: 20px;
  height: 100%;
  overflow: auto;
}

/* Responsive Design */
@media (max-width: 768px) {
  .main-content {
    padding: 10px;
  }
}'''

    def _generate_component_ts(self, component_name: str, tree_node: Dict[str, Any]) -> str:
        """Generate component TypeScript file"""
        class_name = f"{component_name.title().replace('-', '')}Component"
        selector = f"app-{component_name}"
        
        # Extract any specific functionality for this component
        elements = tree_node.get("elements", [])
        has_table = any(e.get("type") == "table" for e in elements)
        has_form = any(e.get("type") == "form" for e in elements)
        
        imports = ["Component", "OnInit"]
        class_content = []
        
        if has_table:
            imports.extend(["ViewChild", "MatTableDataSource", "MatPaginator", "MatSort"])
            class_content.append("  displayedColumns: string[] = ['id', 'name', 'status', 'date', 'actions'];")
            class_content.append("  dataSource = new MatTableDataSource([]);")
            class_content.append("  @ViewChild(MatPaginator) paginator!: MatPaginator;")
            class_content.append("  @ViewChild(MatSort) sort!: MatSort;")
        
        if has_form:
            imports.extend(["FormBuilder", "FormGroup", "Validators"])
            class_content.append("  form: FormGroup;")
        
        constructor_params = []
        constructor_body = []
        
        if has_form:
            constructor_params.append("private fb: FormBuilder")
            constructor_body.append("    this.form = this.fb.group({")
            constructor_body.append("      name: ['', Validators.required],")
            constructor_body.append("      email: ['', [Validators.required, Validators.email]]")
            constructor_body.append("    });")
        
        ng_on_init_body = []
        if has_table:
            ng_on_init_body.append("    this.dataSource.paginator = this.paginator;")
            ng_on_init_body.append("    this.dataSource.sort = this.sort;")
            ng_on_init_body.append("    this.loadData();")
        
        # Build component methods
        methods = []
        if has_table:
            methods.append('''  loadData(): void {
    // Load data from service
    const mockData = [
      { id: 1, name: 'Item 1', status: 'Active', date: new Date() },
      { id: 2, name: 'Item 2', status: 'Inactive', date: new Date() }
    ];
    this.dataSource.data = mockData;
  }''')
        
        if has_form:
            methods.append('''  onSubmit(): void {
    if (this.form.valid) {
      console.log('Form submitted:', this.form.value);
    }
  }''')
        
        return f'''import {{ {", ".join(imports)} }} from '@angular/core';
{self._get_additional_imports(has_table, has_form)}

@Component({{
  selector: '{selector}',
  templateUrl: './{component_name}.component.html',
  styleUrls: ['./{component_name}.component.scss']
}})
export class {class_name} implements OnInit {{
{chr(10).join(class_content)}

  constructor({", ".join(constructor_params)}) {{
{chr(10).join(constructor_body)}
  }}

  ngOnInit(): void {{
{chr(10).join(ng_on_init_body)}
  }}

{chr(10).join(methods)}
}}'''

    def _get_additional_imports(self, has_table: bool, has_form: bool) -> str:
        """Get additional imports for components"""
        imports = []
        
        if has_table:
            imports.append("import { MatTableDataSource } from '@angular/material/table';")
            imports.append("import { MatPaginator } from '@angular/material/paginator';")
            imports.append("import { MatSort } from '@angular/material/sort';")
        
        if has_form:
            imports.append("import { FormBuilder, FormGroup, Validators } from '@angular/forms';")
        
        return "\n".join(imports)

    def _generate_component_html(self, component_name: str, tree_node: Dict[str, Any]) -> str:
        """Generate component HTML template"""
        elements = tree_node.get("elements", [])
        
        if not elements:
            return f'<div class="{component_name}-container">\n  <p>{component_name} works!</p>\n</div>'
        
        html_parts = [f'<div class="{component_name}-container">']
        
        for element in elements:
            element_html = self._generate_element_html(element)
            html_parts.append(f"  {element_html}")
        
        html_parts.append('</div>')
        
        return "\n".join(html_parts)

    def _generate_element_html(self, element: Dict[str, Any]) -> str:
        """Generate HTML for a specific UI element"""
        element_type = element.get("type", "div")
        text = element.get("text", "")
        
        if element_type == "header":
            return f'<header class="header">{text}</header>'
        elif element_type == "navigation":
            return '''<nav class="navigation">
    <mat-nav-list>
      <a mat-list-item routerLink="/dashboard">Dashboard</a>
      <a mat-list-item routerLink="/components">Components</a>
      <a mat-list-item routerLink="/settings">Settings</a>
    </mat-nav-list>
  </nav>'''
        elif element_type == "table":
            return '''<mat-table [dataSource]="dataSource" class="mat-elevation-z8" matSort>
    <ng-container matColumnDef="id">
      <mat-header-cell *matHeaderCellDef mat-sort-header>ID</mat-header-cell>
      <mat-cell *matCellDef="let element">{{element.id}}</mat-cell>
    </ng-container>
    <ng-container matColumnDef="name">
      <mat-header-cell *matHeaderCellDef mat-sort-header>Name</mat-header-cell>
      <mat-cell *matCellDef="let element">{{element.name}}</mat-cell>
    </ng-container>
    <ng-container matColumnDef="status">
      <mat-header-cell *matHeaderCellDef>Status</mat-header-cell>
      <mat-cell *matCellDef="let element">{{element.status}}</mat-cell>
    </ng-container>
    <ng-container matColumnDef="actions">
      <mat-header-cell *matHeaderCellDef>Actions</mat-header-cell>
      <mat-cell *matCellDef="let element">
        <button mat-icon-button>
          <mat-icon>edit</mat-icon>
        </button>
      </mat-cell>
    </ng-container>
    <mat-header-row *matHeaderRowDef="displayedColumns"></mat-header-row>
    <mat-row *matRowDef="let row; columns: displayedColumns;"></mat-row>
  </mat-table>
  <mat-paginator [pageSizeOptions]="[5, 10, 20]" showFirstLastButtons></mat-paginator>'''
        elif element_type == "card":
            return f'''<mat-card class="card">
    <mat-card-header>
      <mat-card-title>{text}</mat-card-title>
    </mat-card-header>
    <mat-card-content>
      <p>Card content goes here.</p>
    </mat-card-content>
    <mat-card-actions>
      <button mat-button>ACTION</button>
    </mat-card-actions>
  </mat-card>'''
        elif element_type == "button":
            return f'<button mat-raised-button color="primary">{text}</button>'
        else:
            return f'<div class="{element_type}">{text}</div>'

    def _generate_component_scss(self, component_name: str, tree_node: Dict[str, Any]) -> str:
        """Generate component SCSS file"""
        return f'''.{component_name}-container {{
  padding: 20px;
  
  .mat-table {{
    width: 100%;
    margin-bottom: 20px;
  }}
  
  .mat-card {{
    margin-bottom: 20px;
    max-width: 400px;
  }}
  
  .header {{
    background: var(--primary-color);
    color: white;
    padding: 1rem;
    margin-bottom: 1rem;
  }}
  
  .navigation {{
    background: var(--surface-color);
    min-height: 100vh;
  }}
}}

/* Responsive Design */
@media (max-width: 768px) {{
  .{component_name}-container {{
    padding: 10px;
    
    .mat-card {{
      max-width: 100%;
    }}
  }}
}}'''

    def _generate_component_spec(self, component_class: str) -> str:
        """Generate component test file"""
        return f'''import {{ ComponentFixture, TestBed }} from '@angular/core/testing';
import {{ {component_class} }} from './{component_class.lower().replace("component", "")}.component';

describe('{component_class}', () => {{
  let component: {component_class};
  let fixture: ComponentFixture<{component_class}>;

  beforeEach(async () => {{
    await TestBed.configureTestingModule({{
      declarations: [ {component_class} ]
    }})
    .compileComponents();

    fixture = TestBed.createComponent({component_class});
    component = fixture.componentInstance;
    fixture.detectChanges();
  }});

  it('should create', () => {{
    expect(component).toBeTruthy();
  }});
}});'''

    async def _generate_services(self, layout: Dict[str, Any], requirements: Dict[str, Any]) -> Dict[str, Dict[str, str]]:
        """Generate Angular service files"""
        services = {}
        
        # Generate data service
        services["data"] = {
            "service.ts": self._generate_data_service(),
            "service.spec.ts": self._generate_service_spec("DataService")
        }
        
        # Generate API service
        services["api"] = {
            "service.ts": self._generate_api_service(),
            "service.spec.ts": self._generate_service_spec("ApiService")
        }
        
        return services

    def _generate_data_service(self) -> str:
        """Generate data service"""
        return '''import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';

export interface DataItem {
  id: number;
  name: string;
  status: string;
  date: Date;
}

@Injectable({
  providedIn: 'root'
})
export class DataService {
  private dataSubject = new BehaviorSubject<DataItem[]>([]);
  public data$ = this.dataSubject.asObservable();

  constructor() {
    this.loadInitialData();
  }

  private loadInitialData(): void {
    const mockData: DataItem[] = [
      { id: 1, name: 'Item 1', status: 'Active', date: new Date() },
      { id: 2, name: 'Item 2', status: 'Inactive', date: new Date() },
      { id: 3, name: 'Item 3', status: 'Active', date: new Date() }
    ];
    this.dataSubject.next(mockData);
  }

  getData(): Observable<DataItem[]> {
    return this.data$;
  }

  addItem(item: Omit<DataItem, 'id'>): void {
    const currentData = this.dataSubject.value;
    const newItem: DataItem = {
      ...item,
      id: Math.max(...currentData.map(d => d.id)) + 1
    };
    this.dataSubject.next([...currentData, newItem]);
  }

  updateItem(id: number, updates: Partial<DataItem>): void {
    const currentData = this.dataSubject.value;
    const updatedData = currentData.map(item => 
      item.id === id ? { ...item, ...updates } : item
    );
    this.dataSubject.next(updatedData);
  }

  deleteItem(id: number): void {
    const currentData = this.dataSubject.value;
    const filteredData = currentData.filter(item => item.id !== id);
    this.dataSubject.next(filteredData);
  }
}'''

    def _generate_api_service(self) -> str:
        """Generate API service"""
        return '''import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private baseUrl = environment.apiUrl;

  constructor(private http: HttpClient) { }

  get<T>(endpoint: string): Observable<T> {
    return this.http.get<T>(`${this.baseUrl}/${endpoint}`);
  }

  post<T>(endpoint: string, data: any): Observable<T> {
    return this.http.post<T>(`${this.baseUrl}/${endpoint}`, data);
  }

  put<T>(endpoint: string, data: any): Observable<T> {
    return this.http.put<T>(`${this.baseUrl}/${endpoint}`, data);
  }

  delete<T>(endpoint: string): Observable<T> {
    return this.http.delete<T>(`${this.baseUrl}/${endpoint}`);
  }
}'''

    def _generate_service_spec(self, service_class: str) -> str:
        """Generate service test file"""
        return f'''import {{ TestBed }} from '@angular/core/testing';
import {{ {service_class} }} from './{service_class.lower().replace("service", "")}.service';

describe('{service_class}', () => {{
  let service: {service_class};

  beforeEach(() => {{
    TestBed.configureTestingModule({{}});
    service = TestBed.inject({service_class});
  }});

  it('should be created', () => {{
    expect(service).toBeTruthy();
  }});
}});'''

    async def _generate_modules(self, components: Dict[str, Any], services: Dict[str, Any]) -> Dict[str, str]:
        """Generate Angular module files"""
        return {
            "app.module.ts": self._generate_app_module(components),
            "shared.module.ts": self._generate_shared_module(),
            "material.module.ts": self._generate_material_module()
        }

    def _generate_app_module(self, components: Dict[str, Any]) -> str:
        """Generate main app module"""
        component_imports = []
        component_declarations = []
        
        for comp_path in components.keys():
            class_name = f"{comp_path.title().replace('/', '').replace('-', '')}Component"
            component_imports.append(f"import {{ {class_name} }} from './{comp_path}/{comp_path}.component';")
            component_declarations.append(class_name)
        
        return f'''import {{ NgModule }} from '@angular/core';
import {{ BrowserModule }} from '@angular/platform-browser';
import {{ BrowserAnimationsModule }} from '@angular/platform-browser/animations';
import {{ HttpClientModule }} from '@angular/common/http';
import {{ ReactiveFormsModule }} from '@angular/forms';

import {{ AppRoutingModule }} from './app-routing.module';
import {{ MaterialModule }} from './material.module';
{chr(10).join(component_imports)}

@NgModule({{
  declarations: [
    {', '.join(component_declarations)}
  ],
  imports: [
    BrowserModule,
    BrowserAnimationsModule,
    HttpClientModule,
    ReactiveFormsModule,
    AppRoutingModule,
    MaterialModule
  ],
  providers: [],
  bootstrap: [AppComponent]
}})
export class AppModule {{ }}'''

    def _generate_shared_module(self) -> str:
        """Generate shared module"""
        return '''import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule } from '@angular/forms';
import { MaterialModule } from './material.module';

@NgModule({
  declarations: [],
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MaterialModule
  ],
  exports: [
    CommonModule,
    ReactiveFormsModule,
    MaterialModule
  ]
})
export class SharedModule { }'''

    def _generate_material_module(self) -> str:
        """Generate Angular Material module"""
        return '''import { NgModule } from '@angular/core';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatSidenavModule } from '@angular/material/sidenav';
import { MatListModule } from '@angular/material/list';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatTableModule } from '@angular/material/table';
import { MatPaginatorModule } from '@angular/material/paginator';
import { MatSortModule } from '@angular/material/sort';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatDialogModule } from '@angular/material/dialog';

const MaterialComponents = [
  MatToolbarModule,
  MatSidenavModule,
  MatListModule,
  MatIconModule,
  MatButtonModule,
  MatCardModule,
  MatTableModule,
  MatPaginatorModule,
  MatSortModule,
  MatFormFieldModule,
  MatInputModule,
  MatSelectModule,
  MatDialogModule
];

@NgModule({
  imports: MaterialComponents,
  exports: MaterialComponents
})
export class MaterialModule { }'''

    async def _generate_app_config(self, requirements: Dict[str, Any]) -> Dict[str, str]:
        """Generate app configuration files"""
        return {
            "environment.prod.ts": self._generate_environment(True),
            "environment.ts": self._generate_environment(False),
            "main.ts": self._generate_main_ts(),
            "index.html": self._generate_index_html()
        }

    def _generate_environment(self, production: bool) -> str:
        """Generate environment configuration"""
        return f'''export const environment = {{
  production: {str(production).lower()},
  apiUrl: '{"https://api.production.com" if production else "http://localhost:3000/api"}'
}};'''

    def _generate_main_ts(self) -> str:
        """Generate main.ts file"""
        return '''import { platformBrowserDynamic } from '@angular/platform-browser-dynamic';
import { AppModule } from './app/app.module';

platformBrowserDynamic().bootstrapModule(AppModule)
  .catch(err => console.error(err));'''

    def _generate_index_html(self) -> str:
        """Generate index.html file"""
        return '''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>AI Generated Angular App</title>
  <base href="/">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="icon" type="image/x-icon" href="favicon.ico">
  <link rel="preconnect" href="https://fonts.gstatic.com">
  <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500&display=swap" rel="stylesheet">
  <link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
</head>
<body class="mat-typography">
  <app-root></app-root>
</body>
</html>'''

    async def _generate_routing(self, components: Dict[str, Any]) -> Dict[str, str]:
        """Generate routing configuration"""
        routes = []
        for comp_path in components.keys():
            if comp_path != "app":
                class_name = f"{comp_path.title().replace('/', '').replace('-', '')}Component"
                routes.append(f"  {{ path: '{comp_path}', component: {class_name} }}")
        
        return {
            "app-routing.module.ts": f'''import {{ NgModule }} from '@angular/core';
import {{ RouterModule, Routes }} from '@angular/router';
{chr(10).join([f"import {{ {comp_path.title().replace('/', '').replace('-', '')}Component }} from './{comp_path}/{comp_path}.component';" for comp_path in components.keys() if comp_path != "app"])}

const routes: Routes = [
{chr(10).join(routes)},
  {{ path: '', redirectTo: '/dashboard', pathMatch: 'full' }},
  {{ path: '**', redirectTo: '/dashboard' }}
];

@NgModule({{
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
}})
export class AppRoutingModule {{ }}'''
        }

    def _generate_package_json(self, requirements: Dict[str, Any]) -> str:
        """Generate package.json file"""
        return '''{
  "name": "ai-generated-angular-app",
  "version": "1.0.0",
  "scripts": {
    "ng": "ng",
    "start": "ng serve",
    "build": "ng build",
    "test": "ng test",
    "lint": "ng lint",
    "e2e": "ng e2e"
  },
  "dependencies": {
    "@angular/animations": "^17.0.0",
    "@angular/cdk": "^17.0.0",
    "@angular/common": "^17.0.0",
    "@angular/compiler": "^17.0.0",
    "@angular/core": "^17.0.0",
    "@angular/forms": "^17.0.0",
    "@angular/material": "^17.0.0",
    "@angular/platform-browser": "^17.0.0",
    "@angular/platform-browser-dynamic": "^17.0.0",
    "@angular/router": "^17.0.0",
    "rxjs": "~7.5.0",
    "tslib": "^2.3.0",
    "zone.js": "~0.14.0"
  },
  "devDependencies": {
    "@angular-devkit/build-angular": "^17.0.0",
    "@angular/cli": "^17.0.0",
    "@angular/compiler-cli": "^17.0.0",
    "@types/jasmine": "~4.3.0",
    "@types/node": "^18.7.0",
    "jasmine-core": "~4.6.0",
    "karma": "~6.4.0",
    "karma-chrome-headless": "~3.1.0",
    "karma-coverage": "~2.2.0",
    "karma-jasmine": "~5.1.0",
    "karma-jasmine-html-reporter": "~2.0.0",
    "typescript": "~5.2.0"
  }
}'''

    def _generate_angular_json(self) -> str:
        """Generate angular.json configuration"""
        return '''{
  "$schema": "./node_modules/@angular/cli/lib/config/schema.json",
  "version": 1,
  "newProjectRoot": "projects",
  "projects": {
    "ai-generated-app": {
      "projectType": "application",
      "schematics": {
        "@schematics/angular:component": {
          "style": "scss"
        }
      },
      "root": "",
      "sourceRoot": "src",
      "prefix": "app",
      "architect": {
        "build": {
          "builder": "@angular-devkit/build-angular:browser",
          "options": {
            "outputPath": "dist/ai-generated-app",
            "index": "src/index.html",
            "main": "src/main.ts",
            "polyfills": ["zone.js"],
            "tsConfig": "tsconfig.app.json",
            "inlineStyleLanguage": "scss",
            "assets": ["src/favicon.ico", "src/assets"],
            "styles": ["src/styles.scss"],
            "scripts": []
          }
        },
        "serve": {
          "builder": "@angular-devkit/build-angular:dev-server",
          "configurations": {
            "production": {
              "buildTarget": "ai-generated-app:build:production"
            },
            "development": {
              "buildTarget": "ai-generated-app:build:development"
            }
          },
          "defaultConfiguration": "development"
        },
        "test": {
          "builder": "@angular-devkit/build-angular:karma",
          "options": {
            "polyfills": ["zone.js", "zone.js/testing"],
            "tsConfig": "tsconfig.spec.json",
            "inlineStyleLanguage": "scss",
            "assets": ["src/favicon.ico", "src/assets"],
            "styles": ["src/styles.scss"],
            "scripts": []
          }
        }
      }
    }
  }
}'''

    def _generate_tsconfig(self) -> str:
        """Generate TypeScript configuration"""
        return '''{
  "compileOnSave": false,
  "compilerOptions": {
    "baseUrl": "./",
    "outDir": "./dist/out-tsc",
    "forceConsistentCasingInFileNames": true,
    "strict": true,
    "noImplicitOverride": true,
    "noPropertyAccessFromIndexSignature": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "sourceMap": true,
    "declaration": false,
    "downlevelIteration": true,
    "experimentalDecorators": true,
    "moduleResolution": "node",
    "importHelpers": true,
    "target": "ES2022",
    "module": "ES2022",
    "useDefineForClassFields": false,
    "lib": ["ES2022", "dom"]
  },
  "angularCompilerOptions": {
    "enableI18nLegacyMessageIdFormat": false,
    "strictInjectionParameters": true,
    "strictInputAccessModifiers": true,
    "strictTemplates": true
  }
}'''

    async def _fix_compilation_errors(self, code_files: Dict[str, Any], error: str) -> Dict[str, Any]:
        """Fix compilation errors"""
        # Simplified error fixing - in practice, this would be more sophisticated
        return code_files

    async def _fix_lint_errors(self, code_files: Dict[str, Any], error: str) -> Dict[str, Any]:
        """Fix lint errors"""
        # Simplified error fixing - in practice, this would be more sophisticated
        return code_files

    async def _fix_test_errors(self, code_files: Dict[str, Any], error: str) -> Dict[str, Any]:
        """Fix test errors"""
        # Simplified error fixing - in practice, this would be more sophisticated
        return code_files

    async def get_status(self) -> Dict[str, Any]:
        """Get agent status"""
        return {
            "name": self.name,
            "version": self.version,
            "angular_version": self.angular_version,
            "status": "active",
            "capabilities": [
                "Angular component generation",
                "TypeScript code generation",
                "HTML template creation",
                "SCSS styling",
                "Service generation",
                "Module configuration",
                "Routing setup",
                "Test file creation",
                "Build configuration"
            ]
        }