"""
Agent state management and lifecycle
"""

from typing import Dict, List, Optional
import asyncio
from datetime import datetime, timedelta

from app.core.logging import get_logger
from app.core.exceptions import OrchestrationException
from app.models.schemas import AgentRole
from .models import AgentInstance, AgentState, AgentTask

logger = get_logger(__name__)


class AgentStateManager:
    """Manages agent instances and their states"""
    
    def __init__(self):
        self.agents: Dict[str, AgentInstance] = {}
        self.role_to_agent: Dict[AgentRole, str] = {}
        self.state_change_callbacks: List[callable] = []
    
    def create_agent(self, agent_id: str, role: AgentRole, workspace_path: Optional[str] = None) -> AgentInstance:
        """Create a new agent instance"""
        if agent_id in self.agents:
            raise OrchestrationException(f"Agent {agent_id} already exists")
        
        if role in self.role_to_agent:
            raise OrchestrationException(f"Agent with role {role} already exists")
        
        agent = AgentInstance(
            id=agent_id,
            role=role,
            workspace_path=workspace_path
        )
        
        self.agents[agent_id] = agent
        self.role_to_agent[role] = agent_id
        
        logger.info(f"Created agent {agent_id} with role {role}")
        return agent
    
    def get_agent(self, agent_id: str) -> Optional[AgentInstance]:
        """Get agent by ID"""
        return self.agents.get(agent_id)
    
    def get_agent_by_role(self, role: AgentRole) -> Optional[AgentInstance]:
        """Get agent by role"""
        agent_id = self.role_to_agent.get(role)
        return self.agents.get(agent_id) if agent_id else None
    
    def get_available_agents(self) -> List[AgentInstance]:
        """Get all available agents"""
        return [agent for agent in self.agents.values() if agent.is_available()]
    
    def get_busy_agents(self) -> List[AgentInstance]:
        """Get all busy agents"""
        return [agent for agent in self.agents.values() if agent.is_busy()]
    
    def assign_task(self, agent_id: str, task: AgentTask) -> None:
        """Assign a task to an agent"""
        agent = self.get_agent(agent_id)
        if not agent:
            raise OrchestrationException(f"Agent {agent_id} not found")
        
        if not agent.is_available():
            raise OrchestrationException(f"Agent {agent_id} is not available")
        
        agent.current_task = task
        agent.state = AgentState.EXECUTING
        agent.update_activity()
        
        self._notify_state_change(agent, AgentState.EXECUTING)
        logger.info(f"Assigned task {task.id} to agent {agent_id}")
    
    def complete_task(self, agent_id: str, result: Optional[Dict] = None) -> None:
        """Mark agent's current task as completed"""
        agent = self.get_agent(agent_id)
        if not agent:
            raise OrchestrationException(f"Agent {agent_id} not found")
        
        if not agent.current_task:
            raise OrchestrationException(f"Agent {agent_id} has no current task")
        
        task_id = agent.current_task.id
        agent.completed_tasks.append(task_id)
        agent.current_task.result = result
        agent.current_task = None
        agent.state = AgentState.COMPLETED
        agent.update_activity()
        
        self._notify_state_change(agent, AgentState.COMPLETED)
        logger.info(f"Agent {agent_id} completed task {task_id}")
    
    def fail_task(self, agent_id: str, error: str) -> None:
        """Mark agent's current task as failed"""
        agent = self.get_agent(agent_id)
        if not agent:
            raise OrchestrationException(f"Agent {agent_id} not found")
        
        if not agent.current_task:
            raise OrchestrationException(f"Agent {agent_id} has no current task")
        
        task_id = agent.current_task.id
        agent.failed_tasks.append(task_id)
        agent.current_task.error = error
        agent.current_task = None
        agent.state = AgentState.FAILED
        agent.update_activity()
        
        self._notify_state_change(agent, AgentState.FAILED)
        logger.error(f"Agent {agent_id} failed task {task_id}: {error}")
    
    def set_agent_state(self, agent_id: str, state: AgentState) -> None:
        """Set agent state"""
        agent = self.get_agent(agent_id)
        if not agent:
            raise OrchestrationException(f"Agent {agent_id} not found")
        
        old_state = agent.state
        agent.state = state
        agent.update_activity()
        
        self._notify_state_change(agent, state, old_state)
        logger.debug(f"Agent {agent_id} state changed from {old_state} to {state}")
    
    def update_agent_context(self, agent_id: str, context: Dict) -> None:
        """Update agent context"""
        agent = self.get_agent(agent_id)
        if not agent:
            raise OrchestrationException(f"Agent {agent_id} not found")
        
        agent.context.update(context)
        agent.update_activity()
        
        logger.debug(f"Updated context for agent {agent_id}")
    
    def get_agent_metrics(self, agent_id: str) -> Dict:
        """Get agent performance metrics"""
        agent = self.get_agent(agent_id)
        if not agent:
            raise OrchestrationException(f"Agent {agent_id} not found")
        
        total_tasks = len(agent.completed_tasks) + len(agent.failed_tasks)
        success_rate = len(agent.completed_tasks) / total_tasks if total_tasks > 0 else 0
        
        metrics = {
            'total_tasks': total_tasks,
            'completed_tasks': len(agent.completed_tasks),
            'failed_tasks': len(agent.failed_tasks),
            'success_rate': success_rate,
            'current_state': agent.state.value,
            'created_at': agent.created_at.isoformat(),
            'last_activity': agent.last_activity.isoformat(),
            'uptime_seconds': (datetime.now() - agent.created_at).total_seconds()
        }
        
        metrics.update(agent.metrics)
        return metrics
    
    def cleanup_inactive_agents(self, timeout_minutes: int = 60) -> List[str]:
        """Clean up agents that have been inactive for too long"""
        cutoff_time = datetime.now() - timedelta(minutes=timeout_minutes)
        inactive_agents = []
        
        for agent_id, agent in list(self.agents.items()):
            if (agent.last_activity < cutoff_time and 
                agent.state in [AgentState.IDLE, AgentState.COMPLETED, AgentState.FAILED]):
                
                # Remove from role mapping
                if agent.role in self.role_to_agent:
                    del self.role_to_agent[agent.role]
                
                # Remove agent
                del self.agents[agent_id]
                inactive_agents.append(agent_id)
                
                logger.info(f"Cleaned up inactive agent {agent_id}")
        
        return inactive_agents
    
    def add_state_change_callback(self, callback: callable) -> None:
        """Add callback for state changes"""
        self.state_change_callbacks.append(callback)
    
    def _notify_state_change(self, agent: AgentInstance, new_state: AgentState, old_state: Optional[AgentState] = None) -> None:
        """Notify callbacks of state changes"""
        for callback in self.state_change_callbacks:
            try:
                callback(agent, new_state, old_state)
            except Exception as e:
                logger.error(f"Error in state change callback: {e}")
    
    def get_all_agents(self) -> List[AgentInstance]:
        """Get all agents"""
        return list(self.agents.values())
    
    def get_statistics(self) -> Dict:
        """Get agent statistics"""
        total_agents = len(self.agents)
        state_counts = {}
        
        for state in AgentState:
            state_counts[state.value] = len([a for a in self.agents.values() if a.state == state])
        
        return {
            'total_agents': total_agents,
            'state_distribution': state_counts,
            'available_agents': len(self.get_available_agents()),
            'busy_agents': len(self.get_busy_agents())
        }