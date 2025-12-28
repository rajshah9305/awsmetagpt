"""
MetaGPT + AWS Bedrock NLP to App Generator
Main FastAPI application
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os
import json
from dotenv import load_dotenv

from app.api.routes import router as api_router
from app.core.config import settings
from app.services.websocket_manager import WebSocketManager

load_dotenv()

# WebSocket manager for real-time updates
websocket_manager = WebSocketManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    print("🚀 Starting MetaGPT + Bedrock App Generator")
    yield
    # Shutdown
    print("👋 Shutting down gracefully")

app = FastAPI(
    title="MetaGPT + AWS Bedrock App Generator",
    description="Generate applications from natural language using MetaGPT agents and AWS Bedrock AI models",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware - Allow all origins for simplicity
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")

# WebSocket endpoint (before static files)
@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket endpoint for real-time agent updates"""
    await websocket_manager.connect(websocket, client_id)
    try:
        while True:
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                
                # Handle different message types
                if message.get("type") == "ping":
                    await websocket_manager.handle_heartbeat(client_id)
                elif message.get("type") == "subscribe":
                    # Handle subscription to specific updates
                    generation_id = message.get("generation_id")
                    if generation_id:
                        # Associate client with generation
                        pass
                else:
                    # Echo other messages for now
                    await websocket_manager.send_personal_message(f"Echo: {data}", client_id)
                    
            except json.JSONDecodeError:
                await websocket_manager.send_error(
                    client_id, 
                    "Invalid JSON message", 
                    "json_error"
                )
                
    except WebSocketDisconnect:
        websocket_manager.disconnect(client_id)

# Serve static files (built frontend) - MUST be last
if os.path.exists("dist"):
    app.mount("/", StaticFiles(directory="dist", html=True), name="static")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "MetaGPT + AWS Bedrock App Generator API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "metagpt-bedrock-generator"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.DEBUG
    )