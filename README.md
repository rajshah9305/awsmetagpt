# MetaGPT + E2B Integration - Real Multi-Agent App Generator

A powerful application that combines **real MetaGPT multi-agent framework** with **E2B live code execution** to generate complete applications from natural language requirements.

## 🚀 Features

- **Real MetaGPT Integration**: Uses actual MetaGPT agents (Product Manager, Architect, Engineer, QA, DevOps)
- **Live Code Execution**: E2B sandboxes for real-time code preview and testing
- **Multiple AI Models**: Support for OpenAI, Anthropic, and AWS Bedrock models
- **Real-time Updates**: WebSocket-based progress tracking
- **Production Ready**: Complete applications with proper architecture

## 🛠️ Prerequisites

- **Python 3.8+**
- **Node.js 16+**
- **npm or yarn**

## 📋 Required API Keys

You'll need at least one of these API key combinations:

### For MetaGPT (choose one):
- **OpenAI API Key** - Get from [OpenAI Platform](https://platform.openai.com/)
- **Anthropic API Key** - Get from [Anthropic Console](https://console.anthropic.com/)

### For AWS Bedrock (optional):
- **AWS Access Key ID & Secret** - For additional model options

### For Live Code Execution:
- **E2B API Key** - Get from [E2B.dev](https://e2b.dev/) (free tier available)

## 🚀 Quick Setup

### Option 1: Automated Setup (Recommended)

```bash
cd awsmetagpt
python setup.py
```

### Option 2: Manual Setup

1. **Clone and navigate:**
   ```bash
   cd awsmetagpt
   ```

2. **Create virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   npm install
   ```

4. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

5. **Create workspace:**
   ```bash
   mkdir -p workspace
   ```

## ⚙️ Configuration

Edit the `.env` file with your API keys:

```env
# MetaGPT Configuration (choose one or more)
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# AWS Bedrock (optional)
AWS_ACCESS_KEY_ID=your_aws_access_key_here
AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key_here
AWS_REGION=us-west-2

# E2B Sandbox (required for live preview)
E2B_API_KEY=your_e2b_api_key_here

# MetaGPT Settings
METAGPT_WORKSPACE=./workspace
METAGPT_LOG_LEVEL=INFO
```

## 🏃‍♂️ Running the Application

### Development Mode (with hot reload):
```bash
./start-dev.sh
```
- Backend: http://localhost:8000
- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs

### Production Mode:
```bash
./start.sh
```
- Application: http://localhost:8000

## 🎯 How It Works

1. **Input Requirements**: Describe your application in natural language
2. **MetaGPT Agents**: Real agents analyze and create:
   - Product Requirements (Product Manager)
   - System Architecture (Architect)
   - Implementation Plan (Engineer)
   - Test Strategy (QA Engineer)
   - Deployment Plan (DevOps)
3. **Code Generation**: Complete, working applications
4. **Live Preview**: E2B sandboxes execute code in real-time
5. **Download**: Get all generated files

## 🔧 API Endpoints

### Generation
- `POST /api/v1/generate` - Start app generation
- `GET /api/v1/generate/{id}/status` - Get generation status
- `GET /api/v1/generate/{id}/artifacts` - Get generated files

### E2B Sandbox
- `POST /api/v1/e2b/sandbox/{id}/create` - Create sandbox
- `POST /api/v1/e2b/sandbox/{id}/files` - Upload files
- `POST /api/v1/e2b/sandbox/{id}/run` - Run application
- `GET /api/v1/e2b/sandbox/{id}/logs` - Get execution logs

### Health & Info
- `GET /health` - Service health check
- `GET /api/v1/models/bedrock` - Available AI models
- `GET /api/v1/agents/roles` - Available agent roles

## 🧪 Testing the Setup

1. **Health Check:**
   ```bash
   curl http://localhost:8000/health
   ```

2. **Test Generation:**
   - Open http://localhost:3000
   - Enter: "Create a simple todo app with React"
   - Watch real MetaGPT agents work
   - See live code execution in E2B sandbox

## 📁 Project Structure

```
awsmetagpt/
├── app/
│   ├── api/routes.py          # API endpoints
│   ├── services/
│   │   ├── metagpt_service.py # Real MetaGPT integration
│   │   └── e2b_service.py     # E2B sandbox management
│   └── core/config.py         # Configuration
├── src/
│   ├── pages/Results.jsx      # Results display
│   └── components/
│       └── E2BSandboxPreview.jsx # Live preview
├── workspace/                 # MetaGPT workspace
├── requirements.txt           # Python dependencies
├── package.json              # Node.js dependencies
├── setup.py                  # Automated setup
├── start.sh                  # Production start
└── start-dev.sh              # Development start
```

## 🔍 Troubleshooting

### Common Issues:

1. **"MetaGPT not found"**
   ```bash
   pip install metagpt>=0.8.0
   ```

2. **"E2B API key invalid"**
   - Verify your E2B API key at https://e2b.dev/
   - Check .env file formatting

3. **"No AI model available"**
   - Ensure at least one API key is configured (OpenAI or Anthropic)
   - Check API key validity

4. **"Sandbox creation failed"**
   - Verify E2B API key
   - Check E2B service status

### Debug Mode:
```bash
export DEBUG=true
export METAGPT_LOG_LEVEL=DEBUG
./start-dev.sh
```

## 🆚 Simulation vs Real Integration

| Feature | Previous (Simulation) | Now (Real Integration) |
|---------|----------------------|------------------------|
| Agents | Fake agent responses | Real MetaGPT agents |
| Code Quality | Basic templates | Production-ready code |
| Architecture | Simple structure | Proper system design |
| Testing | No tests | Real test strategies |
| Execution | Static preview | Live E2B sandboxes |

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with real MetaGPT and E2B
5. Submit a pull request

## 📚 Documentation

- [MetaGPT Documentation](https://github.com/geekan/MetaGPT)
- [E2B Documentation](https://e2b.dev/docs)
- [OpenAI API](https://platform.openai.com/docs)
- [Anthropic API](https://docs.anthropic.com/)

## 🔐 Security

- API keys are stored in `.env` (never commit this file)
- E2B sandboxes are isolated and temporary
- All code execution happens in secure containers

## 📄 License

MIT License - see LICENSE file for details

---

**Ready to build amazing applications with AI agents? Get your API keys and start generating!** 🚀