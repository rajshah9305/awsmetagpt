"""
Clean, modular configuration system
"""

from pydantic_settings import BaseSettings
from pydantic import Field, validator
from typing import Optional, List, Dict, Any
import os
import secrets


class CoreSettings(BaseSettings):
    """Core application settings"""
    
    APP_HOST: str = Field(default="0.0.0.0", description="Application host")
    APP_PORT: int = Field(default=8000, ge=1000, le=65535, description="Application port")
    DEBUG: bool = Field(default=False, description="Debug mode")
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    
    SECRET_KEY: str = Field(
        default_factory=lambda: secrets.token_urlsafe(32) if not os.getenv("SECRET_KEY") else os.getenv("SECRET_KEY", ""),
        description="Application secret key"
    )
    
    @validator('LOG_LEVEL')
    def validate_log_level(cls, v):
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f"LOG_LEVEL must be one of {valid_levels}")
        return v.upper()
    
    def is_production(self) -> bool:
        """Check if running in production mode"""
        return not self.DEBUG


class SecuritySettings(BaseSettings):
    """Security-related settings"""
    
    CORS_ORIGINS: List[str] = Field(default=["*"], description="CORS allowed origins")
    MAX_REQUEST_SIZE: int = Field(default=50 * 1024 * 1024, description="Max request size in bytes")
    RATE_LIMIT_REQUESTS: int = Field(default=100, ge=1, le=10000, description="Rate limit requests per window")
    RATE_LIMIT_WINDOW: int = Field(default=3600, ge=60, le=86400, description="Rate limit window in seconds")
    
    @validator('CORS_ORIGINS')
    def validate_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',')]
        return v


class AWSSettings(BaseSettings):
    """AWS-related settings"""
    
    AWS_ACCESS_KEY_ID: str = Field(default="", description="AWS access key ID")
    AWS_SECRET_ACCESS_KEY: str = Field(default="", description="AWS secret access key")
    AWS_REGION: str = Field(default="us-west-2", description="AWS region")
    AWS_SESSION_TOKEN: Optional[str] = Field(default=None, description="AWS session token")
    
    def get_credentials(self) -> Dict[str, Any]:
        """Get AWS credentials as dictionary"""
        credentials = {
            'aws_access_key_id': self.AWS_ACCESS_KEY_ID,
            'aws_secret_access_key': self.AWS_SECRET_ACCESS_KEY,
            'region_name': self.AWS_REGION
        }
        if self.AWS_SESSION_TOKEN:
            credentials['aws_session_token'] = self.AWS_SESSION_TOKEN
        return credentials


class BedrockSettings(BaseSettings):
    """AWS Bedrock settings"""
    
    BEDROCK_REGION: str = Field(default="us-west-2", description="Bedrock service region")
    BEDROCK_MODEL: str = Field(default="us.amazon.nova-pro-v1:0", description="Default Bedrock model")
    BEDROCK_MAX_TOKENS: int = Field(default=4000, ge=100, le=100000, description="Max tokens per request")
    BEDROCK_TEMPERATURE: float = Field(default=0.7, ge=0.0, le=2.0, description="Model temperature")
    BEDROCK_TIMEOUT: int = Field(default=300, ge=30, le=600, description="Request timeout in seconds")


class MetaGPTSettings(BaseSettings):
    """MetaGPT configuration"""
    
    METAGPT_WORKSPACE: str = Field(default="./workspace", description="MetaGPT workspace directory")
    METAGPT_LOG_LEVEL: str = Field(default="INFO", description="MetaGPT log level")
    METAGPT_MAX_BUDGET: float = Field(default=10.0, ge=0.1, le=100.0, description="Max budget per session")
    METAGPT_SAVE_LOGS: bool = Field(default=True, description="Save MetaGPT logs")
    METAGPT_ENABLE_MEMORY: bool = Field(default=True, description="Enable long-term memory")
    
    # API Keys
    OPENAI_API_KEY: str = Field(default="", description="OpenAI API key")
    ANTHROPIC_API_KEY: str = Field(default="", description="Anthropic API key")
    
    @validator('METAGPT_LOG_LEVEL')
    def validate_log_level(cls, v):
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f"METAGPT_LOG_LEVEL must be one of {valid_levels}")
        return v.upper()
    
    def get_env_vars(self) -> Dict[str, str]:
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
            
        return env_vars


