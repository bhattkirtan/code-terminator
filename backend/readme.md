# 🚀 AI DevOps Agent Platform - Backend Services

## 📁 Cloud Storage Architecture

### Storage Bucket Configuration
```
📦 Bucket: snapit-{projectId}
├── 🔧 {projectId}/
│   ├── dist/                    # Production builds & deployments
│   └── context/                # Project context and analysis
│       ├── ui-images/          # UI image analysis contexts
│       │   └── {imageId}/      # Individual image analysis folder
│       │       ├── analysis/   # Analysis results for this image
│       │       │   ├── complexity_heatmap.png
│       │       │   ├── component_visualization.png
│       │       │   ├── comprehensive_report.json
│       │       │   └── metadata.json
│       │       └── image.png   # Original uploaded image
│       ├── docs/               # Document RAG embeddings & analysis
│       │   └── {docId}/        # Individual document analysis folder
│       │       ├── analysis/   # Document RAG analysis
│       │       │   ├── embeddings.json     # Text embeddings
│       │       │   ├── chunks.json         # Document chunks
│       │       │   ├── summary.json        # AI-generated summary
│       │       │   ├── keywords.json       # Extracted keywords
│       │       │   └── metadata.json       # Document metadata
│       │       ├── document.{ext}  # Original document (pdf, md, txt, etc.)
│       │       └── processed/   # Processed versions
│       │           ├── text.txt        # Extracted text
│       │           ├── markdown.md     # Converted markdown
│       │           └── images/         # Extracted images
│       ├── links/              # External link RAG embeddings & analysis
│       │   └── {linkId}/       # Individual link analysis folder
│       │       ├── analysis/   # Link RAG analysis
│       │       │   ├── embeddings.json     # Text embeddings from fetched content
│       │       │   ├── chunks.json         # Content chunks
│       │       │   ├── summary.json        # AI-generated summary
│       │       │   ├── keywords.json       # Extracted keywords
│       │       │   └── metadata.json       # Link metadata & caching info
│       │       ├── cache/      # Cached content with TTL
│       │       │   ├── content.html    # Cached HTML content
│       │       │   ├── content.md      # Processed markdown
│       │       │   └── last_fetch.json # Last successful fetch data
│       │       └── link.json   # Original link reference & config
│       └── assets/             # Other project assets
│           ├── css/            # Stylesheets & themes
│           ├── images/         # Static images & icons
│           └── raw/            # Original unprocessed files
```

## 🛠️ AI-Powered Microservices Architecture

### Core Services

#### 📤 Upload Service
```typescript
// POST /api/upload
interface UploadService {
  endpoint: "/api/upload"
  method: "POST"
  description: "Handles file uploads with specialized UI image, document RAG, and general asset management"
  
  features: [
    "Multi-file upload support",
    "Progress tracking", 
    "File validation & security",
    "Automatic image optimization & thumbnails",
    "UI image individual folder creation",
    "Document RAG processing with embeddings",
    "Asset categorization by type",
    "Raw file preservation with version history",
    "Bucket initialization per project"
  ]
  
  storageStrategy: {
    "ui-images": "Each image gets its own folder: context/ui-images/{imageId}/",
    "documents": "Each document gets its own folder: context/docs/{docId}/ with RAG analysis",
    "other-assets": "Organized by type: context/assets/{assetType}/{assetId}",
    "rag-processing": "Documents processed for text extraction, chunking, and embeddings",
    "preservation": "Original files always preserved"
  }
  
  payload: {
    files: File[]
    projectId: string
    fileType: "ui-image" | "document" | "css" | "image" | "raw"
    ragEnabled?: boolean  // Enable RAG processing for documents
    chunkSize?: number    // Document chunking size (default: 1000)
    metadata?: object
    generateThumbnails?: boolean
    optimizeImages?: boolean
  }
  
  response: {
    uploadedFiles: UploadedFile[]
    storageUrls: string[]
    imageIds?: string[]    // For UI images
    docIds?: string[]      // For documents
    assetIds?: string[]    // For other assets
    folderPaths: string[]  // Full folder paths in GCS
    ragResults?: RAGProcessingResult[]  // Document processing results
    thumbnailUrls?: string[]
    optimizedUrls?: string[]
    status: "success" | "error"
  }
}
```

