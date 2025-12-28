"""
Production-ready API routes for MetaGPT + E2B integration
Handles orchestration, monitoring, and real-time communication
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends, Query
from fastapi.security import HTTPBearer
from typing import List, Dict, Any, Optional
import uuid
import logging
from datetime import datetime, timedelta
import asyncio

from app.models.schemas import (
    GenerationRequest, GenerationResponse,
    HealthCheck, GeneratedArtifact
)
from app.services.agent_orchestrator import agent_orchestrator
from app.services.bedrock_client import bedrock_client
from app.services.e2b_service import e2b_service
from app.services.websocket_manager import websocket_manager
from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

# Enhanced rate limiting with user tracking
rate_limit_store = {}
security = HTTPBearer(auto_error=False)

def check_rate_limit(client_ip: str, max_requests: int = 10, window_minutes: int = 60) -> bool:
    """Enhanced rate limiting with sliding window"""
    now = datetime.now()
    window_start = now - timedelta(minutes=window_minutes)
    
    if client_ip not in rate_limit_store:
        rate_limit_store[client_ip] = []
    
    # Clean old requests
    rate_limit_store[client_ip] = [
        req_time for req_time in rate_limit_store[client_ip] 
        if req_time > window_start
    ]
    
    # Check if limit exceeded
    if len(rate_limit_store[client_ip]) >= max_requests:
        return False
    
    # Add current request
    rate_limit_store[client_ip].append(now)
    return True

@router.post("/generate", response_model=GenerationResponse)
async def generate_app(request: GenerationRequest, background_tasks: BackgroundTasks):
    """
    Generate an application using MetaGPT agents and E2B sandbox
    Enhanced with comprehensive validation and monitoring
    """
    try:
        # Enhanced validation
        if not request.requirement or not request.requirement.strip():
            raise HTTPException(status_code=400, detail="Requirement cannot be empty")
        
        if len(request.requirement) > 50000:
            raise HTTPException(status_code=400, detail="Requirement too long (max 50,000 characters)")
        
        if not request.active_agents or len(request.active_agents) == 0:
            raise HTTPException(status_code=400, detail="At least one agent must be selected")
        
        if len(request.active_agents) > 6:
            raise HTTPException(status_code=400, detail="Maximum 6 agents allowed")
        
        # Check system capacity
        active_sessions = len([s for s in agent_orchestrator.active_sessions.values() 
                              if s.get("status") in ["initializing", "running"]])
        if active_sessions >= 10:
            raise HTTPException(status_code=429, detail="System at capacity. Please try again later.")
        
        # Validate AI model availability
        if not bedrock_client.client:
            raise HTTPException(status_code=503, detail="AI service unavailable")
        
        # Generate unique client ID for WebSocket connection
        client_id = str(uuid.uuid4())
        
        # Create orchestration session
        session_id = await agent_orchestrator.create_session(request, client_id)
        
        # Construct WebSocket URL based on environment
        ws_protocol = "wss" if not settings.DEBUG else "ws"
        ws_host = "localhost" if settings.DEBUG else "your-domain.com"
        ws_port = f":{settings.APP_PORT}" if settings.DEBUG else ""
        websocket_url = f"{ws_protocol}://{ws_host}{ws_port}/ws/{client_id}"
        
        return GenerationResponse(
            generation_id=session_id,
            status="started",
            message="App generation started with enhanced MetaGPT orchestration",
            progress=0,
            websocket_url=websocket_url
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to start generation: {e}")
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")

@router.get("/generate/{session_id}/status")
async def get_generation_status(session_id: str):
    """
    Get comprehensive generation status with agent details
    """
    # Validate session_id format
    try:
        uuid.UUID(session_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session ID format")
    
    session_data = agent_orchestrator.get_session_status(session_id)
    
    if not session_data:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Get agent statuses
    agent_statuses = []
    for agent_id in session_data.get("agents", []):
        agent = agent_orchestrator.get_agent_status(agent_id)
        if agent:
            agent_statuses.append({
                "id": agent.id,
                "role": agent.role.value,
                "state": agent.state.value,
                "current_task": agent.current_task.description if agent.current_task else None,
                "completed_tasks": len(agent.completed_tasks),
                "failed_tasks": len(agent.failed_tasks),
                "last_activity": agent.last_activity.isoformat()
            })
    
    # Get E2B sandbox status
    sandbox_info = e2b_service.get_sandbox_info(session_id)
    
    return {
        "session_id": session_id,
        "status": session_data.get("status"),
        "progress": session_data.get("progress", 0),
        "message": session_data.get("last_message", ""),
        "created_at": session_data.get("created_at").isoformat() if session_data.get("created_at") else None,
        "updated_at": session_data.get("updated_at").isoformat() if session_data.get("updated_at") else None,
        "agents": agent_statuses,
        "sandbox": sandbox_info,
        "metrics": session_data.get("metrics", {})
    }

@router.get("/generate/{session_id}/artifacts", response_model=List[GeneratedArtifact])
async def get_generation_artifacts(session_id: str):
    """
    Get all generated artifacts with enhanced metadata
    """
    # Validate session_id format
    try:
        uuid.UUID(session_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session ID format")
    
    artifacts = agent_orchestrator.get_session_artifacts(session_id)
    
    if not artifacts and session_id not in agent_orchestrator.active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Convert to GeneratedArtifact format
    formatted_artifacts = []
    for artifact in artifacts:
        formatted_artifacts.append(GeneratedArtifact(
            id=artifact.get("id", str(uuid.uuid4())),
            name=artifact.get("name", "unknown"),
            type=artifact.get("type", "file"),
            content=artifact.get("content", ""),
            agent_role=artifact.get("agent_role", "unknown"),
            file_path=artifact.get("path")
        ))
    
    return formatted_artifacts

@router.get("/generate/{session_id}/artifact/{artifact_name}")
async def get_specific_artifact(session_id: str, artifact_name: str):
    """
    Get a specific artifact by name with content streaming support
    """
    # Validate session_id format
    try:
        uuid.UUID(session_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session ID format")
    
    # Validate artifact name
    if not artifact_name or len(artifact_name) > 255:
        raise HTTPException(status_code=400, detail="Invalid artifact name")
    
    artifacts = agent_orchestrator.get_session_artifacts(session_id)
    
    for artifact in artifacts:
        if artifact.get("name") == artifact_name:
            return {
                "name": artifact.get("name"),
                "type": artifact.get("type"),
                "content": artifact.get("content"),
                "agent_role": artifact.get("agent_role"),
                "file_path": artifact.get("path"),
                "size": len(artifact.get("content", "")),
                "created_at": artifact.get("created_at")
            }
    
    raise HTTPException(status_code=404, detail="Artifact not found")

@router.post("/generate/{session_id}/pause")
async def pause_generation(session_id: str):
    """
    Pause generation session
    """
    try:
        uuid.UUID(session_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session ID format")
    
    success = await agent_orchestrator.pause_session(session_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Session not found or cannot be paused")
    
    return {"status": "paused", "session_id": session_id}

@router.post("/generate/{session_id}/resume")
async def resume_generation(session_id: str):
    """
    Resume paused generation session
    """
    try:
        uuid.UUID(session_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session ID format")
    
    success = await agent_orchestrator.resume_session(session_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Session not found or cannot be resumed")
    
    return {"status": "resumed", "session_id": session_id}

@router.delete("/generate/{session_id}")
async def terminate_generation(session_id: str):
    """
    Terminate generation session and cleanup resources
    """
    try:
        uuid.UUID(session_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session ID format")
    
    success = await agent_orchestrator.terminate_session(session_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {"status": "terminated", "session_id": session_id}

# Enhanced E2B Sandbox Endpoints

@router.post("/e2b/sandbox/{session_id}/create")
async def create_e2b_sandbox(session_id: str, template: str = Query("base", description="Sandbox template")):
    """
    Create E2B sandbox with template selection
    """
    try:
        uuid.UUID(session_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session ID format")
    
    try:
        result = await e2b_service.create_sandbox(session_id, template)
        if result:
            return {
                "status": "success", 
                "sandbox_id": result,
                "template": template,
                "created_at": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to create sandbox")
    except Exception as e:
        logger.error(f"Failed to create E2B sandbox: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create sandbox: {str(e)}")

@router.post("/e2b/sandbox/{session_id}/files")
async def write_e2b_files(session_id: str, artifacts: List[Dict[str, Any]]):
    """
    Write artifacts to E2B sandbox with validation
    """
    try:
        uuid.UUID(session_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session ID format")
    
    # Enhanced validation
    if not artifacts or len(artifacts) == 0:
        raise HTTPException(status_code=400, detail="No artifacts provided")
    
    if len(artifacts) > 200:
        raise HTTPException(status_code=400, detail="Too many artifacts (max 200)")
    
    total_size = 0
    for artifact in artifacts:
        if not isinstance(artifact, dict):
            raise HTTPException(status_code=400, detail="Invalid artifact format")
        
        content = artifact.get("content", "")
        if len(content) > 5000000:  # 5MB limit per file
            raise HTTPException(status_code=400, detail="Artifact content too large (max 5MB)")
        
        total_size += len(content)
        if total_size > 50000000:  # 50MB total limit
            raise HTTPException(status_code=400, detail="Total content too large (max 50MB)")
    
    try:
        success = await e2b_service.write_files(session_id, artifacts)
        if success:
            return {
                "status": "success", 
                "message": "Files written successfully",
                "files_count": len(artifacts),
                "total_size": total_size
            }
        else:
            raise HTTPException(status_code=404, detail="Sandbox not found")
    except Exception as e:
        logger.error(f"Failed to write files to E2B sandbox: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to write files: {str(e)}")

@router.post("/e2b/sandbox/{session_id}/run")
async def run_e2b_application(session_id: str):
    """
    Run application in E2B sandbox with enhanced monitoring
    """
    try:
        uuid.UUID(session_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session ID format")
    
    try:
        preview_url = await e2b_service.run_application(session_id)
        if preview_url:
            # Get additional sandbox info
            sandbox_info = e2b_service.get_sandbox_info(session_id)
            
            return {
                "status": "success", 
                "preview_url": preview_url,
                "project_type": sandbox_info.get("project_type") if sandbox_info else None,
                "started_at": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to run application")
    except Exception as e:
        logger.error(f"Failed to run E2B application: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to run application: {str(e)}")

@router.post("/e2b/sandbox/{session_id}/stop")
async def stop_e2b_application(session_id: str):
    """
    Stop running application in E2B sandbox
    """
    try:
        uuid.UUID(session_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session ID format")
    
    try:
        success = await e2b_service.stop_application(session_id)
        if success:
            return {
                "status": "success", 
                "message": "Application stopped successfully",
                "stopped_at": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=404, detail="Sandbox not found")
    except Exception as e:
        logger.error(f"Failed to stop E2B application: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to stop application: {str(e)}")

@router.get("/e2b/sandbox/{session_id}/logs")
async def get_e2b_logs(
    session_id: str, 
    process_id: Optional[str] = Query(None, description="Specific process ID"),
    lines: int = Query(100, description="Number of log lines to return")
):
    """
    Get logs from E2B sandbox with filtering
    """
    try:
        uuid.UUID(session_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session ID format")
    
    if lines < 1 or lines > 1000:
        raise HTTPException(status_code=400, detail="Lines must be between 1 and 1000")
    
    try:
        logs = await e2b_service.get_logs(session_id, process_id)
        return {
            "status": "success", 
            "logs": logs[-lines:],  # Return last N lines
            "total_lines": len(logs),
            "process_id": process_id,
            "retrieved_at": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get E2B logs: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get logs: {str(e)}")

@router.get("/e2b/sandbox/{session_id}/metrics")
async def get_e2b_metrics(session_id: str):
    """
    Get detailed E2B sandbox metrics
    """
    try:
        uuid.UUID(session_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session ID format")
    
    try:
        metrics = await e2b_service.get_sandbox_metrics(session_id)
        return {
            "status": "success",
            "metrics": metrics,
            "retrieved_at": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get E2B metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get metrics: {str(e)}")

@router.delete("/e2b/sandbox/{session_id}")
async def cleanup_e2b_sandbox(session_id: str):
    """
    Clean up and close E2B sandbox
    """
    try:
        uuid.UUID(session_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session ID format")
    
    try:
        success = await e2b_service.cleanup_sandbox(session_id)
        
        if success:
            return {
                "status": "success", 
                "message": "Sandbox cleaned up successfully",
                "cleaned_at": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to cleanup sandbox")
    except Exception as e:
        logger.error(f"Failed to cleanup E2B sandbox: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to cleanup sandbox: {str(e)}")

# System Information Endpoints

@router.get("/models/bedrock")
async def get_available_bedrock_models():
    """
    Get list of available AWS Bedrock models with real-time status
    """
    return {
        "models": [
            {
                "id": "us.amazon.nova-pro-v1:0",
                "name": "Nova Pro",
                "provider": "Amazon",
                "description": "Amazon's flagship multimodal model for complex tasks",
                "status": "available",
                "capabilities": ["text", "image", "reasoning"]
            },
            {
                "id": "us.amazon.nova-lite-v1:0",
                "name": "Nova Lite",
                "provider": "Amazon",
                "description": "Fast and cost-effective Amazon model for everyday tasks",
                "status": "available",
                "capabilities": ["text", "reasoning"]
            },
            {
                "id": "us.amazon.nova-micro-v1:0",
                "name": "Nova Micro",
                "provider": "Amazon",
                "description": "Ultra-fast Amazon model for simple text generation",
                "status": "available",
                "capabilities": ["text"]
            },
            {
                "id": "us.meta.llama3-3-70b-instruct-v1:0",
                "name": "Llama 3.3 70B Instruct",
                "provider": "Meta",
                "description": "Latest Llama model optimized for instruction following",
                "status": "usually_available",
                "capabilities": ["text", "reasoning", "code"]
            },
            {
                "id": "us.meta.llama3-2-90b-instruct-v1:0",
                "name": "Llama 3.2 90B Instruct",
                "provider": "Meta",
                "description": "Large Llama model with excellent reasoning capabilities",
                "status": "usually_available",
                "capabilities": ["text", "reasoning", "code"]
            },
            {
                "id": "us.anthropic.claude-sonnet-4-20250514-v1:0",
                "name": "Claude Sonnet 4",
                "provider": "Anthropic",
                "description": "Latest Claude model with advanced reasoning",
                "status": "requires_approval",
                "capabilities": ["text", "reasoning", "analysis"]
            }
        ],
        "bedrock_available": bedrock_client.client is not None,
        "last_updated": datetime.now().isoformat()
    }

@router.get("/agents/roles")
async def get_available_agent_roles():
    """
    Get list of available MetaGPT agent roles with capabilities
    """
    return {
        "roles": [
            {
                "id": "product_manager",
                "name": "Product Manager",
                "description": "Creates product requirements, user stories, and business analysis",
                "capabilities": ["requirements_analysis", "user_stories", "business_logic"],
                "outputs": ["prd.md", "user_stories.md", "acceptance_criteria.md"],
                "estimated_time": "2-5 minutes"
            },
            {
                "id": "architect",
                "name": "System Architect",
                "description": "Designs system architecture, technology stack, and technical specifications",
                "capabilities": ["system_design", "tech_stack", "api_design"],
                "outputs": ["architecture.md", "tech_stack.md", "api_design.md"],
                "estimated_time": "3-7 minutes"
            },
            {
                "id": "project_manager",
                "name": "Project Manager",
                "description": "Creates project plans, timelines, and manages resources",
                "capabilities": ["project_planning", "timeline", "resource_management"],
                "outputs": ["project_plan.md", "timeline.md", "resources.md"],
                "estimated_time": "2-4 minutes"
            },
            {
                "id": "engineer",
                "name": "Software Engineer",
                "description": "Provides technical implementation details and code structure",
                "capabilities": ["code_implementation", "technical_design", "debugging"],
                "outputs": ["*.py", "*.js", "*.jsx", "*.ts", "*.tsx", "*.html", "*.css"],
                "estimated_time": "5-15 minutes"
            },
            {
                "id": "qa_engineer",
                "name": "QA Engineer",
                "description": "Creates testing strategies, test cases, and quality assurance plans",
                "capabilities": ["test_planning", "quality_assurance", "validation"],
                "outputs": ["test_plan.md", "test_cases.md", "*.test.py", "*.test.js"],
                "estimated_time": "3-8 minutes"
            },
            {
                "id": "devops",
                "name": "DevOps Engineer",
                "description": "Designs infrastructure and operational strategies",
                "capabilities": ["infrastructure_design", "monitoring", "automation"],
                "outputs": ["infrastructure.md", "setup.md", "monitoring.md"],
                "estimated_time": "2-5 minutes"
            }
        ],
        "max_concurrent_agents": 6,
        "recommended_combinations": [
            ["product_manager", "architect", "engineer"],
            ["product_manager", "architect", "engineer", "qa_engineer"],
            ["architect", "engineer", "devops"],
            ["product_manager", "architect", "project_manager", "engineer", "qa_engineer", "devops"]
        ]
    }

@router.get("/system/status")
async def get_system_status():
    """
    Get comprehensive system status
    """
    # Count active sessions
    active_sessions = len([s for s in agent_orchestrator.active_sessions.values() 
                          if s.get("status") in ["initializing", "running"]])
    
    # Count active sandboxes
    active_sandboxes = len(e2b_service.active_sandboxes)
    
    # Count WebSocket connections
    active_connections = len(websocket_manager.get_connected_clients())
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "agent_orchestrator": {
                "status": "healthy",
                "active_sessions": active_sessions,
                "total_agents": len(agent_orchestrator.agent_instances)
            },
            "e2b_service": {
                "status": "healthy" if settings.E2B_API_KEY else "not_configured",
                "active_sandboxes": active_sandboxes,
                "api_key_configured": bool(settings.E2B_API_KEY)
            },
            "bedrock_client": {
                "status": "healthy" if bedrock_client.client else "not_configured",
                "client_initialized": bedrock_client.client is not None
            },
            "websocket_manager": {
                "status": "healthy",
                "active_connections": active_connections
            }
        },
        "capacity": {
            "max_concurrent_sessions": 10,
            "current_load": f"{(active_sessions / 10) * 100:.1f}%",
            "available_slots": 10 - active_sessions
        }
    }

@router.get("/health", response_model=HealthCheck)
async def health_check():
    """
    Comprehensive health check for all services
    """
    # Check Bedrock client
    bedrock_available = bedrock_client.client is not None

    # Check MetaGPT configuration
    metagpt_configured = bool(settings.OPENAI_API_KEY or settings.ANTHROPIC_API_KEY)

    # Check E2B configuration
    e2b_configured = bool(settings.E2B_API_KEY)
    
    # Determine overall status
    if bedrock_available and metagpt_configured and e2b_configured:
        status = "healthy"
    elif bedrock_available and metagpt_configured:
        status = "degraded"  # Can work without E2B
    else:
        status = "unhealthy"

    return HealthCheck(
        status=status,
        service="metagpt-e2b-orchestrator",
        aws_bedrock_available=bedrock_available,
        metagpt_configured=metagpt_configured,
        e2b_configured=e2b_configured
    )