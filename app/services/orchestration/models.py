"""
Data models for orchestration system
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any

from app.models.schemas import AgentRole


class AgentState(str, Enum):
    """Agent execution states"""
    IDLE = "idle"
    INITIALIZING = "initializing"
    THINKING = "thinking"
    EXECUTING = "executing"
    WAITING = "waiting"
    COMPLETED = "completed"
    FAILED = "failed"
    TERMINATED = "terminated"


class TaskPriority(str, Enum):
    """Task priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class TaskStatus(str, Enum):
    """Task execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class AgentTask:
    """Represents a task for an agent"""
    id: str
    agent_role: AgentRole
    task_type: str
    description: str
    priority: TaskPriority = TaskPriority.NORMAL
    status: TaskStatus = TaskStatus.PENDING
    dependencies: List[str] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    
    def can_execute(self, completed_tasks: List[str]) -> bool:
        """Check if task can be executed based on dependencies"""
        return all(dep in completed_tasks for dep in self.dependencies)
    
    def is_ready(self) -> bool:
        """Check if task is ready to be executed"""
        return self.status == TaskStatus.PENDING
    
    def is_running(self) -> bool:
        """Check if task is currently running"""
        return self.status == TaskStatus.RUNNING
    
    def is_completed(self) -> bool:
        """Check if task is completed"""
        return self.status == TaskStatus.COMPLETED
    
    def is_failed(self) -> bool:
        """Check if task has failed"""
        return self.status == TaskStatus.FAILED
    
    def can_retry(self) -> bool:
        """Check if task can be retried"""
        return self.is_failed() and self.retry_count < self.max_retries


@dataclass
class AgentInstance:
    """Represents an active agent instance"""
    id: str
    role: AgentRole
    state: AgentState = AgentState.IDLE
    current_task: Optional[AgentTask] = None
    completed_tasks: List[str] = field(default_factory=list)
    failed_tasks: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    workspace_path: Optional[Path] = None
    context: Dict[str, Any] = field(default_factory=dict)
    metrics: Dict[str, Any] = field(default_factory=dict)
    
    def is_available(self) -> bool:
        """Check if agent is available for new tasks"""
        return self.state in [AgentState.IDLE, AgentState.COMPLETED]
    
    def is_busy(self) -> bool:
        """Check if agent is currently busy"""
        return self.state in [AgentState.EXECUTING, AgentState.THINKING]
    
    def update_activity(self):
        """Update last activity timestamp"""
        self.last_activity = datetime.now()


@dataclass
class OrchestrationSession:
    """Represents an orchestration session"""
    id: str
    status: str
    progress: int = 0
    message: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    agents: List[AgentInstance] = field(default_factory=list)
    tasks: List[AgentTask] = field(default_factory=list)
    artifacts: List[Dict[str, Any]] = field(default_factory=list)
    client_id: Optional[str] = None
    workspace_path: Optional[Path] = None
    
    def get_agent_by_role(self, role: AgentRole) -> Optional[AgentInstance]:
        """Get agent instance by role"""
        return next((agent for agent in self.agents if agent.role == role), None)
    
    def get_pending_tasks(self) -> List[AgentTask]:
        """Get all pending tasks"""
        return [task for task in self.tasks if task.is_ready()]
    
    def get_completed_task_ids(self) -> List[str]:
        """Get IDs of all completed tasks"""
        return [task.id for task in self.tasks if task.is_completed()]
    
    def update_progress(self, progress: int, message: str):
        """Update session progress"""
        self.progress = progress
        self.message = message
        self.updated_at = datetime.now()