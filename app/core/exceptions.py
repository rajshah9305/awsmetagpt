"""
Custom exception hierarchy for the MetaGPT + E2B system
"""

from typing import Optional, Dict, Any


class MetaGPTSystemException(Exception):
    """Base exception for all system errors"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class ConfigurationException(MetaGPTSystemException):
    """Configuration-related errors"""
    pass


class ValidationException(MetaGPTSystemException):
    """Input validation errors"""
    pass


class AIServiceException(MetaGPTSystemException):
    """AI service-related errors"""
    pass


class BedrockException(AIServiceException):
    """AWS Bedrock-specific errors"""
    pass


class MetaGPTException(AIServiceException):
    """MetaGPT-specific errors"""
    pass


class SandboxException(MetaGPTSystemException):
    """E2B Sandbox-related errors"""
    pass


class SandboxCreationException(SandboxException):
    """Sandbox creation failures"""
    pass


class SandboxExecutionException(SandboxException):
    """Sandbox execution failures"""
    pass


class OrchestrationException(MetaGPTSystemException):
    """Agent orchestration errors"""
    pass


class TaskException(OrchestrationException):
    """Task execution errors"""
    pass


class WebSocketException(MetaGPTSystemException):
    """WebSocket communication errors"""
    pass


class RateLimitException(MetaGPTSystemException):
    """Rate limiting errors"""
    pass


class SessionException(MetaGPTSystemException):
    """Session management errors"""
    pass