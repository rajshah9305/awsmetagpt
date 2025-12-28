"""
Production-ready application configuration settings
Enhanced with validation, security, and monitoring features
"""

from pydantic_settings import BaseSettings
from pydantic import Field, validator
from typing import Optional, List
import os

class Settings(BaseSettings):
    """Enhanced application settings with comprehensive configuration"""
    
    # Core Application Settings
    APP_HOST: str = Field(default="0.0.0.0", description="Application host")
    APP_PORT: int = Field(default=8000, ge=1000, le=65535, description="Application port")
    DEBUG: bool = Field(default=False, description="Debug mode")
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    
    # Security Settings
    SECRET_KEY: str = Field(default="", description="Application secret key")
    CORS_ORIGINS: List[str] = Field(default=["*"], description="CORS allowed origins")
    MAX_REQUEST_SIZE: int = Field(default=50 * 1024 * 1024, description="Max request size in bytes (50MB)")
    
    # AWS Configuration
    AWS_ACCESS_KEY_ID: str = Field(default="", description="AWS access key ID")
    AWS_SECRET_ACCESS_KEY: str = Field(default="", description="AWS secret access key")
    AWS_REGION: str = Field(default="us-east-1", description="AWS region")
    AWS_SESSION_TOKEN: Optional[str] = Field(default=None, description="AWS session token (for temporary credentials)")
    
    # Bedrock Configuration
    BEDROCK_REGION: str = Field(default="us-east-1", description="Bedrock service region")
    BEDROCK_MAX_TOKENS: int = Field(default=4000, ge=100, le=100000, description="Max tokens per request")
    BEDROCK_TEMPERATURE: float = Field(default=0.7, ge=0.0, le=2.0, description="Model temperature")
    BEDROCK_TIMEOUT: int = Field(default=300, ge=30, le=600, description="Bedrock request timeout in seconds")
    
    # MetaGPT Configuration
    METAGPT_API_KEY: str = Field(default="", description="MetaGPT API key (if required)")
    OPENAI_API_KEY: str = Field(default="", description="OpenAI API key for MetaGPT")
    ANTHROPIC_API_KEY: str = Field(default="", description="Anthropic API key for MetaGPT")
    
    # MetaGPT Workspace Settings
    METAGPT_WORKSPACE: str = Field(default="./workspace", description="MetaGPT workspace directory")
    METAGPT_LOG_LEVEL: str = Field(default="INFO", description="MetaGPT log level")
    METAGPT_MAX_BUDGET: float = Field(default=10.0, ge=0.1, le=100.0, description="MetaGPT max budget per session")
    METAGPT_SAVE_LOGS: bool = Field(default=True, description="Save MetaGPT logs")
    METAGPT_ENABLE_MEMORY: bool = Field(default=True, description="Enable MetaGPT long-term memory")
    
    # E2B Configuration
    E2B_API_KEY: str = Field(default="", description="E2B API key")
    E2B_TEMPLATE_ID: str = Field(default="base", description="Default E2B template")
    E2B_TIMEOUT: int = Field(default=1800, ge=300, le=3600, description="E2B sandbox timeout in seconds")
    E2B_MAX_SANDBOXES: int = Field(default=10, ge=1, le=50, description="Maximum concurrent sandboxes")
    E2B_CPU_LIMIT: int = Field(default=2, ge=1, le=8, description="CPU limit per sandbox")
    E2B_MEMORY_LIMIT: int = Field(default=2048, ge=512, le=8192, description="Memory limit per sandbox in MB")
    
    # WebSocket Configuration
    WS_HEARTBEAT_INTERVAL: int = Field(default=30, ge=10, le=300, description="WebSocket heartbeat interval in seconds")
    WS_MAX_CONNECTIONS: int = Field(default=100, ge=1, le=1000, description="Maximum WebSocket connections")
    WS_MESSAGE_QUEUE_SIZE: int = Field(default=1000, ge=100, le=10000, description="WebSocket message queue size")
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = Field(default=100, ge=1, le=10000, description="Rate limit requests per window")
    RATE_LIMIT_WINDOW: int = Field(default=3600, ge=60, le=86400, description="Rate limit window in seconds")
    RATE_LIMIT_BURST: int = Field(default=20, ge=1, le=100, description="Rate limit burst allowance")
    
    # Session Management
    SESSION_TIMEOUT: int = Field(default=7200, ge=300, le=86400, description="Session timeout in seconds")
    MAX_CONCURRENT_SESSIONS: int = Field(default=10, ge=1, le=100, description="Maximum concurrent sessions")
    SESSION_CLEANUP_INTERVAL: int = Field(default=3600, ge=300, le=86400, description="Session cleanup interval in seconds")
    
    # File Management
    MAX_FILE_SIZE: int = Field(default=5 * 1024 * 1024, description="Maximum file size in bytes (5MB)")
    MAX_FILES_PER_SESSION: int = Field(default=200, ge=1, le=1000, description="Maximum files per session")
    WORKSPACE_RETENTION_DAYS: int = Field(default=7, ge=1, le=30, description="Workspace retention in days")
    
    # Monitoring and Metrics
    ENABLE_METRICS: bool = Field(default=True, description="Enable metrics collection")
    METRICS_INTERVAL: int = Field(default=60, ge=10, le=300, description="Metrics collection interval in seconds")
    HEALTH_CHECK_INTERVAL: int = Field(default=30, ge=10, le=300, description="Health check interval in seconds")
    
    # Database Configuration (for future use)
    DATABASE_URL: Optional[str] = Field(default=None, description="Database connection URL")
    DATABASE_POOL_SIZE: int = Field(default=10, ge=1, le=100, description="Database connection pool size")
    
    # Redis Configuration (for future use)
    REDIS_URL: Optional[str] = Field(default=None, description="Redis connection URL")
    REDIS_MAX_CONNECTIONS: int = Field(default=10, ge=1, le=100, description="Redis max connections")
    
    # Feature Flags
    ENABLE_E2B: bool = Field(default=True, description="Enable E2B sandbox integration")
    ENABLE_BEDROCK: bool = Field(default=True, description="Enable AWS Bedrock integration")
    ENABLE_WEBSOCKETS: bool = Field(default=True, description="Enable WebSocket support")
    ENABLE_FILE_UPLOAD: bool = Field(default=True, description="Enable file upload functionality")
    
    # Development Settings
    RELOAD_ON_CHANGE: bool = Field(default=False, description="Reload on file changes (development only)")
    PROFILING_ENABLED: bool = Field(default=False, description="Enable performance profiling")
    
    @validator('SECRET_KEY')
    def validate_secret_key(cls, v):
        if not v and not cls.DEBUG:
            raise ValueError("SECRET_KEY is required in production mode")
        return v
    
    @validator('CORS_ORIGINS')
    def validate_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',')]
        return v
    
    @validator('METAGPT_WORKSPACE')
    def validate_workspace_path(cls, v):
        # Ensure workspace path is absolute or relative to current directory
        if not os.path.isabs(v):
            v = os.path.abspath(v)
        return v
    
    @validator('LOG_LEVEL')
    def validate_log_level(cls, v):
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f"LOG_LEVEL must be one of {valid_levels}")
        return v.upper()
    
    @validator('METAGPT_LOG_LEVEL')
    def validate_metagpt_log_level(cls, v):
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f"METAGPT_LOG_LEVEL must be one of {valid_levels}")
        return v.upper()
    
    def get_aws_credentials(self) -> dict:
        """Get AWS credentials as dictionary"""
        credentials = {
            'aws_access_key_id': self.AWS_ACCESS_KEY_ID,
            'aws_secret_access_key': self.AWS_SECRET_ACCESS_KEY,
            'region_name': self.AWS_REGION
        }
        if self.AWS_SESSION_TOKEN:
            credentials['aws_session_token'] = self.AWS_SESSION_TOKEN
        return credentials
    
    def get_metagpt_env_vars(self) -> dict:
        """Get MetaGPT environment variables"""
        env_vars = {
            'METAGPT_WORKSPACE': self.METAGPT_WORKSPACE,
            'METAGPT_LOG_LEVEL': self.METAGPT_LOG_LEVEL,
            'METAGPT_MAX_BUDGET': str(self.METAGPT_MAX_BUDGET),
            'METAGPT_SAVE_LOGS': str(self.METAGPT_SAVE_LOGS).lower(),
            'METAGPT_ENABLE_LONGTERM_MEMORY': str(self.METAGPT_ENABLE_MEMORY).lower()
        }
        
        if self.OPENAI_API_KEY:
            env_vars['OPENAI_API_KEY'] = self.OPENAI_API_KEY
        if self.ANTHROPIC_API_KEY:
            env_vars['ANTHROPIC_API_KEY'] = self.ANTHROPIC_API_KEY
        if self.METAGPT_API_KEY:
            env_vars['METAGPT_API_KEY'] = self.METAGPT_API_KEY
            
        return env_vars
    
    def get_e2b_config(self) -> dict:
        """Get E2B configuration"""
        return {
            'api_key': self.E2B_API_KEY,
            'template_id': self.E2B_TEMPLATE_ID,
            'timeout': self.E2B_TIMEOUT,
            'cpu_count': self.E2B_CPU_LIMIT,
            'memory_mb': self.E2B_MEMORY_LIMIT
        }
    
    def is_production(self) -> bool:
        """Check if running in production mode"""
        return not self.DEBUG
    
    def validate_required_keys(self) -> List[str]:
        """Validate required configuration keys"""
        missing_keys = []
        
        # Check AWS credentials
        if self.ENABLE_BEDROCK and not (self.AWS_ACCESS_KEY_ID and self.AWS_SECRET_ACCESS_KEY):
            missing_keys.append("AWS credentials (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)")
        
        # Check MetaGPT API keys
        if not (self.OPENAI_API_KEY or self.ANTHROPIC_API_KEY):
            missing_keys.append("AI API key (OPENAI_API_KEY or ANTHROPIC_API_KEY)")
        
        # Check E2B API key
        if self.ENABLE_E2B and not self.E2B_API_KEY:
            missing_keys.append("E2B API key (E2B_API_KEY)")
        
        # Check secret key in production
        if self.is_production() and not self.SECRET_KEY:
            missing_keys.append("SECRET_KEY (required in production)")
        
        return missing_keys
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra environment variables

# Global settings instance
settings = Settings()

# Validate configuration on import
missing_keys = settings.validate_required_keys()
if missing_keys:
    import logging
    logger = logging.getLogger(__name__)
    logger.warning(f"Missing configuration keys: {', '.join(missing_keys)}")
    if settings.is_production():
        raise ValueError(f"Missing required configuration in production: {', '.join(missing_keys)}")