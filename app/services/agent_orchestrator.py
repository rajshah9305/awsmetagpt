"""
Production-ready MetaGPT Agent Orchestration System
Handles agent lifecycle, coordination, and state management
"""

import asyncio
import uuid
import logging
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
from pathlib import Path
import json
import traceback

from app.models.schemas import AgentRole, GenerationRequest
from app.services.websocket_manager import websocket_manager
from app.services.e2b_service import e2b_service
from app.core.config import settings

logger = logging.getLogger(__name__)

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

@dataclass
class AgentTask:
    """Represents a task for an agent"""
    id: str
    agent_role: AgentRole
    task_type: str
    description: str
    priority: TaskPriority
    dependencies: List[str] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3

@dataclass
class AgentInstance:
    """Represents an active agent instance"""
    id: str
    role: AgentRole
    state: AgentState
    current_task: Optional[AgentTask] = None
    completed_tasks: List[str] = field(default_factory=list)
    failed_tasks: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    workspace_path: Optional[Path] = None
    context: Dict[str, Any] = field(default_factory=dict)
    metrics: Dict[str, Any] = field(default_factory=dict)

class AgentOrchestrator:
    """Production-ready agent orchestration system"""
    
    def __init__(self):
        self.active_sessions: Dict[str, Dict] = {}
        self.agent_instances: Dict[str, AgentInstance] = {}
        self.task_queue: Dict[str, List[AgentTask]] = {}
        self.task_registry: Dict[str, AgentTask] = {}
        self.execution_lock = asyncio.Lock()
        self._setup_metagpt()
    
    def _setup_metagpt(self):
        """Initialize MetaGPT configuration with enhanced settings"""
        try:
            import os
            
            # Core API keys
            if settings.OPENAI_API_KEY:
                os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY
            if settings.ANTHROPIC_API_KEY:
                os.environ["ANTHROPIC_API_KEY"] = settings.ANTHROPIC_API_KEY
            
            # MetaGPT specific configuration
            os.environ["METAGPT_WORKSPACE"] = settings.METAGPT_WORKSPACE
            os.environ["METAGPT_LOG_LEVEL"] = settings.METAGPT_LOG_LEVEL
            
            # Enhanced MetaGPT settings for production
            os.environ["METAGPT_MAX_BUDGET"] = "10.0"  # Budget control
            os.environ["METAGPT_SAVE_LOGS"] = "true"
            os.environ["METAGPT_ENABLE_LONGTERM_MEMORY"] = "true"
            
            # Create workspace
            workspace_path = Path(settings.METAGPT_WORKSPACE)
            workspace_path.mkdir(parents=True, exist_ok=True)
            
            logger.info("✅ Enhanced MetaGPT configuration initialized")
            
        except Exception as e:
            logger.error(f"Failed to setup MetaGPT: {e}")
            raise
    
    async def create_session(
        self, 
        request: GenerationRequest, 
        client_id: Optional[str] = None
    ) -> str:
        """Create a new agent orchestration session"""
        session_id = str(uuid.uuid4())
        
        try:
            # Create session workspace
            session_workspace = Path(settings.METAGPT_WORKSPACE) / session_id
            session_workspace.mkdir(parents=True, exist_ok=True)
            
            # Initialize session
            session_data = {
                "id": session_id,
                "request": request,
                "client_id": client_id,
                "status": "initializing",
                "progress": 0,
                "created_at": datetime.now(),
                "workspace_path": session_workspace,
                "agents": [],
                "tasks": [],
                "artifacts": [],
                "metrics": {
                    "total_tasks": 0,
                    "completed_tasks": 0,
                    "failed_tasks": 0,
                    "execution_time": 0,
                    "tokens_used": 0
                }
            }
            
            self.active_sessions[session_id] = session_data
            self.task_queue[session_id] = []
            
            # Create and initialize agents
            await self._initialize_agents(session_id, request.active_agents)
            
            # Generate execution plan
            await self._generate_execution_plan(session_id, request)
            
            # Start execution
            asyncio.create_task(self._execute_session(session_id))
            
            logger.info(f"✅ Created orchestration session {session_id}")
            return session_id
            
        except Exception as e:
            logger.error(f"Failed to create session: {e}")
            await self._cleanup_session(session_id)
            raise
    
    async def _initialize_agents(self, session_id: str, agent_roles: List[AgentRole]):
        """Initialize agent instances for the session"""
        try:
            session_data = self.active_sessions[session_id]
            workspace_path = session_data["workspace_path"]
            
            for role in agent_roles:
                agent_id = f"{session_id}_{role.value}_{uuid.uuid4().hex[:8]}"
                
                # Create agent workspace
                agent_workspace = workspace_path / role.value
                agent_workspace.mkdir(parents=True, exist_ok=True)
                
                # Initialize agent instance
                agent = AgentInstance(
                    id=agent_id,
                    role=role,
                    state=AgentState.IDLE,
                    workspace_path=agent_workspace,
                    context={
                        "session_id": session_id,
                        "workspace": str(agent_workspace),
                        "role_config": self._get_role_config(role)
                    }
                )
                
                self.agent_instances[agent_id] = agent
                session_data["agents"].append(agent_id)
                
                # Send agent initialization update
                if session_data.get("client_id"):
                    await websocket_manager.send_agent_update(
                        session_data["client_id"],
                        role.value,
                        "initialized",
                        current_task="Agent ready for tasks"
                    )
            
            logger.info(f"✅ Initialized {len(agent_roles)} agents for session {session_id}")
            
        except Exception as e:
            logger.error(f"Failed to initialize agents: {e}")
            raise
    
    def _get_role_config(self, role: AgentRole) -> Dict[str, Any]:
        """Get configuration for specific agent role"""
        configs = {
            AgentRole.PRODUCT_MANAGER: {
                "focus": "requirements_analysis",
                "outputs": ["prd.md", "user_stories.md", "acceptance_criteria.md"],
                "tools": ["research", "analysis", "documentation"]
            },
            AgentRole.ARCHITECT: {
                "focus": "system_design",
                "outputs": ["architecture.md", "tech_stack.md", "api_design.md"],
                "tools": ["design", "modeling", "documentation"]
            },
            AgentRole.PROJECT_MANAGER: {
                "focus": "project_planning",
                "outputs": ["project_plan.md", "timeline.md", "resources.md"],
                "tools": ["planning", "scheduling", "coordination"]
            },
            AgentRole.ENGINEER: {
                "focus": "implementation",
                "outputs": ["*.py", "*.js", "*.jsx", "*.ts", "*.tsx", "*.html", "*.css"],
                "tools": ["coding", "testing", "debugging"]
            },
            AgentRole.QA_ENGINEER: {
                "focus": "quality_assurance",
                "outputs": ["test_plan.md", "test_cases.md", "*.test.py", "*.test.js"],
                "tools": ["testing", "validation", "quality_control"]
            },
            AgentRole.DEVOPS: {
                "focus": "infrastructure",
                "outputs": ["infrastructure.md", "setup.md", "monitoring.md"],
                "tools": ["infrastructure", "monitoring", "automation"]
            }
        }
        return configs.get(role, {})
    
    async def _generate_execution_plan(self, session_id: str, request: GenerationRequest):
        """Generate execution plan with task dependencies"""
        try:
            session_data = self.active_sessions[session_id]
            
            # Define task workflow based on agent roles
            task_plan = []
            
            # Phase 1: Analysis and Planning
            if AgentRole.PRODUCT_MANAGER in request.active_agents:
                task_plan.append(AgentTask(
                    id=f"pm_analysis_{uuid.uuid4().hex[:8]}",
                    agent_role=AgentRole.PRODUCT_MANAGER,
                    task_type="requirements_analysis",
                    description="Analyze requirements and create product specification",
                    priority=TaskPriority.HIGH,
                    context={"requirement": request.requirement, "app_type": request.app_type.value}
                ))
            
            if AgentRole.ARCHITECT in request.active_agents:
                pm_deps = [t.id for t in task_plan if t.agent_role == AgentRole.PRODUCT_MANAGER]
                task_plan.append(AgentTask(
                    id=f"arch_design_{uuid.uuid4().hex[:8]}",
                    agent_role=AgentRole.ARCHITECT,
                    task_type="system_design",
                    description="Design system architecture and technical specifications",
                    priority=TaskPriority.HIGH,
                    dependencies=pm_deps,
                    context={"requirement": request.requirement, "tech_preferences": request.tech_stack_preferences}
                ))
            
            if AgentRole.PROJECT_MANAGER in request.active_agents:
                deps = [t.id for t in task_plan if t.agent_role in [AgentRole.PRODUCT_MANAGER, AgentRole.ARCHITECT]]
                task_plan.append(AgentTask(
                    id=f"pm_planning_{uuid.uuid4().hex[:8]}",
                    agent_role=AgentRole.PROJECT_MANAGER,
                    task_type="project_planning",
                    description="Create project plan and timeline",
                    priority=TaskPriority.NORMAL,
                    dependencies=deps
                ))
            
            # Phase 2: Implementation
            if AgentRole.ENGINEER in request.active_agents:
                deps = [t.id for t in task_plan if t.agent_role in [AgentRole.ARCHITECT, AgentRole.PROJECT_MANAGER]]
                task_plan.append(AgentTask(
                    id=f"eng_implementation_{uuid.uuid4().hex[:8]}",
                    agent_role=AgentRole.ENGINEER,
                    task_type="code_implementation",
                    description="Implement application code based on specifications",
                    priority=TaskPriority.CRITICAL,
                    dependencies=deps,
                    context={"requirement": request.requirement}
                ))
            
            # Phase 3: Quality Assurance
            if AgentRole.QA_ENGINEER in request.active_agents:
                eng_deps = [t.id for t in task_plan if t.agent_role == AgentRole.ENGINEER]
                task_plan.append(AgentTask(
                    id=f"qa_testing_{uuid.uuid4().hex[:8]}",
                    agent_role=AgentRole.QA_ENGINEER,
                    task_type="quality_assurance",
                    description="Create test plans and validate implementation",
                    priority=TaskPriority.HIGH,
                    dependencies=eng_deps
                ))
            
            # Phase 4: Infrastructure
            if AgentRole.DEVOPS in request.active_agents:
                deps = [t.id for t in task_plan if t.agent_role in [AgentRole.ENGINEER, AgentRole.QA_ENGINEER]]
                task_plan.append(AgentTask(
                    id=f"devops_infrastructure_{uuid.uuid4().hex[:8]}",
                    agent_role=AgentRole.DEVOPS,
                    task_type="infrastructure_setup",
                    description="Design infrastructure and operational procedures",
                    priority=TaskPriority.NORMAL,
                    dependencies=deps
                ))
            
            # Store tasks
            for task in task_plan:
                self.task_registry[task.id] = task
                self.task_queue[session_id].append(task)
            
            session_data["tasks"] = [t.id for t in task_plan]
            session_data["metrics"]["total_tasks"] = len(task_plan)
            
            logger.info(f"✅ Generated execution plan with {len(task_plan)} tasks for session {session_id}")
            
        except Exception as e:
            logger.error(f"Failed to generate execution plan: {e}")
            raise
    
    async def _execute_session(self, session_id: str):
        """Execute the session with proper task orchestration"""
        try:
            session_data = self.active_sessions[session_id]
            client_id = session_data.get("client_id")
            
            await self._update_session_progress(session_id, "running", 10, "Starting agent execution...")
            
            # Execute tasks in dependency order
            while self.task_queue[session_id]:
                # Find ready tasks (no pending dependencies)
                ready_tasks = []
                for task in self.task_queue[session_id]:
                    if self._are_dependencies_completed(task, session_id):
                        ready_tasks.append(task)
                
                if not ready_tasks:
                    # Check for deadlock
                    if all(task.dependencies for task in self.task_queue[session_id]):
                        logger.error(f"Deadlock detected in session {session_id}")
                        break
                    
                    # Wait for dependencies
                    await asyncio.sleep(1)
                    continue
                
                # Execute ready tasks concurrently (where possible)
                execution_tasks = []
                for task in ready_tasks:
                    if task.agent_role not in [t.agent_role for t in execution_tasks]:
                        execution_tasks.append(task)
                        self.task_queue[session_id].remove(task)
                
                # Execute tasks
                results = await asyncio.gather(
                    *[self._execute_task(task, session_id) for task in execution_tasks],
                    return_exceptions=True
                )
                
                # Process results
                for task, result in zip(execution_tasks, results):
                    if isinstance(result, Exception):
                        logger.error(f"Task {task.id} failed: {result}")
                        task.error = str(result)
                        session_data["metrics"]["failed_tasks"] += 1
                    else:
                        task.result = result
                        task.completed_at = datetime.now()
                        session_data["metrics"]["completed_tasks"] += 1
                        
                        # Send progress update
                        progress = int((session_data["metrics"]["completed_tasks"] / session_data["metrics"]["total_tasks"]) * 80) + 10
                        await self._update_session_progress(
                            session_id, 
                            "running", 
                            progress, 
                            f"Completed {task.task_type} by {task.agent_role.value}"
                        )
            
            # Process artifacts and create E2B sandbox
            await self._process_session_artifacts(session_id)
            
            # Finalize session
            await self._update_session_progress(session_id, "completed", 100, "Session completed successfully!")
            
        except Exception as e:
            logger.error(f"Session execution failed: {e}")
            await self._update_session_progress(session_id, "failed", 0, f"Session failed: {str(e)}")
        finally:
            # Cleanup after delay
            asyncio.create_task(self._delayed_cleanup(session_id, delay=300))  # 5 minutes
    
    def _are_dependencies_completed(self, task: AgentTask, session_id: str) -> bool:
        """Check if all task dependencies are completed"""
        for dep_id in task.dependencies:
            dep_task = self.task_registry.get(dep_id)
            if not dep_task or not dep_task.completed_at:
                return False
        return True
    
    async def _execute_task(self, task: AgentTask, session_id: str) -> Dict[str, Any]:
        """Execute a single agent task"""
        try:
            session_data = self.active_sessions[session_id]
            client_id = session_data.get("client_id")
            
            # Find agent for this task
            agent_id = None
            for aid in session_data["agents"]:
                agent = self.agent_instances[aid]
                if agent.role == task.agent_role and agent.state == AgentState.IDLE:
                    agent_id = aid
                    break
            
            if not agent_id:
                raise Exception(f"No available agent for role {task.agent_role}")
            
            agent = self.agent_instances[agent_id]
            
            # Update agent state
            agent.state = AgentState.EXECUTING
            agent.current_task = task
            task.started_at = datetime.now()
            
            # Send agent update
            if client_id:
                await websocket_manager.send_agent_update(
                    client_id,
                    task.agent_role.value,
                    "executing",
                    current_task=task.description,
                    progress=0
                )
            
            # Execute task based on type
            result = await self._execute_agent_task(agent, task, session_data)
            
            # Update agent state
            agent.state = AgentState.COMPLETED
            agent.current_task = None
            agent.completed_tasks.append(task.id)
            agent.last_activity = datetime.now()
            
            # Send completion update
            if client_id:
                await websocket_manager.send_agent_update(
                    client_id,
                    task.agent_role.value,
                    "completed",
                    current_task=f"Completed {task.task_type}",
                    progress=100
                )
            
            return result
            
        except Exception as e:
            # Handle task failure
            agent.state = AgentState.FAILED
            agent.failed_tasks.append(task.id)
            
            if client_id:
                await websocket_manager.send_error(
                    client_id,
                    f"Task failed: {str(e)}",
                    "task_execution_error"
                )
            
            logger.error(f"Task execution failed: {e}")
            raise
    
    async def _execute_agent_task(self, agent: AgentInstance, task: AgentTask, session_data: Dict) -> Dict[str, Any]:
        """Execute specific agent task using MetaGPT"""
        try:
            # Import MetaGPT components dynamically
            from metagpt.roles import ProductManager, Architect, ProjectManager, Engineer, QaEngineer
            from metagpt.schema import Message
            from metagpt.actions import Action
            
            # Map roles to MetaGPT classes
            role_classes = {
                AgentRole.PRODUCT_MANAGER: ProductManager,
                AgentRole.ARCHITECT: Architect,
                AgentRole.PROJECT_MANAGER: ProjectManager,
                AgentRole.ENGINEER: Engineer,
                AgentRole.QA_ENGINEER: QaEngineer
            }
            
            if agent.role not in role_classes:
                # Handle DevOps role separately (custom implementation)
                return await self._execute_devops_task(agent, task, session_data)
            
            # Create MetaGPT role instance
            role_class = role_classes[agent.role]
            metagpt_agent = role_class()
            
            # Set workspace
            import os
            os.environ["METAGPT_WORKSPACE"] = str(agent.workspace_path)
            
            # Prepare context from dependencies
            context = await self._gather_task_context(task, session_data)
            
            # Create message for the agent
            message_content = self._create_agent_message(task, context)
            message = Message(content=message_content, role="user")
            
            # Execute agent
            response = await metagpt_agent.run(message)
            
            # Process agent output
            artifacts = await self._process_agent_output(agent, task, response)
            
            return {
                "status": "completed",
                "artifacts": artifacts,
                "response": str(response) if response else None,
                "execution_time": (datetime.now() - task.started_at).total_seconds()
            }
            
        except Exception as e:
            logger.error(f"Agent task execution failed: {e}")
            raise
    
    async def _execute_devops_task(self, agent: AgentInstance, task: AgentTask, session_data: Dict) -> Dict[str, Any]:
        """Execute DevOps task (custom implementation)"""
        try:
            # Gather context from other agents
            context = await self._gather_task_context(task, session_data)
            
            # Generate DevOps artifacts based on context
            artifacts = []
            
            # Infrastructure documentation
            infra_doc = self._generate_infrastructure_doc(context, task)
            infra_path = agent.workspace_path / "infrastructure.md"
            infra_path.write_text(infra_doc)
            artifacts.append({
                "name": "infrastructure.md",
                "type": "documentation",
                "path": str(infra_path),
                "content": infra_doc
            })
            
            # Setup instructions
            setup_doc = self._generate_setup_doc(context, task)
            setup_path = agent.workspace_path / "setup.md"
            setup_path.write_text(setup_doc)
            artifacts.append({
                "name": "setup.md",
                "type": "documentation",
                "path": str(setup_path),
                "content": setup_doc
            })
            
            return {
                "status": "completed",
                "artifacts": artifacts,
                "execution_time": (datetime.now() - task.started_at).total_seconds()
            }
            
        except Exception as e:
            logger.error(f"DevOps task execution failed: {e}")
            raise
    
    def _generate_infrastructure_doc(self, context: Dict, task: AgentTask) -> str:
        """Generate infrastructure documentation"""
        return f"""# Infrastructure Plan

## Project Overview
{context.get('requirement', 'Application infrastructure setup')}

## Technology Stack
- **Application Type**: {context.get('app_type', 'Web Application')}
- **Primary Technologies**: {', '.join(context.get('tech_preferences', ['Modern web stack']))}

## Infrastructure Components

### Application Server
- **Runtime Environment**: Production-ready application server
- **Resource Requirements**: CPU, Memory, Storage based on application needs
- **Scaling Strategy**: Horizontal scaling capabilities

### Database
- **Type**: Based on application requirements
- **Backup Strategy**: Automated backups with point-in-time recovery
- **Performance**: Optimized for application workload

### Monitoring & Logging
- **Application Monitoring**: Performance metrics and health checks
- **Log Aggregation**: Centralized logging system
- **Alerting**: Automated alerts for critical issues

### Security
- **Access Control**: Role-based access management
- **Data Protection**: Encryption at rest and in transit
- **Network Security**: Firewall and network isolation

## Operational Procedures

### Deployment Process
1. Code validation and testing
2. Staging environment deployment
3. Production deployment with rollback capability

### Maintenance
- Regular security updates
- Performance optimization
- Capacity planning

### Disaster Recovery
- Backup verification procedures
- Recovery time objectives (RTO)
- Recovery point objectives (RPO)

Generated on: {datetime.now().isoformat()}
"""
    
    def _generate_setup_doc(self, context: Dict, task: AgentTask) -> str:
        """Generate setup documentation"""
        return f"""# Setup Instructions

## Prerequisites
- System requirements based on application needs
- Required software and dependencies
- Access credentials and permissions

## Installation Steps

### 1. Environment Preparation
```bash
# System updates and basic tools
# Environment configuration
# Security hardening
```

### 2. Application Setup
```bash
# Application installation
# Configuration management
# Service initialization
```

### 3. Database Setup
```bash
# Database installation and configuration
# Schema creation and migration
# User and permission setup
```

### 4. Monitoring Setup
```bash
# Monitoring agent installation
# Dashboard configuration
# Alert rule setup
```

## Configuration

### Environment Variables
- Application-specific configuration
- Database connection strings
- External service credentials

### Service Configuration
- Application server settings
- Database optimization
- Monitoring configuration

## Verification

### Health Checks
- Application endpoint verification
- Database connectivity test
- Monitoring system validation

### Performance Testing
- Load testing procedures
- Performance baseline establishment
- Optimization recommendations

## Troubleshooting

### Common Issues
- Connection problems and solutions
- Performance issues and remediation
- Error handling and recovery

### Support Contacts
- Technical support information
- Escalation procedures
- Documentation resources

Generated on: {datetime.now().isoformat()}
"""
    
    async def _gather_task_context(self, task: AgentTask, session_data: Dict) -> Dict[str, Any]:
        """Gather context from completed dependency tasks"""
        context = task.context.copy()
        
        # Add results from dependency tasks
        for dep_id in task.dependencies:
            dep_task = self.task_registry.get(dep_id)
            if dep_task and dep_task.result:
                context[f"{dep_task.agent_role.value}_output"] = dep_task.result
        
        return context
    
    def _create_agent_message(self, task: AgentTask, context: Dict) -> str:
        """Create message content for MetaGPT agent"""
        base_message = f"""
Task: {task.description}
Type: {task.task_type}
Priority: {task.priority.value}

Context:
"""
        
        for key, value in context.items():
            if isinstance(value, dict):
                base_message += f"- {key}: {json.dumps(value, indent=2)}\n"
            else:
                base_message += f"- {key}: {value}\n"
        
        # Add role-specific instructions
        role_instructions = {
            AgentRole.PRODUCT_MANAGER: """
Please analyze the requirements and create:
1. Product Requirements Document (PRD)
2. User stories and acceptance criteria
3. Business logic and constraints
""",
            AgentRole.ARCHITECT: """
Please design the system architecture and create:
1. System architecture diagram and documentation
2. Technology stack recommendations
3. API design and data models
4. Integration patterns and protocols
""",
            AgentRole.PROJECT_MANAGER: """
Please create the project plan including:
1. Project timeline and milestones
2. Resource allocation and dependencies
3. Risk assessment and mitigation strategies
4. Communication and coordination plan
""",
            AgentRole.ENGINEER: """
Please implement the application including:
1. Core application code following best practices
2. Database schemas and migrations
3. API endpoints and business logic
4. Frontend components and user interface
5. Configuration and environment setup
""",
            AgentRole.QA_ENGINEER: """
Please create the quality assurance plan including:
1. Test strategy and test cases
2. Automated testing setup
3. Quality metrics and acceptance criteria
4. Bug tracking and resolution procedures
"""
        }
        
        base_message += role_instructions.get(task.agent_role, "")
        return base_message.strip()
    
    async def _process_agent_output(self, agent: AgentInstance, task: AgentTask, response: Any) -> List[Dict]:
        """Process agent output and extract artifacts"""
        artifacts = []
        
        try:
            # Scan agent workspace for generated files
            if agent.workspace_path and agent.workspace_path.exists():
                for file_path in agent.workspace_path.rglob("*"):
                    if file_path.is_file() and file_path.stat().st_size > 0:
                        try:
                            content = file_path.read_text(encoding='utf-8')
                            artifacts.append({
                                "name": file_path.name,
                                "type": self._determine_file_type(file_path),
                                "path": str(file_path),
                                "content": content,
                                "agent_role": agent.role.value,
                                "task_id": task.id
                            })
                        except Exception as e:
                            logger.warning(f"Could not read file {file_path}: {e}")
            
            # If no files generated, create artifact from response
            if not artifacts and response:
                artifacts.append({
                    "name": f"{task.task_type}_output.md",
                    "type": "documentation",
                    "content": str(response),
                    "agent_role": agent.role.value,
                    "task_id": task.id
                })
            
        except Exception as e:
            logger.error(f"Failed to process agent output: {e}")
        
        return artifacts
    
    def _determine_file_type(self, file_path: Path) -> str:
        """Determine file type based on extension"""
        suffix = file_path.suffix.lower()
        type_mapping = {
            '.md': 'documentation',
            '.py': 'code',
            '.js': 'code',
            '.jsx': 'code',
            '.ts': 'code',
            '.tsx': 'code',
            '.html': 'code',
            '.css': 'code',
            '.json': 'configuration',
            '.yml': 'configuration',
            '.yaml': 'configuration',
            '.txt': 'documentation'
        }
        return type_mapping.get(suffix, 'file')
    
    async def _process_session_artifacts(self, session_id: str):
        """Process all session artifacts and create E2B sandbox"""
        try:
            session_data = self.active_sessions[session_id]
            client_id = session_data.get("client_id")
            
            # Collect all artifacts from completed tasks
            all_artifacts = []
            for task_id in session_data["tasks"]:
                task = self.task_registry.get(task_id)
                if task and task.result and task.result.get("artifacts"):
                    all_artifacts.extend(task.result["artifacts"])
            
            session_data["artifacts"] = all_artifacts
            
            # Create E2B sandbox if we have code artifacts
            code_artifacts = [a for a in all_artifacts if a.get("type") == "code"]
            if code_artifacts:
                await self._create_e2b_preview(session_id, all_artifacts)
            
            # Send artifact updates
            if client_id:
                for artifact in all_artifacts:
                    await websocket_manager.send_artifact_update(client_id, artifact)
            
            logger.info(f"✅ Processed {len(all_artifacts)} artifacts for session {session_id}")
            
        except Exception as e:
            logger.error(f"Failed to process session artifacts: {e}")
    
    async def _create_e2b_preview(self, session_id: str, artifacts: List[Dict]):
        """Create E2B sandbox preview for code artifacts"""
        try:
            session_data = self.active_sessions[session_id]
            client_id = session_data.get("client_id")
            
            # Create E2B sandbox
            sandbox_id = await e2b_service.create_sandbox(session_id)
            if not sandbox_id:
                logger.warning("Failed to create E2B sandbox")
                return
            
            # Write artifacts to sandbox
            success = await e2b_service.write_files(session_id, artifacts)
            if not success:
                logger.warning("Failed to write files to E2B sandbox")
                return
            
            # Run application in sandbox
            preview_url = await e2b_service.run_application(session_id)
            if preview_url:
                session_data["preview_url"] = preview_url
                
                if client_id:
                    await websocket_manager.send_structured_message({
                        "type": "preview_ready",
                        "session_id": session_id,
                        "preview_url": preview_url
                    }, client_id)
            
            logger.info(f"✅ Created E2B preview for session {session_id}")
            
        except Exception as e:
            logger.error(f"Failed to create E2B preview: {e}")
    
    async def _update_session_progress(self, session_id: str, status: str, progress: int, message: str):
        """Update session progress and notify client"""
        try:
            session_data = self.active_sessions[session_id]
            session_data.update({
                "status": status,
                "progress": progress,
                "last_message": message,
                "updated_at": datetime.now()
            })
            
            client_id = session_data.get("client_id")
            if client_id:
                await websocket_manager.send_progress_update(
                    client_id,
                    session_id,
                    status,
                    progress,
                    message
                )
        except Exception as e:
            logger.error(f"Failed to update session progress: {e}")
    
    async def _delayed_cleanup(self, session_id: str, delay: int = 300):
        """Cleanup session after delay"""
        await asyncio.sleep(delay)
        await self._cleanup_session(session_id)
    
    async def _cleanup_session(self, session_id: str):
        """Cleanup session resources"""
        try:
            if session_id in self.active_sessions:
                session_data = self.active_sessions[session_id]
                
                # Cleanup agents
                for agent_id in session_data.get("agents", []):
                    if agent_id in self.agent_instances:
                        del self.agent_instances[agent_id]
                
                # Cleanup tasks
                for task_id in session_data.get("tasks", []):
                    if task_id in self.task_registry:
                        del self.task_registry[task_id]
                
                # Cleanup task queue
                if session_id in self.task_queue:
                    del self.task_queue[session_id]
                
                # Cleanup E2B sandbox
                await e2b_service.cleanup_sandbox(session_id)
                
                # Cleanup workspace (optional - keep for debugging)
                # workspace_path = session_data.get("workspace_path")
                # if workspace_path and workspace_path.exists():
                #     shutil.rmtree(workspace_path)
                
                del self.active_sessions[session_id]
                
            logger.info(f"✅ Cleaned up session {session_id}")
            
        except Exception as e:
            logger.error(f"Failed to cleanup session {session_id}: {e}")
    
    # Public API methods
    
    def get_session_status(self, session_id: str) -> Optional[Dict]:
        """Get session status"""
        return self.active_sessions.get(session_id)
    
    def get_session_artifacts(self, session_id: str) -> List[Dict]:
        """Get session artifacts"""
        session_data = self.active_sessions.get(session_id)
        return session_data.get("artifacts", []) if session_data else []
    
    def get_agent_status(self, agent_id: str) -> Optional[AgentInstance]:
        """Get agent status"""
        return self.agent_instances.get(agent_id)
    
    async def pause_session(self, session_id: str) -> bool:
        """Pause session execution"""
        # Implementation for pausing session
        pass
    
    async def resume_session(self, session_id: str) -> bool:
        """Resume session execution"""
        # Implementation for resuming session
        pass
    
    async def terminate_session(self, session_id: str) -> bool:
        """Terminate session execution"""
        try:
            await self._cleanup_session(session_id)
            return True
        except Exception as e:
            logger.error(f"Failed to terminate session: {e}")
            return False

# Global orchestrator instance
agent_orchestrator = AgentOrchestrator()