#### 🔗 Link Processing Service
```typescript
// Multiple endpoints for external link RAG processing
interface LinkService {
  endpoints: {
    add_link: "/api/links/add"                      // Add external link reference
    fetch_link: "/api/fetch/{linkId}"               // Runtime content fetch with caching
    refresh_link: "/api/refresh/{linkId}"           // Force refresh cached content
    get_status: "/api/status/{linkId}"              // Check cache status and freshness
    search_links: "/api/links/search"               // Search across cached link content
  }
  
  description: "External link processing with intelligent caching, RAG embeddings, and content extraction"
  
  features: [
    "🔗 External Link Content Fetching",
    "⏰ Intelligent TTL-based Caching",
    "📄 HTML to Text Content Extraction",
    "🧠 Vector Embeddings Generation",
    "🔍 Semantic Link Search",
    "📊 Content Type Classification",
    "⚡ Smart Cache Management",
    "🔄 Auto-refresh Scheduling",
    "📈 Link Analytics & Metrics"
  ]
  
  cachingStrategy: {
    contentTypes: {
      "api-docs": "2 hours TTL",
      "news": "1 hour TTL", 
      "blog": "1 hour TTL",
      "release-notes": "6 hours TTL",
      "tutorials": "12 hours TTL",
      "documentation": "6 hours TTL",
      "frameworks": "24 hours TTL",
      "specifications": "72 hours TTL",
      "standards": "7 days TTL",
      "static-content": "14 days TTL",
      "default": "24 hours TTL"
    },
    fallbackPolicy: "Use stale cache if fresh fetch fails",
    storageLocation: "{projectId}/context/links/{linkId}/cache/"
  }
  
  ragCapabilities: {
    contentExtraction: [
      "HTML parsing and text extraction",
      "Content cleanup and formatting",
      "Title and metadata extraction",
      "Content type auto-detection"
    ],
    embeddings: [
      "Vector embeddings per link content",
      "Semantic similarity search",
      "Cross-link content analysis",
      "Tag-based categorization"
    ],
    analytics: [
      "Fetch frequency tracking",
      "Content freshness monitoring",
      "Cache hit/miss statistics",
      "Content change detection"
    ]
  }
  
  storage: {
    structure: "{projectId}/context/links/{linkId}/",
    files: [
      "link.json (metadata and configuration)",
      "cache/content.json (cached content with TTL)",
      "cache/content.html (raw HTML cache)",
      "analysis/embeddings.json (vector embeddings)",
      "analysis/metadata.json (extracted metadata)"
    ],
    workflow: "Add Link → Content Fetch → Cache Storage → RAG Processing → Search Integration"
  }
  
  payload: {
    add: {
      projectId: string
      url: string
      contentType?: string  // Auto-detected or manual classification
      priority?: "low" | "medium" | "high"
      title?: string
      tags?: string[]
    },
    fetch: {
      projectId: string
      forceRefresh?: boolean
      generateEmbeddings?: boolean
    },
    search: {
      projectId: string
      query?: string
      embedding?: number[]
      searchType?: "semantic" | "keyword" | "metadata" | "all"
      threshold?: number
      limit?: number
    }
  }
  
  response: {
    add: {
      status: "success"
      linkId: string
      metadata: LinkMetadata
      folderPath: string
      ttlHours: number
    },
    fetch: {
      status: "success"
      linkId: string
      url: string
      content: string
      embeddings: number[]
      cached: boolean
      fetchedAt: string
      expiresAt: string
      freshness: "fresh" | "stale"
      wordCount: number
    },
    search: {
      status: "success"
      links: SearchResult[]
      count: number
      searchType: string
      query: string
      threshold: number
    }
  }
}
```

#### 🧠 AI Embedding & Analysis Service
```typescript
// Multiple AI-powered endpoints
interface EmbeddingService {
  endpoints: {
    analyze_image: "/api/analyze_image"           // Comprehensive image analysis
    analyze_document: "/api/analyze_document"     // Document RAG processing
    generate_embeddings: "/api/generate_embeddings"  // Text-to-vector conversion
    detect_components: "/api/detect_components"    // UI component detection
    generate_heatmap: "/api/generate_heatmap"     // Complexity heatmap generation
    process_document_rag: "/api/process_document_rag"  // Full document RAG workflow
    search_documents: "/api/search_documents"     // Document semantic search
    comprehensive_analysis: "/api/comprehensive_analysis"  // All-in-one analysis
    get_analysis: "/api/get_analysis/{analysisId}"  // Retrieve analysis results
  }
  
  description: "AI-powered analysis with computer vision, document RAG, embeddings, and complexity metrics"
  
  features: [
    "🎯 UI Component Detection (buttons, inputs, navigation, cards, tables, text)",
    "🔥 Complexity Heatmap Generation",
    "📊 Vector Embeddings with OpenAI",
    "🎨 Visual Component Analysis",
    "� Document RAG Processing",
    "🔍 Document Text Extraction & Chunking",
    "📝 AI-Generated Document Summaries",
    "🏷️ Keyword Extraction & Tagging",
    "�📈 Comprehensive Analysis Reports",
    "☁️ GCS Storage Integration",
    "🔍 Multi-modal Search Support"
  ]
  
  ragCapabilities: {
    documentProcessing: [
      "PDF, Word, Markdown, TXT text extraction",
      "Intelligent document chunking (configurable size)",
      "Vector embeddings per chunk",
      "Document structure preservation",
      "Image extraction from documents"
    ],
    semanticAnalysis: [
      "AI-generated document summaries",
      "Keyword and entity extraction",
      "Topic modeling and categorization",
      "Cross-document similarity analysis"
    ],
    searchAndRetrieval: [
      "Semantic document search",
      "Chunk-level similarity search",
      "Question-answering over documents",
      "Context-aware document recommendations"
    ]
  }
  
  storage: {
    uiImageStructure: "{projectId}/context/ui-images/{imageId}/",
    documentStructure: "{projectId}/context/docs/{docId}/",
    assetStructure: "{projectId}/context/assets/{assetType}/",
    analysisLocation: "Analysis results stored alongside original files",
    outputs: [
      "Original files (image.png, document.{ext} in respective folders)",
      "UI: Component visualizations, complexity heatmaps", 
      "Docs: Text embeddings, chunks, summaries, keywords",
      "Analysis metadata JSON",
      "Comprehensive reports"
    ],
    workflow: "Upload → Individual Folder → AI Analysis → RAG Processing → Results in Same Folder"
  }
}
```

