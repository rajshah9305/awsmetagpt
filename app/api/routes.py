"""
API routes for the MetaGPT + Bedrock app generator
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Dict, Any, Optional
import uuid
import logging

from app.models.schemas import (
    GenerationRequest, GenerationResponse, GenerationResult,
    HealthCheck, GeneratedArtifact
)
from app.services.metagpt_service import metagpt_service
from app.services.bedrock_client import bedrock_client
from app.services.e2b_service import e2b_service
from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/generate", response_model=GenerationResponse)
async def generate_app(request: GenerationRequest, background_tasks: BackgroundTasks):
    """
    Generate an application from natural language requirements
    """
    try:
        # Validate request
        if not request.requirement.strip():
            raise HTTPException(status_code=400, detail="Requirement cannot be empty")
        
        # Generate unique client ID for WebSocket connection
        client_id = str(uuid.uuid4())
        
        # Start generation process
        generation_id = await metagpt_service.generate_app(request, client_id)
        
        return GenerationResponse(
            generation_id=generation_id,
            status="started",
            message="App generation started. Connect to WebSocket for real-time updates.",
            progress=0,
            websocket_url=f"ws://localhost:{settings.APP_PORT}/ws/{client_id}"
        )
        
    except Exception as e:
        logger.error(f"Failed to start generation: {e}")
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")

@router.get("/generate/{generation_id}/status")
async def get_generation_status(generation_id: str):
    """
    Get the current status of a generation process
    """
    status = metagpt_service.get_generation_status(generation_id)
    
    if not status:
        raise HTTPException(status_code=404, detail="Generation not found")
    
    return {
        "generation_id": generation_id,
        "status": status.get("status"),
        "progress": status.get("progress", 0),
        "message": status.get("last_message", ""),
        "created_at": status.get("created_at"),
        "updated_at": status.get("updated_at")
    }

@router.get("/generate/{generation_id}/artifacts", response_model=List[GeneratedArtifact])
async def get_generation_artifacts(generation_id: str):
    """
    Get all generated artifacts for a specific generation
    """
    artifacts = metagpt_service.get_generation_artifacts(generation_id)
    
    if not artifacts and generation_id not in metagpt_service.active_generations:
        raise HTTPException(status_code=404, detail="Generation not found")
    
    return artifacts

@router.get("/generate/{generation_id}/artifact/{artifact_name}")
async def get_specific_artifact(generation_id: str, artifact_name: str):
    """
    Get a specific artifact by name
    """
    artifacts = metagpt_service.get_generation_artifacts(generation_id)
    
    for artifact in artifacts:
        if artifact.name == artifact_name:
            return {
                "name": artifact.name,
                "type": artifact.type,
                "content": artifact.content,
                "agent_role": artifact.agent_role
            }
    
    raise HTTPException(status_code=404, detail="Artifact not found")

@router.get("/models/bedrock")
async def get_available_bedrock_models():
    """
    Get list of available AWS Bedrock models
    """
    return {
        "models": [
            {
                "id": "us.amazon.nova-pro-v1:0",
                "name": "Nova Pro",
                "provider": "Amazon",
                "description": "Amazon's flagship multimodal model for complex tasks (Available by default)"
            },
            {
                "id": "us.amazon.nova-lite-v1:0",
                "name": "Nova Lite",
                "provider": "Amazon",
                "description": "Fast and cost-effective Amazon model for everyday tasks (Available by default)"
            },
            {
                "id": "us.amazon.nova-micro-v1:0",
                "name": "Nova Micro",
                "provider": "Amazon",
                "description": "Ultra-fast Amazon model for simple text generation (Available by default)"
            },
            {
                "id": "us.meta.llama3-3-70b-instruct-v1:0",
                "name": "Llama 3.3 70B Instruct",
                "provider": "Meta",
                "description": "Latest Llama model optimized for instruction following (Usually available)"
            },
            {
                "id": "us.meta.llama3-2-90b-instruct-v1:0",
                "name": "Llama 3.2 90B Instruct",
                "provider": "Meta",
                "description": "Large Llama model with excellent reasoning capabilities (Usually available)"
            },
            {
                "id": "us.meta.llama3-2-11b-instruct-v1:0",
                "name": "Llama 3.2 11B Instruct",
                "provider": "Meta",
                "description": "Smaller, faster Llama model for quick responses (Usually available)"
            },
            {
                "id": "us.anthropic.claude-sonnet-4-20250514-v1:0",
                "name": "Claude Sonnet 4",
                "provider": "Anthropic",
                "description": "Latest Claude model (Requires approval - fill out use case form)"
            },
            {
                "id": "us.anthropic.claude-haiku-4-5-20251001-v1:0",
                "name": "Claude Haiku 4.5",
                "provider": "Anthropic",
                "description": "Fastest Claude model (Requires approval - fill out use case form)"
            },
            {
                "id": "us.anthropic.claude-opus-4-20250514-v1:0",
                "name": "Claude Opus 4",
                "provider": "Anthropic",
                "description": "Most powerful Claude model (Requires approval - fill out use case form)"
            }
        ]
    }

@router.get("/agents/roles")
async def get_available_agent_roles():
    """
    Get list of available MetaGPT agent roles
    """
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
                "id": "project_manager",
                "name": "Project Manager",
                "description": "Creates project plans, timelines, and manages resources"
            },
            {
                "id": "engineer",
                "name": "Software Engineer",
                "description": "Provides technical implementation details and code structure"
            },
            {
                "id": "qa_engineer",
                "name": "QA Engineer",
                "description": "Creates testing strategies, test cases, and quality assurance plans"
            },
            {
                "id": "devops",
                "name": "DevOps Engineer",
                "description": "Designs deployment, infrastructure, and operational strategies"
            }
        ]
    }

@router.post("/e2b/sandbox/{generation_id}/create")
async def create_e2b_sandbox(generation_id: str):
    """
    Create an E2B sandbox for a specific generation
    """
    try:
        result = await e2b_service.create_sandbox(generation_id)
        if result:
            return {"status": "success", "sandbox_id": result}
        else:
            raise HTTPException(status_code=500, detail="Failed to create sandbox")
    except Exception as e:
        logger.error(f"Failed to create E2B sandbox: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create sandbox: {str(e)}")

@router.post("/e2b/sandbox/{generation_id}/files")
async def write_e2b_files(generation_id: str, artifacts: List[Dict[str, Any]]):
    """
    Write artifacts to the E2B sandbox
    """
    try:
        success = await e2b_service.write_files(generation_id, artifacts)
        if success:
            return {"status": "success", "message": "Files written successfully"}
        else:
            raise HTTPException(status_code=404, detail="Sandbox not found")
    except Exception as e:
        logger.error(f"Failed to write files to E2B sandbox: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to write files: {str(e)}")

@router.post("/e2b/sandbox/{generation_id}/run")
async def run_e2b_application(generation_id: str):
    """
    Run the application in the E2B sandbox
    """
    try:
        preview_url = await e2b_service.run_application(generation_id)
        if preview_url:
            return {"status": "success", "preview_url": preview_url}
        else:
            raise HTTPException(status_code=500, detail="Failed to run application")
    except Exception as e:
        logger.error(f"Failed to run E2B application: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to run application: {str(e)}")

@router.post("/e2b/sandbox/{generation_id}/stop")
async def stop_e2b_application(generation_id: str):
    """
    Stop the running application in the E2B sandbox
    """
    try:
        success = await e2b_service.stop_application(generation_id)
        if success:
            return {"status": "success", "message": "Application stopped successfully"}
        else:
            raise HTTPException(status_code=404, detail="Sandbox not found")
    except Exception as e:
        logger.error(f"Failed to stop E2B application: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to stop application: {str(e)}")

@router.get("/e2b/sandbox/{generation_id}/logs")
async def get_e2b_logs(generation_id: str):
    """
    Get logs from the E2B sandbox
    """
    try:
        logs = await e2b_service.get_logs(generation_id)
        return {"status": "success", "logs": logs}
    except Exception as e:
        logger.error(f"Failed to get E2B logs: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get logs: {str(e)}")

@router.delete("/e2b/sandbox/{generation_id}")
async def cleanup_e2b_sandbox(generation_id: str):
    """
    Clean up and close the E2B sandbox
    """
    try:
        success = await e2b_service.cleanup_sandbox(generation_id)
        if success:
            return {"status": "success", "message": "Sandbox cleaned up successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to cleanup sandbox")
    except Exception as e:
        logger.error(f"Failed to cleanup E2B sandbox: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to cleanup sandbox: {str(e)}")

@router.get("/health", response_model=HealthCheck)
async def health_check():
    """
    Comprehensive health check for all services
    """
    # Check if Bedrock client is initialized
    bedrock_available = bedrock_client.client is not None

    # Check MetaGPT configuration
    metagpt_configured = bool(settings.METAGPT_API_KEY)

    # Check E2B configuration
    e2b_configured = bool(settings.E2B_API_KEY)

    return HealthCheck(
        status="healthy" if bedrock_available else "degraded",
        service="metagpt-bedrock-generator",
        aws_bedrock_available=bedrock_available,
        metagpt_configured=metagpt_configured,
        e2b_configured=e2b_configured
    )