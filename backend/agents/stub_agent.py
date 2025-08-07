"""Stub Agent for generating service stubs and mock endpoints."""

from typing import Any, Dict, List

from config.settings import settings
from shared.models import AgentResult, ComponentFile
from shared.utils import estimate_tokens, sanitize_component_name
from .base_agent import BaseAgent


class StubAgent(BaseAgent):
    """Agent that creates service stubs and mock HTTP endpoints."""
    
    def __init__(self):
        super().__init__("StubAgent")
    
    async def process(self, input_data: Dict[str, Any]) -> AgentResult:
        """Generate service stubs and mock data."""
        component_structure = input_data.get("component_structure", {})
        component_name = input_data.get("component_name", "generated-component")
        
        try:
            # Generate service files
            service_files = await self._generate_service_stubs(component_name, component_structure)
            
            # Generate mock data
            mock_data = await self._generate_mock_data(component_structure)
            
            # Generate interceptor for mocking
            interceptor = await self._generate_mock_interceptor()
            
            all_files = service_files + [interceptor]
            total_tokens = sum(estimate_tokens(file.content) for file in all_files)
            
            return AgentResult(
                agent_name=self.name,
                success=True,
                output={
                    "service_files": [f.dict() for f in service_files],
                    "mock_interceptor": interceptor.dict(),
                    "mock_data": mock_data
                },
                tokens_used=total_tokens,
                carbon_emission=self._calculate_carbon_emission(
                    total_tokens,
                    "stub-generation"
                )
            )
            
        except Exception as e:
            return AgentResult(
                agent_name=self.name,
                success=False,
                error=f"Stub generation failed: {str(e)}"
            )
    
    async def _generate_service_stubs(self, component_name: str, structure: Dict[str, Any]) -> List[ComponentFile]:
        """Generate Angular service stubs."""
        clean_name = sanitize_component_name(component_name)
        service_files = []
        
        # Main data service
        data_service = self._generate_data_service(clean_name)
        service_files.append(ComponentFile(
            filename=f"{clean_name}.service.ts",
            content=data_service,
            file_type="ts"
        ))
        
        # API service for HTTP calls
        api_service = self._generate_api_service(clean_name)
        service_files.append(ComponentFile(
            filename=f"{clean_name}-api.service.ts",
            content=api_service,
            file_type="ts"
        ))
        
        # Model interfaces
        models = self._generate_model_interfaces(clean_name)
        service_files.append(ComponentFile(
            filename=f"{clean_name}.models.ts",
            content=models,
            file_type="ts"
        ))
        
        return service_files
    
    def _generate_data_service(self, name: str) -> str:
        """Generate main data service."""
        class_name = "".join(word.capitalize() for word in name.split("-"))
        
        return f"""import {{ Injectable }} from '@angular/core';
import {{ BehaviorSubject, Observable, of }} from 'rxjs';
import {{ delay, map }} from 'rxjs/operators';
import {{ {class_name}Item, {class_name}Filter }} from './{name}.models';

@Injectable({{
  providedIn: 'root'
}})
export class {class_name}Service {{
  private dataSubject = new BehaviorSubject<{class_name}Item[]>([]);
  private loadingSubject = new BehaviorSubject<boolean>(false);
  
  public data$ = this.dataSubject.asObservable();
  public loading$ = this.loadingSubject.asObservable();

  constructor() {{
    this.loadInitialData();
  }}

  /**
   * Load initial mock data
   */
  private loadInitialData(): void {{
    const mockData: {class_name}Item[] = [
      {{
        id: '1',
        title: 'Sample Item 1',
        description: 'This is a sample item for testing',
        status: 'active',
        createdAt: new Date(),
        updatedAt: new Date()
      }},
      {{
        id: '2', 
        title: 'Sample Item 2',
        description: 'Another sample item',
        status: 'pending',
        createdAt: new Date(),
        updatedAt: new Date()
      }}
    ];
    
    this.dataSubject.next(mockData);
  }}

  /**
   * Get all items
   */
  public getItems(): Observable<{class_name}Item[]> {{
    this.loadingSubject.next(true);
    
    return of(this.dataSubject.value).pipe(
      delay(500), // Simulate network delay
      map(items => {{
        this.loadingSubject.next(false);
        return items;
      }})
    );
  }}

  /**
   * Get item by ID
   */
  public getItemById(id: string): Observable<{class_name}Item | null> {{
    return this.data$.pipe(
      map(items => items.find(item => item.id === id) || null)
    );
  }}

  /**
   * Create new item
   */
  public createItem(item: Partial<{class_name}Item>): Observable<{class_name}Item> {{
    const newItem: {class_name}Item = {{
      id: Date.now().toString(),
      title: item.title || 'New Item',
      description: item.description || '',
      status: item.status || 'pending',
      createdAt: new Date(),
      updatedAt: new Date(),
      ...item
    }};

    const currentData = this.dataSubject.value;
    this.dataSubject.next([...currentData, newItem]);

    return of(newItem).pipe(delay(300));
  }}

  /**
   * Update existing item
   */
  public updateItem(id: string, updates: Partial<{class_name}Item>): Observable<{class_name}Item> {{
    const currentData = this.dataSubject.value;
    const index = currentData.findIndex(item => item.id === id);
    
    if (index === -1) {{
      throw new Error('Item not found');
    }}

    const updatedItem = {{
      ...currentData[index],
      ...updates,
      updatedAt: new Date()
    }};

    const newData = [...currentData];
    newData[index] = updatedItem;
    this.dataSubject.next(newData);

    return of(updatedItem).pipe(delay(300));
  }}

  /**
   * Delete item
   */
  public deleteItem(id: string): Observable<boolean> {{
    const currentData = this.dataSubject.value;
    const filteredData = currentData.filter(item => item.id !== id);
    this.dataSubject.next(filteredData);

    return of(true).pipe(delay(300));
  }}

  /**
   * Filter items
   */
  public filterItems(filter: {class_name}Filter): Observable<{class_name}Item[]> {{
    return this.data$.pipe(
      map(items => {{
        let filtered = items;

        if (filter.status) {{
          filtered = filtered.filter(item => item.status === filter.status);
        }}

        if (filter.searchTerm) {{
          const term = filter.searchTerm.toLowerCase();
          filtered = filtered.filter(item => 
            item.title.toLowerCase().includes(term) ||
            item.description.toLowerCase().includes(term)
          );
        }}

        return filtered;
      }})
    );
  }}
}}"""

    def _generate_api_service(self, name: str) -> str:
        """Generate API service for HTTP calls."""
        class_name = "".join(word.capitalize() for word in name.split("-"))
        
        return f"""import {{ Injectable }} from '@angular/core';
import {{ HttpClient, HttpParams }} from '@angular/common/http';
import {{ Observable }} from 'rxjs';
import {{ {class_name}Item, {class_name}Filter }} from './{name}.models';

@Injectable({{
  providedIn: 'root'
}})
export class {class_name}ApiService {{
  private readonly baseUrl = '/api/{name}';

  constructor(private http: HttpClient) {{}}

  /**
   * Get all items from API
   */
  public getItems(filter?: {class_name}Filter): Observable<{class_name}Item[]> {{
    let params = new HttpParams();
    
    if (filter?.status) {{
      params = params.set('status', filter.status);
    }}
    
    if (filter?.searchTerm) {{
      params = params.set('search', filter.searchTerm);
    }}

    return this.http.get<{class_name}Item[]>(this.baseUrl, {{ params }});
  }}

  /**
   * Get single item by ID
   */
  public getItem(id: string): Observable<{class_name}Item> {{
    return this.http.get<{class_name}Item>(`${{this.baseUrl}}/${{id}}`);
  }}

  /**
   * Create new item
   */
  public createItem(item: Partial<{class_name}Item>): Observable<{class_name}Item> {{
    return this.http.post<{class_name}Item>(this.baseUrl, item);
  }}

  /**
   * Update existing item
   */
  public updateItem(id: string, item: Partial<{class_name}Item>): Observable<{class_name}Item> {{
    return this.http.put<{class_name}Item>(`${{this.baseUrl}}/${{id}}`, item);
  }}

  /**
   * Delete item
   */
  public deleteItem(id: string): Observable<void> {{
    return this.http.delete<void>(`${{this.baseUrl}}/${{id}}`);
  }}

  /**
   * Bulk operations
   */
  public bulkCreate(items: Partial<{class_name}Item>[]): Observable<{class_name}Item[]> {{
    return this.http.post<{class_name}Item[]>(`${{this.baseUrl}}/bulk`, items);
  }}

  public bulkUpdate(updates: {{ id: string, data: Partial<{class_name}Item> }}[]): Observable<{class_name}Item[]> {{
    return this.http.patch<{class_name}Item[]>(`${{this.baseUrl}}/bulk`, updates);
  }}

  public bulkDelete(ids: string[]): Observable<void> {{
    return this.http.delete<void>(`${{this.baseUrl}}/bulk`, {{ 
      body: {{ ids }} 
    }});
  }}
}}"""

    def _generate_model_interfaces(self, name: str) -> str:
        """Generate TypeScript model interfaces."""
        class_name = "".join(word.capitalize() for word in name.split("-"))
        
        return f"""/**
 * Data models for {class_name} component
 */

export interface {class_name}Item {{
  id: string;
  title: string;
  description: string;
  status: 'active' | 'pending' | 'completed' | 'cancelled';
  createdAt: Date;
  updatedAt: Date;
  metadata?: Record<string, any>;
}}

export interface {class_name}Filter {{
  status?: string;
  searchTerm?: string;
  dateFrom?: Date;
  dateTo?: Date;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
}}

export interface {class_name}ApiResponse<T> {{
  data: T;
  message: string;
  success: boolean;
  timestamp: Date;
}}

export interface {class_name}PaginatedResponse<T> {{
  data: T[];
  totalItems: number;
  totalPages: number;
  currentPage: number;
  pageSize: number;
}}

export interface {class_name}BulkOperation {{
  operation: 'create' | 'update' | 'delete';
  items: Partial<{class_name}Item>[];
}}

export interface {class_name}ValidationError {{
  field: string;
  message: string;
  code: string;
}}

export type {class_name}Status = {class_name}Item['status'];

export class {class_name}FilterBuilder {{
  private filter: {class_name}Filter = {{}};

  public status(status: string): this {{
    this.filter.status = status;
    return this;
  }}

  public search(term: string): this {{
    this.filter.searchTerm = term;
    return this;
  }}

  public dateRange(from: Date, to: Date): this {{
    this.filter.dateFrom = from;
    this.filter.dateTo = to;
    return this;
  }}

  public sortBy(field: string, order: 'asc' | 'desc' = 'asc'): this {{
    this.filter.sortBy = field;
    this.filter.sortOrder = order;
    return this;
  }}

  public build(): {class_name}Filter {{
    return {{ ...this.filter }};
  }}
}}"""

    async def _generate_mock_data(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Generate mock data for testing."""
        return {
            "items": [
                {
                    "id": f"item-{i}",
                    "title": f"Sample Item {i}",
                    "description": f"Description for item {i}",
                    "status": ["active", "pending", "completed"][i % 3],
                    "createdAt": "2024-01-01T00:00:00Z",
                    "updatedAt": "2024-01-01T00:00:00Z"
                }
                for i in range(1, 11)
            ],
            "metadata": {
                "totalItems": 10,
                "version": "1.0.0",
                "lastUpdated": "2024-01-01T00:00:00Z"
            }
        }

    async def _generate_mock_interceptor(self) -> ComponentFile:
        """Generate HTTP interceptor for mocking API calls."""
        content = """import { Injectable } from '@angular/core';
import { HttpInterceptor, HttpRequest, HttpHandler, HttpResponse } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { delay } from 'rxjs/operators';

@Injectable()
export class MockDataInterceptor implements HttpInterceptor {
  private mockData: Record<string, any> = {
    // Mock data will be populated by the service
  };

  intercept(req: HttpRequest<any>, next: HttpHandler): Observable<any> {
    // Only intercept API calls in development mode
    if (!req.url.startsWith('/api/') || !this.isDevMode()) {
      return next.handle(req);
    }

    // Handle different HTTP methods
    switch (req.method) {
      case 'GET':
        return this.handleGet(req);
      case 'POST':
        return this.handlePost(req);
      case 'PUT':
      case 'PATCH':
        return this.handleUpdate(req);
      case 'DELETE':
        return this.handleDelete(req);
      default:
        return next.handle(req);
    }
  }

  private handleGet(req: HttpRequest<any>): Observable<HttpResponse<any>> {
    const urlParts = req.url.split('/');
    const resource = urlParts[urlParts.length - 1];
    
    // Simulate network delay
    return of(new HttpResponse({
      status: 200,
      body: this.mockData[resource] || { message: 'Mock data not found' }
    })).pipe(delay(300));
  }

  private handlePost(req: HttpRequest<any>): Observable<HttpResponse<any>> {
    return of(new HttpResponse({
      status: 201,
      body: { 
        ...req.body, 
        id: Date.now().toString(),
        createdAt: new Date().toISOString()
      }
    })).pipe(delay(300));
  }

  private handleUpdate(req: HttpRequest<any>): Observable<HttpResponse<any>> {
    return of(new HttpResponse({
      status: 200,
      body: { 
        ...req.body,
        updatedAt: new Date().toISOString()
      }
    })).pipe(delay(300));
  }

  private handleDelete(req: HttpRequest<any>): Observable<HttpResponse<any>> {
    return of(new HttpResponse({
      status: 204,
      body: null
    })).pipe(delay(300));
  }

  private isDevMode(): boolean {
    // Check if running in development mode
    return !environment.production;
  }

  public setMockData(data: Record<string, any>): void {
    this.mockData = { ...this.mockData, ...data };
  }
}

// Helper function to register the interceptor
export function provideMockDataInterceptor() {
  return {
    provide: HTTP_INTERCEPTORS,
    useClass: MockDataInterceptor,
    multi: true
  };
}"""
        
        return ComponentFile(
            filename="mock-data.interceptor.ts",
            content=content,
            file_type="ts"
        )