"""
SSE (Server-Sent Events) manager for real-time communication.
Replaces WebSocket manager — works in Vercel serverless.
"""

import asyncio
import json
from typing import Dict, Any, Optional, AsyncGenerator
from datetime import datetime

from app.core.logging import get_logger

logger = get_logger(__name__)

# In-memory event queues per client_id
# Each client gets an asyncio.Queue of SSE-formatted strings
_queues: Dict[str, asyncio.Queue] = {}


def _get_queue(client_id: str) -> asyncio.Queue:
    if client_id not in _queues:
        _queues[client_id] = asyncio.Queue(maxsize=200)
    return _queues[client_id]


def _remove_queue(client_id: str):
    _queues.pop(client_id, None)


def _format_event(data: Dict[str, Any]) -> str:
    """Format a dict as an SSE data line."""
    payload = json.dumps({**data, "timestamp": datetime.now().isoformat()})
    return f"data: {payload}\n\n"


async def _push(client_id: str, data: Dict[str, Any]):
    """Push an event to a client's queue (non-blocking, drops if full)."""
    q = _get_queue(client_id)
    try:
        q.put_nowait(_format_event(data))
    except asyncio.QueueFull:
        logger.warning(f"SSE queue full for client {client_id}, dropping event")


async def event_stream(client_id: str) -> AsyncGenerator[str, None]:
    """
    Async generator consumed by StreamingResponse.
    Yields SSE-formatted strings until the client disconnects or generation ends.
    """
    q = _get_queue(client_id)
    logger.info(f"SSE stream opened for client {client_id}")

    # Send a connection confirmation immediately
    yield _format_event({"type": "connection", "client_id": client_id,
                          "message": "SSE stream connected"})

    try:
        while True:
            try:
                # Wait up to 25s then send a keep-alive comment
                event = await asyncio.wait_for(q.get(), timeout=25)
                yield event

                # Signal the consumer that we're done streaming
                if '"type": "stream_end"' in event or '"type": "error"' in event:
                    break
            except asyncio.TimeoutError:
                # Keep-alive ping so Vercel doesn't close the connection
                yield ": ping\n\n"
    finally:
        _remove_queue(client_id)
        logger.info(f"SSE stream closed for client {client_id}")


# ── Public API (mirrors the old WebSocketManager interface) ──────────────────

class SSEManager:
    """Drop-in replacement for WebSocketManager using SSE queues."""

    async def send_progress_update(self, client_id: str, generation_id: str,
                                   status: str, progress: int, message: str,
                                   current_agent: Optional[str] = None,
                                   estimated_time: Optional[str] = None):
        await _push(client_id, {
            "type": "progress_update",
            "generation_id": generation_id,
            "status": status,
            "progress": progress,
            "message": message,
            "current_agent": current_agent,
            "estimated_time": estimated_time,
        })

    async def send_agent_update(self, client_id: str, agent_role: str,
                                status: str, current_task: Optional[str] = None,
                                progress: Optional[int] = None,
                                thinking: Optional[str] = None):
        await _push(client_id, {
            "type": "agent_update",
            "agent_role": agent_role,
            "status": status,
            "current_task": current_task,
            "progress": progress,
            "thinking": thinking,
        })

    async def send_artifact_update(self, client_id: str, artifact: Dict[str, Any]):
        await _push(client_id, {"type": "artifact_update", "artifact": artifact})

    async def send_streaming_content(self, client_id: str, content: str,
                                     agent_role: str,
                                     artifact_name: Optional[str] = None):
        await _push(client_id, {
            "type": "streaming_content",
            "content": content,
            "agent_role": agent_role,
            "artifact_name": artifact_name,
        })

    async def send_error(self, client_id: str, error_message: str,
                         error_type: str = "general",
                         details: Optional[Dict] = None):
        await _push(client_id, {
            "type": "error",
            "error_type": error_type,
            "message": error_message,
            "details": details,
        })

    async def send_stream_end(self, client_id: str):
        """Signal the client that the stream is finished."""
        await _push(client_id, {"type": "stream_end"})

    def is_connected(self, client_id: str) -> bool:
        return client_id in _queues
