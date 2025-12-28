# MetaGPT + E2B Integration System

A production-ready, modular system for generating complete applications using multi-agent AI orchestration with AWS Bedrock and live sandbox execution via E2B.

## ✨ Features

- **Multi-Agent AI Generation**: Uses MetaGPT with AWS Bedrock for intelligent application generation
- **Live Sandbox Execution**: Integrated E2B sandboxes for real-time code execution and preview
- **Modular Architecture**: Clean, maintainable codebase with proper separation of concerns
- **Production Ready**: Comprehensive error handling, logging, monitoring, and security
- **Real-time Updates**: WebSocket-based progress tracking and live log streaming
- **Multiple AI Models**: Support for Claude, Nova, Llama, and other Bedrock models
- **Framework Detection**: Automatic project type detection and appropriate runners
- **Scalable Design**: Built for horizontal scaling and high availability

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Node.js 16+
- AWS Account with Bedrock access
- E2B API key (optional, for live execution)

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd metagpt-e2b-system

# Run automated setup
python scripts/setup.py

# Configure environment
cp .env.example .env
# Edit .env with your AWS credentials and configuration
```

### Configuration

Update your `.env` file with the required settings:

```bash
# AWS Bedrock Configuration (Required)
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_access_key_here
AWS_REGION=us-west-2
BEDROCK_MODEL=us.amazon.nova-pro-v1:0

# Application Settings
SECRET_KEY=your_secret_key_here
DEBUG=false
LOG_LEVEL=INFO

# E2B Configuration (Optional - for live execution)
E2B_API_KEY=your_e2b_api_key_here
```

### Development

```bash
# Start development servers (backend + frontend)
python scripts/dev.py

# Or start manually:
# Backend: python main_clean.py
# Frontend: npm run dev
```

### Production

```bash
# Build frontend
npm run build

# Start production server
python main_clean.py
```

## 🏗️ Architecture

### System Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │    │   API Layer      │    │  Orchestration  │
│   (React)       │◄──►│   (FastAPI)      │◄──►│   (MetaGPT)     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Sandbox       │    │   AI Services    │    │   File System   │
│   (E2B)         │    │   (Bedrock)      │    │   (Local/S3)    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### Key Components

- **Orchestration Layer**: Task scheduling, agent management, and workflow coordination
- **Sandbox Layer**: E2B integration for secure code execution and live previews
- **API Layer**: Clean REST API with proper validation and error handling
- **Frontend Layer**: Modern React interface with real-time updates

## 📚 Documentation

- [Architecture Guide](ARCHITECTURE.md) - Detailed system architecture and design patterns
- [Deployment Guide](DEPLOYMENT.md) - Production deployment and configuration
- [API Documentation](http://localhost:8000/docs) - Interactive API documentation (when running)

## 🧪 Testing

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test categories
python -m pytest tests/test_orchestration.py -v
python -m pytest tests/test_sandbox.py -v

# Run with coverage
python -m pytest tests/ --cov=app --cov-report=html
```

## 🔧 Configuration

### Environment Variables

The system uses a modular configuration system with the following sections:

#### Core Settings
- `APP_HOST`, `APP_PORT`: Server configuration
- `DEBUG`, `LOG_LEVEL`: Development settings
- `SECRET_KEY`: Application security

#### AWS Bedrock
- `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`: AWS credentials
- `AWS_REGION`: AWS region (us-west-2 recommended)
- `BEDROCK_MODEL`: AI model to use
- `BEDROCK_MAX_TOKENS`, `BEDROCK_TEMPERATURE`: Model parameters

#### E2B Sandbox
- `E2B_API_KEY`: E2B API key for sandbox execution
- `E2B_TEMPLATE_ID`: Default sandbox template
- `E2B_TIMEOUT`: Sandbox timeout in seconds

#### Performance
- `MAX_CONCURRENT_SESSIONS`: Maximum parallel generations
- `RATE_LIMIT_REQUESTS`: API rate limiting
- `SESSION_TIMEOUT`: Session timeout in seconds

### Supported AI Models

The system supports multiple AI models via AWS Bedrock:

- **Amazon Nova**: `us.amazon.nova-pro-v1:0`, `us.amazon.nova-lite-v1:0`
- **Anthropic Claude**: `us.anthropic.claude-sonnet-4-20250514-v1:0`
- **Meta Llama**: `us.meta.llama3-3-70b-instruct-v1:0`
- **And more**: Check `/api/v1/models/bedrock` for available models

## 🎯 Usage Examples

### Generate a React Application