#### 💾 Advanced Data Service
```typescript
// Multiple endpoints with extensive Firestore integration
interface DataService {
  endpoints: {
    get: "/api/data/{collection}/{projectId?}"
    post: "/api/data/{collection}"
    put: "/api/data/{collection}/{id}"
    delete: "/api/data/{collection}/{id}"
    create_project: "/api/create_project"
    load_data: "/api/load_data"
    get_project: "/api/get_project/{projectId}"
  }
  
  description: "Advanced project data management with comprehensive Firestore collections"
  
  features: [
    "🔥 Advanced Firestore Collections (50+ collection types)",
    "📊 Project-centric subcollection architecture", 
    "⚡ Real-time synchronization",
    "🔒 Document validation & schema enforcement",
    "💾 Automatic backup & recovery",
    "📈 Analytics and performance tracking",
    "🌱 Carbon footprint monitoring",
    "📋 Quality gates and validation",
    "🔄 Version control and snapshots"
  ]
  
  collections: {
    core: ["projects", "assets", "embeddings", "components", "heatmaps", "metadata"],
    agents: ["agent_executions", "agent_timeline", "prompt_history", "agent_performance"],
    versions: ["project_versions", "version_snapshots", "prompt_lineage", "code_diffs"],
    quality: ["validation_results", "code_reviews", "accuracy_validation", "test_results", "accessibility_checks"],
    analysis: ["ui_analysis", "layout_analysis", "complexity_analysis", "pattern_detection"],
    carbon: ["carbon_tracking", "model_usage", "sustainability_metrics", "carbon_reports"],
    documentation: ["documentation", "walkthroughs", "export_history", "delivery_checklists"],
    users: ["users", "teams", "user_preferences", "project_permissions"],
    system: ["analytics", "system_logs", "error_logs", "performance_logs"],
    testing: ["test_data", "mock_apis", "faker_schemas"],
    devops: ["pipelines", "deployments", "environments", "secrets"]
  }
}
```

#### 🔍 Enhanced Search Service
```typescript
// Advanced semantic and similarity search
interface SearchService {
  endpoints: {
    semantic_search: "/api/search"                    // Vector similarity search
    search_assets: "/api/search_assets"               // Asset metadata search
    search_components: "/api/search_components"       // Component type/analysis search
    search_analysis: "/api/search_analysis"           // Analysis results search
    search_by_complexity: "/api/search_by_complexity" // Complexity score filtering
    search_project: "/api/search_project/{projectId}" // Project search metadata
    find_similar_components: "/api/search_similar_components/{componentId}" // Component similarity
  }
  
  description: "Multi-modal search with AI-powered similarity and filtering"
  
  features: [
    "🔍 Semantic Search via Vector Embeddings",
    "🎯 Component Similarity Matching",
    "📊 Complexity-based Filtering",
    "🔬 Analysis Results Search",
    "📈 Advanced Query Filtering",
    "⚡ Real-time Search Statistics",
    "🎨 Multi-collection Search Support"
  ]
  
  searchCapabilities: {
    vectorSearch: "Cosine similarity with configurable thresholds",
    componentSimilarity: "Type, confidence, size, and aspect ratio matching",
    complexityFiltering: "Min/max complexity score ranges",
    analysisSearch: "Cross-collection analysis result querying",
    assetFiltering: "Content type and metadata filtering"
  }
}
```

