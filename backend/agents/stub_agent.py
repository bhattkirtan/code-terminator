"""
StubAgent - Creates service stubs and mock HTTP endpoints
"""
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class StubAgent:
    def __init__(self):
        self.name = "StubAgent"
        self.version = "1.0.0"
    
    async def create_service_stubs(self, code_files: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create service stubs and mock endpoints based on generated components
        """
        logger.info("Creating service stubs and mock endpoints")
        
        # Analyze components to identify required services
        required_services = await self._analyze_required_services(code_files)
        
        # Generate service interfaces
        service_interfaces = await self._generate_service_interfaces(required_services)
        
        # Generate mock implementations
        mock_implementations = await self._generate_mock_implementations(required_services)
        
        # Generate HTTP interceptors for mocking
        http_interceptors = await self._generate_http_interceptors(required_services)
        
        # Generate environment configurations
        environment_configs = await self._generate_environment_configs(required_services)
        
        result = {
            "service_interfaces": service_interfaces,
            "mock_implementations": mock_implementations,
            "http_interceptors": http_interceptors,
            "environment_configs": environment_configs,
            "mock_data": await self._generate_mock_data(required_services)
        }
        
        logger.info(f"Generated {len(service_interfaces)} service stubs")
        return result
    
    async def _analyze_required_services(self, code_files: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze components to identify required services"""
        services = []
        
        # Check if components exist
        components = code_files.get("components", {})
        
        # Common services based on component patterns
        if any("table" in comp_name or "data" in comp_name for comp_name in components.keys()):
            services.append({
                "name": "DataService",
                "type": "data_management",
                "endpoints": [
                    {"method": "GET", "path": "/api/data", "response": "DataItem[]"},
                    {"method": "POST", "path": "/api/data", "response": "DataItem"},
                    {"method": "PUT", "path": "/api/data/{id}", "response": "DataItem"},
                    {"method": "DELETE", "path": "/api/data/{id}", "response": "void"}
                ]
            })
        
        if any("user" in comp_name or "auth" in comp_name for comp_name in components.keys()):
            services.append({
                "name": "AuthService",
                "type": "authentication",
                "endpoints": [
                    {"method": "POST", "path": "/api/auth/login", "response": "AuthResponse"},
                    {"method": "POST", "path": "/api/auth/logout", "response": "void"},
                    {"method": "GET", "path": "/api/auth/profile", "response": "UserProfile"},
                    {"method": "POST", "path": "/api/auth/refresh", "response": "AuthResponse"}
                ]
            })
        
        if any("notification" in comp_name or "alert" in comp_name for comp_name in components.keys()):
            services.append({
                "name": "NotificationService",
                "type": "notification",
                "endpoints": [
                    {"method": "GET", "path": "/api/notifications", "response": "Notification[]"},
                    {"method": "POST", "path": "/api/notifications/mark-read", "response": "void"},
                    {"method": "DELETE", "path": "/api/notifications/{id}", "response": "void"}
                ]
            })
        
        # Add default API service
        services.append({
            "name": "ApiService",
            "type": "generic_api",
            "endpoints": [
                {"method": "GET", "path": "/api/{endpoint}", "response": "T"},
                {"method": "POST", "path": "/api/{endpoint}", "response": "T"},
                {"method": "PUT", "path": "/api/{endpoint}", "response": "T"},
                {"method": "DELETE", "path": "/api/{endpoint}", "response": "T"}
            ]
        })
        
        return services
    
    async def _generate_service_interfaces(self, services: List[Dict[str, Any]]) -> Dict[str, str]:
        """Generate TypeScript interfaces for services"""
        interfaces = {}
        
        for service in services:
            service_name = service["name"]
            interface_content = self._create_service_interface(service)
            interfaces[f"{service_name.lower()}.interface.ts"] = interface_content
        
        return interfaces
    
    def _create_service_interface(self, service: Dict[str, Any]) -> str:
        """Create TypeScript interface for a service"""
        service_name = service["name"]
        service_type = service["type"]
        endpoints = service["endpoints"]
        
        # Generate method signatures
        method_signatures = []
        for endpoint in endpoints:
            method_name = self._endpoint_to_method_name(endpoint)
            method_signature = self._generate_method_signature(endpoint, method_name)
            method_signatures.append(method_signature)
        
        return f'''import {{ Observable }} from 'rxjs';

// Data models for {service_name}
{self._generate_data_models(service)}

/**
 * Interface for {service_name}
 * Service type: {service_type}
 */
export interface I{service_name} {{
{chr(10).join("  " + sig for sig in method_signatures)}
}}

// Request/Response types
{self._generate_request_response_types(service)}
'''

    def _generate_data_models(self, service: Dict[str, Any]) -> str:
        """Generate data model interfaces"""
        service_name = service["name"]
        
        if service["type"] == "data_management":
            return '''export interface DataItem {
  id: number;
  name: string;
  description?: string;
  status: 'active' | 'inactive' | 'pending';
  createdAt: Date;
  updatedAt: Date;
}

export interface DataFilter {
  search?: string;
  status?: string;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
  page?: number;
  limit?: number;
}'''
        
        elif service["type"] == "authentication":
            return '''export interface AuthResponse {
  token: string;
  refreshToken: string;
  user: UserProfile;
  expiresIn: number;
}

export interface UserProfile {
  id: string;
  username: string;
  email: string;
  firstName: string;
  lastName: string;
  roles: string[];
  lastLogin?: Date;
}

export interface LoginRequest {
  username: string;
  password: string;
  rememberMe?: boolean;
}'''
        
        elif service["type"] == "notification":
            return '''export interface Notification {
  id: string;
  title: string;
  message: string;
  type: 'info' | 'success' | 'warning' | 'error';
  read: boolean;
  createdAt: Date;
  actionUrl?: string;
}'''
        
        else:
            return '''export interface ApiResponse<T> {
  data: T;
  success: boolean;
  message?: string;
  errors?: string[];
}'''

    def _generate_request_response_types(self, service: Dict[str, Any]) -> str:
        """Generate request and response type definitions"""
        return '''// HTTP Response wrapper
export interface HttpResponse<T> {
  data: T;
  status: number;
  message?: string;
  timestamp: Date;
}

// Error response
export interface ErrorResponse {
  error: string;
  message: string;
  statusCode: number;
  timestamp: Date;
}

// Pagination response
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  limit: number;
  totalPages: number;
}'''

    def _endpoint_to_method_name(self, endpoint: Dict[str, Any]) -> str:
        """Convert endpoint to method name"""
        method = endpoint["method"].lower()
        path = endpoint["path"]
        
        # Extract meaningful parts from path
        path_parts = [part for part in path.split('/') if part and not part.startswith('{')]
        
        if method == "get":
            if path.endswith('}'):  # Single item
                return f"get{path_parts[-1].title()}"
            else:  # Collection
                return f"get{path_parts[-1].title()}"
        elif method == "post":
            return f"create{path_parts[-1].title()}"
        elif method == "put":
            return f"update{path_parts[-1].title()}"
        elif method == "delete":
            return f"delete{path_parts[-1].title()}"
        
        return f"{method}{path_parts[-1].title()}"

    def _generate_method_signature(self, endpoint: Dict[str, Any], method_name: str) -> str:
        """Generate TypeScript method signature"""
        method = endpoint["method"]
        response_type = endpoint["response"]
        
        # Determine parameters based on method and path
        params = []
        
        if "{id}" in endpoint["path"]:
            params.append("id: string | number")
        
        if method in ["POST", "PUT"]:
            if "auth" in endpoint["path"]:
                params.append("credentials: LoginRequest")
            else:
                params.append("data: any")
        
        if method == "GET" and not "{id}" in endpoint["path"]:
            params.append("filter?: any")
        
        param_str = ", ".join(params)
        return f"{method_name}({param_str}): Observable<{response_type}>;"

    async def _generate_mock_implementations(self, services: List[Dict[str, Any]]) -> Dict[str, str]:
        """Generate mock service implementations"""
        implementations = {}
        
        for service in services:
            service_name = service["name"]
            impl_content = self._create_mock_implementation(service)
            implementations[f"mock-{service_name.lower()}.service.ts"] = impl_content
        
        return implementations

    def _create_mock_implementation(self, service: Dict[str, Any]) -> str:
        """Create mock service implementation"""
        service_name = service["name"]
        service_type = service["type"]
        
        # Generate mock methods
        mock_methods = []
        for endpoint in service["endpoints"]:
            method_name = self._endpoint_to_method_name(endpoint)
            mock_method = self._generate_mock_method(endpoint, method_name, service_type)
            mock_methods.append(mock_method)
        
        return f'''import {{ Injectable }} from '@angular/core';
import {{ Observable, of, delay, throwError }} from 'rxjs';
import {{ I{service_name} }} from './{service_name.lower()}.interface';
{self._get_mock_imports(service)}

@Injectable({{
  providedIn: 'root'
}})
export class Mock{service_name} implements I{service_name} {{
  private mockData = {self._generate_mock_data_property(service)};
  
  constructor() {{
    console.log('Mock{service_name} initialized');
  }}

{chr(10).join("  " + method for method in mock_methods)}

  // Utility methods
  private delay(ms: number = 500): Observable<any> {{
    return of(null).pipe(delay(ms));
  }}

  private simulateError(probability: number = 0.1): boolean {{
    return Math.random() < probability;
  }}
}}'''

    def _get_mock_imports(self, service: Dict[str, Any]) -> str:
        """Get imports for mock service"""
        service_type = service["type"]
        
        if service_type == "data_management":
            return "import { DataItem, DataFilter } from './data.interface';"
        elif service_type == "authentication":
            return "import { AuthResponse, UserProfile, LoginRequest } from './auth.interface';"
        elif service_type == "notification":
            return "import { Notification } from './notification.interface';"
        else:
            return ""

    def _generate_mock_data_property(self, service: Dict[str, Any]) -> str:
        """Generate mock data property for service"""
        service_type = service["type"]
        
        if service_type == "data_management":
            return '''[
    { id: 1, name: 'Item 1', description: 'First item', status: 'active', createdAt: new Date(), updatedAt: new Date() },
    { id: 2, name: 'Item 2', description: 'Second item', status: 'inactive', createdAt: new Date(), updatedAt: new Date() },
    { id: 3, name: 'Item 3', description: 'Third item', status: 'pending', createdAt: new Date(), updatedAt: new Date() }
  ]'''
        
        elif service_type == "notification":
            return '''[
    { id: '1', title: 'Welcome', message: 'Welcome to the application', type: 'info', read: false, createdAt: new Date() },
    { id: '2', title: 'Update Available', message: 'A new version is available', type: 'success', read: false, createdAt: new Date() }
  ]'''
        
        else:
            return "[]"

    def _generate_mock_method(self, endpoint: Dict[str, Any], method_name: str, service_type: str) -> str:
        """Generate individual mock method"""
        method = endpoint["method"]
        response_type = endpoint["response"]
        
        if service_type == "data_management":
            return self._generate_data_service_method(endpoint, method_name, method)
        elif service_type == "authentication":
            return self._generate_auth_service_method(endpoint, method_name, method)
        elif service_type == "notification":
            return self._generate_notification_service_method(endpoint, method_name, method)
        else:
            return self._generate_generic_method(endpoint, method_name, method)

    def _generate_data_service_method(self, endpoint: Dict[str, Any], method_name: str, method: str) -> str:
        """Generate data service mock method"""
        if method == "GET":
            if "{id}" in endpoint["path"]:
                return f'''
{method_name}(id: string | number): Observable<DataItem> {{
  if (this.simulateError()) {{
    return throwError(() => new Error('Item not found'));
  }}
  
  const item = this.mockData.find(item => item.id === Number(id));
  return of(item).pipe(delay(300));
}}'''
            else:
                return f'''
{method_name}(filter?: DataFilter): Observable<DataItem[]> {{
  if (this.simulateError()) {{
    return throwError(() => new Error('Failed to fetch data'));
  }}
  
  let result = [...this.mockData];
  
  if (filter?.search) {{
    result = result.filter(item => 
      item.name.toLowerCase().includes(filter.search!.toLowerCase())
    );
  }}
  
  if (filter?.status) {{
    result = result.filter(item => item.status === filter.status);
  }}
  
  return of(result).pipe(delay(500));
}}'''
        
        elif method == "POST":
            return f'''
{method_name}(data: Partial<DataItem>): Observable<DataItem> {{
  if (this.simulateError()) {{
    return throwError(() => new Error('Failed to create item'));
  }}
  
  const newItem: DataItem = {{
    id: Math.max(...this.mockData.map(i => i.id)) + 1,
    name: data.name || 'New Item',
    description: data.description || '',
    status: data.status || 'pending',
    createdAt: new Date(),
    updatedAt: new Date()
  }};
  
  this.mockData.push(newItem);
  return of(newItem).pipe(delay(400));
}}'''
        
        elif method == "PUT":
            return f'''
{method_name}(id: string | number, data: Partial<DataItem>): Observable<DataItem> {{
  if (this.simulateError()) {{
    return throwError(() => new Error('Failed to update item'));
  }}
  
  const index = this.mockData.findIndex(item => item.id === Number(id));
  if (index === -1) {{
    return throwError(() => new Error('Item not found'));
  }}
  
  this.mockData[index] = {{
    ...this.mockData[index],
    ...data,
    updatedAt: new Date()
  }};
  
  return of(this.mockData[index]).pipe(delay(400));
}}'''
        
        elif method == "DELETE":
            return f'''
{method_name}(id: string | number): Observable<void> {{
  if (this.simulateError()) {{
    return throwError(() => new Error('Failed to delete item'));
  }}
  
  const index = this.mockData.findIndex(item => item.id === Number(id));
  if (index === -1) {{
    return throwError(() => new Error('Item not found'));
  }}
  
  this.mockData.splice(index, 1);
  return of(undefined).pipe(delay(300));
}}'''
        
        return ""

    def _generate_auth_service_method(self, endpoint: Dict[str, Any], method_name: str, method: str) -> str:
        """Generate auth service mock method"""
        if "login" in endpoint["path"]:
            return f'''
{method_name}(credentials: LoginRequest): Observable<AuthResponse> {{
  if (this.simulateError()) {{
    return throwError(() => new Error('Invalid credentials'));
  }}
  
  // Simulate authentication
  if (credentials.username === 'admin' && credentials.password === 'password') {{
    const response: AuthResponse = {{
      token: 'mock-jwt-token-' + Date.now(),
      refreshToken: 'mock-refresh-token-' + Date.now(),
      user: {{
        id: '1',
        username: credentials.username,
        email: 'admin@example.com',
        firstName: 'Admin',
        lastName: 'User',
        roles: ['admin'],
        lastLogin: new Date()
      }},
      expiresIn: 3600
    }};
    
    return of(response).pipe(delay(800));
  }}
  
  return throwError(() => new Error('Invalid username or password'));
}}'''
        
        elif "logout" in endpoint["path"]:
            return f'''
{method_name}(): Observable<void> {{
  return of(undefined).pipe(delay(200));
}}'''
        
        elif "profile" in endpoint["path"]:
            return f'''
{method_name}(): Observable<UserProfile> {{
  const profile: UserProfile = {{
    id: '1',
    username: 'admin',
    email: 'admin@example.com',
    firstName: 'Admin',
    lastName: 'User',
    roles: ['admin'],
    lastLogin: new Date()
  }};
  
  return of(profile).pipe(delay(300));
}}'''
        
        return ""

    def _generate_notification_service_method(self, endpoint: Dict[str, Any], method_name: str, method: str) -> str:
        """Generate notification service mock method"""
        if method == "GET":
            return f'''
{method_name}(): Observable<Notification[]> {{
  return of(this.mockData).pipe(delay(400));
}}'''
        
        return ""

    def _generate_generic_method(self, endpoint: Dict[str, Any], method_name: str, method: str) -> str:
        """Generate generic API method"""
        return f'''
{method_name}(...args: any[]): Observable<any> {{
  // Generic mock implementation
  return of({{ success: true, data: null, message: 'Mock response for {method_name}' }}).pipe(delay(500));
}}'''

    async def _generate_http_interceptors(self, services: List[Dict[str, Any]]) -> Dict[str, str]:
        """Generate HTTP interceptors for mock responses"""
        return {
            "mock-http.interceptor.ts": self._create_mock_http_interceptor(services),
            "error-handling.interceptor.ts": self._create_error_handling_interceptor(),
            "loading.interceptor.ts": self._create_loading_interceptor()
        }

    def _create_mock_http_interceptor(self, services: List[Dict[str, Any]]) -> str:
        """Create HTTP interceptor for mocking API calls"""
        mock_routes = []
        
        for service in services:
            for endpoint in service["endpoints"]:
                route = f"    // {endpoint['method']} {endpoint['path']}"
                mock_routes.append(route)
        
        return f'''import {{ Injectable }} from '@angular/core';
import {{ HttpInterceptor, HttpRequest, HttpHandler, HttpEvent, HttpResponse }} from '@angular/common/http';
import {{ Observable, of, delay, throwError }} from 'rxjs';
import {{ environment }} from '../environments/environment';

@Injectable()
export class MockHttpInterceptor implements HttpInterceptor {{
  
  intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {{
    // Only mock in development mode
    if (!environment.production && environment.useMockData) {{
      return this.handleMockRequest(req);
    }}
    
    return next.handle(req);
  }}
  
  private handleMockRequest(req: HttpRequest<any>): Observable<HttpEvent<any>> {{
    const {{ method, url }} = req;
    
    // Mock routes mapping
{chr(10).join(mock_routes)}
    
    // Default mock response
    const mockResponse = {{
      success: true,
      data: null,
      message: `Mock response for ${{method}} ${{url}}`,
      timestamp: new Date()
    }};
    
    return of(new HttpResponse({{
      status: 200,
      body: mockResponse
    }})).pipe(delay(Math.random() * 1000 + 300)); // Random delay 300-1300ms
  }}
  
  private simulateError(probability: number = 0.1): boolean {{
    return Math.random() < probability;
  }}
}}'''

    def _create_error_handling_interceptor(self) -> str:
        """Create error handling interceptor"""
        return '''import { Injectable } from '@angular/core';
import { HttpInterceptor, HttpRequest, HttpHandler, HttpEvent, HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError, retry } from 'rxjs/operators';

@Injectable()
export class ErrorHandlingInterceptor implements HttpInterceptor {
  
  intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    return next.handle(req).pipe(
      retry(1), // Retry failed requests once
      catchError((error: HttpErrorResponse) => {
        let errorMessage = 'An error occurred';
        
        if (error.error instanceof ErrorEvent) {
          // Client-side error
          errorMessage = `Client Error: ${error.error.message}`;
        } else {
          // Server-side error
          errorMessage = `Server Error: ${error.status} - ${error.message}`;
        }
        
        console.error('HTTP Error:', errorMessage);
        
        // You can add notification service here to show user-friendly messages
        
        return throwError(() => error);
      })
    );
  }
}'''

    def _create_loading_interceptor(self) -> str:
        """Create loading interceptor"""
        return '''import { Injectable } from '@angular/core';
import { HttpInterceptor, HttpRequest, HttpHandler, HttpEvent } from '@angular/common/http';
import { Observable } from 'rxjs';
import { finalize } from 'rxjs/operators';

export interface LoadingService {
  show(): void;
  hide(): void;
}

@Injectable()
export class LoadingInterceptor implements HttpInterceptor {
  private totalRequests = 0;
  
  constructor(private loadingService: LoadingService) {}
  
  intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    this.totalRequests++;
    this.loadingService.show();
    
    return next.handle(req).pipe(
      finalize(() => {
        this.totalRequests--;
        if (this.totalRequests === 0) {
          this.loadingService.hide();
        }
      })
    );
  }
}'''

    async def _generate_environment_configs(self, services: List[Dict[str, Any]]) -> Dict[str, str]:
        """Generate environment configurations"""
        return {
            "environment.mock.ts": self._create_mock_environment(),
            "environment.dev.ts": self._create_dev_environment(),
            "environment.staging.ts": self._create_staging_environment()
        }

    def _create_mock_environment(self) -> str:
        """Create mock environment configuration"""
        return '''export const environment = {
  production: false,
  apiUrl: 'http://localhost:3000/api',
  useMockData: true,
  mockDelay: 500,
  errorProbability: 0.1,
  features: {
    enableLogging: true,
    enableMockNotifications: true,
    enableOfflineMode: true
  },
  auth: {
    tokenKey: 'mock_auth_token',
    refreshTokenKey: 'mock_refresh_token',
    tokenExpiry: 3600000 // 1 hour
  }
};'''

    def _create_dev_environment(self) -> str:
        """Create development environment configuration"""
        return '''export const environment = {
  production: false,
  apiUrl: 'http://localhost:3000/api',
  useMockData: false,
  features: {
    enableLogging: true,
    enableDebugTools: true
  },
  auth: {
    tokenKey: 'dev_auth_token',
    refreshTokenKey: 'dev_refresh_token'
  }
};'''

    def _create_staging_environment(self) -> str:
        """Create staging environment configuration"""
        return '''export const environment = {
  production: false,
  apiUrl: 'https://staging-api.example.com/api',
  useMockData: false,
  features: {
    enableLogging: true,
    enableAnalytics: true
  },
  auth: {
    tokenKey: 'staging_auth_token',
    refreshTokenKey: 'staging_refresh_token'
  }
};'''

    async def _generate_mock_data(self, services: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate comprehensive mock data"""
        mock_data = {}
        
        for service in services:
            service_type = service["type"]
            service_name = service["name"].lower()
            
            if service_type == "data_management":
                mock_data[f"{service_name}_data"] = self._generate_data_service_mocks()
            elif service_type == "authentication":
                mock_data[f"{service_name}_data"] = self._generate_auth_service_mocks()
            elif service_type == "notification":
                mock_data[f"{service_name}_data"] = self._generate_notification_service_mocks()
        
        return mock_data

    def _generate_data_service_mocks(self) -> Dict[str, Any]:
        """Generate mock data for data service"""
        return {
            "items": [
                {"id": 1, "name": "Project Alpha", "description": "First project", "status": "active", "priority": "high"},
                {"id": 2, "name": "Project Beta", "description": "Second project", "status": "inactive", "priority": "medium"},
                {"id": 3, "name": "Project Gamma", "description": "Third project", "status": "pending", "priority": "low"},
                {"id": 4, "name": "Project Delta", "description": "Fourth project", "status": "active", "priority": "high"},
                {"id": 5, "name": "Project Epsilon", "description": "Fifth project", "status": "completed", "priority": "medium"}
            ],
            "pagination": {
                "total": 25,
                "page": 1,
                "limit": 10,
                "totalPages": 3
            },
            "filters": {
                "statuses": ["active", "inactive", "pending", "completed"],
                "priorities": ["low", "medium", "high"]
            }
        }

    def _generate_auth_service_mocks(self) -> Dict[str, Any]:
        """Generate mock data for auth service"""
        return {
            "users": [
                {"username": "admin", "password": "password", "role": "admin"},
                {"username": "user", "password": "user123", "role": "user"},
                {"username": "demo", "password": "demo", "role": "demo"}
            ],
            "profiles": {
                "admin": {
                    "id": "1",
                    "username": "admin",
                    "email": "admin@example.com",
                    "firstName": "Admin",
                    "lastName": "User",
                    "roles": ["admin", "user"]
                },
                "user": {
                    "id": "2",
                    "username": "user",
                    "email": "user@example.com",
                    "firstName": "Regular",
                    "lastName": "User",
                    "roles": ["user"]
                }
            }
        }

    def _generate_notification_service_mocks(self) -> Dict[str, Any]:
        """Generate mock data for notification service"""
        return {
            "notifications": [
                {
                    "id": "1",
                    "title": "Welcome to the App",
                    "message": "Thank you for using our application!",
                    "type": "info",
                    "read": False,
                    "createdAt": "2024-01-01T10:00:00Z"
                },
                {
                    "id": "2",
                    "title": "System Update",
                    "message": "The system will be updated tonight at 2 AM",
                    "type": "warning",
                    "read": False,
                    "createdAt": "2024-01-02T14:30:00Z"
                },
                {
                    "id": "3",
                    "title": "Success!",
                    "message": "Your profile has been updated successfully",
                    "type": "success",
                    "read": True,
                    "createdAt": "2024-01-03T09:15:00Z"
                }
            ]
        }

    async def get_status(self) -> Dict[str, Any]:
        """Get agent status"""
        return {
            "name": self.name,
            "version": self.version,
            "status": "active",
            "capabilities": [
                "Service interface generation",
                "Mock implementation creation",
                "HTTP interceptor generation",
                "Environment configuration",
                "Mock data generation",
                "API endpoint stubbing",
                "Error simulation",
                "Response mocking"
            ]
        }