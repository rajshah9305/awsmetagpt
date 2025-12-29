"""Application services"""

# Global instances - initialized lazily
_bedrock_client = None
_e2b_service = None
_websocket_manager = None
_agent_orchestrator = None

def get_bedrock_client():
    """Get or create the global bedrock client instance"""
    global _bedrock_client
    if _bedrock_client is None:
        from .bedrock_client import BedrockClient
        _bedrock_client = BedrockClient()
    return _bedrock_client

def get_e2b_service():
    """Get or create the global E2B service instance"""
    global _e2b_service
    if _e2b_service is None:
        from .e2b_service import E2BService
        _e2b_service = E2BService()
    return _e2b_service

def get_websocket_manager():
    """Get or create the global websocket manager instance"""
    global _websocket_manager
    if _websocket_manager is None:
        from .websocket_manager import WebSocketManager
        _websocket_manager = WebSocketManager()
    return _websocket_manager

def get_agent_orchestrator():
    """Get or create the global agent orchestrator instance"""
    global _agent_orchestrator
    if _agent_orchestrator is None:
        from .orchestration import get_agent_orchestrator
        _agent_orchestrator = get_agent_orchestrator()
    return _agent_orchestrator

# For backward compatibility
bedrock_client = get_bedrock_client()
e2b_service = get_e2b_service()
websocket_manager = get_websocket_manager()
agent_orchestrator = get_agent_orchestrator()

__all__ = [
    'bedrock_client',
    'e2b_service', 
    'websocket_manager',
    'agent_orchestrator',
    'get_bedrock_client',
    'get_e2b_service',
    'get_websocket_manager',
    'get_agent_orchestrator'
]