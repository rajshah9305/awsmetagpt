"""
Data models for sandbox system
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any


class SandboxState(str, Enum):
    """Sandbox states"""
    CREATING = "creating"
    READY = "ready"
    RUNNING = "running"
    STOPPED = "stopped"
    ERROR = "error"
    TERMINATED = "terminated"


class ProcessState(str, Enum):
    """Process states"""
    STARTING = "starting"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    KILLED = "killed"


@dataclass
class ProcessInfo:
    """Information about a running process"""
    id: str
    command: str
    pid: Optional[int] = None
    state: ProcessState = ProcessState.STARTING
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    exit_code: Optional[int] = None
    stdout_buffer: List[str] = field(default_factory=list)
    stderr_buffer: List[str] = field(default_factory=list)
    
    def add_stdout(self, line: str):
        """Add line to stdout buffer"""
        self.stdout_buffer.append(line)
        # Keep only last 1000 lines
        if len(self.stdout_buffer) > 1000:
            self.stdout_buffer = self.stdout_buffer[-1000:]
    
    def add_stderr(self, line: str):
        """Add line to stderr buffer"""
        self.stderr_buffer.append(line)
        # Keep only last 1000 lines
        if len(self.stderr_buffer) > 1000:
            self.stderr_buffer = self.stderr_buffer[-1000:]
    
    def get_recent_output(self, lines: int = 50) -> Dict[str, List[str]]:
        """Get recent output"""
        return {
            'stdout': self.stdout_buffer[-lines:],
            'stderr': self.stderr_buffer[-lines:]
        }


@dataclass
class SandboxInfo:
    """Information about a sandbox"""
    id: str
    session_id: str
    state: SandboxState
    created_at: datetime = field(default_factory=datetime.now)
    sandbox_instance: Any = None
    files: List[str] = field(default_factory=list)
    processes: Dict[str, ProcessInfo] = field(default_factory=dict)
    preview_url: Optional[str] = None
    project_type: Optional[str] = None
    metrics: Dict[str, Any] = field(default_factory=dict)
    last_activity: datetime = field(default_factory=datetime.now)
    resource_usage: Dict[str, float] = field(default_factory=dict)
    
    def update_activity(self):
        """Update last activity timestamp"""
        self.last_activity = datetime.now()
    
    def add_process(self, process: ProcessInfo):
        """Add a process to the sandbox"""
        self.processes[process.id] = process
        self.update_activity()
    
    def remove_process(self, process_id: str):
        """Remove a process from the sandbox"""
        if process_id in self.processes:
            del self.processes[process_id]
            self.update_activity()
    
    def get_running_processes(self) -> List[ProcessInfo]:
        """Get all running processes"""
        return [p for p in self.processes.values() if p.state == ProcessState.RUNNING]
    
    def get_process_count(self) -> int:
        """Get total process count"""
        return len(self.processes)


@dataclass
class SandboxConfig:
    """Sandbox configuration"""
    template_id: str = "base"
    cpu_limit: int = 2
    memory_limit: int = 2048  # MB
    timeout: int = 1800  # seconds
    max_processes: int = 10
    max_files: int = 1000
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'template_id': self.template_id,
            'cpu_limit': self.cpu_limit,
            'memory_limit': self.memory_limit,
            'timeout': self.timeout,
            'max_processes': self.max_processes,
            'max_files': self.max_files
        }