#### 🏗️ Project Initialization Service
```typescript
// Project setup and GCS bucket management
interface ProjectInitService {
  endpoint: "/api/init"
  description: "Initialize GCS buckets and Firestore structure for new projects"
  
  features: [
    "🪣 GCS Bucket Creation & Configuration",
    "🔥 Firestore Collection Initialization", 
    "🔐 IAM Permissions Setup",
    "📁 Folder Structure Creation",
    "🔗 Link Service Setup & Configuration",
    "⚙️ Project Settings Configuration"
  ]
  
  folderStructure: {
    bucketSetup: "snapit-{projectId}/",
    contextFolders: [
      "context/ui-images/",
      "context/docs/", 
      "context/links/",
      "context/assets/"
    ],
    linkServiceInit: "Pre-configure link TTL policies and cache structure"
  }
}
```
```

## 🔧 Infrastructure & Deployment

### Comprehensive Firestore Database Structure
```
📚 Firestore Collections (50+ Advanced Collections):

├── projects/                               # Main project documents
│   └── {projectId}/
│       ├── 🎯 Core Collections
│       │   ├── assets/                     # Project assets & files
│       │   ├── embeddings/                 # Vector embeddings
│       │   ├── metadata/                   # Project metadata
│       │   ├── components/                 # Detected UI components
│       │   └── heatmaps/                   # Complexity heatmaps
│       ├── 🤖 Agent & Execution Collections  
│       │   ├── agent_executions/           # Time-stamped agent runs
│       │   ├── agent_timeline/             # Execution traces with diffs
│       │   ├── prompt_history/             # Prompt lineage and versions
│       │   └── agent_performance/          # Model latency and metrics
│       ├── 📋 Version Management Collections
│       │   ├── project_versions/           # Semantic project versions
│       │   ├── version_snapshots/          # Version rollback data
│       │   ├── prompt_lineage/             # Prompt change tracking
│       │   └── code_diffs/                 # Code change history
│       ├── 🌱 Carbon & Sustainability Collections
│       │   ├── carbon_tracking/            # CO2 emissions per model run
│       │   ├── model_usage/                # Model usage statistics
│       │   ├── sustainability_metrics/     # Green coding metrics
│       │   └── carbon_reports/             # Aggregated carbon reports
│       ├── ✅ Quality & Validation Collections
│       │   ├── validation_results/         # Build, test, lint results
│       │   ├── code_reviews/               # AI code review results
│       │   ├── accuracy_validation/        # Visual accuracy scores
│       │   ├── test_results/               # Unit/E2E test outcomes
│       │   └── accessibility_checks/       # WCAG compliance results
│       ├── 🔬 AI Analysis Collections
│       │   ├── ui_analysis/                # Vision agent results
│       │   ├── layout_analysis/            # Layout detection data
│       │   ├── complexity_analysis/        # Code complexity scores
│       │   └── pattern_detection/          # UI pattern recognition
│       ├── 📚 Documentation & Export Collections
│       │   ├── documentation/              # Auto-generated docs
│       │   ├── walkthroughs/              # AI walkthrough videos
│       │   ├── export_history/            # Export logs and artifacts
│       │   └── delivery_checklists/       # Project handoff data
│       └── 🧪 Test Data & DevOps Collections
│           ├── test_data/                 # Generated test datasets
│           ├── mock_apis/                 # API stubs and responses
│           ├── faker_schemas/             # Test data generation schemas
│           ├── pipelines/                 # CI/CD pipeline configs
│           ├── deployments/               # Deployment history
│           ├── environments/              # Environment configurations
│           └── secrets/                   # Encrypted secrets storage
├── 👥 User & Team Management
│   ├── users/                             # User management
│   ├── teams/                             # Team collaboration
│   ├── user_preferences/                  # User settings
│   └── project_permissions/               # Access control
└── 📊 System & Analytics
    ├── analytics/                         # Usage analytics
    ├── system_logs/                       # System monitoring
    ├── error_logs/                        # Error tracking
    └── performance_logs/                  # Performance monitoring
