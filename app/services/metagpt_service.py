"""
MetaGPT service for multi-agent app generation
"""

import asyncio
import uuid
import os
import tempfile
import shutil
from typing import Dict, List, Optional
import logging
from datetime import datetime
from pathlib import Path

from app.models.schemas import (
    GenerationRequest, AgentRole, GeneratedArtifact
)
from app.services.websocket_manager import websocket_manager
from app.core.config import settings

logger = logging.getLogger(__name__)

class MetaGPTService:
    """Service for orchestrating real MetaGPT agents"""
    
    def __init__(self):
        self.active_generations: Dict[str, Dict] = {}
        self._setup_metagpt()
    
    def _setup_metagpt(self):
        """Initialize MetaGPT configuration"""
        try:
            # Set up MetaGPT environment variables
            if settings.OPENAI_API_KEY:
                os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY
            if settings.ANTHROPIC_API_KEY:
                os.environ["ANTHROPIC_API_KEY"] = settings.ANTHROPIC_API_KEY
            if settings.METAGPT_API_KEY:
                os.environ["METAGPT_API_KEY"] = settings.METAGPT_API_KEY
            
            # Set workspace
            os.environ["METAGPT_WORKSPACE"] = settings.METAGPT_WORKSPACE
            os.environ["METAGPT_LOG_LEVEL"] = settings.METAGPT_LOG_LEVEL
            
            # Create workspace directory if it doesn't exist
            workspace_path = Path(settings.METAGPT_WORKSPACE)
            workspace_path.mkdir(parents=True, exist_ok=True)
            
            logger.info("✅ MetaGPT configuration initialized")
            
        except Exception as e:
            logger.error(f"Failed to setup MetaGPT: {e}")
    
    async def generate_app(
        self, 
        request: GenerationRequest, 
        client_id: Optional[str] = None
    ) -> str:
        """Start app generation process using real MetaGPT"""
        generation_id = str(uuid.uuid4())
        
        # Store generation info
        self.active_generations[generation_id] = {
            "request": request,
            "status": "started",
            "progress": 0,
            "artifacts": [],
            "client_id": client_id,
            "created_at": datetime.now(),
            "workspace_path": None
        }
        
        # Start generation in background
        asyncio.create_task(self._run_metagpt_generation(generation_id))
        
        return generation_id
    
    async def _run_metagpt_generation(self, generation_id: str):
        """Run the complete generation process using MetaGPT"""
        try:
            generation_data = self.active_generations[generation_id]
            request = generation_data["request"]
            client_id = generation_data.get("client_id")
            
            # Update status
            await self._update_progress(generation_id, "initializing", 5, "Initializing MetaGPT...")
            
            # Import MetaGPT components
            from metagpt.software_company import SoftwareCompany
            from metagpt.team import Team
            from metagpt.roles import ProductManager, Architect, ProjectManager, Engineer, QaEngineer
            
            # Create workspace for this generation
            workspace_path = Path(settings.METAGPT_WORKSPACE) / generation_id
            workspace_path.mkdir(parents=True, exist_ok=True)
            generation_data["workspace_path"] = str(workspace_path)
            
            await self._update_progress(generation_id, "running", 10, "Setting up MetaGPT team...")
            
            # Create team based on selected agents
            team_roles = []
            role_mapping = {
                AgentRole.PRODUCT_MANAGER: ProductManager,
                AgentRole.ARCHITECT: Architect,
                AgentRole.PROJECT_MANAGER: ProjectManager,
                AgentRole.ENGINEER: Engineer,
                AgentRole.QA_ENGINEER: QaEngineer
            }
            
            for agent_role in request.active_agents:
                if agent_role in role_mapping:
                    team_roles.append(role_mapping[agent_role]())
            
            # Create software company
            company = SoftwareCompany()
            company.hire(team_roles)
            
            await self._update_progress(generation_id, "running", 20, "Starting MetaGPT generation...")
            
            # Send real-time updates
            if client_id:
                await websocket_manager.send_message(
                    client_id,
                    {
                        "type": "agent_update",
                        "agent": "metagpt_orchestrator",
                        "status": "running",
                        "message": f"Running MetaGPT with {len(team_roles)} agents",
                        "progress": 25
                    }
                )
            
            # Run MetaGPT generation
            await self._run_metagpt_company(company, request, generation_id, workspace_path)
            
            # Process generated artifacts
            await self._process_metagpt_artifacts(generation_id, workspace_path)
            
            # Finalize
            await self._update_progress(generation_id, "completed", 100, "MetaGPT generation completed!")
            
        except Exception as e:
            logger.error(f"MetaGPT generation {generation_id} failed: {e}")
            await self._update_progress(generation_id, "failed", 0, f"Generation failed: {str(e)}")
            
            # Cleanup on failure
            try:
                self.cleanup_generation(generation_id)
            except Exception as cleanup_error:
                logger.error(f"Cleanup failed for {generation_id}: {cleanup_error}")
    
    async def _run_metagpt_company(self, company, request: GenerationRequest, generation_id: str, workspace_path: Path):
        """Run the MetaGPT software company"""
        try:
            client_id = self.active_generations[generation_id].get("client_id")
            
            # Prepare the requirement with context
            enhanced_requirement = self._enhance_requirement(request)
            
            await self._update_progress(generation_id, "running", 30, "MetaGPT agents analyzing requirements...")
            
            # Set workspace for this generation
            os.environ["METAGPT_WORKSPACE"] = str(workspace_path)
            
            # Run the company with the requirement in executor to avoid blocking
            def run_metagpt_sync():
                try:
                    # This is the actual MetaGPT execution
                    return company.run_project(enhanced_requirement)
                except Exception as e:
                    logger.error(f"MetaGPT execution error: {e}")
                    raise
            
            # Execute MetaGPT in thread pool to avoid blocking event loop
            result = await asyncio.get_event_loop().run_in_executor(
                None,
                run_metagpt_sync
            )
            
            # Send progress updates during execution
            progress_steps = [40, 50, 60, 70, 80, 90]
            agent_names = ["Product Manager", "Architect", "Project Manager", "Engineer", "QA Engineer"]
            
            for i, (progress, agent_name) in enumerate(zip(progress_steps, agent_names)):
                if client_id:
                    await websocket_manager.send_agent_update(
                        client_id,
                        agent_name.lower().replace(" ", "_"),
                        "running" if i < len(progress_steps) - 1 else "completed",
                        current_task=f"{agent_name} working on requirements",
                        progress=progress
                    )
                await asyncio.sleep(0.5)  # Small delay for realistic progress
            
            logger.info(f"✅ MetaGPT company execution completed for {generation_id}")
            return result
            
        except Exception as e:
            logger.error(f"MetaGPT company execution failed: {e}")
            # Send error update via WebSocket
            client_id = self.active_generations[generation_id].get("client_id")
            if client_id:
                await websocket_manager.send_error(
                    client_id,
                    f"MetaGPT execution failed: {str(e)}",
                    "metagpt_error"
                )
            raise
    
    def _enhance_requirement(self, request: GenerationRequest) -> str:
        """Enhance the requirement with additional context"""
        enhanced = f"""
Project Requirement: {request.requirement}

Application Type: {request.app_type.value}
Target Technology Stack: {', '.join(request.tech_stack) if request.tech_stack else 'Modern web technologies'}

Additional Context:
- Create a complete, production-ready application
- Include proper error handling and validation
- Follow best practices for the chosen technology stack
- Generate comprehensive documentation
- Include testing strategies where applicable

Please create a full application that meets these requirements with proper architecture and implementation.
"""
        return enhanced.strip()
    
    async def _process_metagpt_artifacts(self, generation_id: str, workspace_path: Path):
        """Process artifacts generated by MetaGPT"""
        try:
            generation_data = self.active_generations[generation_id]
            client_id = generation_data.get("client_id")
            
            await self._update_progress(generation_id, "processing", 95, "Processing generated artifacts...")
            
            # Find all generated files in the workspace
            artifacts = []
            
            # Common file patterns to look for
            file_patterns = [
                "**/*.md",    # Documentation
                "**/*.py",    # Python code
                "**/*.js",    # JavaScript
                "**/*.jsx",   # React
                "**/*.ts",    # TypeScript
                "**/*.tsx",   # TypeScript React
                "**/*.html",  # HTML
                "**/*.css",   # CSS
                "**/*.json",  # Configuration
                "**/*.yml",   # YAML configs
                "**/*.yaml",  # YAML configs
                "**/*.txt",   # Text files
            ]
            
            for pattern in file_patterns:
                for file_path in workspace_path.glob(pattern):
                    if file_path.is_file() and file_path.stat().st_size > 0:
                        try:
                            content = file_path.read_text(encoding='utf-8')
                            
                            # Determine artifact type
                            artifact_type = self._determine_artifact_type(file_path)
                            
                            # Create artifact
                            artifact = GeneratedArtifact(
                                id=str(uuid.uuid4()),
                                name=file_path.name,
                                type=artifact_type,
                                content=content,
                                agent_role=self._determine_agent_role(file_path),
                                file_path=str(file_path.relative_to(workspace_path))
                            )
                            
                            artifacts.append(artifact)
                            
                            # Send artifact update
                            if client_id:
                                await websocket_manager.send_artifact_update(
                                    client_id,
                                    {
                                        "id": artifact.id,
                                        "name": artifact.name,
                                        "type": artifact.type,
                                        "content": artifact.content,
                                        "agent_role": artifact.agent_role,
                                        "status": "completed",
                                        "progress": 100
                                    }
                                )
                            
                        except Exception as e:
                            logger.warning(f"Could not read file {file_path}: {e}")
            
            # Store artifacts
            generation_data["artifacts"] = artifacts
            
            logger.info(f"✅ Processed {len(artifacts)} artifacts for generation {generation_id}")
            
        except Exception as e:
            logger.error(f"Failed to process MetaGPT artifacts: {e}")
    
    def _determine_artifact_type(self, file_path: Path) -> str:
        """Determine artifact type based on file extension"""
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
    
    def _determine_agent_role(self, file_path: Path) -> str:
        """Determine which agent likely created this artifact"""
        file_name = file_path.name.lower()
        path_str = str(file_path).lower()
        
        if any(keyword in file_name for keyword in ['requirements', 'prd', 'product']):
            return 'product_manager'
        elif any(keyword in file_name for keyword in ['architecture', 'design', 'system']):
            return 'architect'
        elif any(keyword in file_name for keyword in ['project', 'plan', 'timeline']):
            return 'project_manager'
        elif any(keyword in path_str for keyword in ['test', 'spec', 'qa']):
            return 'qa_engineer'
        elif any(keyword in file_name for keyword in ['deploy', 'docker', 'ci', 'cd']):
            return 'devops'
        else:
            return 'engineer'
    
    async def _update_progress(
        self, 
        generation_id: str, 
        status: str, 
        progress: int, 
        message: str,
        current_agent: Optional[str] = None
    ):
        """Update generation progress"""
        if generation_id in self.active_generations:
            generation_data = self.active_generations[generation_id]
            generation_data.update({
                "status": status,
                "progress": progress,
                "last_message": message,
                "updated_at": datetime.now()
            })
            
            if current_agent:
                generation_data["current_agent"] = current_agent
            
            # Send WebSocket update
            client_id = generation_data.get("client_id")
            if client_id:
                await websocket_manager.send_progress_update(
                    client_id,
                    generation_id,
                    status,
                    progress,
                    message
                )
    
    def get_generation_status(self, generation_id: str) -> Optional[Dict]:
        """Get generation status"""
        return self.active_generations.get(generation_id)
    
    def get_generation_artifacts(self, generation_id: str) -> List[GeneratedArtifact]:
        """Get generation artifacts"""
        generation_data = self.active_generations.get(generation_id)
        if generation_data:
            return generation_data.get("artifacts", [])
        return []
    
    def cleanup_generation(self, generation_id: str):
        """Clean up generation workspace"""
        try:
            generation_data = self.active_generations.get(generation_id)
            if generation_data and generation_data.get("workspace_path"):
                workspace_path = Path(generation_data["workspace_path"])
                if workspace_path.exists():
                    shutil.rmtree(workspace_path)
                    logger.info(f"✅ Cleaned up workspace for generation {generation_id}")
        except Exception as e:
            logger.error(f"Failed to cleanup generation {generation_id}: {e}")

# Global service instance
metagpt_service = MetaGPTService()