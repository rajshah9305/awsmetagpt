# MetaGPT + E2B Integration

A powerful application generator that combines MetaGPT multi-agent framework with E2B sandbox for live code execution and preview.

## Features

- **Multi-Agent Generation**: Real MetaGPT agents working together
- **Live Code Execution**: E2B sandboxes for instant preview
- **Real-time Updates**: WebSocket-based progress tracking
- **Multiple AI Models**: AWS Bedrock integration (Nova, Claude, Llama)
- **Complete Applications**: Full-stack code generation
- **Interactive Preview**: Live application testing

## Architecture

### Core Components

1. **MetaGPT Integration** (`app/services/metagpt_service.py`)
   - Real multi-agent execution
   - Workspace management
   - Artifact generation and processing

2. **E2B Sandbox Service** (`app/services/e2b_service.py`)
   - Isolated code execution environments
   - Multi-framework support (React, Python, Node.js, HTML)
   - Real-time application running

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
- E2B API key
- OpenAI or Anthropic API key

### Installation

1. **Clone and setup environment:**
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

# E2B Configuration
E2B_API_KEY=your_e2b_key
E2B_TEMPLATE_ID=base

# Application Settings
APP_HOST=0.0.0.0
APP_PORT=8000
DEBUG=false
METAGPT_WORKSPACE=./workspace
METAGPT_LOG_LEVEL=INFO
```

## Agent Roles

The system includes specialized MetaGPT agents:

1. **Product Manager** - Requirements analysis and user stories
2. **System Architect** - Technical architecture and design
3. **Project Manager** - Project planning and coordination
4. **Software Engineer** - Code implementation
5. **QA Engineer** - Testing strategies and quality assurance
6. **DevOps Engineer** - Infrastructure and deployment

## Generation Process

1. **Initialization** - MetaGPT team setup and workspace creation
2. **Multi-Agent Execution** - Collaborative work across specialized agents
3. **Code Generation** - Complete, working applications
4. **Live Preview** - E2B sandboxes execute code in real-time
5. **Artifact Processing** - Documentation, code, and configurations

## API Endpoints

### Generation
- `POST /api/v1/generate` - Start app generation
- `GET /api/v1/generate/{id}/status` - Get generation status
- `GET /api/v1/generate/{id}/artifacts` - Get all artifacts

### E2B Sandbox
- `POST /api/v1/e2b/sandbox/{id}/create` - Create sandbox
- `POST /api/v1/e2b/sandbox/{id}/files` - Write files to sandbox
- `POST /api/v1/e2b/sandbox/{id}/run` - Run application
- `GET /api/v1/e2b/sandbox/{id}/logs` - Get execution logs
- `DELETE /api/v1/e2b/sandbox/{id}` - Cleanup sandbox

### Information
- `GET /api/v1/models/bedrock` - Available AI models
- `GET /api/v1/agents/roles` - Available agent roles
- `GET /health` - System health check

### WebSocket
- `WS /ws/{client_id}` - Real-time updates

## E2B Integration

### Supported Frameworks

- **React Applications**: npm install + npm start
- **Python Applications**: Streamlit, Flask, FastAPI
- **Node.js Applications**: Express, basic HTTP servers
- **HTML/CSS/JS**: Static file serving
- **Auto-detection**: Project type identification

### Sandbox Features

- Isolated execution environments
- Real-time log streaming
- Multi-port application support
- Automatic dependency installation
- File system operations
- Process management

## Project Structure

```
├── app/                    # Backend application
│   ├── api/               # API routes
│   ├── core/              # Configuration
│   ├── models/            # Pydantic schemas
│   └── services/          # Core services
├── src/                   # Frontend React app
│   ├── components/        # UI components
│   ├── pages/            # Application pages
│   └── services/         # Frontend services
├── main.py               # FastAPI application
├── requirements.txt      # Python dependencies
├── package.json         # Node.js dependencies
├── vercel.json          # Vercel deployment config
└── start-dev.sh         # Development startup
```

## Deployment

### Vercel Deployment

This project is configured for deployment on Vercel:

1. Push your changes to GitHub
2. Import the repository in Vercel
3. Configure environment variables in Vercel dashboard
4. Deploy

The `vercel.json` configuration handles both the FastAPI backend and React frontend.

## Usage

1. **Start the application** using development or production scripts
2. **Open the web interface** at http://localhost:3000 (dev) or http://localhost:8000 (prod)
3. **Describe your application** in natural language
4. **Select agents** to include in the generation process
5. **Choose AI model** from available Bedrock models
6. **Monitor progress** through real-time WebSocket updates
7. **Preview live application** in E2B sandbox
8. **Download artifacts** including code and documentation

## Security

- Input validation and sanitization
- Rate limiting on API endpoints
- Isolated E2B sandbox execution
- Secure WebSocket connections
- Environment variable protection

## License

This project integrates with:
- [MetaGPT](https://github.com/FoundationAgents/MetaGPT) - Multi-agent framework
- [E2B](https://e2b.dev/) - Code execution sandboxes
- AWS Bedrock - AI model services
