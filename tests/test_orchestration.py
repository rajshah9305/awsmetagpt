"""
Tests for orchestration system
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock

from app.services.orchestration.task_scheduler import TaskScheduler
from app.services.orchestration.agent_state_manager import AgentStateManager
from app.services.orchestration.models import AgentTask, TaskPriority, AgentState
from app.models.schemas import AgentRole


class TestTaskScheduler:
    """Test task scheduler functionality"""
    
    def setup_method(self):
        self.scheduler = TaskScheduler()
    
    def test_add_task(self):
        """Test adding a task"""
        task = AgentTask(
            id="test_task",
            agent_role=AgentRole.ENGINEER,
            task_type="implementation",
            description="Test task"
        )
        
        self.scheduler.add_task(task)
        assert "test_task" in self.scheduler.task_registry
        assert task == self.scheduler.task_registry["test_task"]
    
    def test_get_ready_tasks(self):
        """Test getting ready tasks"""
        # Add task with no dependencies
        task1 = AgentTask(
            id="task1",
            agent_role=AgentRole.ENGINEER,
            task_type="implementation",
            description="Task 1"
        )
        
        # Add task with dependency
        task2 = AgentTask(
            id="task2",
            agent_role=AgentRole.QA_ENGINEER,
            task_type="testing",
            description="Task 2",
            dependencies=["task1"]
        )
        
        self.scheduler.add_task(task1)
        self.scheduler.add_task(task2)
        
        # Initially, only task1 should be ready
        ready_tasks = self.scheduler.get_ready_tasks(set())
        assert len(ready_tasks) == 1
        assert ready_tasks[0].id == "task1"
        
        # After task1 is completed, task2 should be ready
        ready_tasks = self.scheduler.get_ready_tasks({"task1"})
        assert len(ready_tasks) == 1
        assert ready_tasks[0].id == "task2"
    
    def test_priority_ordering(self):
        """Test task priority ordering"""
        high_task = AgentTask(
            id="high_task",
            agent_role=AgentRole.ENGINEER,
            task_type="implementation",
            description="High priority task",
            priority=TaskPriority.HIGH
        )
        
        low_task = AgentTask(
            id="low_task",
            agent_role=AgentRole.ENGINEER,
            task_type="implementation", 
            description="Low priority task",
            priority=TaskPriority.LOW
        )
        
        self.scheduler.add_task(low_task)
        self.scheduler.add_task(high_task)
        
        ready_tasks = self.scheduler.get_ready_tasks(set())
        assert len(ready_tasks) == 2
        assert ready_tasks[0].id == "high_task"  # High priority first
        assert ready_tasks[1].id == "low_task"
    
    def test_validate_dependencies(self):
        """Test dependency validation"""
        # Add task with missing dependency
        task = AgentTask(
            id="task1",
            agent_role=AgentRole.ENGINEER,
            task_type="implementation",
            description="Task with missing dependency",
            dependencies=["missing_task"]
        )
        
        self.scheduler.add_task(task)
        errors = self.scheduler.validate_dependencies()
        assert len(errors) == 1
        assert "missing_task" in errors[0]


class TestAgentStateManager:
    """Test agent state manager functionality"""
    
    def setup_method(self):
        self.manager = AgentStateManager()
    
    def test_create_agent(self):
        """Test creating an agent"""
        agent = self.manager.create_agent("agent1", AgentRole.ENGINEER)
        
        assert agent.id == "agent1"
        assert agent.role == AgentRole.ENGINEER
        assert agent.state == AgentState.IDLE
        assert "agent1" in self.manager.agents
    
    def test_get_agent_by_role(self):
        """Test getting agent by role"""
        agent = self.manager.create_agent("agent1", AgentRole.ENGINEER)
        
        found_agent = self.manager.get_agent_by_role(AgentRole.ENGINEER)
        assert found_agent == agent
        
        # Test non-existent role
        not_found = self.manager.get_agent_by_role(AgentRole.QA_ENGINEER)
        assert not_found is None
    
    def test_assign_task(self):
        """Test assigning task to agent"""
        agent = self.manager.create_agent("agent1", AgentRole.ENGINEER)
        task = AgentTask(
            id="task1",
            agent_role=AgentRole.ENGINEER,
            task_type="implementation",
            description="Test task"
        )
        
        self.manager.assign_task("agent1", task)
        
        assert agent.current_task == task
        assert agent.state == AgentState.EXECUTING
    
    def test_complete_task(self):
        """Test completing a task"""
        agent = self.manager.create_agent("agent1", AgentRole.ENGINEER)
        task = AgentTask(
            id="task1",
            agent_role=AgentRole.ENGINEER,
            task_type="implementation",
            description="Test task"
        )
        
        self.manager.assign_task("agent1", task)
        self.manager.complete_task("agent1", {"result": "success"})
        
        assert agent.current_task is None
        assert agent.state == AgentState.COMPLETED
        assert "task1" in agent.completed_tasks
        assert task.result == {"result": "success"}
    
    def test_get_available_agents(self):
        """Test getting available agents"""
        agent1 = self.manager.create_agent("agent1", AgentRole.ENGINEER)
        agent2 = self.manager.create_agent("agent2", AgentRole.QA_ENGINEER)
        
        # Both should be available initially
        available = self.manager.get_available_agents()
        assert len(available) == 2
        
        # Assign task to one agent
        task = AgentTask(
            id="task1",
            agent_role=AgentRole.ENGINEER,
            task_type="implementation",
            description="Test task"
        )
        self.manager.assign_task("agent1", task)
        
        # Only one should be available now
        available = self.manager.get_available_agents()
        assert len(available) == 1
        assert available[0] == agent2


@pytest.mark.asyncio
class TestIntegration:
    """Integration tests for orchestration components"""
    
    async def test_task_execution_flow(self):
        """Test complete task execution flow"""
        scheduler = TaskScheduler()
        manager = AgentStateManager()
        
        # Create agent
        agent = manager.create_agent("agent1", AgentRole.ENGINEER)
        
        # Create task
        task = AgentTask(
            id="task1",
            agent_role=AgentRole.ENGINEER,
            task_type="implementation",
            description="Test implementation task"
        )
        
        # Add task to scheduler
        scheduler.add_task(task)
        
        # Get ready tasks
        ready_tasks = scheduler.get_ready_tasks(set())
        assert len(ready_tasks) == 1
        
        # Assign task to agent
        manager.assign_task("agent1", ready_tasks[0])
        
        # Complete task
        manager.complete_task("agent1", {"code": "print('hello')"})
        
        # Mark task as completed in scheduler
        newly_available = scheduler.mark_task_completed("task1")
        
        # Verify final state
        assert agent.state == AgentState.COMPLETED
        assert len(agent.completed_tasks) == 1
        assert task.result == {"code": "print('hello')"}


if __name__ == "__main__":
    pytest.main([__file__])