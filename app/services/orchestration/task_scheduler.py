"""
Task scheduling and dependency management
"""

from typing import Dict, List, Optional, Set
import asyncio
from datetime import datetime

from app.core.logging import get_logger
from app.core.exceptions import TaskException, OrchestrationException
from .models import AgentTask, TaskStatus, TaskPriority, AgentInstance

logger = get_logger(__name__)


class TaskScheduler:
    """Manages task scheduling and dependency resolution"""
    
    def __init__(self):
        self.task_registry: Dict[str, AgentTask] = {}
        self.dependency_graph: Dict[str, Set[str]] = {}
        self.reverse_dependencies: Dict[str, Set[str]] = {}
    
    def add_task(self, task: AgentTask) -> None:
        """Add a task to the scheduler"""
        if task.id in self.task_registry:
            raise TaskException(f"Task {task.id} already exists")
        
        self.task_registry[task.id] = task
        self.dependency_graph[task.id] = set(task.dependencies)
        
        # Build reverse dependency graph
        for dep in task.dependencies:
            if dep not in self.reverse_dependencies:
                self.reverse_dependencies[dep] = set()
            self.reverse_dependencies[dep].add(task.id)
        
        logger.info(f"Added task {task.id} with dependencies: {task.dependencies}")
    
    def get_ready_tasks(self, completed_tasks: Set[str]) -> List[AgentTask]:
        """Get tasks that are ready to execute"""
        ready_tasks = []
        
        for task_id, task in self.task_registry.items():
            if (task.status == TaskStatus.PENDING and 
                self.dependency_graph[task_id].issubset(completed_tasks)):
                ready_tasks.append(task)
        
        # Sort by priority
        ready_tasks.sort(key=lambda t: self._priority_value(t.priority), reverse=True)
        return ready_tasks
    
    def mark_task_completed(self, task_id: str) -> List[str]:
        """Mark task as completed and return newly available tasks"""
        if task_id not in self.task_registry:
            raise TaskException(f"Task {task_id} not found")
        
        task = self.task_registry[task_id]
        task.status = TaskStatus.COMPLETED
        task.completed_at = datetime.now()
        
        # Find tasks that might now be ready
        newly_available = []
        if task_id in self.reverse_dependencies:
            for dependent_task_id in self.reverse_dependencies[task_id]:
                dependent_task = self.task_registry[dependent_task_id]
                if dependent_task.status == TaskStatus.PENDING:
                    newly_available.append(dependent_task_id)
        
        logger.info(f"Task {task_id} completed, newly available: {newly_available}")
        return newly_available
    
    def mark_task_failed(self, task_id: str, error: str) -> None:
        """Mark task as failed"""
        if task_id not in self.task_registry:
            raise TaskException(f"Task {task_id} not found")
        
        task = self.task_registry[task_id]
        task.status = TaskStatus.FAILED
        task.error = error
        task.completed_at = datetime.now()
        
        logger.error(f"Task {task_id} failed: {error}")
    
    def can_retry_task(self, task_id: str) -> bool:
        """Check if task can be retried"""
        if task_id not in self.task_registry:
            return False
        
        task = self.task_registry[task_id]
        return task.can_retry()
    
    def retry_task(self, task_id: str) -> None:
        """Retry a failed task"""
        if task_id not in self.task_registry:
            raise TaskException(f"Task {task_id} not found")
        
        task = self.task_registry[task_id]
        if not task.can_retry():
            raise TaskException(f"Task {task_id} cannot be retried")
        
        task.status = TaskStatus.PENDING
        task.retry_count += 1
        task.error = None
        task.started_at = None
        task.completed_at = None
        
        logger.info(f"Retrying task {task_id} (attempt {task.retry_count})")
    
    def get_task_status(self, task_id: str) -> Optional[TaskStatus]:
        """Get status of a task"""
        task = self.task_registry.get(task_id)
        return task.status if task else None
    
    def get_all_tasks(self) -> List[AgentTask]:
        """Get all tasks"""
        return list(self.task_registry.values())
    
    def get_tasks_by_status(self, status: TaskStatus) -> List[AgentTask]:
        """Get tasks by status"""
        return [task for task in self.task_registry.values() if task.status == status]
    
    def validate_dependencies(self) -> List[str]:
        """Validate task dependencies for cycles and missing tasks"""
        errors = []
        
        # Check for missing dependencies
        all_task_ids = set(self.task_registry.keys())
        for task_id, dependencies in self.dependency_graph.items():
            missing_deps = dependencies - all_task_ids
            if missing_deps:
                errors.append(f"Task {task_id} has missing dependencies: {missing_deps}")
        
        # Check for cycles using DFS
        visited = set()
        rec_stack = set()
        
        def has_cycle(node: str) -> bool:
            if node in rec_stack:
                return True
            if node in visited:
                return False
            
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in self.dependency_graph.get(node, set()):
                if has_cycle(neighbor):
                    return True
            
            rec_stack.remove(node)
            return False
        
        for task_id in self.task_registry:
            if task_id not in visited:
                if has_cycle(task_id):
                    errors.append(f"Circular dependency detected involving task {task_id}")
        
        return errors
    
    def get_execution_order(self) -> List[str]:
        """Get optimal execution order using topological sort"""
        # Kahn's algorithm for topological sorting
        in_degree = {task_id: len(deps) for task_id, deps in self.dependency_graph.items()}
        queue = [task_id for task_id, degree in in_degree.items() if degree == 0]
        result = []
        
        while queue:
            # Sort by priority
            queue.sort(key=lambda tid: self._priority_value(self.task_registry[tid].priority), reverse=True)
            current = queue.pop(0)
            result.append(current)
            
            # Update in-degrees of dependent tasks
            for dependent in self.reverse_dependencies.get(current, set()):
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)
        
        if len(result) != len(self.task_registry):
            raise OrchestrationException("Cannot determine execution order due to cycles")
        
        return result
    
    def _priority_value(self, priority: TaskPriority) -> int:
        """Convert priority to numeric value for sorting"""
        priority_map = {
            TaskPriority.LOW: 1,
            TaskPriority.NORMAL: 2,
            TaskPriority.HIGH: 3,
            TaskPriority.CRITICAL: 4
        }
        return priority_map.get(priority, 2)
    
    def get_statistics(self) -> Dict[str, int]:
        """Get scheduler statistics"""
        stats = {
            'total_tasks': len(self.task_registry),
            'pending': len(self.get_tasks_by_status(TaskStatus.PENDING)),
            'running': len(self.get_tasks_by_status(TaskStatus.RUNNING)),
            'completed': len(self.get_tasks_by_status(TaskStatus.COMPLETED)),
            'failed': len(self.get_tasks_by_status(TaskStatus.FAILED)),
            'cancelled': len(self.get_tasks_by_status(TaskStatus.CANCELLED))
        }
        return stats