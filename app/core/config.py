"""
Application configuration settings
"""

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings"""
    
    # App settings
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    DEBUG: bool = True
    
    # AWS Configuration
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION: str = "us-east-1"
    
    # MetaGPT Configuration
    METAGPT_API_KEY: str = ""
    OPENAI_API_KEY: str = ""  # MetaGPT can use OpenAI
    ANTHROPIC_API_KEY: str = ""  # MetaGPT can use Anthropic
    
    # MetaGPT Workspace Settings
    METAGPT_WORKSPACE: str = "./workspace"
    METAGPT_LOG_LEVEL: str = "INFO"

    # E2B Configuration (for live code preview)
    E2B_API_KEY: str = ""
    E2B_TEMPLATE_ID: str = "base"  # Default E2B template
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()