"""
Enhanced Pydantic models for production-ready API requests and responses
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Union
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
    # Claude models (using inference profiles)
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

class Priority(str, Enum):
    """Task priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"

class GenerationRequest(BaseModel):
    """Enhanced request model for app generation"""
    requirement: str = Field(
        ..., 
        description="Natural language description of the app to build",
        min_length=10,
        max_length=50000
    )
    app_type: AppType = Field(
        default=AppType.WEB_APP, 
        description="Type of application to generate"
    )
    preferred_model: BedrockModel = Field(
        default=BedrockModel.CLAUDE_SONNET_4, 
        description="Preferred Bedrock model"
    )
    active_agents: List[AgentRole] = Field(
        default_factory=lambda: [AgentRole.PRODUCT_MANAGER, AgentRole.ARCHITECT, AgentRole.ENGINEER], 
        description="Agents to include in generation",
        min_items=1,
        max_items=6
    )
    additional_requirements: Optional[str] = Field(
        None, 
        description="Additional specific requirements",
        max_length=10000
    )
    tech_stack_preferences: Optional[List[str]] = Field(
        None, 
        description="Preferred technologies/frameworks",
        max_items=10
    )
    priority: Priority = Field(
        default=Priority.NORMAL,
        description="Generation priority level"
    )
    timeout_minutes: int = Field(
        default=30,
        description="Maximum generation time in minutes",
        ge=5,
        le=120
    )
    
    @validator('tech_stack_preferences')
    def validate_tech_stack(cls, v):
        if v:
            # Remove empty strings and limit length
            v = [tech.strip() for tech in v if tech.strip()]
            if len(v) > 10:
                raise ValueError("Maximum 10 technology preferences allowed")
        return v

class AgentUpdate(BaseModel):
    """Real-time agent update model"""
    agent_role: AgentRole
    status: str
    message: str
    progress: int = Field(ge=0, le=100)
    timestamp: datetime = Field(default_factory=datetime.now)
    artifacts: Optional[List[str]] = None
    current_task: Optional[str] = None
    estimated_completion: Optional[datetime] = None

class GenerationResponse(BaseModel):
    """Enhanced response model for app generation"""
    generation_id: str = Field(..., description="Unique generation session ID")
    status: str = Field(..., description="Current generation status")
    message: str = Field(..., description="Status message")
    progress: int = Field(ge=0, le=100, description="Progress percentage")
    websocket_url: Optional[str] = Field(None, description="WebSocket URL for real-time updates")
    estimated_completion: Optional[datetime] = Field(None, description="Estimated completion time")
    active_agents: Optional[List[str]] = Field(None, description="List of active agent roles")

class GeneratedArtifact(BaseModel):
    """Enhanced model for generated artifacts"""
    id: str = Field(..., description="Unique artifact ID")
    name: str = Field(..., description="Artifact filename")
    type: str = Field(..., description="Artifact type (code, documentation, configuration)")
    content: str = Field(..., description="Artifact content")
    agent_role: str = Field(..., description="Agent that created this artifact")
    file_path: Optional[str] = Field(None, description="Relative file path")
    size: Optional[int] = Field(None, description="Content size in bytes")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    language: Optional[str] = Field(None, description="Programming language or format")
    dependencies: Optional[List[str]] = Field(None, description="File dependencies")

class SessionStatus(BaseModel):
    """Enhanced session status model"""
    session_id: str
    status: str
    progress: int = Field(ge=0, le=100)
    message: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    estimated_completion: Optional[datetime] = None
    agents: List[Dict[str, Any]] = Field(default_factory=list)
    sandbox: Optional[Dict[str, Any]] = None
    metrics: Dict[str, Any] = Field(default_factory=dict)
    artifacts_count: int = 0

class SandboxInfo(BaseModel):
    """E2B Sandbox information model"""
    id: str
    session_id: str
    state: str
    created_at: datetime
    last_activity: datetime
    project_type: Optional[str] = None
    preview_url: Optional[str] = None
    files_count: int = 0
    active_processes: int = 0
    metrics: Dict[str, Any] = Field(default_factory=dict)

class ProcessInfo(BaseModel):
    """Process information model"""
    id: str
    command: str
    state: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    exit_code: Optional[int] = None
    pid: Optional[int] = None

class LogEntry(BaseModel):
    """Log entry model"""
    timestamp: datetime
    level: str
    source: str
    message: str
    process_id: Optional[str] = None

class SystemMetrics(BaseModel):
    """System metrics model"""
    active_sessions: int
    active_sandboxes: int
    active_connections: int
    total_agents: int
    cpu_usage: Optional[float] = None
    memory_usage: Optional[float] = None
    disk_usage: Optional[float] = None

class HealthCheck(BaseModel):
    """Enhanced health check response"""
    status: str = Field(..., description="Overall system status")
    service: str = Field(..., description="Service name")
    timestamp: datetime = Field(default_factory=datetime.now)
    aws_bedrock_available: bool = False
    metagpt_configured: bool = False
    e2b_configured: bool = False
    services: Optional[Dict[str, Any]] = None
    capacity: Optional[Dict[str, Any]] = None

class ErrorResponse(BaseModel):
    """Standardized error response"""
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    request_id: Optional[str] = None

class WebSocketMessage(BaseModel):
    """WebSocket message model"""
    type: str
    data: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.now)
    client_id: Optional[str] = None

# Request/Response models for specific endpoints

class CreateSandboxRequest(BaseModel):
    """Request to create E2B sandbox"""
    template: str = Field(default="base", description="Sandbox template")
    timeout_minutes: int = Field(default=30, ge=5, le=120)
    resource_limits: Optional[Dict[str, Any]] = None

class WriteFilesRequest(BaseModel):
    """Request to write files to sandbox"""
    artifacts: List[Dict[str, Any]] = Field(..., min_items=1, max_items=200)
    overwrite: bool = Field(default=True, description="Overwrite existing files")

class RunApplicationRequest(BaseModel):
    """Request to run application in sandbox"""
    command: Optional[str] = Field(None, description="Custom run command")
    environment: Optional[Dict[str, str]] = Field(None, description="Environment variables")
    working_directory: str = Field(default="/home/user/app", description="Working directory")

class GetLogsRequest(BaseModel):
    """Request to get logs from sandbox"""
    process_id: Optional[str] = None
    lines: int = Field(default=100, ge=1, le=1000)
    level: Optional[str] = Field(None, description="Log level filter")
    since: Optional[datetime] = Field(None, description="Get logs since timestamp")

# Configuration models

class AgentConfig(BaseModel):
    """Agent configuration model"""
    role: AgentRole
    enabled: bool = True
    timeout_minutes: int = Field(default=15, ge=1, le=60)
    max_retries: int = Field(default=3, ge=0, le=10)
    custom_instructions: Optional[str] = None
    tools: Optional[List[str]] = None

class GenerationConfig(BaseModel):
    """Generation configuration model"""
    agents: List[AgentConfig]
    model: BedrockModel = BedrockModel.CLAUDE_SONNET_4
    timeout_minutes: int = Field(default=30, ge=5, le=120)
    max_artifacts: int = Field(default=100, ge=1, le=500)
    enable_e2b: bool = True
    sandbox_template: str = "base"

# Validation models

class ValidationResult(BaseModel):
    """Validation result model"""
    valid: bool
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)