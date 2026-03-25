"""
FastAPI application — Vercel serverless deployment
"""

import sys
if sys.version_info < (3, 11):
    raise RuntimeError(
        f"Python 3.11+ is required. Current version: {sys.version_info.major}.{sys.version_info.minor}"
    )

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from datetime import datetime
import os
from dotenv import load_dotenv

from app.api.routes import router as api_router
from app.core.config import settings
from app.core.logging import SystemLogger
from app.core.exceptions import MetaGPTSystemException
from app.api.middleware import error_handler

load_dotenv()
SystemLogger.configure()
logger = SystemLogger.get_logger(__name__)

app = FastAPI(
    title="MetaGPT + E2B Integration System",
    description="Multi-agent application generator with live sandbox execution",
    version="2.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")

# Serve static files from the frontend build directory
if os.path.exists("dist"):
    if os.path.exists("dist/assets"):
        app.mount("/assets", StaticFiles(directory="dist/assets"), name="assets")

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "MetaGPT + E2B Integration System",
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat(),
    }


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}")
    return error_handler.create_error_response(exc)


@app.exception_handler(MetaGPTSystemException)
async def metagpt_exception_handler(request: Request, exc: MetaGPTSystemException):
    return error_handler.create_error_response(exc)

# Catch-all route to serve the frontend SPA
@app.get("/{full_path:path}")
async def serve_spa(request: Request, full_path: str):
    # For paths that should be handled by other routes but weren't (e.g. invalid API calls)
    # return a 404 instead of serving index.html
    if full_path.startswith("api/") or full_path.startswith("docs") or \
       full_path.startswith("redoc") or full_path == "health":
        return JSONResponse(
            status_code=404,
            content={"error": "Not Found", "message": f"API endpoint {full_path} not found"}
        )

    index_path = os.path.join("dist", "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)

    return JSONResponse(
        status_code=404,
        content={"error": "Not Found", "message": f"Path {full_path} not found and frontend not built"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
