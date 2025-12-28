# MetaGPT + E2B Integration

A powerful application generator that combines **real MetaGPT multi-agent framework** with **E2B sandbox** for live code execution and preview.

## Features

- **Multi-Agent Generation**: Real MetaGPT agents (ProductManager, Architect, Engineer, QA) working together
- **Live Code Execution**: E2B sandboxes for instant preview and execution
- **Real-time Updates**: WebSocket-based progress tracking
- **Multiple AI Models**: AWS Bedrock integration (Nova, Claude, Llama)
- **Complete Applications**: Full-stack code generation
- **Interactive Preview**: Live application testing in isolated sandboxes

## Architecture

### Core Components

1. **MetaGPT Integration** (`app/services/metagpt_service.py`)
   - Real multi-agent execution using [MetaGPT framework](https://github.com/FoundationAgents/MetaGPT)
   - SoftwareCompany orchestration with specialized roles
   - Workspace management and artifact generation

2. **E2B Sandbox Service** (`app/services/e2b_service.py`)
   - Isolated code execution using [E2B sandboxes](https://e2b.dev/docs)
   - Multi-framework support (React, Python, Node.js, HTML)
   - Real-time application running and preview

3. **WebSocket Manager** (`app/services/websocket_manager.py`)
   - Real-time progress updates
   - Agent status tracking
   - Live communication

4. **AWS Bedrock Client** (`app/services/bedrock_client.py`)
   - Multiple AI model support
   - Async model invocation
   - Error handling and retries

## Setup

### Prerequisites

- Python 3.8+
- Node.js 16+
- AWS Account with Bedrock access
- E2B API key ([Get it here](https://e2b.dev))
- OpenAI or Anthropic API key

### Local Installation

1. **Clone repository:**
   ```bash
   git clone https://github.com/rajshah9305/awsmetagpt.git
   cd awsmetagpt
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Development mode:**
   ```bash
   chmod +x start-dev.sh
   ./start-dev.sh
   ```

4. **Production mode:**
   ```bash
   chmod +x start.sh
   ./start.sh
   ```

### Environment Variables

```env
# AWS Configuration (Required)
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=us-east-1

# MetaGPT Configuration (Choose one)
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key

# E2B Configuration (Required)
E2B_API_KEY=your_e2b_key
E2B_TEMPLATE_ID=base

# Application Settings
APP_HOST=0.0.0.0
APP_PORT=8000
DEBUG=false
SECRET_KEY=your_secret_key
```

## MetaGPT Agent Roles

The system uses **real MetaGPT agents** from the official framework:

1. **Product Manager** (`metagpt.roles.ProductManager`)
   - Requirements analysis
   - User stories creation
   - Business logic definition

2. **System Architect** (`metagpt.roles.Architect`)
   - Technical architecture design
   - Technology stack selection
   - System specifications

3. **Project Manager** (`metagpt.roles.ProjectManager`)
   - Project planning
   - Timeline management
   - Resource coordination

4. **Software Engineer** (`metagpt.roles.Engineer`)
   - Code implementation
   - Technical solutions
   - Code structure design

5. **QA Engineer** (`metagpt.roles.QaEngineer`)
   - Testing strategies
   - Quality assurance plans
   - Test case creation

## Generation Process

1. **Initialization**
   - MetaGPT SoftwareCompany setup
   - Workspace creation
   - Agent configuration

2. **Multi-Agent Execution**
   - Real MetaGPT agents collaborate
   - `company.run_project(requirement)` execution
   - Artifact generation in workspace

3. **Code Generation**
   - Complete, working applications
   - Documentation and tests

4. **Live Preview**
   - E2B Sandbox creation
   - Code deployment to sandbox
   - Real-time execution and preview

5. **Artifact Processing**
   - Code files, documentation, configurations
   - Available for download

## API Endpoints

### Generation
- `POST /api/v1/generate` - Start app generation with MetaGPT
- `GET /api/v1/generate/{id}/status` - Get generation status
- `GET /api/v1/generate/{id}/artifacts` - Get all generated artifacts

### E2B Sandbox
- `POST /api/v1/e2b/sandbox/{id}/create` - Create E2B sandbox
- `POST /api/v1/e2b/sandbox/{id}/files` - Write files to sandbox
- `POST /api/v1/e2b/sandbox/{id}/run` - Run application in sandbox
- `GET /api/v1/e2b/sandbox/{id}/logs` - Get execution logs
- `DELETE /api/v1/e2b/sandbox/{id}` - Cleanup sandbox

### Information
- `GET /api/v1/models/bedrock` - Available AI models
- `GET /api/v1/agents/roles` - Available MetaGPT agent roles
- `GET /health` - System health check

### WebSocket
- `WS /ws/{client_id}` - Real-time updates from agents

## E2B Integration

### Supported Frameworks

- **React Applications**: npm install + npm start
- **Python Applications**: Streamlit, Flask, FastAPI
- **Node.js Applications**: Express, basic HTTP servers
- **HTML/CSS/JS**: Static file serving
- **Auto-detection**: Project type identification

### Sandbox Features

- Isolated execution environments using [E2B](https://e2b.dev)
- Real-time log streaming
- Multi-port application support
- Automatic dependency installation
- File system operations
- Process management

## Deployment

### Railway Deployment (Recommended)

**Quick Deploy:**

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template?template=https://github.com/rajshah9305/awsmetagpt)

**Manual Deploy:**

1. **Create Railway Project**
   - Go to [railway.app](https://railway.app)
   - Click "New Project" → "Deploy from GitHub repo"
   - Select `rajshah9305/awsmetagpt`

2. **Configure Environment Variables**
   - Add all required environment variables (see [RAILWAY_DEPLOYMENT.md](RAILWAY_DEPLOYMENT.md))

3. **Deploy**
   - Railway will automatically build and deploy
   - Access via provided Railway URL

**Detailed Instructions:** See [RAILWAY_DEPLOYMENT.md](RAILWAY_DEPLOYMENT.md)

### Vercel Deployment (Alternative)

The repository also includes `vercel.json` for Vercel deployment. See deployment documentation for details.

## Project Structure

```
awsmetagpt/
├── app/                          # Backend FastAPI application
│   ├── api/                     # API routes
│   │   └── routes.py           # All API endpoints
│   ├── core/                    # Configuration
│   │   └── config.py           # Settings and env vars
│   ├── models/                  # Pydantic schemas
│   │   └── schemas.py          # Request/response models
│   └── services/                # Core services
│       ├── agent_orchestrator.py   # Multi-agent orchestration
│       ├── metagpt_service.py      # Real MetaGPT integration
│       ├── e2b_service.py          # E2B sandbox management
│       ├── bedrock_client.py       # AWS Bedrock client
│       └── websocket_manager.py    # WebSocket handling
├── src/                         # Frontend React application
│   ├── components/              # UI components
│   ├── pages/                   # Application pages
│   └── services/                # Frontend services
├── main.py                      # FastAPI entry point
├── requirements.txt             # Python dependencies (optimized)
├── package.json                 # Node.js dependencies
├── railway.json                 # Railway configuration
├── nixpacks.toml               # Nixpacks build config
├── Procfile                     # Process configuration
└── RAILWAY_DEPLOYMENT.md        # Deployment guide
```

## Usage

1. **Start the application**
2. **Open web interface** at http://localhost:8000
3. **Describe your application** in natural language
4. **Select MetaGPT agents** to include
5. **Choose AI model** from Bedrock
6. **Monitor progress** via real-time WebSocket updates
7. **Preview live application** in E2B sandbox
8. **Download artifacts** including code and documentation

## Real Implementation Details

### MetaGPT Integration

The application uses the **official MetaGPT framework**:

```python
from metagpt.software_company import SoftwareCompany
from metagpt.roles import ProductManager, Architect, Engineer, QaEngineer

# Create company with real agents
company = SoftwareCompany()
company.hire([ProductManager(), Architect(), Engineer(), QaEngineer()])

# Run actual MetaGPT generation
result = company.run_project(requirement)
```

### E2B Sandbox Integration

The application uses **real E2B sandboxes**:

```python
from e2b import Sandbox

# Create actual E2B sandbox
sandbox = Sandbox(
    template="base",
    api_key=settings.E2B_API_KEY,
    timeout=1800,
    cpu_count=2,
    memory_mb=2048
)

# Execute code in sandbox
process = sandbox.process.start(command)
```

## Security

- Input validation and sanitization
- Rate limiting on API endpoints
- Isolated E2B sandbox execution
- Secure WebSocket connections
- Environment variable protection

## Performance

- **MetaGPT Generation**: 2-5 minutes (depends on complexity)
- **E2B Sandbox Creation**: 5-10 seconds
- **WebSocket Latency**: <100ms
- **API Response Time**: 100-300ms

## Monitoring

- Health check: `/health` endpoint
- Real-time WebSocket status
- Generation progress tracking
- E2B sandbox logs
- System metrics

## License

This project integrates with:
- [MetaGPT](https://github.com/FoundationAgents/MetaGPT) - Multi-agent framework
- [E2B](https://e2b.dev/) - Code execution sandboxes
- AWS Bedrock - AI model services

## Support

- **MetaGPT Issues**: [github.com/FoundationAgents/MetaGPT/issues](https://github.com/FoundationAgents/MetaGPT/issues)
- **E2B Documentation**: [e2b.dev/docs](https://e2b.dev/docs)
- **Railway Support**: [railway.app/help](https://railway.app/help)
