# Deployment Guide

## Quick Start

### 1. Prerequisites

- Python 3.8+
- Node.js 16+
- AWS Account with Bedrock access
- E2B API key (optional)

### 2. Setup

```bash
# Clone and setup
git clone <repository>
cd metagpt-e2b-system

# Run automated setup
python scripts/setup.py

# Configure environment
cp .env.example .env
# Edit .env with your configuration
```

### 3. Development

```bash
# Start development servers
python scripts/dev.py

# Or manually:
# Backend: python main_clean.py
# Frontend: npm run dev
```

### 4. Production

```bash
# Build frontend
npm run build

# Start production server
python main_clean.py
```

## Environment Configuration

### Required Variables

```bash
# AWS Bedrock Configuration
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-west-2
BEDROCK_MODEL=us.amazon.nova-pro-v1:0

# Application Settings
SECRET_KEY=your_secret_key_here
DEBUG=false
LOG_LEVEL=INFO
```

### Optional Variables

```bash
# E2B Sandbox (for live execution)
E2B_API_KEY=your_e2b_api_key

# MetaGPT API Keys (fallback)
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key

# Performance Tuning
MAX_CONCURRENT_SESSIONS=10
RATE_LIMIT_REQUESTS=100
SESSION_TIMEOUT=7200
```

## Docker Deployment

### Dockerfile

```dockerfile
FROM python:3.11-slim

# Install Node.js
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs

# Set working directory
WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy and install Node dependencies
COPY package*.json ./
RUN npm ci --only=production

# Copy application code
COPY . .

# Build frontend
RUN npm run build

# Expose port
EXPOSE 8000

# Start application
CMD ["python", "main_clean.py"]
```

### Docker Compose

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DEBUG=false
      - LOG_LEVEL=INFO
    env_file:
      - .env
    volumes:
      - ./logs:/app/logs
      - ./workspace:/app/workspace
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - app
    restart: unless-stopped
```

## Kubernetes Deployment

### Deployment Manifest

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: metagpt-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: metagpt-app
  template:
    metadata:
      labels:
        app: metagpt-app
    spec:
      containers:
      - name: app
        image: metagpt-app:latest
        ports:
        - containerPort: 8000
        env:
        - name: DEBUG
          value: "false"
        - name: LOG_LEVEL
          value: "INFO"
        envFrom:
        - secretRef:
            name: metagpt-secrets
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: metagpt-service
spec:
  selector:
    app: metagpt-app
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

### ConfigMap and Secrets

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: metagpt-secrets
type: Opaque
stringData:
  AWS_ACCESS_KEY_ID: "your_access_key"
  AWS_SECRET_ACCESS_KEY: "your_secret_key"
  SECRET_KEY: "your_secret_key"
  E2B_API_KEY: "your_e2b_key"
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: metagpt-config
data:
  AWS_REGION: "us-west-2"
  BEDROCK_MODEL: "us.amazon.nova-pro-v1:0"
  MAX_CONCURRENT_SESSIONS: "10"
```

## Cloud Platform Deployment

### Railway

```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "python main_clean.py",
    "healthcheckPath": "/health",
    "healthcheckTimeout": 100,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### Heroku

```yaml
# Procfile
web: python main_clean.py
release: python scripts/setup.py --production

# app.json
{
  "name": "MetaGPT E2B System",
  "description": "Multi-agent application generator with live sandbox execution",
  "keywords": ["ai", "metagpt", "e2b", "python", "react"],
  "website": "https://github.com/your-repo",
  "repository": "https://github.com/your-repo",
  "stack": "heroku-22",
  "buildpacks": [
    {
      "url": "heroku/nodejs"
    },
    {
      "url": "heroku/python"
    }
  ],
  "env": {
    "AWS_ACCESS_KEY_ID": {
      "description": "AWS Access Key ID for Bedrock",
      "required": true
    },
    "AWS_SECRET_ACCESS_KEY": {
      "description": "AWS Secret Access Key for Bedrock",
      "required": true
    },
    "AWS_REGION": {
      "description": "AWS Region",
      "value": "us-west-2"
    },
    "SECRET_KEY": {
      "description": "Application secret key",
      "generator": "secret"
    }
  }
}
```

### Vercel (Frontend Only)

```json
{
  "name": "metagpt-frontend",
  "version": 2,
  "builds": [
    {
      "src": "package.json",
      "use": "@vercel/static-build",
      "config": {
        "distDir": "dist"
      }
    }
  ],
  "routes": [
    {
      "handle": "filesystem"
    },
    {
      "src": "/api/(.*)",
      "dest": "https://your-backend-api.com/api/$1"
    },
    {
      "src": "/(.*)",
      "dest": "/index.html"
    }
  ]
}
```

## Production Considerations

### Performance Optimization

```python
# main_clean.py production settings
if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main_clean:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        workers=4,  # Multiple workers
        loop="uvloop",  # Faster event loop
        http="httptools",  # Faster HTTP parser
        access_log=False,  # Disable access logs in production
        log_level="info"
    )
