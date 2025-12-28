"""
API middleware for validation, rate limiting, and error handling
"""

import time
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse

from app.core.logging import get_logger
from app.core.exceptions import MetaGPTSystemException, RateLimitException
from app.core.config_clean import settings

logger = get_logger(__name__)


class RateLimiter:
    """Rate limiting middleware"""
    
    def __init__(self):
        self.requests: Dict[str, list] = {}
    
    def check_rate_limit(self, client_ip: str, max_requests: int = None, window_seconds: int = None) -> bool:
        """Check if request is within rate limits"""
        max_requests = max_requests or settings.security.RATE_LIMIT_REQUESTS
        window_seconds = window_seconds or settings.security.RATE_LIMIT_WINDOW
        
        now = time.time()
        window_start = now - window_seconds
        
        # Initialize client if not exists
        if client_ip not in self.requests:
            self.requests[client_ip] = []
        
        # Clean old requests
        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip] 
            if req_time > window_start
        ]
        
        # Check limit
        if len(self.requests[client_ip]) >= max_requests:
            return False
        
        # Add current request
        self.requests[client_ip].append(now)
        return True
    
    def get_rate_limit_info(self, client_ip: str) -> Dict[str, Any]:
        """Get rate limit information for client"""
        if client_ip not in self.requests:
            return {
                'requests_made': 0,
                'requests_remaining': settings.security.RATE_LIMIT_REQUESTS,
                'reset_time': None
            }
        
        now = time.time()
        window_start = now - settings.security.RATE_LIMIT_WINDOW
        
        # Clean old requests
        recent_requests = [
            req_time for req_time in self.requests[client_ip] 
            if req_time > window_start
        ]
        
        requests_made = len(recent_requests)
        requests_remaining = max(0, settings.security.RATE_LIMIT_REQUESTS - requests_made)
        
        # Calculate reset time (when oldest request expires)
        reset_time = None
        if recent_requests:
            oldest_request = min(recent_requests)
            reset_time = oldest_request + settings.security.RATE_LIMIT_WINDOW
        
        return {
            'requests_made': requests_made,
            'requests_remaining': requests_remaining,
            'reset_time': reset_time
        }


class RequestValidator:
    """Request validation middleware"""
    
    @staticmethod
    def validate_content_length(request: Request, max_size: int = None) -> None:
        """Validate request content length"""
        max_size = max_size or settings.security.MAX_REQUEST_SIZE
        
        content_length = request.headers.get('content-length')
        if content_length and int(content_length) > max_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"Request too large. Maximum size: {max_size} bytes"
            )
    
    @staticmethod
    def validate_content_type(request: Request, allowed_types: list = None) -> None:
        """Validate request content type"""
        if not allowed_types:
            allowed_types = ['application/json', 'multipart/form-data']
        
        content_type = request.headers.get('content-type', '').split(';')[0]
        if content_type and content_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=f"Unsupported content type: {content_type}"
            )
    
    @staticmethod
    def validate_user_agent(request: Request) -> None:
        """Validate user agent (basic bot detection)"""
        user_agent = request.headers.get('user-agent', '').lower()
        
        # Block obvious bots/crawlers
        blocked_agents = ['bot', 'crawler', 'spider', 'scraper']
        if any(agent in user_agent for agent in blocked_agents):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Automated requests not allowed"
            )


class ErrorHandler:
    """Centralized error handling"""
    
    @staticmethod
    def create_error_response(
        error: Exception, 
        request_id: Optional[str] = None
    ) -> JSONResponse:
        """Create standardized error response"""
        
        # Handle custom exceptions
        if isinstance(error, MetaGPTSystemException):
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    'error': error.__class__.__name__,
                    'message': error.message,
                    'details': error.details,
                    'timestamp': datetime.now().isoformat(),
                    'request_id': request_id
                }
            )
        
        # Handle rate limit exceptions
        elif isinstance(error, RateLimitException):
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    'error': 'RateLimitExceeded',
                    'message': error.message,
                    'timestamp': datetime.now().isoformat(),
                    'request_id': request_id
                }
            )
        
        # Handle HTTP exceptions
        elif isinstance(error, HTTPException):
            return JSONResponse(
                status_code=error.status_code,
                content={
                    'error': 'HTTPException',
                    'message': error.detail,
                    'timestamp': datetime.now().isoformat(),
                    'request_id': request_id
                }
            )
        
        # Handle generic exceptions
        else:
            logger.error(f"Unhandled exception: {error}", error=error)
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    'error': 'InternalServerError',
                    'message': 'An unexpected error occurred',
                    'timestamp': datetime.now().isoformat(),
                    'request_id': request_id
                }
            )


# Global instances
rate_limiter = RateLimiter()
request_validator = RequestValidator()
error_handler = ErrorHandler()