class E2BSettings(BaseSettings):
    """E2B Sandbox settings"""
    
    E2B_API_KEY: str = Field(default="", description="E2B API key")
    E2B_TEMPLATE_ID: str = Field(default="base", description="Default E2B template")
    E2B_TIMEOUT: int = Field(default=1800, ge=300, le=3600, description="Sandbox timeout in seconds")
    E2B_MAX_SANDBOXES: int = Field(default=10, ge=1, le=50, description="Maximum concurrent sandboxes")
    E2B_CPU_LIMIT: int = Field(default=2, ge=1, le=8, description="CPU limit per sandbox")
    E2B_MEMORY_LIMIT: int = Field(default=2048, ge=512, le=8192, description="Memory limit in MB")
    
    def get_config(self) -> Dict[str, Any]:
        """Get E2B configuration"""
        return {
            'api_key': self.E2B_API_KEY,
            'template_id': self.E2B_TEMPLATE_ID,
            'timeout': self.E2B_TIMEOUT,
            'cpu_count': self.E2B_CPU_LIMIT,
            'memory_mb': self.E2B_MEMORY_LIMIT
        }


class WebSocketSettings(BaseSettings):
    """WebSocket configuration"""
    
    WS_HEARTBEAT_INTERVAL: int = Field(default=30, ge=10, le=300, description="Heartbeat interval in seconds")
    WS_MAX_CONNECTIONS: int = Field(default=100, ge=1, le=1000, description="Maximum connections")
    WS_MESSAGE_QUEUE_SIZE: int = Field(default=1000, ge=100, le=10000, description="Message queue size")


class SessionSettings(BaseSettings):
    """Session management settings"""
    
    SESSION_TIMEOUT: int = Field(default=7200, ge=300, le=86400, description="Session timeout in seconds")
    MAX_CONCURRENT_SESSIONS: int = Field(default=10, ge=1, le=100, description="Maximum concurrent sessions")
    SESSION_CLEANUP_INTERVAL: int = Field(default=3600, ge=300, le=86400, description="Cleanup interval in seconds")


class FileSettings(BaseSettings):
    """File management settings"""
    
    MAX_FILE_SIZE: int = Field(default=5 * 1024 * 1024, description="Maximum file size in bytes")
    MAX_FILES_PER_SESSION: int = Field(default=200, ge=1, le=1000, description="Maximum files per session")
    WORKSPACE_RETENTION_DAYS: int = Field(default=7, ge=1, le=30, description="Workspace retention in days")


class FeatureFlags(BaseSettings):
    """Feature flags"""
    
    ENABLE_E2B: bool = Field(default=True, description="Enable E2B sandbox integration")
    ENABLE_BEDROCK: bool = Field(default=True, description="Enable AWS Bedrock integration")
    ENABLE_WEBSOCKETS: bool = Field(default=True, description="Enable WebSocket support")
    ENABLE_FILE_UPLOAD: bool = Field(default=True, description="Enable file upload functionality")
    ENABLE_METRICS: bool = Field(default=True, description="Enable metrics collection")


class Settings(BaseSettings):
    """Main settings class combining all configuration sections"""
    
    # Include all setting sections
    core: CoreSettings = Field(default_factory=CoreSettings)
    security: SecuritySettings = Field(default_factory=SecuritySettings)
    aws: AWSSettings = Field(default_factory=AWSSettings)
    bedrock: BedrockSettings = Field(default_factory=BedrockSettings)
    metagpt: MetaGPTSettings = Field(default_factory=MetaGPTSettings)
    e2b: E2BSettings = Field(default_factory=E2BSettings)
    websocket: WebSocketSettings = Field(default_factory=WebSocketSettings)
    session: SessionSettings = Field(default_factory=SessionSettings)
    files: FileSettings = Field(default_factory=FileSettings)
    features: FeatureFlags = Field(default_factory=FeatureFlags)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Initialize subsections with environment variables
        self.core = CoreSettings()
        self.security = SecuritySettings()
        self.aws = AWSSettings()
        self.bedrock = BedrockSettings()
        self.metagpt = MetaGPTSettings()
        self.e2b = E2BSettings()
        self.websocket = WebSocketSettings()
        self.session = SessionSettings()
        self.files = FileSettings()
        self.features = FeatureFlags()
    
    def validate_required_keys(self) -> List[str]:
        """Validate required configuration keys"""
        missing_keys = []
        
        # Check AWS credentials (required for Bedrock)
        if self.features.ENABLE_BEDROCK and not (self.aws.AWS_ACCESS_KEY_ID and self.aws.AWS_SECRET_ACCESS_KEY):
            missing_keys.append("AWS credentials (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)")
        
        # Check E2B API key
        if self.features.ENABLE_E2B and not self.e2b.E2B_API_KEY:
            missing_keys.append("E2B API key (E2B_API_KEY)")
        
        # Check secret key in production
        if self.core.is_production() and not self.core.SECRET_KEY:
            missing_keys.append("SECRET_KEY (required in production)")
        
        return missing_keys
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


# Global settings instance
settings = Settings()

# Validate configuration on import
missing_keys = settings.validate_required_keys()
if missing_keys:
    import logging
    logger = logging.getLogger(__name__)
    logger.warning(f"Missing configuration keys: {', '.join(missing_keys)}")
    if settings.core.is_production():
        raise ValueError(f"Missing required configuration in production: {', '.join(missing_keys)}")