```

### Nginx Configuration

```nginx
upstream app {
    server app:8000;
}

server {
    listen 80;
    server_name your-domain.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    
    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    
    # Gzip compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript;
    
    # Static files
    location /static/ {
        alias /app/dist/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # WebSocket support
    location /ws/ {
        proxy_pass http://app;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # API routes
    location /api/ {
        proxy_pass http://app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 300s;  # Long timeout for generation
    }
    
    # Frontend
    location / {
        try_files $uri $uri/ /index.html;
        root /app/dist;
    }
}
```

### Database Setup (Future)

```sql
-- PostgreSQL setup for session persistence
CREATE DATABASE metagpt_system;

CREATE TABLE sessions (
    id UUID PRIMARY KEY,
    status VARCHAR(50) NOT NULL,
    progress INTEGER DEFAULT 0,
    message TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    client_id UUID,
    config JSONB
);

CREATE TABLE artifacts (
    id UUID PRIMARY KEY,
    session_id UUID REFERENCES sessions(id),
    name VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    type VARCHAR(50),
    language VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_sessions_status ON sessions(status);
CREATE INDEX idx_sessions_created_at ON sessions(created_at);
CREATE INDEX idx_artifacts_session_id ON artifacts(session_id);
```

### Monitoring Setup

```yaml
# docker-compose.monitoring.yml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    
  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana-storage:/var/lib/grafana

volumes:
  grafana-storage:
```

### Backup Strategy

```bash
#!/bin/bash
# backup.sh

# Backup workspace files
tar -czf "workspace-backup-$(date +%Y%m%d).tar.gz" workspace/

# Backup logs
tar -czf "logs-backup-$(date +%Y%m%d).tar.gz" logs/

# Upload to S3 (optional)
aws s3 cp workspace-backup-*.tar.gz s3://your-backup-bucket/
aws s3 cp logs-backup-*.tar.gz s3://your-backup-bucket/

# Clean old backups (keep last 7 days)
find . -name "*-backup-*.tar.gz" -mtime +7 -delete
```

## Security Checklist

### Application Security
- [ ] Environment variables secured
- [ ] Input validation enabled
- [ ] Rate limiting configured
- [ ] CORS properly configured
- [ ] Security headers added
- [ ] File upload restrictions
- [ ] Process isolation enabled

### Infrastructure Security
- [ ] SSL/TLS certificates installed
- [ ] Firewall rules configured
- [ ] Database access restricted
- [ ] Backup encryption enabled
- [ ] Log access controlled
- [ ] Monitoring alerts setup

### AWS Security
- [ ] IAM roles with minimal permissions
- [ ] Bedrock access properly scoped
- [ ] API keys rotated regularly
- [ ] CloudTrail logging enabled
- [ ] VPC security groups configured

## Troubleshooting

### Common Issues

1. **Bedrock Access Denied**
   - Check AWS credentials
   - Verify model access permissions
   - Confirm region settings

2. **E2B Sandbox Failures**
   - Validate API key
   - Check quota limits
   - Review sandbox logs

3. **High Memory Usage**
   - Monitor process counts
   - Check for memory leaks
   - Adjust resource limits

4. **WebSocket Connection Issues**
   - Verify proxy configuration
   - Check firewall rules
   - Monitor connection counts

### Debug Commands

```bash
# Check system health
curl http://localhost:8000/health

# View application logs
tail -f logs/app.log

# Monitor resource usage
docker stats

# Test Bedrock connection
python test_bedrock_config.py

# Run health checks
python -c "from app.api.dependencies import check_system_health; check_system_health()"
```