```

### Advanced Firestore Security Rules
```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Projects with comprehensive subcollection access
    match /projects/{projectId} {
      allow read, write: if request.auth != null 
        && request.auth.uid == resource.data.owner;
      
      // All AI analysis subcollections
      match /{subcollection=**} {
        allow read, write: if request.auth != null
          && (subcollection in [
            'assets', 'embeddings', 'metadata', 'components', 'heatmaps',
            'agent_executions', 'agent_timeline', 'prompt_history', 'agent_performance',
            'project_versions', 'version_snapshots', 'prompt_lineage', 'code_diffs',
            'carbon_tracking', 'model_usage', 'sustainability_metrics', 'carbon_reports',
            'validation_results', 'code_reviews', 'accuracy_validation', 'test_results',
            'ui_analysis', 'layout_analysis', 'complexity_analysis', 'pattern_detection',
            'documentation', 'walkthroughs', 'export_history', 'delivery_checklists',
            'test_data', 'mock_apis', 'faker_schemas', 'pipelines', 'deployments'
          ]);
      }
    }
    
    // System collections (admin only)
    match /{systemCollection}/{document=**} {
      allow read, write: if request.auth != null 
        && request.auth.token.admin == true
        && systemCollection in ['analytics', 'system_logs', 'error_logs', 'performance_logs'];
    }
    
    // User management
    match /users/{userId} {
      allow read, write: if request.auth != null 
        && request.auth.uid == userId;
    }
  }
}
```

### Enhanced Cloud Functions Configuration
```yaml
functions:
  upload-service:
    runtime: "python39"
    generation: "gen2"
    memory: "512Mi" 
    timeout: "60s"
    trigger: "https"
    env_vars:
      GCS_BUCKET: "snapit-{projectId}"
    
  embedding-service:
    runtime: "python39"
    generation: "gen2"
    memory: "2Gi"                    # Increased for AI processing
    timeout: "540s"                  # 9 minutes for complex analysis
    trigger: "https"
    env_vars:
      OPENAI_API_KEY: "${OPENAI_API_KEY}"
      CV2_ENABLE: "true"
    
  data-service:
    runtime: "python39"
    generation: "gen2"
    memory: "1Gi"                    # Increased for large collections
    timeout: "60s"
    trigger: "https"
    
  search-service:
    runtime: "python39"
    generation: "gen2"
    memory: "1Gi"                    # For vector operations
    timeout: "60s"
    trigger: "https"
    
  link-service:
    runtime: "python39"
    generation: "gen2"
    memory: "1Gi"                    # For content parsing & embeddings
    timeout: "120s"                  # Extended for link fetching
    trigger: "https"
    env_vars:
      OPENAI_API_KEY: "${OPENAI_API_KEY}"
      REQUESTS_TIMEOUT: "30"
    
  project-init-service:
    runtime: "python39"
    generation: "gen2"
    memory: "256Mi"
    timeout: "30s"
    trigger: "https"
```

### Advanced Environment Variables
```bash
# AI & Analysis Configuration
OPENAI_API_KEY=sk-...
OPENAI_MODEL=text-embedding-3-small
CV2_ENABLE=true
AI_ANALYSIS_TIMEOUT=540

# Storage Configuration  
STORAGE_BUCKET_PREFIX=snapit
STORAGE_REGION=us-central1
GCS_CONTEXT_FOLDER=context

# Database Configuration
FIRESTORE_PROJECT_ID=your-project-id
FIRESTORE_DATABASE_ID=(default)
FIRESTORE_COLLECTION_COUNT=50+

# Performance & Monitoring
REDIS_URL=redis://...
CARBON_TRACKING_ENABLED=true
PERFORMANCE_MONITORING=true

# API Keys & External Services
GOOGLE_CLOUD_PROJECT=your-project-id

# Security & Authentication
JWT_SECRET=your-jwt-secret
CORS_ORIGINS=https://yourdomain.com
FIRESTORE_SECURITY_RULES=strict

