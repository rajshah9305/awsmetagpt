"""
Agent orchestration module
"""

from .task_scheduler import TaskScheduler
from .agent_state_manager import AgentStateManager
from .metagpt_executor import MetaGPTExecutor
from .artifact_processor import ArtifactProcessor
from .orchestrator import AgentOrchestrator

# Global instance - initialized lazily
_agent_orchestrator = None

def get_agent_orchestrator() -> AgentOrchestrator:
    """Get or create the global agent orchestrator instance"""
    global _agent_orchestrator
    if _agent_orchestrator is None:
        _agent_orchestrator = AgentOrchestrator()
    return _agent_orchestrator

# For backward compatibility
agent_orchestrator = get_agent_orchestrator()

__all__ = [
    'TaskScheduler',
    'AgentStateManager',
    'MetaGPTExecutor',
    'ArtifactProcessor',
    'AgentOrchestrator',
    'agent_orchestrator',
    'get_agent_orchestrator'
]