"""
WebSocket manager for real-time communication
"""

from fastapi import WebSocket
from typing import Dict, List, Optional, Any
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class WebSocketManager:
    """Manages WebSocket connections for real-time updates"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.client_data: Dict[str, Dict] = {}
    
    async def connect(self, websocket: WebSocket, client_id: str):
        """Accept a new WebSocket connection"""
        await websocket.accept()
        self.active_connections[client_id] = websocket
        self.client_data[client_id] = {
            'connected_at': datetime.now(),
            'last_heartbeat': datetime.now()
        }
        logger.info(f"✅ WebSocket client {client_id} connected")
        
        # Send welcome message
        await self.send_personal_message(
            json.dumps({
                "type": "connection",
                "message": "Connected to MetaGPT + Bedrock Generator",
                "client_id": client_id,
                "timestamp": datetime.now().isoformat()
            }),
            client_id
        )
    
    def disconnect(self, client_id: str):
        """Remove a WebSocket connection"""
        if client_id in self.active_connections:
            del self.active_connections[client_id]
        if client_id in self.client_data:
            del self.client_data[client_id]
        logger.info(f"❌ WebSocket client {client_id} disconnected")
    
    async def send_personal_message(self, message: str, client_id: str):
        """Send a message to a specific client"""
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].send_text(message)
            except Exception as e:
                logger.error(f"Failed to send message to {client_id}: {e}")
                # Remove broken connection
                self.disconnect(client_id)
    
    async def send_structured_message(self, data: Dict[str, Any], client_id: str):
        """Send a structured message to a specific client"""
        try:
            message = json.dumps({
                **data,
                "timestamp": datetime.now().isoformat()
            })
            await self.send_personal_message(message, client_id)
        except Exception as e:
            logger.error(f"Failed to send structured message to {client_id}: {e}")
    
    async def broadcast(self, message: str):
        """Broadcast a message to all connected clients"""
        disconnected_clients = []
        
        for client_id, connection in self.active_connections.items():
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Failed to broadcast to {client_id}: {e}")
                disconnected_clients.append(client_id)
        
        # Clean up disconnected clients
        for client_id in disconnected_clients:
            self.disconnect(client_id)
    
    async def broadcast_structured(self, data: Dict[str, Any]):
        """Broadcast a structured message to all connected clients"""
        try:
            message = json.dumps({
                **data,
                "timestamp": datetime.now().isoformat()
            })
            await self.broadcast(message)
        except Exception as e:
            logger.error(f"Failed to broadcast structured message: {e}")
    
    # Enhanced message types for real-time features
    
    async def send_progress_update(self, client_id: str, generation_id: str, 
                                 status: str, progress: int, message: str,
                                 current_agent: Optional[str] = None,
                                 estimated_time: Optional[str] = None):
        """Send progress update"""
        await self.send_structured_message({
            "type": "progress_update",
            "generation_id": generation_id,
            "status": status,
            "progress": progress,
            "message": message,
            "current_agent": current_agent,
            "estimated_time": estimated_time
        }, client_id)
    
    async def send_agent_update(self, client_id: str, agent_role: str, 
                              status: str, current_task: Optional[str] = None,
                              progress: Optional[int] = None,
                              thinking: Optional[str] = None):
        """Send agent-specific update"""
        await self.send_structured_message({
            "type": "agent_update",
            "agent_role": agent_role,
            "status": status,
            "current_task": current_task,
            "progress": progress,
            "thinking": thinking
        }, client_id)
    
    async def send_tool_call(self, client_id: str, agent_role: str,
                           tool_name: str, parameters: Optional[Dict] = None,
                           result: Optional[Any] = None, error: Optional[str] = None):
        """Send tool call information"""
        await self.send_structured_message({
            "type": "tool_call",
            "agent_role": agent_role,
            "tool_name": tool_name,
            "parameters": parameters,
            "result": result,
            "error": error
        }, client_id)
    
    async def send_conversation(self, client_id: str, msg_type: str,
                              content: str, agent_role: Optional[str] = None):
        """Send conversation message"""
        await self.send_structured_message({
            "type": "conversation",
            "msg_type": msg_type,  # 'user', 'agent', 'system'
            "content": content,
            "agent_role": agent_role
        }, client_id)
    
    async def send_streaming_content(self, client_id: str, content: str,
                                   agent_role: str, artifact_name: Optional[str] = None):
        """Send streaming content as it's being generated"""
        await self.send_structured_message({
            "type": "streaming_content",
            "content": content,
            "agent_role": agent_role,
            "artifact_name": artifact_name
        }, client_id)
    
    async def send_artifact_update(self, client_id: str, artifact: Dict[str, Any]):
        """Send artifact update"""
        await self.send_structured_message({
            "type": "artifact_update",
            "artifact": artifact
        }, client_id)
    
    async def send_system_metrics(self, client_id: str, tokens_used: int = 0,
                                api_calls: int = 0, execution_time: float = 0,
                                memory_usage: float = 0):
        """Send system metrics"""
        await self.send_structured_message({
            "type": "system_metrics",
            "tokens_used": tokens_used,
            "api_calls": api_calls,
            "execution_time": execution_time,
            "memory_usage": memory_usage
        }, client_id)
    
    async def send_error(self, client_id: str, error_message: str,
                        error_type: str = "general", details: Optional[Dict] = None):
        """Send error message"""
        await self.send_structured_message({
            "type": "error",
            "error_type": error_type,
            "message": error_message,
            "details": details
        }, client_id)
    
    async def handle_heartbeat(self, client_id: str):
        """Handle heartbeat from client"""
        if client_id in self.client_data:
            self.client_data[client_id]['last_heartbeat'] = datetime.now()
            
        # Send heartbeat response
        await self.send_structured_message({
            "type": "heartbeat",
            "status": "alive"
        }, client_id)
    
    def get_connected_clients(self) -> List[str]:
        """Get list of connected client IDs"""
        return list(self.active_connections.keys())
    
    def is_connected(self, client_id: str) -> bool:
        """Check if a client is connected"""
        return client_id in self.active_connections
    
    def get_client_info(self, client_id: str) -> Optional[Dict]:
        """Get client connection info"""
        return self.client_data.get(client_id)

# Global instance
websocket_manager = WebSocketManager()