# Feature Flags
ENABLE_COMPONENT_DETECTION=true
ENABLE_COMPLEXITY_ANALYSIS=true
ENABLE_SEMANTIC_SEARCH=true
ENABLE_CARBON_TRACKING=true
```

## 📊 Comprehensive API Endpoints Overview

| Service | Endpoint | Method | Description | AI Features |
|---------|----------|--------|-------------|-------------|
| 📤 **Upload** | `/api/upload` | POST | UI image, document & asset upload | Auto optimization, RAG processing |
| 📤 **Upload** | `/api/ui-images/{imageId}` | GET/DELETE | UI image management | Individual folder per image |
| 📤 **Upload** | `/api/docs/{docId}` | GET/DELETE | Document management | RAG-enabled document folders |
| 📤 **Upload** | `/api/assets/{assetType}/{assetId}` | GET/DELETE | Asset management by type | Type-based organization |
| 🧠 **AI Analysis** | `/api/analyze_image` | POST | Comprehensive image analysis | 🎯 Component detection, 🔥 Heatmaps |
| 🧠 **AI Analysis** | `/api/analyze_document` | POST | Document RAG processing | 📄 Text extraction, chunking, embeddings |
| 🧠 **AI Analysis** | `/api/process_document_rag` | POST | Full RAG workflow | 📝 Summary, keywords, embeddings |
| 🧠 **AI Analysis** | `/api/detect_components` | POST | UI component detection | 🎯 6 component types with confidence |
| 🧠 **AI Analysis** | `/api/generate_heatmap` | POST | Complexity heatmap generation | 🔥 Visual complexity scoring |
| 🧠 **AI Analysis** | `/api/generate_embeddings` | POST | Vector embeddings | 📊 OpenAI embeddings (1536D) |
| 🧠 **AI Analysis** | `/api/search_documents` | POST | Document semantic search | 🔍 RAG-powered document search |
| 🧠 **AI Analysis** | `/api/comprehensive_analysis` | POST | All-in-one analysis | 🎯🔥📊 Combined AI analysis |
| 🧠 **AI Analysis** | `/api/get_analysis/{id}` | GET | Retrieve analysis results | Access to all AI outputs |
| � **Link Processing** | `/api/links/add` | POST | Add external link reference | Smart TTL caching configuration |
| 🔗 **Link Processing** | `/api/fetch/{linkId}` | GET | Runtime content fetch | Intelligent cache management |
| 🔗 **Link Processing** | `/api/refresh/{linkId}` | POST | Force refresh cached content | Cache invalidation & update |
| 🔗 **Link Processing** | `/api/status/{linkId}` | GET | Check cache status | Freshness monitoring |
| 🔗 **Link Processing** | `/api/links/search` | POST | Search cached link content | 🔍 Semantic & keyword search |
| �💾 **Data** | `/api/data/{collection}` | GET/POST/PUT/DELETE | Advanced data management | 50+ Firestore collections |
| 💾 **Data** | `/api/create_project` | POST | Project initialization | Auto-setup all collections |
| 💾 **Data** | `/api/get_project/{id}` | GET | Complete project data | Categorized collection data |
| 🔍 **Search** | `/api/search` | POST | Semantic search | 🔍 Vector similarity search |
| � **Search** | `/api/search_components` | POST | Component search | 🎯 Type & analysis filtering |
| 🔍 **Search** | `/api/search_analysis` | POST | Analysis results search | 🔬 Cross-collection queries |
| 🔍 **Search** | `/api/search_by_complexity` | POST | Complexity filtering | 📊 Score-based search |
| 🔍 **Search** | `/api/search_similar_components/{id}` | GET | Similar component finder | 🎯 AI similarity matching |
| 🔍 **Search** | `/api/search_ui_images` | POST | UI image & analysis search | 📁 Image folder filtering |
| 🔍 **Search** | `/api/search_documents` | POST | Document RAG search | 📄 Semantic document search |
| 🔍 **Search** | `/api/search_assets_by_type` | POST | Asset search by type | 📁 Type-based filtering |
| 🏗️ **Project Init** | `/api/init` | POST | Project & bucket setup | 🪣 GCS & Firestore initialization |

## 🤖 AI & ML Capabilities

### Computer Vision Features
- **Component Detection**: Buttons, inputs, navigation, cards, tables, text elements
- **Confidence Scoring**: 0.0-1.0 accuracy ratings for each detection
- **Bounding Box Mapping**: Precise pixel-level component localization
- **Overlap Resolution**: Smart merging of overlapping detections
- **Visual Characteristics Analysis**: Color variance, edge density, texture analysis

### Complexity Analysis
- **Heatmap Generation**: Visual complexity visualization with color coding
- **Multi-metric Scoring**: Edge density + texture + color variance
- **Complexity Score**: 0-100 normalized complexity rating
- **High Complexity Region Detection**: Automated identification of complex areas
- **Recommendation Engine**: AI-generated UX improvement suggestions

### Semantic Search & Embeddings
- **OpenAI Integration**: text-embedding-3-small model (1536 dimensions)
- **Vector Similarity**: Cosine similarity with configurable thresholds
- **Multi-modal Search**: Text and visual content search
- **Component Similarity**: Type, size, aspect ratio, and confidence matching
- **Cross-collection Queries**: Search across multiple Firestore collections

## 🌱 Sustainability & Performance

### Carbon Tracking
- **Model Usage Monitoring**: Track AI model calls and token usage
- **Emission Calculation**: CO2 estimation per model execution
- **Sustainability Metrics**: Green coding score and recommendations
- **Carbon Reports**: Aggregated environmental impact analysis

### Performance Optimization
- **Parallel Processing**: Concurrent analysis operations
- **GCS Storage Optimization**: Organized folder structure for fast retrieval
- **Firestore Indexing**: Optimized queries across 50+ collections
- **Memory Management**: Right-sized function allocation (256MB-2GB)

## 🚦 Enhanced Status & Health Checks

```typescript
// GET /api/health
interface AdvancedHealthCheck {
  status: "healthy" | "degraded" | "unhealthy"
  services: {
    upload: ServiceStatus & { bucketAccess: boolean }
    embedding: ServiceStatus & { 
      openaiConnectivity: boolean,
      cv2Ready: boolean,
      modelAvailability: string[]
    }
    data: ServiceStatus & { 
      firestoreConnectivity: boolean,
      collectionCounts: Record<string, number>
    }
    search: ServiceStatus & {
      indexHealth: boolean,
      vectorSearchReady: boolean
    }
    storage: ServiceStatus & { 
      bucketAccessible: boolean,
      contextFolderStructure: boolean
    }
  }
  aiCapabilities: {
    componentDetection: boolean
    complexityAnalysis: boolean
    embeddingGeneration: boolean
    semanticSearch: boolean
  }
  sustainability: {
    carbonTrackingEnabled: boolean
    totalEmissions: number
    modelCallsToday: number
  }
  performance: {
    avgResponseTime: number
    successRate: number
    activeAnalyses: number
  }
  timestamp: string
  version: string
}
```

## 📚 Implementation Summary

### ✅ Completed Features

#### 🧠 AI Embedding & Analysis Service
- ✅ **Comprehensive Image Analysis** with component detection + heatmaps + embeddings
- ✅ **UI Component Detection** for 6 component types (buttons, inputs, navigation, cards, tables, text)
- ✅ **Complexity Heatmap Generation** with visual scoring and recommendations  
- ✅ **OpenAI Embeddings Integration** (text-embedding-3-small, 1536D vectors)
- ✅ **GCS Storage** with organized folder structure (`{projectId}/context/{analysisId}/`)
- ✅ **Firestore Integration** across multiple collections (ui_analysis, complexity_analysis, components, embeddings)

#### 💾 Advanced Data Service  
- ✅ **50+ Firestore Collections** organized by categories (core, agents, versions, quality, analysis, carbon, documentation, testing, devops, users, system)
- ✅ **Project-centric Architecture** with comprehensive subcollection support
- ✅ **Advanced CRUD Operations** with filtering, pagination, and batch operations
- ✅ **Project Statistics** with quality scores and carbon footprint calculation
- ✅ **Collection Metadata** with schema definitions and automatic initialization

#### 🔍 Enhanced Search Service
- ✅ **Semantic Vector Search** with cosine similarity and configurable thresholds
- ✅ **Component Similarity Matching** based on type, confidence, size, and aspect ratio
- ✅ **Complexity-based Filtering** with min/max score ranges
- ✅ **Cross-collection Analysis Search** across ui_analysis, complexity_analysis, and heatmaps
- ✅ **Advanced Asset and Component Filtering** with metadata-based queries
- ✅ **Search Statistics** with comprehensive project search metadata

#### 📤 Upload Service & 🏗️ Project Init Service
- ✅ **Multi-file Upload Support** with automatic bucket creation per project
- ✅ **GCS Bucket Initialization** with proper folder structure setup
- ✅ **Project Setup Automation** with Firestore collection initialization

#### ☁️ Infrastructure & Storage
- ✅ **Organized GCS Structure** (`{projectId}/context/{analysisId}/analysis|heatmaps|comprehensive/`)
- ✅ **Comprehensive Firestore Security Rules** supporting all 50+ collections
- ✅ **Advanced Cloud Functions Configuration** with optimized memory and timeout settings
- ✅ **Environment Variable Management** for AI, storage, database, and feature flags

### 🔄 Integration Points

1. **Upload → UI Image Folders**: UI images get individual folders (`{projectId}/context/ui-images/{imageId}/`)
2. **Upload → Document RAG**: Documents get individual folders with RAG processing (`{projectId}/context/docs/{docId}/`)
3. **Upload → Asset Storage**: Other assets organized by type (`{projectId}/context/assets/{assetType}/`)
4. **Link → External RAG**: External links get individual folders with smart caching (`{projectId}/context/links/{linkId}/`)
5. **UI Image → AI Analysis**: Analysis results stored in same folder as original image
6. **Document → RAG Processing**: Text extraction, chunking, embeddings, and summaries stored with document
7. **Link → Content Processing**: Cached content, embeddings, and metadata stored with TTL policies
8. **Analysis → Data Service**: Results stored in Firestore with folder path references and embeddings
9. **Search Service**: Semantic search across UI images, documents (RAG), links (RAG), analysis results, and typed assets
10. **Project Init**: Automated setup ensures proper folder structure for all workflows

### 📁 Asset Management Workflow

```mermaid
flowchart TD
    A[File Upload] --> B{File Type?}
    B -->|UI Image| C[Create Individual Image Folder]
    B -->|Document| D[Create Individual Document Folder]
    B -->|Other Asset| E[Store in Type-Based Asset Folder]
    
    C --> F[Store image.png in /ui-images/{imageId}/]
    F --> G[Trigger AI Analysis]
    G --> H[Component Detection]
    G --> I[Complexity Analysis]
    G --> J[Heatmap Generation]
    H --> K[Store Results in /analysis/ subfolder]
    I --> K
    J --> K
    
    D --> L[Store document.{ext} in /docs/{docId}/]
    L --> M[Trigger RAG Processing]
    M --> N[Text Extraction]
    M --> O[Document Chunking]
    M --> P[Generate Embeddings]
    M --> Q[Create Summary & Keywords]
    N --> R[Store RAG Results in /analysis/ subfolder]
    O --> R
    P --> R
    Q --> R
    
    E --> S[Store in /assets/{type}/{assetId}]
    S --> T[Asset Available for Cross-Reference]
    
    K --> U[Complete UI Image Analysis Package]
    R --> V[Complete Document RAG Package]
    T --> W[Typed Asset Available]
    U --> X[Searchable Image + Analysis Data]
    V --> Y[Searchable Document + RAG Data]
    W --> X
    Y --> Z[Multi-modal Semantic Search]
    X --> Z
