"""Application services — lazy singletons"""

_bedrock_client = None
_e2b_service = None
_websocket_manager = None
_agent_orchestrator = None


def get_bedrock_client():
    global _bedrock_client
    if _bedrock_client is None:
        from .bedrock_client import BedrockClient
        _bedrock_client = BedrockClient()
    return _bedrock_client


def get_e2b_service():
    global _e2b_service
    if _e2b_service is None:
        from .e2b_service import E2BService
        _e2b_service = E2BService()
    return _e2b_service


def get_websocket_manager():
    global _websocket_manager
    if _websocket_manager is None:
        from .websocket_manager import WebSocketManager
        _websocket_manager = WebSocketManager()
    return _websocket_manager


def get_agent_orchestrator():
    global _agent_orchestrator
    if _agent_orchestrator is None:
        from .orchestration import get_agent_orchestrator as _get
        _agent_orchestrator = _get()
    return _agent_orchestrator


__all__ = [
    'get_bedrock_client',
    'get_e2b_service',
    'get_websocket_manager',
    'get_agent_orchestrator',
]