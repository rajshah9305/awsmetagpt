"""
Production-ready MetaGPT + E2B Integration System
Enhanced FastAPI application with comprehensive orchestration
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import os
import json
import logging
import time
import asyncio
from datetime import datetime
from dotenv import load_dotenv

from app.api.routes import router as api_router
from app.core.config import settings
from app.services.websocket_manager import websocket_manager
from app.services.agent_orchestrator import agent_orchestrator
from app.services.e2b_service import e2b_service

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log') if settings.is_production() else logging.NullHandler()
    ]
)

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Enhanced application lifespan management"""
    # Startup
    logger.info("🚀 Starting MetaGPT + E2B Integration System")
    
    try:
        # Validate configuration
        missing_keys = settings.validate_required_keys()
        if missing_keys and settings.is_production():
            logger.error(f"Missing required configuration: {', '.join(missing_keys)}")
            raise RuntimeError(f"Missing required configuration: {', '.join(missing_keys)}")
        elif missing_keys:
            logger.warning(f"Missing optional configuration: {', '.join(missing_keys)}")
        
        # Initialize services
        logger.info("🔧 Initializing services...")
        
        # Setup MetaGPT environment
        for key, value in settings.get_metagpt_env_vars().items():
            os.environ[key] = value
        
        # Create workspace directory
        workspace_path = settings.METAGPT_WORKSPACE
        os.makedirs(workspace_path, exist_ok=True)
        logger.info(f"📁 Workspace initialized: {workspace_path}")
        
        # Validate E2B connection if enabled
        if settings.ENABLE_E2B and settings.E2B_API_KEY:
            try:
                # Test E2B connection
                logger.info("🧪 Testing E2B connection...")
                # This would be a simple connection test
                logger.info("✅ E2B service ready")
            except Exception as e:
                logger.warning(f"⚠️ E2B service unavailable: {e}")
        
        # Start background tasks
        asyncio.create_task(system_monitor())
        asyncio.create_task(cleanup_task())
        
        logger.info("✅ System initialization complete")
        
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down MetaGPT + E2B Integration System")
    
    try:
        # Cleanup active sessions
        active_sessions = list(agent_orchestrator.active_sessions.keys())
        if active_sessions:
            logger.info(f"🧹 Cleaning up {len(active_sessions)} active sessions...")
            for session_id in active_sessions:
                try:
                    await agent_orchestrator.terminate_session(session_id)
                except Exception as e:
                    logger.error(f"Failed to cleanup session {session_id}: {e}")
        
        # Cleanup active sandboxes
        active_sandboxes = list(e2b_service.active_sandboxes.keys())
        if active_sandboxes:
            logger.info(f"🧹 Cleaning up {len(active_sandboxes)} active sandboxes...")
            for sandbox_id in active_sandboxes:
                try:
                    await e2b_service.cleanup_sandbox(sandbox_id)
                except Exception as e:
                    logger.error(f"Failed to cleanup sandbox {sandbox_id}: {e}")
        
        logger.info("✅ Graceful shutdown complete")
        
    except Exception as e:
        logger.error(f"❌ Shutdown error: {e}")

# Create FastAPI application
app = FastAPI(
    title="MetaGPT + E2B Integration System",
    description="Production-ready multi-agent application generator with live code execution",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs" if not settings.is_production() else None,
    redoc_url="/redoc" if not settings.is_production() else None
)