```

## 🛠️ Local Development & Testing

### Quick Start Guide
```bash
# 1. Install dependencies for each service
cd backend/functions/upload-service && pip install -r requirements.txt
cd ../embedding-service && pip install -r requirements.txt
cd ../data-service && pip install -r requirements.txt
cd ../search-service && pip install -r requirements.txt
cd ../link-service && pip install -r requirements.txt
cd ../project-init-service && pip install -r requirements.txt

# 2. Set environment variables
export OPENAI_API_KEY="your-openai-api-key"
export GOOGLE_APPLICATION_CREDENTIALS="path/to/service-account.json"
export GCS_BUCKET="snapit-test-project"

# 3. Run individual services locally
# Upload Service (Port 8080)
cd upload-service && functions-framework --target=upload_file --port=8080

# AI Embedding Service (Port 8081)
cd embedding-service && functions-framework --target=embedding_service --port=8081

# Data Service (Port 8082) 
cd data-service && functions-framework --target=data_service --port=8082

# Search Service (Port 8083)
cd search-service && functions-framework --target=semantic_search --port=8083

# Link Service (Port 8084)
cd link-service && functions-framework --target=link_processor --port=8084

# Project Init Service (Port 8085)
cd project-init-service && functions-framework --target=project_init_service --port=8085
```

### Test Endpoints Locally
```bash
# Test Upload Service
curl -X POST http://localhost:8080/api/upload \
  -F "files=@test-image.png" \
  -F "projectId=test-project" \
  -F "fileType=ui-image"

