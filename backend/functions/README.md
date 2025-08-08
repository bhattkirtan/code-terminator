# 🐍 Simple Python Cloud Functions

## 📁 Function Structure

```
backend/
├── functions/
│   ├── upload-service/         # 📤 File upload & asset management
│   │   ├── main.py
│   │   ├── requirements.txt
│   │   └── deploy.sh
│   ├── embedding-service/      # 🧠 AI analysis & embeddings
│   │   ├── main.py
│   │   ├── requirements.txt
│   │   └── deploy.sh
│   ├── data-service/          # 💾 Firestore CRUD operations
│   │   ├── main.py
│   │   ├── requirements.txt
│   │   └── deploy.sh
│   ├── search-service/        # 🔍 Advanced semantic search
│   │   ├── main.py
│   │   ├── requirements.txt
│   │   └── deploy.sh
│   ├── link-service/          # 🔗 Link processing & RAG
│   │   ├── main.py
│   │   ├── requirements.txt
│   │   └── deploy.sh
│   ├── project-init-service/  # 🏗️ Project initialization
│   │   ├── main.py
│   │   ├── requirements.txt
│   │   └── deploy.sh
│   ├── deploy-all.sh          # 🚀 Master deployment script
│   └── README.md              # 📖 Complete documentation
```

## 🚀 Quick Deploy

```bash
# Set your OpenAI API key
export OPENAI_API_KEY="your-api-key"

# Deploy all functions at once
./deploy-all.sh

# Or deploy individual services
cd upload-service && ./deploy.sh
cd embedding-service && ./deploy.sh
cd data-service && ./deploy.sh
cd search-service && ./deploy.sh
cd link-service && ./deploy.sh
cd project-init-service && ./deploy.sh
```

## 📤 Upload Service

**Endpoint:** `POST /upload-service`

```python
# File upload with metadata
files = {'file': open('image.png', 'rb')}
data = {'projectId': 'my-project-123', 'analysisId': 'analysis-456'}
response = requests.post(url, files=files, data=data)

# Asset management
response = requests.get(f"{url}/api/assets/{project_id}")
response = requests.delete(f"{url}/api/assets/{project_id}/{file_id}")
```

## 🧠 Embedding Service

**Endpoint:** `POST /embedding-service`

```python
# Component detection & heatmap analysis
payload = {
    "action": "analyze_components",
    "projectId": "my-project-123",
    "analysisId": "analysis-456",
    "gcs_path": "path/to/image.png"
}
response = requests.post(url, json=payload)

# Generate embeddings
payload = {
    "action": "generate_embedding",
    "content": "This is sample text",
    "projectId": "my-project-123"
}
response = requests.post(url, json=payload)

# Create heatmap
payload = {
    "action": "create_heatmap",
    "projectId": "my-project-123",
    "analysisId": "analysis-456",
    "gcs_path": "path/to/image.png"
}
response = requests.post(url, json=payload)
```

## 💾 Data Service

**Endpoint:** `GET|POST|PUT|DELETE /data-service`

```python
# Create project with advanced collections
payload = {
    "collection": "projects",
    "data": {
        "name": "My Project",
        "owner": "user123",
        "metadata": {"description": "Test project"}
    }
}
response = requests.post(url, json=payload)

# Advanced Firestore operations (50+ collections supported)
# Including: carbon_tracking, version_control, agent_timeline, etc.
response = requests.get(f"{url}/api/data/user_analytics/{user_id}")
response = requests.post(f"{url}/api/data/carbon_tracking", json=carbon_data)
```

## 🔍 Search Service

**Endpoint:** `POST /search-service`

```python
# Semantic search with advanced features
payload = {
    "action": "semantic_search",
    "embedding": [0.1, 0.2, 0.3, ...],
    "projectId": "my-project-123",
    "threshold": 0.7,
    "limit": 10
}
response = requests.post(url, json=payload)

# Complexity-based search
payload = {
    "action": "complexity_search",
    "projectId": "my-project-123",
    "min_complexity": 0.5,
    "max_complexity": 0.9
}
response = requests.post(url, json=payload)

# Similarity search
payload = {
    "action": "similarity_search",
    "projectId": "my-project-123",
    "reference_embedding": [0.1, 0.2, 0.3, ...],
    "threshold": 0.8
}
response = requests.post(url, json=payload)
```

## 🔗 Link Service

**Endpoint:** `POST /link-service`

```python
# Process and analyze links with RAG capabilities
payload = {
    "action": "process_link",
    "url": "https://example.com/article",
    "projectId": "my-project-123",
    "analysisId": "analysis-456"
}
response = requests.post(url, json=payload)

# Extract content and metadata
payload = {
    "action": "extract_content",
    "url": "https://example.com/page",
    "projectId": "my-project-123"
}
response = requests.post(url, json=payload)
```

## 🏗️ Project Init Service

**Endpoint:** `POST /project-init-service`

```python
# Initialize project with GCS bucket and Firestore setup
payload = {
    "projectId": "my-project-123",
    "bucketRegion": "us-central1",
    "initializeCollections": True
}
response = requests.post(url, json=payload)

# Setup storage structure
payload = {
    "action": "setup_storage",
    "projectId": "my-project-123"
}
response = requests.post(url, json=payload)
```

## 🔧 Environment Variables

```bash
export OPENAI_API_KEY="sk-..."
export GOOGLE_CLOUD_PROJECT="your-project-id"
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account.json"
```

## �️ Storage Architecture

### GCS Bucket Structure
```
snapit-{projectId}/
├── context/
│   ├── ui-images/           # Raw UI screenshots & uploads
│   ├── docs/               # Document storage (RAG-enabled)
│   ├── assets/             # Processed assets & components
│   └── links/              # Link content & metadata (RAG-enabled)
├── analysis/
│   └── {analysisId}/       # Analysis results & AI outputs
└── temp/                   # Temporary processing files
```

### Firestore Collections (50+ Advanced Collections)
```
projects/                   # Main project data
users/                      # User profiles & settings
analysis_results/           # AI analysis outputs
components/                 # Detected UI components
embeddings/                 # Vector embeddings storage
carbon_tracking/            # Environmental impact data
version_control/            # Version management
agent_timeline/             # AI agent interaction history
user_analytics/             # User behavior analytics
project_analytics/          # Project performance metrics
collaboration/              # Team collaboration data
notifications/              # System notifications
audit_logs/                 # Security & audit trails
... and 37+ more specialized collections
```

## 📋 Dependencies

Each function uses Python 3.13 compatible packages:
- `functions-framework==3.8.0` - Google Cloud Functions framework
- `google-cloud-storage` - Cloud Storage client  
- `google-cloud-firestore` - Firestore client
- `google-cloud-logging` - Cloud Logging
- `openai` - OpenAI API client
- `opencv-python-headless` - Computer vision (embedding-service)
- `pillow>=10.2.0` - Image processing
- `numpy>=1.26.0` - Vector operations
- `sentence-transformers` - Text embeddings (embedding-service)
- `beautifulsoup4` - HTML parsing (link-service)
- `lxml>=5.0.0` - XML parsing (link-service)
- `requests` - HTTP client
- `flask` - Web framework

## 🚀 Deployment Configuration

All services are configured for:
- **Runtime:** Python 3.13 (Cloud Functions Gen2)
- **Memory:** 512Mi (1Gi for embedding-service)
- **Timeout:** 540s
- **Region:** us-central1
- **Trigger:** HTTP with unauthenticated access

## ✅ Deployment Status

Use the master deployment script to deploy all services:
```bash
./deploy-all.sh
```

Individual service deployment:
```bash
cd {service-name} && ./deploy.sh
```
