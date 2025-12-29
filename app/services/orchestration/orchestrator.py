"""
Main agent orchestrator that coordinates all components
"""

import asyncio
import uuid
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
from pathlib import Path

from app.core.logging import get_logger
from app.core.exceptions import OrchestrationException, SessionException
from app.models.schemas import GenerationRequest, AgentRole
from .models import OrchestrationSession, AgentTask, TaskPriority, AgentState
from .task_scheduler import TaskScheduler
from .agent_state_manager import AgentStateManager
from .metagpt_executor import MetaGPTExecutor
from .artifact_processor import ArtifactProcessor

logger = get_logger(__name__)


class AgentOrchestrator:
    """Main orchestrator for agent-based application generation"""
    
    def __init__(self):
        self.sessions: Dict[str, OrchestrationSession] = {}
        self.task_scheduler = TaskScheduler()
        self.agent_manager = AgentStateManager()
        self.metagpt_executor = MetaGPTExecutor()
        self.artifact_processor = ArtifactProcessor()
        
        # Setup callbacks
        self.agent_manager.add_state_change_callback(self._on_agent_state_change)
        
        # Background tasks (will be started when needed)
        self._cleanup_task = None
        self._background_tasks_started = False
    
    def _start_background_tasks(self):
        """Start background maintenance tasks"""
        if not self._background_tasks_started:
            try:
                # Check if we're in an async context
                loop = asyncio.get_running_loop()
                if not self._cleanup_task:
                    self._cleanup_task = loop.create_task(self._cleanup_loop())
                self._background_tasks_started = True
            except RuntimeError:
                # No event loop running, tasks will be started when needed
                logger.debug("No event loop running, background tasks will be started later")
                pass
    
    async def create_session(
        self, 
        request: GenerationRequest, 
        client_id: Optional[str] = None
    ) -> str:
        """Create a new orchestration session"""
        # Start background tasks if not already started
        if not self._background_tasks_started:
            self._start_background_tasks()
        session_id = str(uuid.uuid4())
        
        try:
            # Validate request
            validation_errors = self.metagpt_executor.validate_request(request)
            if validation_errors:
                raise OrchestrationException(f"Invalid request: {', '.join(validation_errors)}")
            
            # Create session
            session = OrchestrationSession(
                id=session_id,
                status="initializing",
                client_id=client_id,
                workspace_path=Path(f"./workspace/{session_id}")
            )
            
            # Create agents for selected roles
            for role in request.active_agents:
                agent_id = f"{session_id}_{role.value}"
                agent = self.agent_manager.create_agent(
                    agent_id=agent_id,
                    role=role,
                    workspace_path=str(session.workspace_path)
                )
                session.agents.append(agent)
            
            # Create tasks
            tasks = self._create_tasks_for_request(request, session_id)
            session.tasks = tasks
            
            # Add tasks to scheduler
            for task in tasks:
                self.task_scheduler.add_task(task)
            
            # Validate task dependencies
            validation_errors = self.task_scheduler.validate_dependencies()
            if validation_errors:
                raise OrchestrationException(f"Invalid task dependencies: {', '.join(validation_errors)}")
            
            self.sessions[session_id] = session
            
            # Start execution
            asyncio.create_task(self._execute_session(session_id, request))
            
            logger.info(f"Created session {session_id} with {len(session.agents)} agents and {len(tasks)} tasks")
            return session_id
            
        except Exception as e:
            logger.error(f"Failed to create session: {e}")
            # Cleanup on failure
            if session_id in self.sessions:
                del self.sessions[session_id]
            raise OrchestrationException(f"Session creation failed: {e}")
    
    def _create_tasks_for_request(self, request: GenerationRequest, session_id: str) -> List[AgentTask]:
        """Create tasks based on generation request"""
        tasks = []
        
        # Task creation based on selected agents
        if AgentRole.PRODUCT_MANAGER in request.active_agents:
            tasks.append(AgentTask(
                id=f"{session_id}_pm_analysis",
                agent_role=AgentRole.PRODUCT_MANAGER,
                task_type="requirement_analysis",
                description="Analyze requirements and create product specification",
                priority=TaskPriority.HIGH
            ))
        
        if AgentRole.ARCHITECT in request.active_agents:
            architect_deps = []
            if AgentRole.PRODUCT_MANAGER in request.active_agents:
                architect_deps.append(f"{session_id}_pm_analysis")
            
            tasks.append(AgentTask(
                id=f"{session_id}_arch_design",
                agent_role=AgentRole.ARCHITECT,
                task_type="system_design",
                description="Create system architecture and design",
                priority=TaskPriority.HIGH,
                dependencies=architect_deps
            ))
        
        if AgentRole.PROJECT_MANAGER in request.active_agents:
            pm_deps = []
            if AgentRole.ARCHITECT in request.active_agents:
                pm_deps.append(f"{session_id}_arch_design")
            
            tasks.append(AgentTask(
                id=f"{session_id}_proj_plan",
                agent_role=AgentRole.PROJECT_MANAGER,
                task_type="project_planning",
                description="Create project plan and task breakdown",
                priority=TaskPriority.NORMAL,
                dependencies=pm_deps
            ))
        
        if AgentRole.ENGINEER in request.active_agents:
            eng_deps = []
            if AgentRole.ARCHITECT in request.active_agents:
                eng_deps.append(f"{session_id}_arch_design")
            if AgentRole.PROJECT_MANAGER in request.active_agents:
                eng_deps.append(f"{session_id}_proj_plan")
            
            tasks.append(AgentTask(
                id=f"{session_id}_implementation",
                agent_role=AgentRole.ENGINEER,
                task_type="implementation",
                description="Implement the application code",
                priority=TaskPriority.CRITICAL,
                dependencies=eng_deps
            ))
        
        if AgentRole.QA_ENGINEER in request.active_agents:
            qa_deps = []
            if AgentRole.ENGINEER in request.active_agents:
                qa_deps.append(f"{session_id}_implementation")
            
            tasks.append(AgentTask(
                id=f"{session_id}_testing",
                agent_role=AgentRole.QA_ENGINEER,
                task_type="testing",
                description="Create and run tests",
                priority=TaskPriority.HIGH,
                dependencies=qa_deps
            ))
        
        return tasks
    
    async def _execute_session(self, session_id: str, request: GenerationRequest):
        """Execute orchestration session"""
        session = self.sessions.get(session_id)
        if not session:
            raise SessionException(f"Session {session_id} not found")
        
        try:
            session.status = "running"
            session.update_progress(5, "Starting generation process...")
            
            # Execute MetaGPT generation
            result = await self.metagpt_executor.execute_generation(
                request=request,
                session_id=session_id,
                progress_callback=lambda p, m: self._update_session_progress(session_id, p, m)
            )
            
            # Process artifacts
            if result.get('success') and result.get('artifacts'):
                processed_artifacts = self.artifact_processor.process_artifacts(
                    session_id=session_id,
                    raw_artifacts=result['artifacts']
                )
                session.artifacts = processed_artifacts
                
                # Save to disk
                workspace_path = self.artifact_processor.save_artifacts_to_disk(
                    session_id=session_id,
                    artifacts=processed_artifacts
                )
                session.workspace_path = Path(workspace_path)
            
            # Mark session as completed
            session.status = "completed"
            session.update_progress(100, "Generation completed successfully")
            
            # Update agent states
            for agent in session.agents:
                self.agent_manager.set_agent_state(agent.id, AgentState.COMPLETED)
            
            logger.info(f"Session {session_id} completed successfully with {len(session.artifacts)} artifacts")
            
        except Exception as e:
            logger.error(f"Session {session_id} execution failed: {e}")
            session.status = "failed"
            session.update_progress(0, f"Generation failed: {str(e)}")
            
            # Update agent states
            for agent in session.agents:
                self.agent_manager.set_agent_state(agent.id, AgentState.FAILED)
    
    async def _update_session_progress(self, session_id: str, progress: int, message: str):
        """Update session progress"""
        session = self.sessions.get(session_id)
        if session:
            session.update_progress(progress, message)
            logger.debug(f"Session {session_id} progress: {progress}% - {message}")
    
    def _on_agent_state_change(self, agent, new_state, old_state=None):
        """Handle agent state changes"""
        logger.debug(f"Agent {agent.id} state changed from {old_state} to {new_state}")
        
        # Update session status based on agent states
        for session in self.sessions.values():
            session_agent = session.get_agent_by_role(agent.role)
            if session_agent and session_agent.id == agent.id:
                # Update session based on agent state
                if new_state == AgentState.FAILED:
                    session.status = "failed"
                elif new_state == AgentState.COMPLETED:
                    # Check if all agents are completed
                    all_completed = all(a.state == AgentState.COMPLETED for a in session.agents)
                    if all_completed:
                        session.status = "completed"
    
    def get_session(self, session_id: str) -> Optional[OrchestrationSession]:
        """Get session by ID"""
        return self.sessions.get(session_id)
    
    def get_session_status(self, session_id: str) -> Optional[Dict]:
        """Get session status"""
        session = self.sessions.get(session_id)
        if not session:
            return None
        
        return {
            'session_id': session.id,
            'status': session.status,
            'progress': session.progress,
            'message': session.message,
            'created_at': session.created_at.isoformat(),
            'updated_at': session.updated_at.isoformat() if session.updated_at else None,
            'agents': [
                {
                    'id': agent.id,
                    'role': agent.role.value,
                    'state': agent.state.value,
                    'last_activity': agent.last_activity.isoformat()
                }
                for agent in session.agents
            ],
            'artifacts_count': len(session.artifacts),
            'workspace_path': str(session.workspace_path) if session.workspace_path else None
        }
    
    def get_session_artifacts(self, session_id: str) -> List[Dict]:
        """Get artifacts for session"""
        session = self.sessions.get(session_id)
        return session.artifacts if session else []
    
    def cancel_session(self, session_id: str) -> bool:
        """Cancel a running session"""
        session = self.sessions.get(session_id)
        if not session:
            return False
        
        if session.status in ["completed", "failed", "cancelled"]:
            return False
        
        session.status = "cancelled"
        session.update_progress(0, "Session cancelled by user")
        
        # Update agent states
        for agent in session.agents:
            if agent.state in [AgentState.EXECUTING, AgentState.THINKING]:
                self.agent_manager.set_agent_state(agent.id, AgentState.TERMINATED)
        
        logger.info(f"Session {session_id} cancelled")
        return True
    
    async def _cleanup_loop(self):
        """Background cleanup loop"""
        while True:
            try:
                await asyncio.sleep(3600)  # Run every hour
                await self._cleanup_old_sessions()
                self.agent_manager.cleanup_inactive_agents(timeout_minutes=120)
            except Exception as e:
                logger.error(f"Cleanup loop error: {e}")
    
    async def _cleanup_old_sessions(self):
        """Clean up old completed sessions"""
        cutoff_time = datetime.now().timestamp() - (24 * 3600)  # 24 hours ago
        
        sessions_to_remove = []
        for session_id, session in self.sessions.items():
            if (session.status in ["completed", "failed", "cancelled"] and
                session.created_at.timestamp() < cutoff_time):
                sessions_to_remove.append(session_id)
        
        for session_id in sessions_to_remove:
            del self.sessions[session_id]
            logger.info(f"Cleaned up old session {session_id}")
    
    def get_statistics(self) -> Dict:
        """Get orchestrator statistics"""
        total_sessions = len(self.sessions)
        status_counts = {}
        
        for session in self.sessions.values():
            status = session.status
            status_counts[status] = status_counts.get(status, 0) + 1
        
        return {
            'total_sessions': total_sessions,
            'status_distribution': status_counts,
            'task_scheduler_stats': self.task_scheduler.get_statistics(),
            'agent_manager_stats': self.agent_manager.get_statistics(),
            'artifact_processor_stats': self.artifact_processor.get_statistics()
        }


# Global instance
agent_orchestrator = AgentOrchestrator()