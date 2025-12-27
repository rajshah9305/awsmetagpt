"""
Application configuration settings
"""

from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    """Application settings"""
    
    # App settings
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    DEBUG: bool = True
    SECRET_KEY: str = "your-secret-key-change-in-production"
    
    # AWS Configuration
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION: str = "us-east-1"
    
    # Latest Bedrock Models (2025)
    BEDROCK_CLAUDE_SONNET_4: str = "anthropic.claude-sonnet-4-20250514-v1:0"
    BEDROCK_CLAUDE_HAIKU_45: str = "anthropic.claude-haiku-4-5-20251001-v1:0"
    BEDROCK_CLAUDE_OPUS_4: str = "anthropic.claude-opus-4-20250514-v1:0"
    BEDROCK_LLAMA_33_70B: str = "meta.llama3-3-70b-instruct-v1:0"
    BEDROCK_NOVA_PRO: str = "amazon.nova-pro-v1:0"
    BEDROCK_NOVA_LITE: str = "amazon.nova-lite-v1:0"
    
    # MetaGPT Configuration (Optional - can work without)
    METAGPT_API_KEY: str = ""
    METAGPT_MODEL: str = "claude-sonnet-4"

    # E2B Configuration (for live code preview)
    E2B_API_KEY: str = ""
    VITE_E2B_API_KEY: str = ""

    # Frontend Configuration
    FRONTEND_URL: str = "http://localhost:3000"
    VITE_API_URL: str = "http://localhost:8000"
    VITE_APP_NAME: str = "MetaGPT + Bedrock Generator"
    VITE_APP_VERSION: str = "1.0.0"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()