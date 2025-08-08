# 🐍 Simple Python Cloud Functions

## 📁 Function Structure

```
backend/
├── functions/
│   ├── upload-service/         # 📤 File upload handler
│   │   ├── main.py
│   │   └── requirements.txt
│   ├── embedding-service/      # 🧠 Vector embeddings
│   │   ├── main.py
│   │   └── requirements.txt
│   ├── data-service/          # 💾 CRUD operations
│   │   ├── main.py
│   │   └── requirements.txt
│   └── search-service/        # 🔍 Semantic search
│       ├── main.py
│       └── requirements.txt
├── deploy.sh                  # 🚀 Deployment script
└── readme.md                 # 📖 Main documentation
```

## 🚀 Quick Deploy

```bash
# Set your OpenAI API key
export OPENAI_API_KEY="your-api-key"

# Deploy all functions
./deploy.sh
```

## 📤 Upload Service

**Endpoint:** `POST /upload-service`

```python
# Simple file upload
files = {'file': open('image.png', 'rb')}
data = {'projectId': 'my-project-123'}
response = requests.post(url, files=files, data=data)
```

## 🧠 Embedding Service

**Endpoint:** `POST /embedding-service`

```python
# Generate embeddings
payload = {
    "content": "This is sample text",
    "type": "text",
    "projectId": "my-project-123"
}
response = requests.post(url, json=payload)
```

## 💾 Data Service

**Endpoint:** `GET|POST|PUT|DELETE /data-service`

```python
# Create project
payload = {
    "name": "My Project",
    "owner": "user123",
    "metadata": {"description": "Test project"}
}
response = requests.post(url, json=payload)

# Get project data
response = requests.get(f"{url}/api/data/{project_id}")
```

## 🔍 Search Service

**Endpoint:** `POST /search-service`

```python
# Semantic search
payload = {
    "embedding": [0.1, 0.2, 0.3, ...],  # Your query embedding
    "projectId": "my-project-123",
    "threshold": 0.7,
    "limit": 10
}
response = requests.post(url, json=payload)
```

## 🔧 Environment Variables

```bash
export OPENAI_API_KEY="sk-..."
export GOOGLE_CLOUD_PROJECT="your-project-id"
```

## 📋 Dependencies

Each function is minimal with only essential packages:
- `functions-framework` - Google Cloud Functions framework
- `google-cloud-storage` - Cloud Storage client
- `google-cloud-firestore` - Firestore client
- `openai` - OpenAI API client
- `Pillow` - Image processing
- `numpy` - Vector operations
