# 🚀 Backend Cloud Functions & Services

## 📁 Cloud Storage Architecture

### Storage Bucket Configuration
```
📦 Bucket: snapit
├── 🔧 {projectId}/
│   ├── dist/                    # Production builds & deployments
│   └── context/
│       ├── ui-images/          # UI screenshots & visual assets
│       └── assets/
│           ├── css/            # Stylesheets & themes
│           ├── images/         # Static images & icons
│           └── docs/           # Documentation & specs
```

## 🛠️ Microservices Architecture

### Core Services

#### 📤 Upload Service
```typescript
// POST /api/upload
interface UploadService {
  endpoint: "/api/upload"
  method: "POST"
  description: "Handles file uploads to cloud storage"
  
  features: [
    "Multi-file upload support",
    "Progress tracking",
    "File validation & security",
    "Automatic image optimization"
  ]
  
  payload: {
    files: File[]
    projectId: string
    metadata?: object
  }
  
  response: {
    uploadedFiles: UploadedFile[]
    storageUrls: string[]
    status: "success" | "error"
  }
}
```

#### 🧠 Embedding Service
```typescript
// POST /api/embeddings
interface EmbeddingService {
  endpoint: "/api/embeddings"
  method: "POST"
  description: "Generates vector embeddings for content"
  
  features: [
    "Text-to-vector conversion",
    "Image embedding generation",
    "Semantic similarity search",
    "Multi-modal embeddings"
  ]
  
  payload: {
    content: string | Buffer
    type: "text" | "image" | "multimodal"
    projectId: string
  }
  
  response: {
    embeddings: number[]
    dimensions: number
    model: string
    similarity_threshold: number
  }
}
```

#### 💾 Data Service
```typescript
// Multiple endpoints
interface DataService {
  endpoints: {
    get: "/api/data/{projectId}"
    post: "/api/data"
    put: "/api/data/{id}"
    delete: "/api/data/{id}"
  }
  
  description: "Manages project data & metadata storage with Firestore"
  
  features: [
    "CRUD operations with Firestore",
    "Real-time synchronization",
    "Document validation & schema enforcement",
    "Automatic backup & recovery",
    "Subcollection support"
  ]
  
  collections: {
    projects: "projects/{projectId}",
    assets: "projects/{projectId}/assets/{assetId}",
    embeddings: "projects/{projectId}/embeddings/{embeddingId}",
    analytics: "analytics/{date}"
  }
  
  models: {
    Project: {
      id: string
      name: string
      metadata: object
      createdAt: Timestamp
      updatedAt: Timestamp
      owner: string
    }
    
    Asset: {
      id: string
      projectId: string
      type: "image" | "css" | "document"
      url: string
      embeddings?: number[]
      createdAt: Timestamp
      size: number
    }
    
    Embedding: {
      id: string
      assetId: string
      vector: number[]
      dimensions: number
      model: string
      createdAt: Timestamp
    }
  }
}
```

## 🔧 Infrastructure & Deployment

### Firestore Database Structure
```
📚 Firestore Collections:
├── projects/                    # Main project documents
│   └── {projectId}/
│       ├── assets/             # Subcollection: project assets
│       │   └── {assetId}       # Individual asset documents
│       ├── embeddings/         # Subcollection: vector embeddings
│       │   └── {embeddingId}   # Embedding documents
│       └── metadata/           # Subcollection: project metadata
│           └── {metaId}        # Metadata documents
├── users/                      # User management
│   └── {userId}               # User documents
└── analytics/                  # Usage analytics
    └── {date}                 # Daily analytics documents
```

### Firestore Security Rules
```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Projects are readable by authenticated users
    match /projects/{projectId} {
      allow read, write: if request.auth != null 
        && request.auth.uid == resource.data.owner;
      
      // Assets subcollection
      match /assets/{assetId} {
        allow read, write: if request.auth != null;
      }
      
      // Embeddings subcollection
      match /embeddings/{embeddingId} {
        allow read, write: if request.auth != null;
      }
    }
    
    // Users can only access their own data
    match /users/{userId} {
      allow read, write: if request.auth != null 
        && request.auth.uid == userId;
    }
  }
}
```

### Cloud Functions Configuration
```yaml
functions:
  upload-service:
    runtime: "nodejs18"
    memory: "512MB"
    timeout: "60s"
    trigger: "https"
    
  embedding-service:
    runtime: "python39"
    memory: "1GB"
    timeout: "300s"
    trigger: "https"
    
  data-service:
    runtime: "nodejs18"
    memory: "256MB"
    timeout: "30s"
    trigger: "https"
```

### Environment Variables
```bash
# Storage Configuration
STORAGE_BUCKET=snapit
STORAGE_REGION=us-central1

# Database Configuration
FIRESTORE_PROJECT_ID=your-project-id
FIRESTORE_DATABASE_ID=(default)
REDIS_URL=redis://...

# API Keys
OPENAI_API_KEY=sk-...
GOOGLE_CLOUD_PROJECT=your-project-id

# Security
JWT_SECRET=your-jwt-secret
CORS_ORIGINS=https://yourdomain.com
```

## 📊 API Endpoints Overview

| Service | Endpoint | Method | Description |
|---------|----------|--------|-------------|
| 📤 Upload | `/api/upload` | POST | File upload & storage |
| 🧠 Embedding | `/api/embeddings` | POST | Generate vector embeddings |
| 💾 Data | `/api/data` | GET/POST/PUT/DELETE | Data management |
| 🔍 Search | `/api/search` | POST | Semantic search |
| 📈 Analytics | `/api/analytics` | GET | Usage analytics |

## 🚦 Status & Health Checks

```typescript
// GET /api/health
interface HealthCheck {
  status: "healthy" | "degraded" | "unhealthy"
  services: {
    upload: ServiceStatus
    embedding: ServiceStatus
    data: ServiceStatus
    storage: ServiceStatus
  }
  timestamp: string
  version: string
}
```

## 📚 Next Steps

Each service will be expanded with detailed documentation including:
- 📖 **API Specifications** - Complete OpenAPI/Swagger docs
- 🧪 **Testing Guide** - Unit, integration & e2e tests
- 🔒 **Security** - Authentication, authorization & data protection
- 📊 **Monitoring** - Logging, metrics & alerting
- 🚀 **Deployment** - CI/CD pipelines & infrastructure as code
