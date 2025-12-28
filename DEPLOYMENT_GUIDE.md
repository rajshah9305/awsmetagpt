# 🚀 MetaGPT + E2B Deployment Guide

## 📋 Overview

This repository contains a production-ready MetaGPT + E2B Sandbox integration that generates complete applications from natural language using AI agents and provides live code execution.

## ⚡ Quick Deploy

### 1. Clone Repository
```bash
git clone https://github.com/rajshah9305/awsmetagpt.git
cd awsmetagpt
```

### 2. Automated Setup
```bash
python setup.py
```

### 3. Configure Environment
```bash
cp .env.example .env
# Edit .env with your API keys
```

### 4. Start Application
```bash
# Production
./start.sh

# Development  
./start-dev.sh
```

### 5. Access Application
Open http://localhost:8000 in your browser

## 🔑 Required API Keys

### AWS Bedrock (Required)
1. Create AWS account: https://aws.amazon.com/
2. Enable Bedrock service
3. Request model access (Nova models available by default)
4. Create IAM user with Bedrock permissions
5. Add credentials to `.env`:
   ```env
   AWS_ACCESS_KEY_ID=your_key
   AWS_SECRET_ACCESS_KEY=your_secret
   ```

### AI Models (Choose One)
**Option 1: OpenAI**
- Get key: https://platform.openai.com/
- Add to `.env`: `OPENAI_API_KEY=your_key`

**Option 2: Anthropic**  
- Get key: https://console.anthropic.com/
- Add to `.env`: `ANTHROPIC_API_KEY=your_key`

### E2B Sandbox (Optional)
- Get key: https://e2b.dev/
- Add to `.env`: `E2B_API_KEY=your_key`
- Enables live code execution and preview

## 🏗️ Architecture

```
Frontend (React + Vite + Tailwind)
    ↓ WebSocket + REST API
Backend (FastAPI + Python)
    ↓ Multi-Agent Framework  
MetaGPT Agents (PM, Architect, Engineer, QA, DevOps)
    ↓ AI Model Integration
AWS Bedrock Foundation Models + E2B Sandbox
```

## 🎯 Features

- **Real MetaGPT Integration**: Actual multi-agent collaboration
- **E2B Live Sandbox**: Execute and preview generated code
- **AWS Bedrock Models**: Nova, Claude, Llama support
- **Real-time Updates**: WebSocket-based progress tracking
- **Production Ready**: Security, validation, error handling
- **Modern Stack**: React + FastAPI + Tailwind CSS

## 🔧 Verification

Run the deployment verification script:
```bash
python verify-deployment.py
```

This checks:
- ✅ Python version compatibility
- ✅ Dependencies installation
- ✅ Environment configuration
- ✅ Port availability
- ✅ Workspace setup

## 🌐 Production Deployment

### Full Stack Deployment (Recommended)

**Docker**
```bash
# Build image
docker build -t awsmetagpt .

# Run container
docker run -p 8000:8000 --env-file .env awsmetagpt
```

**AWS EC2**
1. Launch EC2 instance (t3.medium+)
2. Install Python 3.8+, Node.js 16+
3. Clone repo and run setup
4. Configure security groups for port 8000

**Railway/Render (Full Stack)**
1. Connect GitHub repository
2. Set environment variables
3. Deploy with: `python -m uvicorn main:app --host 0.0.0.0 --port $PORT`

### Frontend-Only Deployment

**Vercel (Frontend + Simplified API)**
```bash
npm run build
vercel deploy
```

**Note**: Vercel deployment provides a simplified API due to serverless limitations. MetaGPT and E2B integration require persistent processes not available in serverless environments. For full functionality, use Docker or VPS deployment.

## 📊 API Endpoints

- `POST /api/v1/generate` - Start app generation
- `GET /api/v1/generate/{id}/status` - Get status
- `GET /api/v1/generate/{id}/artifacts` - Get artifacts
- `GET /api/v1/models/bedrock` - Available models
- `GET /api/v1/agents/roles` - Available agents
- `GET /api/v1/health` - Health check
- `WS /ws/{client_id}` - Real-time updates

## 🔒 Security Features

- Input validation and sanitization
- Rate limiting (10 requests/hour per IP)
- UUID validation for all IDs
- File size limits (1MB per artifact)
- Maximum 5 concurrent generations
- Proper error handling without information leakage

## 🐛 Troubleshooting

### Common Issues

**MetaGPT Import Error:**
```bash
pip install metagpt==0.8.1
```

**E2B Connection Failed:**
- Verify API key is correct
- Check E2B service status at https://e2b.dev/

**AWS Bedrock Access Denied:**
- Request model access in AWS console
- Verify IAM permissions include Bedrock access
- Check region is set to us-east-1

**Port Already in Use:**
```bash
# Kill processes on ports 8000/3000
lsof -ti:8000 | xargs kill -9
lsof -ti:3000 | xargs kill -9
```

### Debug Mode
Enable detailed logging:
```env
DEBUG=true
METAGPT_LOG_LEVEL=DEBUG
```

## 📈 Performance

- **Cold start**: ~2-3 seconds
- **Generation time**: 30-120 seconds
- **WebSocket latency**: <100ms
- **Memory usage**: ~200MB backend + ~50MB frontend
- **Concurrent users**: 50+ per instance

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open Pull Request

## 📄 License

MIT License - see LICENSE file for details.

## 🔗 Links

- **Repository**: https://github.com/rajshah9305/awsmetagpt
- **MetaGPT**: https://github.com/geekan/MetaGPT
- **E2B Docs**: https://e2b.dev/docs
- **AWS Bedrock**: https://docs.aws.amazon.com/bedrock/

---

**Built with ❤️ for developers who want to accelerate app development using AI agents**