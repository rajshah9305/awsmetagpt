# Railway Deployment Guide

## Prerequisites

Before deploying to Railway, ensure you have:

1. **Railway Account** - Sign up at [railway.app](https://railway.app)
2. **GitHub Repository** - This repository must be on GitHub
3. **API Keys** - Obtain the following:
   - AWS credentials (for Bedrock)
   - OpenAI or Anthropic API key (for MetaGPT)
   - E2B API key (for sandbox execution)

## Quick Deploy to Railway

### Option 1: Deploy via Railway Dashboard (Recommended)

1. **Login to Railway**
   - Go to [railway.app](https://railway.app)
   - Sign in with GitHub

2. **Create New Project**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose `rajshah9305/awsmetagpt`

3. **Configure Environment Variables**
   
   Add the following environment variables in Railway dashboard:
   
   ```
   # AWS Configuration (Required)
   AWS_ACCESS_KEY_ID=your_aws_access_key
   AWS_SECRET_ACCESS_KEY=your_aws_secret_key
   AWS_REGION=us-east-1
   
   # MetaGPT Configuration (Required - Choose at least one)
   OPENAI_API_KEY=your_openai_api_key
   ANTHROPIC_API_KEY=your_anthropic_api_key
   
   # E2B Configuration (Required)
   E2B_API_KEY=your_e2b_api_key
   E2B_TEMPLATE_ID=base
   
   # Application Settings
   APP_HOST=0.0.0.0
   APP_PORT=$PORT
   DEBUG=false
   LOG_LEVEL=INFO
   SECRET_KEY=your_random_secret_key_here
   
   # CORS Settings
   CORS_ORIGINS=*
   
   # MetaGPT Settings
   METAGPT_WORKSPACE=/app/workspace
   METAGPT_LOG_LEVEL=INFO
   METAGPT_MAX_BUDGET=10.0
   METAGPT_SAVE_LOGS=true
   METAGPT_ENABLE_MEMORY=true
   
   # E2B Settings
   E2B_TIMEOUT=1800
   E2B_MAX_SANDBOXES=10
   E2B_CPU_LIMIT=2
   E2B_MEMORY_LIMIT=2048
   
   # WebSocket Settings
   WS_HEARTBEAT_INTERVAL=30
   WS_MAX_CONNECTIONS=100
   
   # Session Management
   SESSION_TIMEOUT=7200
   MAX_CONCURRENT_SESSIONS=10
   
   # Feature Flags
   ENABLE_E2B=true
   ENABLE_BEDROCK=true
   ENABLE_WEBSOCKETS=true
   ```

4. **Deploy**
   - Railway will automatically detect the configuration
   - Build and deployment will start automatically
   - Wait for deployment to complete (usually 3-5 minutes)

5. **Access Your Application**
   - Railway will provide a public URL (e.g., `your-app.railway.app`)
   - Visit the URL to access your deployed application

### Option 2: Deploy via Railway CLI

1. **Install Railway CLI**
   ```bash
   npm i -g @railway/cli
   ```

2. **Login to Railway**
   ```bash
   railway login
   ```

3. **Initialize Project**
   ```bash
   cd awsmetagpt
   railway init
   ```

4. **Set Environment Variables**
   ```bash
   railway variables set AWS_ACCESS_KEY_ID=your_key
   railway variables set AWS_SECRET_ACCESS_KEY=your_secret
   railway variables set OPENAI_API_KEY=your_openai_key
   railway variables set E2B_API_KEY=your_e2b_key
   # ... set all other variables
   ```

5. **Deploy**
   ```bash
   railway up
   ```

## Configuration Files

The repository includes Railway-specific configuration files:

1. **railway.json** - Railway service configuration
2. **nixpacks.toml** - Build configuration for Nixpacks
3. **Procfile** - Process configuration
4. **requirements.txt** - Python dependencies
5. **package.json** - Node.js dependencies

## Build Process

Railway will automatically:

1. **Setup Phase**
   - Install Python 3.11
   - Install Node.js 18
   - Setup build environment

2. **Install Phase**
   - Install Python dependencies: `pip install -r requirements.txt`
   - Install Node.js dependencies: `npm ci`

3. **Build Phase**
   - Build frontend: `npm run build`
   - Create optimized production bundle

4. **Start Phase**
   - Start FastAPI server with Uvicorn
   - Serve static frontend files
   - Enable WebSocket support

## Port Configuration

Railway automatically assigns a port via the `$PORT` environment variable. The application is configured to use this port automatically.

## Health Checks

Railway will monitor your application health via:
- HTTP endpoint: `GET /health`
- Expected response: 200 OK

## Logs and Monitoring

Access logs via Railway dashboard:
1. Go to your project
2. Click on "Deployments"
3. View real-time logs

## Troubleshooting

### Build Failures

**Issue:** Python dependencies fail to install
```bash
# Solution: Check requirements.txt for incompatible versions
# Railway uses Python 3.11, ensure compatibility
```

**Issue:** Frontend build fails
```bash
# Solution: Check Node.js version compatibility
# Railway uses Node.js 18, ensure package.json compatibility
```

### Runtime Issues

**Issue:** Application crashes on startup
```bash
# Check logs in Railway dashboard
# Common causes:
# - Missing environment variables
# - Invalid API keys
# - Port binding issues
```

**Issue:** MetaGPT agents not working
```bash
# Verify environment variables:
# - OPENAI_API_KEY or ANTHROPIC_API_KEY is set
# - METAGPT_WORKSPACE is writable
# - Check logs for MetaGPT initialization errors
```

**Issue:** E2B sandbox creation fails
```bash
# Verify:
# - E2B_API_KEY is valid
# - E2B account has sufficient quota
# - Check E2B dashboard for sandbox status
```

### WebSocket Connection Issues

**Issue:** WebSocket connections fail
```bash
# Ensure:
# - ENABLE_WEBSOCKETS=true
# - WS_MAX_CONNECTIONS is not exceeded
# - Check Railway logs for WebSocket errors
```

## Scaling

Railway supports automatic scaling:

1. **Vertical Scaling**
   - Upgrade Railway plan for more resources
   - Increase memory and CPU allocation

2. **Horizontal Scaling**
   - Note: WebSocket support requires sticky sessions
   - Use single worker for WebSocket compatibility

## Cost Optimization

1. **Resource Limits**
   - Set `MAX_CONCURRENT_SESSIONS` to control load
   - Set `E2B_MAX_SANDBOXES` to limit sandbox usage
   - Configure `SESSION_TIMEOUT` to cleanup inactive sessions

2. **E2B Sandbox Management**
   - Sandboxes auto-cleanup after 2 hours of inactivity
   - Monitor E2B usage in dashboard
   - Set appropriate timeouts

## Security Best Practices

1. **Environment Variables**
   - Never commit API keys to repository
   - Use Railway's environment variable management
   - Rotate keys regularly

2. **CORS Configuration**
   - Set `CORS_ORIGINS` to your domain in production
   - Don't use `*` in production

3. **Secret Key**
   - Generate strong random `SECRET_KEY`
   - Use: `openssl rand -hex 32`

4. **Rate Limiting**
   - Configure `RATE_LIMIT_REQUESTS` appropriately
   - Monitor for abuse

## Production Checklist

Before going to production:

- [ ] All environment variables configured
- [ ] API keys validated and working
- [ ] CORS_ORIGINS set to production domain
- [ ] Strong SECRET_KEY generated
- [ ] DEBUG=false
- [ ] LOG_LEVEL=INFO or WARNING
- [ ] Health check endpoint responding
- [ ] WebSocket connections tested
- [ ] MetaGPT agents tested
- [ ] E2B sandbox creation tested
- [ ] Rate limiting configured
- [ ] Monitoring setup in Railway dashboard

## Support

For issues:
- **Railway Support:** [railway.app/help](https://railway.app/help)
- **MetaGPT Issues:** [github.com/FoundationAgents/MetaGPT/issues](https://github.com/FoundationAgents/MetaGPT/issues)
- **E2B Support:** [e2b.dev/docs](https://e2b.dev/docs)

## Architecture on Railway

```
Railway Service
├── FastAPI Backend (Port $PORT)
│   ├── API Endpoints (/api/v1/*)
│   ├── WebSocket Server (/ws/*)
│   ├── MetaGPT Integration
│   │   ├── Software Company
│   │   ├── Multi-Agent Orchestration
│   │   └── Artifact Generation
│   └── E2B Sandbox Service
│       ├── Sandbox Creation
│       ├── Code Execution
│       └── Live Preview
└── Static Frontend (/)
    ├── React Application
    ├── Real-time Updates
    └── Artifact Viewer
```

## Performance

Expected performance on Railway:
- **Cold start:** 10-15 seconds
- **API response:** 100-300ms
- **MetaGPT generation:** 2-5 minutes (depends on complexity)
- **E2B sandbox creation:** 5-10 seconds
- **WebSocket latency:** <100ms

## Next Steps

After successful deployment:

1. Test the application thoroughly
2. Monitor logs for errors
3. Set up custom domain (optional)
4. Configure SSL/TLS (automatic on Railway)
5. Set up monitoring and alerts
6. Document your specific use cases
7. Share feedback and improvements

Your application is now live on Railway! 🚀
