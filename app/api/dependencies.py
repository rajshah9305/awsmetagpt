"""
API dependencies for dependency injection
"""

import uuid
from typing import Optional
from fastapi import Request, HTTPException, Depends, status

from app.core.config import settings
from app.core.exceptions import RateLimitException
from app.services.orchestration import AgentOrchestrator
from app.services.e2b_service import E2BService
from app.services.bedrock_client import BedrockClient
from .middleware import rate_limiter, request_validator


def get_client_ip(request: Request) -> str:
    """Get client IP address"""
    # Check for forwarded headers first
    forwarded_for = request.headers.get('x-forwarded-for')
    if forwarded_for:
        return forwarded_for.split(',')[0].strip()
    
    real_ip = request.headers.get('x-real-ip')
    if real_ip:
        return real_ip
    
    # Fallback to direct connection
    return request.client.host if request.client else 'unknown'


def get_request_id() -> str:
    """Generate unique request ID"""
    return str(uuid.uuid4())


def check_rate_limit(request: Request) -> str:
    """Check rate limiting for request"""
    client_ip = get_client_ip(request)
    
    if not rate_limiter.check_rate_limit(client_ip):
        rate_info = rate_limiter.get_rate_limit_info(client_ip)
        raise RateLimitException(
            f"Rate limit exceeded. Try again in {settings.RATE_LIMIT_WINDOW} seconds",
            details=rate_info
        )
    
    return client_ip


def validate_request(request: Request) -> None:
    """Validate incoming request"""
    # Validate content length
    request_validator.validate_content_length(request)
    
    # Validate content type for POST/PUT requests
    if request.method in ['POST', 'PUT', 'PATCH']:
        request_validator.validate_content_type(request)
    
    # Validate user agent
    request_validator.validate_user_agent(request)


def get_orchestrator() -> AgentOrchestrator:
    """Get agent orchestrator instance"""
    from app.services import get_agent_orchestrator
    return get_agent_orchestrator()


def get_e2b_service() -> E2BService:
    """Get E2B service instance"""
    from app.services import get_e2b_service
    return get_e2b_service()


def get_bedrock_client() -> BedrockClient:
    """Get Bedrock client instance"""
    from app.services import get_bedrock_client
    return get_bedrock_client()


def check_system_health() -> None:
    """Check system health before processing requests"""
    # Check if required services are available
    if settings.ENABLE_BEDROCK:
        bedrock = get_bedrock_client()
        if not bedrock.client:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="AI service unavailable"
            )
    
    # Check system capacity
    orchestrator = get_orchestrator()
    stats = orchestrator.get_statistics()
    
    active_sessions = stats.get('status_distribution', {}).get('running', 0)
    if active_sessions >= settings.MAX_CONCURRENT_SESSIONS:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="System at capacity. Please try again later."
        )


# Dependency combinations
def get_validated_request(
    request: Request,
    client_ip: str = Depends(check_rate_limit),
    _: None = Depends(validate_request),
    request_id: str = Depends(get_request_id)
) -> dict:
    """Get validated request with metadata"""
    return {
        'request': request,
        'client_ip': client_ip,
        'request_id': request_id
    }


def get_services() -> dict:
    """Get all service instances"""
    return {
        'orchestrator': get_orchestrator(),
        'e2b_service': get_e2b_service(),
        'bedrock_client': get_bedrock_client()
    }