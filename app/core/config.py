"""
Application configuration
"""

import os
import secrets
from typing import List, Optional, Dict, Any
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Flat settings class for easy env var support"""

    # Core
    APP_HOST: str = Field(default="0.0.0.0")
    APP_PORT: int = Field(default=8000, ge=1000, le=65535)
    DEBUG: bool = Field(default=False)
    LOG_LEVEL: str = Field(default="INFO")
    SECRET_KEY: str = Field(default_factory=lambda: os.getenv("SECRET_KEY") or secrets.token_urlsafe(32))

    # Security
    CORS_ORIGINS: List[str] = Field(default=["*"])
    MAX_REQUEST_SIZE: int = Field(default=50 * 1024 * 1024)
    RATE_LIMIT_REQUESTS: int = Field(default=100, ge=1, le=10000)
    RATE_LIMIT_WINDOW: int = Field(default=3600, ge=60, le=86400)

    # AWS
    AWS_ACCESS_KEY_ID: str = Field(default="")
    AWS_SECRET_ACCESS_KEY: str = Field(default="")
    AWS_REGION: str = Field(default="us-east-1")

    # Bedrock
    BEDROCK_REGION: str = Field(default="us-east-1")
    BEDROCK_MODEL: str = Field(default="anthropic.claude-3-haiku-20240307-v1:0")  # Must match a BedrockModel enum value

    # MetaGPT
    METAGPT_WORKSPACE: str = Field(default="./workspace")
    METAGPT_CONFIG_DIR: str = Field(default="./metagpt_config")
    OPENAI_API_KEY: str = Field(default="")
    ANTHROPIC_API_KEY: str = Field(default="")

    # E2B
    E2B_API_KEY: str = Field(default="")
    E2B_TEMPLATE_ID: str = Field(default="base")
    E2B_TIMEOUT: int = Field(default=1800, ge=300, le=3600)
    E2B_CPU_LIMIT: int = Field(default=2, ge=1, le=8)
    E2B_MEMORY_LIMIT: int = Field(default=2048, ge=512, le=8192)

    # Session
    SESSION_TIMEOUT: int = Field(default=7200, ge=300, le=86400)
    MAX_CONCURRENT_SESSIONS: int = Field(default=10, ge=1, le=100)

    # File limits
    MAX_FILE_SIZE: int = Field(default=5 * 1024 * 1024)
    MAX_FILES_PER_SESSION: int = Field(default=200, ge=1, le=1000)

    # Feature flags
    ENABLE_E2B: bool = Field(default=True)
    ENABLE_BEDROCK: bool = Field(default=True)

    @field_validator("LOG_LEVEL")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        valid = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        upper = v.upper()
        if upper not in valid:
            raise ValueError(f"LOG_LEVEL must be one of {valid}")
        return upper

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def validate_cors_origins(cls, v: Any) -> List[str]:
        if isinstance(v, str):
            return [o.strip() for o in v.split(",")]
        return v

    def is_production(self) -> bool:
        return not self.DEBUG

    def get_metagpt_env_vars(self) -> Dict[str, str]:
        env: Dict[str, str] = {
            "METAGPT_WORKSPACE": self.METAGPT_WORKSPACE,
            "METAGPT_CONFIG_PATH": os.path.join(self.METAGPT_CONFIG_DIR, "config2.yaml"),
        }
        if self.OPENAI_API_KEY:
            env["OPENAI_API_KEY"] = self.OPENAI_API_KEY
        if self.ANTHROPIC_API_KEY:
            env["ANTHROPIC_API_KEY"] = self.ANTHROPIC_API_KEY
        return env

    def validate_required_keys(self) -> List[str]:
        missing: List[str] = []
        if self.ENABLE_BEDROCK and not (self.AWS_ACCESS_KEY_ID and self.AWS_SECRET_ACCESS_KEY):
            missing.append("AWS credentials (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)")
        if self.ENABLE_E2B and not self.E2B_API_KEY:
            missing.append("E2B API key (E2B_API_KEY)")
        if self.is_production() and not self.SECRET_KEY:
            missing.append("SECRET_KEY")
        return missing

    model_config = {"env_file": ".env", "case_sensitive": True, "extra": "ignore"}


settings = Settings()
