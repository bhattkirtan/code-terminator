"""
PipelineAgent - Generates GitHub Actions, Dockerfiles, and CI/CD configs
"""
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class PipelineAgent:
    def __init__(self):
        self.name = "PipelineAgent"
        self.version = "1.0.0"
    
    async def generate_pipeline(self, code_files: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate comprehensive CI/CD pipeline configurations
        """
        logger.info("Generating CI/CD pipeline configurations")
        
        pipeline_configs = {
            "github_actions": await self._generate_github_actions(code_files),
            "docker": await self._generate_docker_configs(code_files),
            "azure_pipelines": await self._generate_azure_pipelines(code_files),
            "gitlab_ci": await self._generate_gitlab_ci(code_files),
            "jenkins": await self._generate_jenkins_config(code_files),
            "deployment_scripts": await self._generate_deployment_scripts(code_files)
        }
        
        logger.info("Pipeline generation completed")
        return pipeline_configs
    
    async def _generate_github_actions(self, code_files: Dict[str, Any]) -> Dict[str, str]:
        """Generate GitHub Actions workflows"""
        
        workflows = {
            ".github/workflows/ci.yml": self._create_ci_workflow(),
            ".github/workflows/cd.yml": self._create_cd_workflow(),
            ".github/workflows/pr-check.yml": self._create_pr_workflow(),
            ".github/workflows/security-scan.yml": self._create_security_workflow(),
            ".github/workflows/performance.yml": self._create_performance_workflow()
        }
        
        return workflows
    
    def _create_ci_workflow(self) -> str:
        """Create CI workflow for GitHub Actions"""
        return '''name: Continuous Integration

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    strategy:
      matrix:
        node-version: [18.x, 20.x]
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
      
    - name: Use Node.js ${{ matrix.node-version }}
      uses: actions/setup-node@v4
      with:
        node-version: ${{ matrix.node-version }}
        cache: 'npm'
        
    - name: Install dependencies
      run: npm ci
      
    - name: Lint code
      run: npm run lint
      
    - name: Run unit tests
      run: npm run test:ci
      
    - name: Run e2e tests
      run: npm run e2e:ci
      
    - name: Build application
      run: npm run build
      
    - name: Upload coverage reports
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage/lcov.info
        
    - name: Upload build artifacts
      uses: actions/upload-artifact@v3
      with:
        name: build-${{ matrix.node-version }}
        path: dist/
        retention-days: 1

  lighthouse:
    runs-on: ubuntu-latest
    needs: test
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
      
    - name: Setup Node.js
      uses: actions/setup-node@v4
      with:
        node-version: '18.x'
        cache: 'npm'
        
    - name: Install dependencies
      run: npm ci
      
    - name: Build application
      run: npm run build
      
    - name: Serve application
      run: |
        npm install -g http-server
        http-server dist/ -p 4200 &
        sleep 5
        
    - name: Run Lighthouse CI
      run: |
        npm install -g @lhci/cli@0.12.x
        lhci autorun
      env:
        LHCI_GITHUB_APP_TOKEN: ${{ secrets.LHCI_GITHUB_APP_TOKEN }}

  security:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
      
    - name: Run npm audit
      run: npm audit --audit-level moderate
      
    - name: Run Snyk to check for vulnerabilities
      uses: snyk/actions/node@master
      env:
        SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
      with:
        args: --severity-threshold=high
'''

    def _create_cd_workflow(self) -> str:
        """Create CD workflow for GitHub Actions"""
        return '''name: Continuous Deployment

on:
  push:
    branches: [ main ]
    tags: [ 'v*' ]

jobs:
  deploy-staging:
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    environment:
      name: staging
      url: https://staging.yourapp.com
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
      
    - name: Setup Node.js
      uses: actions/setup-node@v4
      with:
        node-version: '18.x'
        cache: 'npm'
        
    - name: Install dependencies
      run: npm ci
      
    - name: Build for staging
      run: npm run build:staging
      
    - name: Deploy to Firebase Hosting (Staging)
      uses: FirebaseExtended/action-hosting-deploy@v0
      with:
        repoToken: '${{ secrets.GITHUB_TOKEN }}'
        firebaseServiceAccount: '${{ secrets.FIREBASE_SERVICE_ACCOUNT_STAGING }}'
        projectId: ${{ secrets.FIREBASE_PROJECT_ID_STAGING }}
        channelId: live
        
    - name: Run smoke tests
      run: npm run test:smoke
      env:
        BASE_URL: https://staging.yourapp.com

  deploy-production:
    runs-on: ubuntu-latest
    if: startsWith(github.ref, 'refs/tags/v')
    
    environment:
      name: production
      url: https://yourapp.com
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
      
    - name: Setup Node.js
      uses: actions/setup-node@v4
      with:
        node-version: '18.x'
        cache: 'npm'
        
    - name: Install dependencies
      run: npm ci
      
    - name: Build for production
      run: npm run build:prod
      
    - name: Run security scan
      run: npm audit --audit-level moderate
      
    - name: Deploy to Firebase Hosting (Production)
      uses: FirebaseExtended/action-hosting-deploy@v0
      with:
        repoToken: '${{ secrets.GITHUB_TOKEN }}'
        firebaseServiceAccount: '${{ secrets.FIREBASE_SERVICE_ACCOUNT_PROD }}'
        projectId: ${{ secrets.FIREBASE_PROJECT_ID_PROD }}
        channelId: live
        
    - name: Create GitHub Release
      uses: actions/create-release@v1
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      with:
        tag_name: ${{ github.ref }}
        release_name: Release ${{ github.ref }}
        draft: false
        prerelease: false
        
    - name: Notify Slack
      uses: 8398a7/action-slack@v3
      with:
        status: ${{ job.status }}
        channel: '#deployments'
        webhook_url: ${{ secrets.SLACK_WEBHOOK }}
      if: always()

  docker-build:
    runs-on: ubuntu-latest
    if: startsWith(github.ref, 'refs/tags/v')
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
      
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v3
      
    - name: Login to DockerHub
      uses: docker/login-action@v3
      with:
        username: ${{ secrets.DOCKERHUB_USERNAME }}
        password: ${{ secrets.DOCKERHUB_TOKEN }}
        
    - name: Extract metadata
      id: meta
      uses: docker/metadata-action@v5
      with:
        images: yourorg/angular-app
        tags: |
          type=ref,event=branch
          type=ref,event=pr
          type=semver,pattern={{version}}
          type=semver,pattern={{major}}.{{minor}}
          
    - name: Build and push Docker image
      uses: docker/build-push-action@v5
      with:
        context: .
        push: true
        tags: ${{ steps.meta.outputs.tags }}
        labels: ${{ steps.meta.outputs.labels }}
        cache-from: type=gha
        cache-to: type=gha,mode=max
'''

    def _create_pr_workflow(self) -> str:
        """Create PR check workflow"""
        return '''name: Pull Request Checks

on:
  pull_request:
    types: [opened, synchronize, reopened]

jobs:
  pr-checks:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
      with:
        fetch-depth: 0
        
    - name: Setup Node.js
      uses: actions/setup-node@v4
      with:
        node-version: '18.x'
        cache: 'npm'
        
    - name: Install dependencies
      run: npm ci
      
    - name: Check commit messages
      run: |
        npm install -g @commitlint/cli @commitlint/config-conventional
        npx commitlint --from=${{ github.event.pull_request.base.sha }}
        
    - name: Lint code
      run: npm run lint
      
    - name: Check formatting
      run: npm run format:check
      
    - name: Type check
      run: npm run type-check
      
    - name: Run tests with coverage
      run: npm run test:coverage
      
    - name: Build application
      run: npm run build
      
    - name: Bundle size check
      run: npm run bundle-analyzer
      
    - name: Comment PR
      uses: actions/github-script@v7
      with:
        script: |
          const fs = require('fs');
          
          // Read bundle analysis results
          const bundleStats = fs.readFileSync('bundle-stats.txt', 'utf8');
          
          // Create comment body
          const comment = `## 📊 Build Results
          
          ### Bundle Analysis
          \`\`\`
          ${bundleStats}
          \`\`\`
          
          ### Test Coverage
          Coverage report will be available after tests complete.
          
          ### Performance Budget
          - ✅ Main bundle: Under 500KB
          - ✅ Vendor bundle: Under 2MB
          - ✅ Runtime bundle: Under 50KB
          `;
          
          // Post comment
          github.rest.issues.createComment({
            issue_number: context.issue.number,
            owner: context.repo.owner,
            repo: context.repo.repo,
            body: comment
          });

  accessibility-check:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
      
    - name: Setup Node.js
      uses: actions/setup-node@v4
      with:
        node-version: '18.x'
        cache: 'npm'
        
    - name: Install dependencies
      run: npm ci
      
    - name: Build application
      run: npm run build
      
    - name: Start application
      run: |
        npm install -g http-server
        http-server dist/ -p 4200 &
        sleep 5
        
    - name: Run accessibility tests
      run: |
        npm install -g @axe-core/cli
        axe http://localhost:4200 --exit
        
    - name: Upload accessibility report
      uses: actions/upload-artifact@v3
      with:
        name: accessibility-report
        path: axe-results.json
      if: failure()
'''

    def _create_security_workflow(self) -> str:
        """Create security scan workflow"""
        return '''name: Security Scan

on:
  schedule:
    - cron: '0 2 * * 1'  # Weekly on Monday at 2 AM
  workflow_dispatch:

jobs:
  security-scan:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
      
    - name: Setup Node.js
      uses: actions/setup-node@v4
      with:
        node-version: '18.x'
        cache: 'npm'
        
    - name: Install dependencies
      run: npm ci
      
    - name: Run npm audit
      run: npm audit --audit-level moderate
      
    - name: Run Snyk vulnerability scan
      uses: snyk/actions/node@master
      env:
        SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
      with:
        args: --severity-threshold=medium
        
    - name: Run CodeQL analysis
      uses: github/codeql-action/init@v3
      with:
        languages: javascript
        
    - name: Autobuild
      uses: github/codeql-action/autobuild@v3
      
    - name: Perform CodeQL analysis
      uses: github/codeql-action/analyze@v3
      
    - name: OWASP ZAP Baseline Scan
      uses: zaproxy/action-baseline@v0.7.0
      with:
        target: 'https://staging.yourapp.com'
        
  dependency-review:
    runs-on: ubuntu-latest
    if: github.event_name == 'pull_request'
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
      
    - name: Dependency Review
      uses: actions/dependency-review-action@v3
      with:
        fail-on-severity: moderate
'''

    def _create_performance_workflow(self) -> str:
        """Create performance monitoring workflow"""
        return '''name: Performance Monitoring

on:
  schedule:
    - cron: '0 */6 * * *'  # Every 6 hours
  workflow_dispatch:

jobs:
  lighthouse-monitoring:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
      
    - name: Setup Node.js
      uses: actions/setup-node@v4
      with:
        node-version: '18.x'
        cache: 'npm'
        
    - name: Install dependencies
      run: npm ci
      
    - name: Build application
      run: npm run build
      
    - name: Run Lighthouse against staging
      run: |
        npm install -g lighthouse
        lighthouse https://staging.yourapp.com --output=json --output-path=./lighthouse-staging.json
        
    - name: Run Lighthouse against production
      run: |
        lighthouse https://yourapp.com --output=json --output-path=./lighthouse-prod.json
      if: github.ref == 'refs/heads/main'
      
    - name: Upload Lighthouse reports
      uses: actions/upload-artifact@v3
      with:
        name: lighthouse-reports
        path: |
          lighthouse-staging.json
          lighthouse-prod.json
        retention-days: 30
        
    - name: Analyze performance metrics
      run: |
        node scripts/analyze-performance.js
        
    - name: Create performance report
      uses: actions/github-script@v7
      with:
        script: |
          const fs = require('fs');
          const lighthouse = JSON.parse(fs.readFileSync('lighthouse-staging.json', 'utf8'));
          
          const metrics = {
            'First Contentful Paint': lighthouse.audits['first-contentful-paint'].displayValue,
            'Largest Contentful Paint': lighthouse.audits['largest-contentful-paint'].displayValue,
            'Speed Index': lighthouse.audits['speed-index'].displayValue,
            'Time to Interactive': lighthouse.audits['interactive'].displayValue,
            'Total Blocking Time': lighthouse.audits['total-blocking-time'].displayValue,
            'Cumulative Layout Shift': lighthouse.audits['cumulative-layout-shift'].displayValue
          };
          
          const score = Math.round(lighthouse.categories.performance.score * 100);
          
          console.log(`Performance Score: ${score}/100`);
          for (const [metric, value] of Object.entries(metrics)) {
            console.log(`${metric}: ${value}`);
          }
'''

    async def _generate_docker_configs(self, code_files: Dict[str, Any]) -> Dict[str, str]:
        """Generate Docker configurations"""
        
        docker_configs = {
            "Dockerfile": self._create_dockerfile(),
            "docker-compose.yml": self._create_docker_compose(),
            "docker-compose.prod.yml": self._create_docker_compose_prod(),
            ".dockerignore": self._create_dockerignore(),
            "nginx.conf": self._create_nginx_config()
        }
        
        return docker_configs
    
    def _create_dockerfile(self) -> str:
        """Create Dockerfile"""
        return '''# Multi-stage build for Angular application

# Stage 1: Build environment
FROM node:18-alpine AS builder

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production && npm cache clean --force

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Stage 2: Production environment
FROM nginx:alpine AS production

# Copy custom nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Copy built application from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Add labels for better maintainability
LABEL maintainer="your-team@yourcompany.com"
LABEL version="1.0.0"
LABEL description="Angular application"

# Expose port 80
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \\
  CMD curl -f http://localhost/ || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
'''

    def _create_docker_compose(self) -> str:
        """Create docker-compose.yml for development"""
        return '''version: '3.8'

services:
  angular-app:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "4200:80"
    environment:
      - NODE_ENV=development
      - API_URL=http://localhost:3000
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - api
    networks:
      - app-network

  api:
    image: node:18-alpine
    working_dir: /app
    command: npm start
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=development
      - DATABASE_URL=postgresql://user:password@db:5432/appdb
    volumes:
      - ./api:/app
    depends_on:
      - db
    networks:
      - app-network

  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: appdb
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"
    networks:
      - app-network

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - app-network

volumes:
  postgres_data:
  redis_data:

networks:
  app-network:
    driver: bridge
'''

    def _create_docker_compose_prod(self) -> str:
        """Create docker-compose.prod.yml for production"""
        return '''version: '3.8'

services:
  angular-app:
    build:
      context: .
      dockerfile: Dockerfile
      target: production
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    environment:
      - NODE_ENV=production
      - API_URL=https://api.yourapp.com
    volumes:
      - ./ssl:/etc/nginx/ssl:ro
      - ./logs:/var/log/nginx
    deploy:
      replicas: 2
      resources:
        limits:
          memory: 512M
        reservations:
          memory: 256M
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost/"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    networks:
      - app-network

  nginx-proxy:
    image: nginx:alpine
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx-proxy.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
      - ./logs:/var/log/nginx
    depends_on:
      - angular-app
    networks:
      - app-network

  watchtower:
    image: containrrr/watchtower
    restart: unless-stopped
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    environment:
      - WATCHTOWER_CLEANUP=true
      - WATCHTOWER_POLL_INTERVAL=300
    command: --interval 300

networks:
  app-network:
    driver: overlay
    attachable: true
'''

    def _create_dockerignore(self) -> str:
        """Create .dockerignore file"""
        return '''# Dependencies
node_modules
npm-debug.log*

# Build outputs
dist
*.tgz

# Development files
.angular
.vscode
.idea

# Testing
coverage
*.spec.ts

# Environment files
.env
.env.local
.env.development
.env.test
.env.production

# Logs
logs
*.log

# Runtime data
pids
*.pid
*.seed
*.pid.lock

# Coverage directory used by tools like istanbul
coverage

# Dependency directories
jspm_packages/

# Optional npm cache directory
.npm

# Optional REPL history
.node_repl_history

# Output of 'npm pack'
*.tgz

# Yarn Integrity file
.yarn-integrity

# dotenv environment variables file
.env

# next.js build output
.next

# Storybook build outputs
.out
.storybook-out

# Temporary folders
tmp/
temp/

# OS generated files
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Git
.git
.gitignore
README.md
.github/

# Docker
Dockerfile
docker-compose*.yml
.dockerignore
'''

    def _create_nginx_config(self) -> str:
        """Create nginx configuration"""
        return '''events {
    worker_connections 1024;
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;

    # Logging
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';

    access_log /var/log/nginx/access.log main;
    error_log /var/log/nginx/error.log warn;

    # Basic settings
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    client_max_body_size 16M;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types
        application/javascript
        application/json
        application/xml
        text/css
        text/javascript
        text/plain
        text/xml;

    # Security headers
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' https:; connect-src 'self' https:;" always;

    server {
        listen 80;
        server_name _;
        root /usr/share/nginx/html;
        index index.html;

        # Security
        server_tokens off;

        # Cache static assets
        location ~* \\.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
            access_log off;
        }

        # Cache HTML files for a short time
        location ~* \\.html$ {
            expires 5m;
            add_header Cache-Control "public, must-revalidate";
        }

        # Angular routes
        location / {
            try_files $uri $uri/ /index.html;
            
            # Cache control for HTML
            expires -1;
            add_header Cache-Control "no-store, no-cache, must-revalidate, proxy-revalidate, max-age=0";
        }

        # API proxy (if needed)
        location /api/ {
            proxy_pass http://api:3000/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Health check endpoint
        location /health {
            access_log off;
            return 200 "healthy\\n";
            add_header Content-Type text/plain;
        }

        # Error pages
        error_page 404 /index.html;
        error_page 500 502 503 504 /50x.html;
        location = /50x.html {
            root /usr/share/nginx/html;
        }
    }
}
'''

    async def _generate_azure_pipelines(self, code_files: Dict[str, Any]) -> Dict[str, str]:
        """Generate Azure DevOps pipelines"""
        
        return {
            "azure-pipelines.yml": '''# Azure DevOps Pipeline for Angular Application

trigger:
  branches:
    include:
    - main
    - develop
  tags:
    include:
    - v*

pr:
  branches:
    include:
    - main
    - develop

variables:
  nodeVersion: '18.x'
  buildConfiguration: 'production'

stages:
- stage: Build
  displayName: 'Build and Test'
  jobs:
  - job: BuildTest
    displayName: 'Build and Test Application'
    pool:
      vmImage: 'ubuntu-latest'
    
    steps:
    - task: NodeTool@0
      displayName: 'Install Node.js'
      inputs:
        versionSpec: '$(nodeVersion)'
    
    - task: Cache@2
      displayName: 'Cache node_modules'
      inputs:
        key: 'npm | "$(Agent.OS)" | package-lock.json'
        restoreKeys: |
          npm | "$(Agent.OS)"
        path: '$(System.DefaultWorkingDirectory)/node_modules'
    
    - script: npm ci
      displayName: 'Install dependencies'
    
    - script: npm run lint
      displayName: 'Lint code'
    
    - script: npm run test:ci
      displayName: 'Run unit tests'
    
    - script: npm run build
      displayName: 'Build application'
    
    - task: PublishTestResults@2
      displayName: 'Publish test results'
      inputs:
        testResultsFormat: 'JUnit'
        testResultsFiles: 'test-results.xml'
        mergeTestResults: true
    
    - task: PublishCodeCoverageResults@1
      displayName: 'Publish code coverage'
      inputs:
        codeCoverageTool: 'Cobertura'
        summaryFileLocation: 'coverage/cobertura-coverage.xml'
    
    - task: PublishBuildArtifacts@1
      displayName: 'Publish build artifacts'
      inputs:
        pathToPublish: 'dist'
        artifactName: 'angular-app'

- stage: Deploy
  displayName: 'Deploy to Azure'
  dependsOn: Build
  condition: and(succeeded(), eq(variables['Build.SourceBranch'], 'refs/heads/main'))
  jobs:
  - deployment: DeployToStaging
    displayName: 'Deploy to Staging'
    environment: 'staging'
    pool:
      vmImage: 'ubuntu-latest'
    strategy:
      runOnce:
        deploy:
          steps:
          - task: DownloadBuildArtifacts@0
            inputs:
              artifactName: 'angular-app'
              downloadPath: '$(System.DefaultWorkingDirectory)'
          
          - task: AzureStaticWebApp@0
            inputs:
              app_location: 'angular-app'
              api_location: ''
              output_location: ''
              azure_static_web_apps_api_token: $(AZURE_STATIC_WEB_APPS_API_TOKEN)
'''
        }
    
    async def _generate_gitlab_ci(self, code_files: Dict[str, Any]) -> Dict[str, str]:
        """Generate GitLab CI configuration"""
        
        return {
            ".gitlab-ci.yml": '''# GitLab CI/CD Pipeline for Angular Application

stages:
  - test
  - security
  - build
  - deploy

variables:
  NODE_VERSION: "18"
  CACHE_FALLBACK_KEY: "$CI_JOB_NAME"

cache:
  key: "$CI_COMMIT_REF_SLUG"
  paths:
    - node_modules/
    - .npm/

before_script:
  - apt-get update -qq && apt-get install -y -qq git curl
  - curl -sL https://deb.nodesource.com/setup_${NODE_VERSION}.x | bash -
  - apt-get install -y nodejs
  - npm ci --cache .npm --prefer-offline

# Test stage
unit-tests:
  stage: test
  script:
    - npm run test:ci
    - npm run lint
  artifacts:
    when: always
    reports:
      junit: test-results.xml
      coverage_report:
        coverage_format: cobertura
        path: coverage/cobertura-coverage.xml
    paths:
      - coverage/
    expire_in: 1 week

e2e-tests:
  stage: test
  script:
    - npm run e2e:ci
  artifacts:
    when: on_failure
    paths:
      - cypress/screenshots/
      - cypress/videos/
    expire_in: 1 week

# Security stage
security-scan:
  stage: security
  script:
    - npm audit --audit-level moderate
    - npm install -g snyk
    - snyk test --severity-threshold=medium
  allow_failure: true

sast:
  stage: security
  include:
    - template: Security/SAST.gitlab-ci.yml

# Build stage
build:
  stage: build
  script:
    - npm run build
  artifacts:
    paths:
      - dist/
    expire_in: 1 week
  only:
    - main
    - develop
    - tags

# Deploy stages
deploy-staging:
  stage: deploy
  script:
    - echo "Deploying to staging..."
    - npm install -g firebase-tools
    - firebase deploy --project $FIREBASE_PROJECT_STAGING --token $FIREBASE_TOKEN
  environment:
    name: staging
    url: https://staging.yourapp.com
  only:
    - develop

deploy-production:
  stage: deploy
  script:
    - echo "Deploying to production..."
    - npm install -g firebase-tools
    - firebase deploy --project $FIREBASE_PROJECT_PROD --token $FIREBASE_TOKEN
  environment:
    name: production
    url: https://yourapp.com
  when: manual
  only:
    - main
    - tags

# Performance testing
lighthouse:
  stage: deploy
  script:
    - npm install -g lighthouse
    - lighthouse https://staging.yourapp.com --output=json --output-path=lighthouse-report.json
  artifacts:
    paths:
      - lighthouse-report.json
    expire_in: 1 week
  only:
    - develop
'''
        }
    
    async def _generate_jenkins_config(self, code_files: Dict[str, Any]) -> Dict[str, str]:
        """Generate Jenkins pipeline configuration"""
        
        return {
            "Jenkinsfile": '''pipeline {
    agent any
    
    environment {
        NODE_VERSION = '18'
        SONAR_SCANNER_VERSION = '4.8.0.2856'
    }
    
    options {
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timeout(time: 60, unit: 'MINUTES')
        retry(3)
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
                script {
                    env.GIT_COMMIT_MSG = sh(
                        script: 'git log -1 --pretty=%B',
                        returnStdout: true
                    ).trim()
                }
            }
        }
        
        stage('Setup') {
            steps {
                script {
                    def nodeHome = tool name: "Node-${NODE_VERSION}", type: 'nodejs'
                    env.PATH = "${nodeHome}/bin:${env.PATH}"
                }
                sh 'node --version'
                sh 'npm --version'
                sh 'npm ci'
            }
        }
        
        stage('Code Quality') {
            parallel {
                stage('Lint') {
                    steps {
                        sh 'npm run lint'
                    }
                    post {
                        always {
                            publishHTML([
                                allowMissing: false,
                                alwaysLinkToLastBuild: true,
                                keepAll: true,
                                reportDir: 'lint-results',
                                reportFiles: 'index.html',
                                reportName: 'ESLint Report'
                            ])
                        }
                    }
                }
                
                stage('Security Scan') {
                    steps {
                        sh 'npm audit --audit-level moderate'
                        script {
                            try {
                                sh 'npx snyk test --severity-threshold=medium'
                            } catch (Exception e) {
                                currentBuild.result = 'UNSTABLE'
                                echo "Security vulnerabilities found: ${e.getMessage()}"
                            }
                        }
                    }
                }
            }
        }
        
        stage('Test') {
            parallel {
                stage('Unit Tests') {
                    steps {
                        sh 'npm run test:ci'
                    }
                    post {
                        always {
                            publishTestResults testResultsPattern: 'test-results.xml'
                            publishHTML([
                                allowMissing: false,
                                alwaysLinkToLastBuild: true,
                                keepAll: true,
                                reportDir: 'coverage/lcov-report',
                                reportFiles: 'index.html',
                                reportName: 'Coverage Report'
                            ])
                        }
                    }
                }
                
                stage('E2E Tests') {
                    steps {
                        sh 'npm run e2e:ci'
                    }
                    post {
                        always {
                            archiveArtifacts artifacts: 'cypress/screenshots/**/*', allowEmptyArchive: true
                            archiveArtifacts artifacts: 'cypress/videos/**/*', allowEmptyArchive: true
                        }
                    }
                }
            }
        }
        
        stage('SonarQube Analysis') {
            when {
                anyOf {
                    branch 'main'
                    branch 'develop'
                }
            }
            steps {
                script {
                    def scannerHome = tool name: 'SonarQubeScanner', type: 'hudson.plugins.sonar.SonarRunnerInstallation'
                    withSonarQubeEnv('SonarQube') {
                        sh "${scannerHome}/bin/sonar-scanner"
                    }
                }
            }
        }
        
        stage('Build') {
            steps {
                script {
                    if (env.BRANCH_NAME == 'main') {
                        sh 'npm run build:prod'
                    } else {
                        sh 'npm run build'
                    }
                }
                archiveArtifacts artifacts: 'dist/**/*', fingerprint: true
            }
        }
        
        stage('Deploy') {
            when {
                anyOf {
                    branch 'main'
                    branch 'develop'
                }
            }
            steps {
                script {
                    if (env.BRANCH_NAME == 'main') {
                        // Deploy to production
                        sh '''
                            echo "Deploying to production..."
                            # Add your production deployment commands here
                        '''
                    } else if (env.BRANCH_NAME == 'develop') {
                        // Deploy to staging
                        sh '''
                            echo "Deploying to staging..."
                            # Add your staging deployment commands here
                        '''
                    }
                }
            }
        }
        
        stage('Performance Test') {
            when {
                branch 'develop'
            }
            steps {
                sh '''
                    npm install -g lighthouse
                    lighthouse https://staging.yourapp.com --output=json --output-path=lighthouse-report.json
                '''
                archiveArtifacts artifacts: 'lighthouse-report.json'
            }
        }
    }
    
    post {
        always {
            cleanWs()
        }
        success {
            emailext (
                subject: "✅ Build Success - ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                body: "Build completed successfully!\\n\\nCommit: ${env.GIT_COMMIT_MSG}",
                to: "${env.CHANGE_AUTHOR_EMAIL}"
            )
        }
        failure {
            emailext (
                subject: "❌ Build Failed - ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                body: "Build failed!\\n\\nCommit: ${env.GIT_COMMIT_MSG}\\n\\nCheck console output at ${env.BUILD_URL}",
                to: "${env.CHANGE_AUTHOR_EMAIL}"
            )
        }
    }
}
'''
        }
    
    async def _generate_deployment_scripts(self, code_files: Dict[str, Any]) -> Dict[str, str]:
        """Generate deployment scripts"""
        
        return {
            "scripts/deploy.sh": '''#!/bin/bash

# Deployment script for Angular application
set -e

# Configuration
ENVIRONMENT=${1:-staging}
BUILD_DIR="dist"
BACKUP_DIR="backups"

echo "🚀 Starting deployment to $ENVIRONMENT..."

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup current deployment
if [ -d "$BUILD_DIR" ]; then
    echo "📦 Creating backup..."
    tar -czf "$BACKUP_DIR/backup-$(date +%Y%m%d-%H%M%S).tar.gz" $BUILD_DIR
fi

# Install dependencies
echo "📥 Installing dependencies..."
npm ci

# Run tests
echo "🧪 Running tests..."
npm run test:ci

# Build application
echo "🔨 Building application..."
if [ "$ENVIRONMENT" = "production" ]; then
    npm run build:prod
else
    npm run build:staging
fi

# Deploy based on environment
case $ENVIRONMENT in
    "production")
        echo "🌟 Deploying to production..."
        firebase deploy --project production --token $FIREBASE_TOKEN
        ;;
    "staging")
        echo "🎭 Deploying to staging..."
        firebase deploy --project staging --token $FIREBASE_TOKEN
        ;;
    *)
        echo "❌ Unknown environment: $ENVIRONMENT"
        exit 1
        ;;
esac

echo "✅ Deployment completed successfully!"
''',
            "scripts/rollback.sh": '''#!/bin/bash

# Rollback script
set -e

ENVIRONMENT=${1:-staging}
BACKUP_FILE=${2}

echo "⏪ Rolling back deployment in $ENVIRONMENT..."

if [ -z "$BACKUP_FILE" ]; then
    # Find latest backup
    BACKUP_FILE=$(ls -t backups/*.tar.gz | head -n1)
fi

if [ ! -f "$BACKUP_FILE" ]; then
    echo "❌ Backup file not found: $BACKUP_FILE"
    exit 1
fi

echo "📦 Restoring from backup: $BACKUP_FILE"
tar -xzf "$BACKUP_FILE"

echo "🚀 Redeploying previous version..."
case $ENVIRONMENT in
    "production")
        firebase deploy --project production --token $FIREBASE_TOKEN
        ;;
    "staging")
        firebase deploy --project staging --token $FIREBASE_TOKEN
        ;;
esac

echo "✅ Rollback completed!"
''',
            "scripts/health-check.sh": '''#!/bin/bash

# Health check script
URL=${1:-https://staging.yourapp.com}
MAX_ATTEMPTS=5
ATTEMPT=1

echo "🏥 Performing health check on $URL..."

while [ $ATTEMPT -le $MAX_ATTEMPTS ]; do
    echo "Attempt $ATTEMPT of $MAX_ATTEMPTS..."
    
    STATUS_CODE=$(curl -s -o /dev/null -w "%{http_code}" $URL)
    
    if [ $STATUS_CODE -eq 200 ]; then
        echo "✅ Health check passed! ($STATUS_CODE)"
        exit 0
    else
        echo "❌ Health check failed with status $STATUS_CODE"
        if [ $ATTEMPT -eq $MAX_ATTEMPTS ]; then
            echo "💀 Max attempts reached. Deployment may have failed."
            exit 1
        fi
        sleep 10
    fi
    
    ATTEMPT=$((ATTEMPT + 1))
done
'''
        }
    
    async def get_status(self) -> Dict[str, Any]:
        """Get agent status"""
        return {
            "name": self.name,
            "version": self.version,
            "status": "active",
            "capabilities": [
                "GitHub Actions workflow generation",
                "Docker configuration creation",
                "Azure DevOps pipeline setup",
                "GitLab CI configuration",
                "Jenkins pipeline creation",
                "Deployment script generation",
                "Security scan integration",
                "Performance monitoring setup",
                "Container orchestration",
                "CI/CD best practices implementation"
            ]
        }