# Test Link Service - Add Link
curl -X POST http://localhost:8084/api/links/add \
  -H "Content-Type: application/json" \
  -d '{
    "projectId": "test-project",
    "url": "https://docs.python.org/3/tutorial/",
    "contentType": "documentation",
    "title": "Python Tutorial",
    "tags": ["python", "tutorial", "programming"]
  }'

# Test Link Service - Fetch Content
curl "http://localhost:8084/api/fetch/{linkId}?projectId=test-project&generateEmbeddings=true"

# Test Link Service - Search
curl -X POST http://localhost:8084/api/links/search \
  -H "Content-Type: application/json" \
  -d '{
    "projectId": "test-project",
    "query": "python tutorial",
    "searchType": "keyword",
    "limit": 5
  }'

# Test AI Analysis
curl -X POST http://localhost:8081/api/analyze_image \
  -H "Content-Type: application/json" \
  -d '{"projectId": "test-project", "imageId": "img123"}'

# Test Search Service
curl -X POST http://localhost:8083/api/search \
  -H "Content-Type: application/json" \
  -d '{"projectId": "test-project", "query": "button component", "searchType": "semantic"}'
```

### 🚀 Next Steps & Enhancements

Each service is now production-ready with comprehensive functionality. Future enhancements could include:

- 📖 **Complete API Documentation** - OpenAPI/Swagger specifications for all endpoints
- 🧪 **Testing Suite** - Unit, integration & e2e tests for all AI analysis workflows
- 🔒 **Enhanced Security** - Advanced authentication, role-based access, and data encryption
- 📊 **Advanced Monitoring** - Real-time analytics, performance metrics, and alerting
- 🌐 **Multi-region Deployment** - Geographic distribution for improved performance
- 🤖 **Extended AI Capabilities** - Additional computer vision models and analysis types
- 🔄 **Real-time Processing** - WebSocket support for live analysis updates
- 📱 **Mobile Optimization** - Enhanced mobile app support and offline capabilities

The backend now provides a solid foundation for an AI-powered DevOps agent platform with comprehensive analysis, search, and data management capabilities.