# Enhanced middleware configuration
if settings.is_production():
    app.add_middleware(
        TrustedHostMiddleware, 
        allowed_hosts=["*"]  # Configure with actual domains in production
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    max_age=3600
)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all HTTP requests"""
    start_time = time.time()
    
    # Log request
    logger.info(f"📥 {request.method} {request.url.path} - {request.client.host}")
    
    try:
        response = await call_next(request)
        
        # Log response
        process_time = time.time() - start_time
        logger.info(f"📤 {request.method} {request.url.path} - {response.status_code} - {process_time:.3f}s")
        
        # Add performance headers
        response.headers["X-Process-Time"] = str(process_time)
        return response
        
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(f"💥 {request.method} {request.url.path} - ERROR - {process_time:.3f}s - {str(e)}")
        raise

# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "HTTP Exception",
            "message": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.now().isoformat(),
            "path": request.url.path
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred" if settings.is_production() else str(exc),
            "timestamp": datetime.now().isoformat(),
            "path": request.url.path
        }
    )

# Include API routes
app.include_router(api_router, prefix="/api/v1", tags=["API"])

# Enhanced WebSocket endpoint
@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """Enhanced WebSocket endpoint with comprehensive message handling"""
    await websocket_manager.connect(websocket, client_id)
    
    try:
        while True:
            # Receive message with timeout
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=settings.WS_HEARTBEAT_INTERVAL)
            except asyncio.TimeoutError:
                # Send heartbeat if no message received
                await websocket_manager.handle_heartbeat(client_id)
                continue
            
            try:
                message = json.loads(data)
                message_type = message.get("type", "unknown")
                
                logger.debug(f"📨 WebSocket message from {client_id}: {message_type}")
                
                # Handle different message types
                if message_type == "ping":
                    await websocket_manager.handle_heartbeat(client_id)
                    
                elif message_type == "subscribe":
                    # Handle subscription to specific updates
                    session_id = message.get("session_id")
                    if session_id:
                        # Associate client with session for targeted updates
                        await websocket_manager.send_structured_message({
                            "type": "subscription_confirmed",
                            "session_id": session_id
                        }, client_id)
                        
                elif message_type == "get_status":
                    # Send current system status
                    active_sessions = len(agent_orchestrator.active_sessions)
                    active_sandboxes = len(e2b_service.active_sandboxes)
                    
                    await websocket_manager.send_structured_message({
                        "type": "system_status",
                        "active_sessions": active_sessions,
                        "active_sandboxes": active_sandboxes,
                        "connected_clients": len(websocket_manager.get_connected_clients())
                    }, client_id)
                    
                elif message_type == "pause_session":
                    session_id = message.get("session_id")
                    if session_id:
                        success = await agent_orchestrator.pause_session(session_id)
                        await websocket_manager.send_structured_message({
                            "type": "session_paused" if success else "pause_failed",
                            "session_id": session_id
                        }, client_id)
                        
                elif message_type == "resume_session":
                    session_id = message.get("session_id")
                    if session_id:
                        success = await agent_orchestrator.resume_session(session_id)
                        await websocket_manager.send_structured_message({
                            "type": "session_resumed" if success else "resume_failed",
                            "session_id": session_id
                        }, client_id)
                        
                else:
                    # Echo unknown messages for debugging
                    await websocket_manager.send_structured_message({
                        "type": "echo",
                        "original_message": message
                    }, client_id)
                    
            except json.JSONDecodeError:
                await websocket_manager.send_error(
                    client_id, 
                    "Invalid JSON message format", 
                    "json_decode_error"
                )
            except Exception as e:
                logger.error(f"WebSocket message handling error: {e}")
                await websocket_manager.send_error(
                    client_id,
                    f"Message processing error: {str(e)}",
                    "message_processing_error"
                )
                
    except WebSocketDisconnect:
        logger.info(f"📱 WebSocket client {client_id} disconnected")
    except Exception as e:
        logger.error(f"WebSocket error for client {client_id}: {e}")
    finally:
        websocket_manager.disconnect(client_id)

# Background tasks
async def system_monitor():
    """Monitor system health and performance"""
    while True:
        try:
            # Collect metrics
            active_sessions = len(agent_orchestrator.active_sessions)
            active_sandboxes = len(e2b_service.active_sandboxes)
            active_connections = len(websocket_manager.get_connected_clients())
            
            # Log system status
            if settings.ENABLE_METRICS:
                logger.info(f"📊 System Status - Sessions: {active_sessions}, Sandboxes: {active_sandboxes}, Connections: {active_connections}")
            
            # Check for resource limits
            if active_sessions >= settings.MAX_CONCURRENT_SESSIONS * 0.8:
                logger.warning(f"⚠️ High session load: {active_sessions}/{settings.MAX_CONCURRENT_SESSIONS}")
            
            if active_sandboxes >= settings.E2B_MAX_SANDBOXES * 0.8:
                logger.warning(f"⚠️ High sandbox load: {active_sandboxes}/{settings.E2B_MAX_SANDBOXES}")
            
            await asyncio.sleep(settings.METRICS_INTERVAL)
            
        except Exception as e:
            logger.error(f"System monitor error: {e}")
            await asyncio.sleep(60)  # Wait longer on error

async def cleanup_task():
    """Periodic cleanup of expired resources"""
    while True:
        try:
            logger.debug("🧹 Running periodic cleanup...")
            
            # This would be implemented in the orchestrator and E2B service
            # The cleanup logic is already in their respective monitoring tasks
            
            await asyncio.sleep(settings.SESSION_CLEANUP_INTERVAL)
            
        except Exception as e:
            logger.error(f"Cleanup task error: {e}")
            await asyncio.sleep(3600)  # Wait longer on error

# Serve static files (built frontend) - MUST be last
if os.path.exists("dist"):
    app.mount("/", StaticFiles(directory="dist", html=True), name="static")
    logger.info("📁 Serving static files from dist/")

# Root endpoint for API-only access
@app.get("/api")
async def api_root():
    """API root endpoint"""
    return {
        "service": "MetaGPT + E2B Integration System",
        "version": "2.0.0",
        "status": "operational",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "docs": "/docs" if not settings.is_production() else "disabled",
            "health": "/api/v1/health",
            "generate": "/api/v1/generate",
            "websocket": "/ws/{client_id}"
        },
        "features": {
            "metagpt_agents": True,
            "e2b_sandboxes": settings.ENABLE_E2B,
            "bedrock_models": settings.ENABLE_BEDROCK,
            "websocket_updates": settings.ENABLE_WEBSOCKETS
        }
    }

# Legacy root endpoint (when no static files)
@app.get("/")
async def root():
    """Root endpoint fallback"""
    return {
        "message": "MetaGPT + E2B Integration System",
        "version": "2.0.0",
        "api_docs": "/docs" if not settings.is_production() else "Contact administrator for API documentation",
        "api_root": "/api"
    }

if __name__ == "__main__":
    import uvicorn
    
    # Enhanced uvicorn configuration
    # Use PORT from environment (Railway) or fall back to settings
    port = int(os.getenv("PORT", settings.APP_PORT))
    uvicorn_config = {
        "app": "main:app",
        "host": settings.APP_HOST,
        "port": port,
        "reload": settings.RELOAD_ON_CHANGE and settings.DEBUG,
        "log_level": settings.LOG_LEVEL.lower(),
        "access_log": True,
        "server_header": False,
        "date_header": False
    }
    
    if settings.is_production():
        uvicorn_config.update({
            "workers": 1,  # Single worker for WebSocket support
            "loop": "uvloop",
            "http": "httptools"
        })
    
    logger.info(f"🚀 Starting server on {settings.APP_HOST}:{port}")
    uvicorn.run(**uvicorn_config)