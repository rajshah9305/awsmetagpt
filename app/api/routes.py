"""
Clean API routes with proper separation of concerns
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends, Query
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.models.schemas import (
    GenerationRequest, GenerationResponse, HealthCheck, 
    GeneratedArtifact, SessionStatus
)
from app.core.exceptions import MetaGPTSystemException
from app.core.logging import get_logger
from app.core.config import settings
from .dependencies import get_validated_request, get_services, check_system_health
from .middleware import error_handler

logger = get_logger(__name__)
router = APIRouter()


# Generation endpoints
@router.post("/generate", response_model=GenerationResponse)
async def generate_app(
    gen_request: GenerationRequest,
    background_tasks: BackgroundTasks,
    request_data: dict = Depends(get_validated_request),
    services: dict = Depends(get_services),
    _health: None = Depends(check_system_health),
):
    """Generate an application using MetaGPT agents"""
    request_id = request_data.get('request_id')
    logger.info(f"Received generation request {request_id} for app type: {gen_request.app_type}")

    try:
        orchestrator = services['orchestrator']
        
        # Create session
        session_id = await orchestrator.create_session(
            request=gen_request,
            client_id=request_id
        )
        
        # Construct WebSocket URL
        ws_protocol = "wss" if not settings.DEBUG else "ws"
        # Access FastAPI Request object from request_data
        http_request = request_data.get('request')
        ws_host = http_request.headers.get('host', 'localhost:8000') if http_request else 'localhost:8000'
        websocket_url = f"{ws_protocol}://{ws_host}/ws/{request_id}"
        
        logger.info(f"Successfully created session {session_id} for request {request_id}")
        return GenerationResponse(
            generation_id=session_id,
            status="initializing",
            message="Generation started successfully",
            progress=0,
            websocket_url=websocket_url,
            estimated_completion=None,
            active_agents=[role.value for role in gen_request.active_agents]
        )
        
    except MetaGPTSystemException as e:
        logger.error(f"Generation failed for request {request_id}: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in generation for request {request_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/generate/{generation_id}/status", response_model=SessionStatus)
async def get_generation_status(
    generation_id: str,
    services: dict = Depends(get_services)
):
    """Get generation status"""
    logger.debug(f"Getting status for generation {generation_id}")
    try:
        orchestrator = services['orchestrator']
        status = orchestrator.get_session_status(generation_id)
        
        if not status:
            logger.warning(f"Generation session {generation_id} not found")
            raise HTTPException(status_code=404, detail="Generation not found")
        
        return SessionStatus(**status)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting status for generation {generation_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/generate/{generation_id}/artifacts", response_model=List[GeneratedArtifact])
async def get_generation_artifacts(
    generation_id: str,
    services: dict = Depends(get_services)
):
    """Get generated artifacts"""
    try:
        orchestrator = services['orchestrator']
        artifacts = orchestrator.get_session_artifacts(generation_id)
        return [GeneratedArtifact(**artifact) for artifact in artifacts]
    except Exception as e:
        logger.error(f"Error getting artifacts: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/generate/{generation_id}/artifact/{artifact_name:path}")
async def get_specific_artifact(
    generation_id: str,
    artifact_name: str,
    services: dict = Depends(get_services)
):
    """Get a specific artifact by name"""
    try:
        orchestrator = services['orchestrator']
        artifacts = orchestrator.get_session_artifacts(generation_id)
        artifact = next((a for a in artifacts if a.get('name') == artifact_name), None)
        if not artifact:
            raise HTTPException(status_code=404, detail="Artifact not found")
        return artifact
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting artifact: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/generate/{generation_id}")
async def cancel_generation(
    generation_id: str,
    services: dict = Depends(get_services)
):
    """Cancel a running generation"""
    try:
        orchestrator = services['orchestrator']
        success = orchestrator.cancel_session(generation_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Generation not found or cannot be cancelled")
        
        return {"message": "Generation cancelled successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling generation: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# E2B Sandbox endpoints
@router.post("/e2b/sandbox/{generation_id}/create")
async def create_sandbox(
    generation_id: str,
    template: str = Query(default="base", description="Sandbox template"),
    services: dict = Depends(get_services)
):
    """Create E2B sandbox for generation"""
    try:
        e2b_service = services['e2b_service']
        sandbox_id = await e2b_service.create_sandbox(generation_id, template)
        
        return {
            "success": True,
            "sandbox_id": sandbox_id,
            "message": "Sandbox created successfully"
        }
        
    except MetaGPTSystemException as e:
        logger.error(f"Sandbox creation failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error creating sandbox: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/e2b/sandbox/{generation_id}/files")
async def write_sandbox_files(
    generation_id: str,
    artifacts: List[Dict[str, Any]],
    services: dict = Depends(get_services)
):
    """Write files to sandbox"""
    try:
        e2b_service = services['e2b_service']
        result = await e2b_service.write_files(generation_id, artifacts)
        
        return result
        
    except MetaGPTSystemException as e:
        logger.error(f"File write failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error writing files: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/e2b/sandbox/{generation_id}/run")
async def run_sandbox_application(
    generation_id: str,
    command: Optional[str] = None,
    services: dict = Depends(get_services)
):
    """Run application in sandbox"""
    try:
        e2b_service = services['e2b_service']
        result = await e2b_service.run_application(generation_id, command)
        
        return result
        
    except MetaGPTSystemException as e:
        logger.error(f"Application run failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error running application: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/e2b/sandbox/{generation_id}/stop")
async def stop_sandbox_application(
    generation_id: str,
    services: dict = Depends(get_services)
):
    """Stop application in sandbox"""
    try:
        e2b_service = services['e2b_service']
        success = await e2b_service.stop_application(generation_id)
        
        return {
            "success": success,
            "message": "Application stopped" if success else "No running application found"
        }
        
    except Exception as e:
        logger.error(f"Error stopping application: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/e2b/sandbox/{generation_id}/logs")
async def get_sandbox_logs(
    generation_id: str,
    lines: int = Query(default=100, ge=1, le=1000, description="Number of log lines"),
    services: dict = Depends(get_services)
):
    """Get sandbox logs"""
    try:
        e2b_service = services['e2b_service']
        logs = await e2b_service.get_logs(generation_id, lines)
        
        return logs
        
    except MetaGPTSystemException as e:
        logger.error(f"Log retrieval failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error getting logs: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/e2b/sandbox/{generation_id}/info")
async def get_sandbox_info(
    generation_id: str,
    services: dict = Depends(get_services)
):
    """Get sandbox information"""
    try:
        e2b_service = services['e2b_service']
        info = e2b_service.get_sandbox_info(generation_id)
        
        if not info:
            raise HTTPException(status_code=404, detail="Sandbox not found")
        
        return info
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting sandbox info: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/e2b/sandbox/{generation_id}")
async def cleanup_sandbox(
    generation_id: str,
    services: dict = Depends(get_services)
):
    """Clean up sandbox"""
    try:
        e2b_service = services['e2b_service']
        success = await e2b_service.cleanup_session(generation_id)
        
        return {
            "success": success,
            "message": "Sandbox cleaned up" if success else "Sandbox not found"
        }
        
    except Exception as e:
        logger.error(f"Error cleaning up sandbox: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# System endpoints
@router.get("/health", response_model=HealthCheck)
async def health_check(services: dict = Depends(get_services)):
    """System health check"""
    try:
        orchestrator = services['orchestrator']
        e2b_service = services['e2b_service']
        bedrock_client = services['bedrock_client']
        
        # Check service availability
        bedrock_available = bedrock_client.client is not None
        
        # Get system statistics
        orchestrator_stats = orchestrator.get_statistics()
        e2b_stats = e2b_service.get_statistics()
        
        return HealthCheck(
            status="healthy",
            service="MetaGPT + E2B Integration System",
            timestamp=datetime.now(),
            aws_bedrock_available=bedrock_available,
            metagpt_configured=True,  # Assume configured if we got this far
            e2b_configured=True,      # Assume configured if we got this far
            services={
                "orchestrator": orchestrator_stats,
                "e2b": e2b_stats
            },
            capacity={
                "active_sessions": orchestrator_stats.get('status_distribution', {}).get('running', 0),
                "max_sessions": 10,  # Default value since we simplified settings
                "active_sandboxes": e2b_stats.get('total_sandboxes', 0)
            }
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthCheck(
            status="unhealthy",
            service="MetaGPT + E2B Integration System",
            timestamp=datetime.now(),
            aws_bedrock_available=False,
            metagpt_configured=False,
            e2b_configured=False
        )


@router.get("/models/bedrock")
async def get_available_bedrock_models():
    """Get available Bedrock models"""
    try:
        from app.models.schemas import BedrockModel
        
        provider_names = {
            "us.amazon": "Amazon",
            "us.meta": "Meta",
            "us.anthropic": "Anthropic",
            "amazon": "Amazon",
            "meta": "Meta",
            "anthropic": "Anthropic",
        }
        
        model_display_names = {
            "NOVA_PRO": "Nova Pro",
            "NOVA_LITE": "Nova Lite",
            "NOVA_MICRO": "Nova Micro",
            "LLAMA_33_70B": "Llama 3.3 70B",
            "LLAMA_32_90B": "Llama 3.2 90B",
            "LLAMA_32_11B": "Llama 3.2 11B",
            "CLAUDE_SONNET_4": "Claude Sonnet 4",
            "CLAUDE_HAIKU_45": "Claude Haiku 4.5",
            "CLAUDE_OPUS_4": "Claude Opus 4",
        }
        
        models = []
        try:
            for model in BedrockModel:
                parts = model.value.split(".")
                prefix = ".".join(parts[:2]) if len(parts) >= 2 else parts[0]
                provider = provider_names.get(prefix, parts[0].title())
                display_name = model_display_names.get(model.name, model.name.replace("_", " ").title())
                models.append({
                    "id": model.value,
                    "name": display_name,
                    "provider": provider
                })
        except Exception as enum_err:
            logger.error(f"Error iterating BedrockModel enum: {enum_err}")
            # Fallback to a few default models if enum iteration fails
            models = [
                {"id": "us.amazon.nova-pro-v1:0", "name": "Nova Pro", "provider": "Amazon"},
                {"id": "us.anthropic.claude-sonnet-4-20250514-v1:0", "name": "Claude Sonnet 4", "provider": "Anthropic"}
            ]

        if not models:
            logger.warning("No models found in BedrockModel enum, using fallback")
            models = [
                {"id": "us.amazon.nova-pro-v1:0", "name": "Nova Pro", "provider": "Amazon"},
                {"id": "us.anthropic.claude-sonnet-4-20250514-v1:0", "name": "Claude Sonnet 4", "provider": "Anthropic"}
            ]
        
        logger.info(f"Returning {len(models)} available Bedrock models")
        return {
            "models": models,
            "current_model": settings.BEDROCK_MODEL
        }
        
    except Exception as e:
        logger.error(f"Error getting Bedrock models: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/agents/roles")
async def get_agent_roles_endpoint():
    """Get available agent roles"""
    try:
        from app.models.schemas import AgentRole
        
        role_descriptions = {
            AgentRole.PRODUCT_MANAGER: "Analyzes requirements, creates user stories, and defines product specifications",
            AgentRole.ARCHITECT: "Designs system architecture, selects tech stack, and creates technical specifications",
            AgentRole.PROJECT_MANAGER: "Creates project plans, manages timelines, and coordinates development activities",
            AgentRole.ENGINEER: "Implements application code following architecture and best practices",
            AgentRole.QA_ENGINEER: "Creates test strategies, writes test cases, and ensures quality standards",
            AgentRole.DEVOPS: "Designs infrastructure, CI/CD pipelines, and deployment configurations",
        }
        
        role_display_names = {
            AgentRole.PRODUCT_MANAGER: "Product Manager",
            AgentRole.ARCHITECT: "System Architect",
            AgentRole.PROJECT_MANAGER: "Project Manager",
            AgentRole.ENGINEER: "Software Engineer",
            AgentRole.QA_ENGINEER: "QA Engineer",
            AgentRole.DEVOPS: "DevOps Engineer",
        }
        
        roles = [
            {
                "id": role.value,
                "name": role_display_names.get(role, role.name.replace('_', ' ').title()),
                "description": role_descriptions.get(role, role.value.replace('_', ' ').title())
            }
            for role in AgentRole
        ]
        
        return {"roles": roles}
        
    except Exception as e:
        logger.error(f"Error getting agent roles: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


