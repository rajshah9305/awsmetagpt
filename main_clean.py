"""
Clean main application with modular structure
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import os
import asyncio
from datetime import datetime
from dotenv import load_dotenv

from app.api.routes_clean import router as api_router
from app.core.config_clean import settings
from app.core.logging import SystemLogger
from app.core.exceptions import MetaGPTSystemException
from app.services.websocket_manager import websocket_manager
from app.api.middleware import error_handler

# Load environment variables
load_dotenv()

# Configure logging
SystemLogger.configure()
logger = SystemLogger.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    # Startup
    logger.info("🚀 Starting MetaGPT + E2B Integration System")
    
    try:
        # Validate configuration
        missing_keys = settings.validate_required_keys()
        if missing_keys and settings.core.is_production():
            raise ValueError(f"Missing required configuration: {', '.join(missing_keys)}")
        
        if missing_keys:
            logger.warning(f"Missing optional configuration: {', '.join(missing_keys)}")
        
        # Initialize services
        logger.info("Initializing services...")
        
        # Services are initialized lazily through dependency injection
        logger.info("✅ All services initialized successfully")
        
        yield
        
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        raise
    finally:
        # Shutdown
        logger.info("🛑 Shutting down MetaGPT + E2B Integration System")


# Create FastAPI app
app = FastAPI(
    title="MetaGPT + E2B Integration System",
    description="Production-ready multi-agent application generator with live sandbox execution",
    version="2.0.0",
    docs_url="/docs" if settings.core.DEBUG else None,
    redoc_url="/redoc" if settings.core.DEBUG else None,
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.security.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if settings.core.is_production():
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*"]  # Configure appropriately for production
    )

# Add API routes
app.include_router(api_router, prefix="/api/v1")

# Serve static files in production
if settings.core.is_production() and os.path.exists("dist"):
    app.mount("/", StaticFiles(directory="dist", html=True), name="static")


# WebSocket endpoint
@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket endpoint for real-time communication"""
    try:
        await websocket_manager.connect(websocket, client_id)
        
        while True:
            try:
                # Wait for messages from client
                data = await websocket.receive_text()
                
                # Echo back for now (can be extended for bidirectional communication)
                await websocket_manager.send_personal_message(
                    {"type": "echo", "data": data}, client_id
                )
                
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"WebSocket error for client {client_id}: {e}")
                await websocket_manager.send_personal_message(
                    {"type": "error", "message": str(e)}, client_id
                )
                
    except Exception as e:
        logger.error(f"WebSocket connection error: {e}")
    finally:
        websocket_manager.disconnect(client_id)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    return error_handler.create_error_response(exc)


# Custom exception handlers
@app.exception_handler(MetaGPTSystemException)
async def metagpt_exception_handler(request: Request, exc: MetaGPTSystemException):
    """Handle MetaGPT system exceptions"""
    return error_handler.create_error_response(exc)


# Health check endpoint (outside API versioning)
@app.get("/health")
async def root_health_check():
    """Root health check"""
    return {
        "status": "healthy",
        "service": "MetaGPT + E2B Integration System",
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat()
    }


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    if settings.core.DEBUG:
        return {
            "message": "MetaGPT + E2B Integration System",
            "version": "2.0.0",
            "docs": "/docs",
            "api": "/api/v1"
        }
    else:
        # In production, this will be handled by static files
        return {"message": "MetaGPT + E2B Integration System"}


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main_clean:app",
        host=settings.core.APP_HOST,
        port=settings.core.APP_PORT,
        reload=settings.core.DEBUG,
        log_level=settings.core.LOG_LEVEL.lower()
    )