"""
Pydantic models for API requests and responses
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime

class AgentRole(str, Enum):
    """Available MetaGPT agent roles"""
    PRODUCT_MANAGER = "product_manager"
    ARCHITECT = "architect"
    PROJECT_MANAGER = "project_manager"
    ENGINEER = "engineer"
    QA_ENGINEER = "qa_engineer"
    DEVOPS = "devops"

class BedrockModel(str, Enum):
    """Available AWS Bedrock models (Latest 2025 - Using Inference Profiles)"""
    # Amazon Nova models (usually available by default)
    NOVA_PRO = "us.amazon.nova-pro-v1:0"
    NOVA_LITE = "us.amazon.nova-lite-v1:0"
    NOVA_MICRO = "us.amazon.nova-micro-v1:0"
    # Meta Llama models (usually available)
    LLAMA_33_70B = "us.meta.llama3-3-70b-instruct-v1:0"
    LLAMA_32_90B = "us.meta.llama3-2-90b-instruct-v1:0"
    LLAMA_32_11B = "us.meta.llama3-2-11b-instruct-v1:0"
    # Claude models (require approval)
    CLAUDE_SONNET_4 = "us.anthropic.claude-sonnet-4-20250514-v1:0"
    CLAUDE_HAIKU_45 = "us.anthropic.claude-haiku-4-5-20251001-v1:0"
    CLAUDE_OPUS_4 = "us.anthropic.claude-opus-4-20250514-v1:0"

class AppType(str, Enum):
    """Types of applications that can be generated"""
    WEB_APP = "web_app"
    MOBILE_APP = "mobile_app"
    API_SERVICE = "api_service"
    DESKTOP_APP = "desktop_app"
    CLI_TOOL = "cli_tool"

class GenerationRequest(BaseModel):
    """Request model for app generation"""
    requirement: str = Field(..., description="Natural language description of the app to build")
    app_type: AppType = Field(default=AppType.WEB_APP, description="Type of application to generate")
    preferred_model: BedrockModel = Field(default=BedrockModel.NOVA_PRO, description="Preferred Bedrock model")
    active_agents: List[AgentRole] = Field(default_factory=lambda: list(AgentRole), description="Agents to include in generation")
    additional_requirements: Optional[str] = Field(None, description="Additional specific requirements")
    tech_stack_preferences: Optional[List[str]] = Field(None, description="Preferred technologies/frameworks")

class AgentUpdate(BaseModel):
    """Real-time agent update model"""
    agent_role: AgentRole
    status: str
    message: str
    progress: int = Field(ge=0, le=100)
    timestamp: datetime = Field(default_factory=datetime.now)
    artifacts: Optional[List[str]] = None

class GenerationResponse(BaseModel):
    """Response model for app generation"""
    generation_id: str
    status: str
    message: str
    progress: int = Field(ge=0, le=100)
    websocket_url: Optional[str] = None

class GeneratedArtifact(BaseModel):
    """Model for generated artifacts"""
    name: str
    type: str  # "document", "code", "diagram", etc.
    content: str
    file_path: Optional[str] = None
    agent_role: AgentRole

class GenerationResult(BaseModel):
    """Final generation result"""
    generation_id: str
    requirement: str
    app_type: AppType
    status: str
    artifacts: List[GeneratedArtifact]
    created_at: datetime
    completed_at: Optional[datetime] = None
    total_duration: Optional[int] = None  # seconds

class HealthCheck(BaseModel):
    """Health check response"""
    status: str
    service: str
    timestamp: datetime = Field(default_factory=datetime.now)
    aws_bedrock_available: bool = False
    metagpt_configured: bool = False