```bash
curl -X POST "http://localhost:8000/api/v1/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "requirement": "Create a modern todo application with user authentication",
    "app_type": "web_app",
    "preferred_model": "us.amazon.nova-pro-v1:0",
    "active_agents": ["product_manager", "architect", "engineer"],
    "tech_stack_preferences": ["react", "typescript", "tailwind"]
  }'
```

### Monitor Generation Progress

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/your-client-id');
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Progress:', data.progress, data.message);
};
```

### Execute in Sandbox

```bash
# Create sandbox
curl -X POST "http://localhost:8000/api/v1/e2b/sandbox/{generation_id}/create"

# Write files
curl -X POST "http://localhost:8000/api/v1/e2b/sandbox/{generation_id}/files" \
  -H "Content-Type: application/json" \
  -d '[{"name": "app.py", "content": "print(\"Hello World\")", "type": "code"}]'

# Run application
curl -X POST "http://localhost:8000/api/v1/e2b/sandbox/{generation_id}/run"
```

## 🔒 Security

### Security Features

- **Input Validation**: Comprehensive validation using Pydantic models
- **Rate Limiting**: Configurable rate limiting per client IP
- **Sandbox Isolation**: Secure code execution in isolated E2B environments
- **Error Handling**: Secure error responses without information disclosure
- **File Sanitization**: Path traversal prevention and content validation

### Security Best Practices

1. **Environment Variables**: Never commit sensitive data to version control
2. **AWS IAM**: Use minimal required permissions for Bedrock access
3. **API Keys**: Rotate API keys regularly
4. **HTTPS**: Always use HTTPS in production
5. **Monitoring**: Enable comprehensive logging and monitoring

## 🚀 Deployment

### Docker

```bash
# Build image
docker build -t metagpt-system .

# Run container
docker run -p 8000:8000 --env-file .env metagpt-system
```

### Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f
```

### Cloud Platforms

The system supports deployment on:

- **Railway**: One-click deployment with `railway.json`
- **Heroku**: Heroku-ready with `Procfile` and `app.json`
- **AWS**: ECS/EKS deployment with provided configurations
- **Kubernetes**: Production-ready manifests included

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions.

## 🤝 Contributing

### Development Setup

```bash
# Install development dependencies
pip install -r requirements.txt
npm install

# Install pre-commit hooks
pre-commit install

# Run linting
black app/ tests/
isort app/ tests/
flake8 app/ tests/

# Run tests
python -m pytest tests/ -v
```

### Code Style

- **Python**: Black formatting, isort imports, flake8 linting
- **JavaScript**: ESLint with React configuration
- **Documentation**: Comprehensive docstrings and comments
- **Testing**: High test coverage with pytest

### Pull Request Process

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Ensure all tests pass
5. Submit a pull request

## 📊 Monitoring

### Health Checks

```bash
# System health
curl http://localhost:8000/health

# Detailed health with metrics
curl http://localhost:8000/api/v1/health
```

### Metrics

The system provides comprehensive metrics:

- **Request/Response**: API performance and error rates
- **Resource Usage**: Memory, CPU, and disk utilization
- **Session Management**: Active sessions and completion rates
- **Sandbox Usage**: E2B sandbox utilization and performance

### Logging

Structured logging with:

- **Correlation IDs**: Request tracking across services
- **Performance Metrics**: Response times and resource usage
- **Error Tracking**: Comprehensive error logging and aggregation
- **Audit Trails**: Security and access logging

## 🐛 Troubleshooting

### Common Issues

1. **Bedrock Access Denied**
   ```bash
   # Test Bedrock configuration
   python test_bedrock_config.py
   ```

2. **E2B Sandbox Failures**
   ```bash
   # Check E2B API key and quota
   curl -H "Authorization: Bearer $E2B_API_KEY" https://api.e2b.dev/sandboxes
   ```

3. **Memory Issues**
   ```bash
   # Monitor resource usage
   python -c "from app.services.orchestration import agent_orchestrator; print(agent_orchestrator.get_statistics())"
   ```

### Debug Mode

Enable debug mode for detailed logging:

```bash
export DEBUG=true
export LOG_LEVEL=DEBUG
python main_clean.py
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **MetaGPT**: Multi-agent framework for application generation
- **E2B**: Cloud sandboxes for secure code execution
- **AWS Bedrock**: Managed AI model inference
- **FastAPI**: Modern Python web framework
- **React**: Frontend user interface library

## 📞 Support

- **Documentation**: Check the [docs](ARCHITECTURE.md) for detailed information
- **Issues**: Report bugs and feature requests via GitHub Issues
- **Discussions**: Join community discussions for questions and ideas

---

**Built with ❤️ for developers who want to generate applications with AI**