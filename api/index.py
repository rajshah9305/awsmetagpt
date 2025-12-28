"""
Vercel-compatible API entry point for MetaGPT + Bedrock App Generator
Simplified version without heavy dependencies for serverless deployment
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Create FastAPI app
app = FastAPI(
    title="MetaGPT + AWS Bedrock App Generator API",
    description="Generate applications from natural language using MetaGPT agents and AWS Bedrock AI models",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "MetaGPT + AWS Bedrock App Generator API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "note": "This is a simplified API for Vercel deployment. For full functionality, deploy the complete application."
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy", 
        "service": "metagpt-bedrock-generator",
        "deployment": "vercel-simplified"
    }

@app.get("/api/v1/models/bedrock")
async def get_available_bedrock_models():
    """Get list of available AWS Bedrock models"""
    return {
        "models": [
            {
                "id": "us.amazon.nova-pro-v1:0",
                "name": "Nova Pro",
                "provider": "Amazon",
                "description": "Amazon's flagship multimodal model for complex tasks"
            },
            {
                "id": "us.amazon.nova-lite-v1:0",
                "name": "Nova Lite", 
                "provider": "Amazon",
                "description": "Fast and cost-effective Amazon model for everyday tasks"
            },
            {
                "id": "us.meta.llama3-3-70b-instruct-v1:0",
                "name": "Llama 3.3 70B Instruct",
                "provider": "Meta",
                "description": "Latest Llama model optimized for instruction following"
            }
        ]
    }

@app.get("/api/v1/agents/roles")
async def get_available_agent_roles():
    """Get list of available MetaGPT agent roles"""
    return {
        "roles": [
            {
                "id": "product_manager",
                "name": "Product Manager",
                "description": "Creates product requirements, user stories, and business analysis"
            },
            {
                "id": "architect",
                "name": "System Architect", 
                "description": "Designs system architecture, technology stack, and technical specifications"
            },
            {
                "id": "engineer",
                "name": "Software Engineer",
                "description": "Provides technical implementation details and code structure"
            }
        ]
    }

@app.post("/api/v1/generate")
async def generate_app_placeholder():
    """Placeholder for app generation - requires full deployment"""
    return {
        "error": "App generation requires the full deployment with MetaGPT and E2B integration",
        "message": "This is a simplified Vercel deployment. For full functionality, deploy using Docker or VPS",
        "full_deployment_guide": "https://github.com/rajshah9305/awsmetagpt/blob/main/DEPLOYMENT_GUIDE.md"
    }

# For Vercel deployment
handler = app
