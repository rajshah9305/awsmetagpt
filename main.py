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
from fastapi.responses import JSONResponse
from datetime import datetime
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
