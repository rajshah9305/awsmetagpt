"""
MetaGPT execution and integration
"""

import asyncio
import os
import yaml
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from app.core.logging import get_logger
from app.core.exceptions import MetaGPTException
from app.core.config import settings
from app.models.schemas import AgentRole, GenerationRequest, BedrockModel
from .models import AgentTask, AgentInstance

logger = get_logger(__name__)


class MetaGPTExecutor:
    """Handles MetaGPT execution and configuration"""
    
    def __init__(self):
        self.metagpt_configured = False
        self._setup_metagpt()
    
    def _setup_metagpt(self) -> None:
        """Initialize MetaGPT with Bedrock configuration"""
        try:
            # Create MetaGPT config directory
            config_dir = Path.home() / ".metagpt"
            config_dir.mkdir(exist_ok=True)
            
            # Create Bedrock configuration for MetaGPT
            bedrock_config = {
                "llm": {
                    "api_type": "bedrock",
                    "model": settings.BEDROCK_MODEL,
                    "aws_access_key_id": settings.AWS_ACCESS_KEY_ID,
                    "aws_secret_access_key": settings.AWS_SECRET_ACCESS_KEY,
                    "aws_region": settings.AWS_REGION,
                    "max_tokens": 4000,
                    "temperature": 0.7
                }
            }
            
            config_file = config_dir / "config2.yaml"
            with open(config_file, 'w') as f:
                yaml.dump(bedrock_config, f, default_flow_style=False)
            
            # Set environment variables
            env_vars = settings.get_env_vars()
            for key, value in env_vars.items():
                os.environ[key] = value
            
            # Create workspace directory
            workspace_path = Path(settings.METAGPT_WORKSPACE)
            if not workspace_path.is_absolute():
                workspace_path = Path.cwd() / workspace_path
            workspace_path.mkdir(parents=True, exist_ok=True)
            
            self.metagpt_configured = True
            logger.info(f"MetaGPT configured with model: {settings.BEDROCK_MODEL}")
            
        except Exception as e:
            logger.error(f"Failed to setup MetaGPT: {e}")
            raise MetaGPTException(f"MetaGPT setup failed: {e}")
    
    def update_model(self, model: BedrockModel) -> None:
        """Update MetaGPT configuration with new model"""
        try:
            config_dir = Path.home() / ".metagpt"
            config_file = config_dir / "config2.yaml"
            
            # Model mapping for MetaGPT
            model_mapping = {
                BedrockModel.NOVA_PRO: "us.amazon.nova-pro-v1:0",
                BedrockModel.NOVA_LITE: "us.amazon.nova-lite-v1:0",
                BedrockModel.NOVA_MICRO: "us.amazon.nova-micro-v1:0",
                BedrockModel.CLAUDE_SONNET_4: "us.anthropic.claude-sonnet-4-20250514-v1:0",
                BedrockModel.LLAMA_33_70B: "us.meta.llama3-3-70b-instruct-v1:0",
                BedrockModel.LLAMA_32_90B: "us.meta.llama3-2-90b-instruct-v1:0"
            }
            
            metagpt_model = model_mapping.get(model, model.value)
            
            # Update config
            bedrock_config = {
                "llm": {
                    "api_type": "bedrock",
                    "model": metagpt_model,
                    "aws_access_key_id": settings.AWS_ACCESS_KEY_ID,
                    "aws_secret_access_key": settings.AWS_SECRET_ACCESS_KEY,
                    "aws_region": settings.AWS_REGION,
                    "max_tokens": 4000,
                    "temperature": 0.7
                }
            }
            
            with open(config_file, 'w') as f:
                yaml.dump(bedrock_config, f, default_flow_style=False)
            
            logger.info(f"Updated MetaGPT model to: {metagpt_model}")
            
        except Exception as e:
            logger.error(f"Failed to update MetaGPT model: {e}")
            raise MetaGPTException(f"Model update failed: {e}")
    
    async def execute_generation(
        self, 
        request: GenerationRequest, 
        session_id: str,
        progress_callback: Optional[callable] = None
    ) -> Dict[str, Any]:
        """Execute MetaGPT generation process"""
        if not self.metagpt_configured:
            raise MetaGPTException("MetaGPT not configured")
        
        try:
            # Update model if different from current
            if request.preferred_model != BedrockModel(settings.BEDROCK_MODEL):
                self.update_model(request.preferred_model)
            
            # Import MetaGPT (lazy import to avoid startup issues)
            from metagpt.software_company import SoftwareCompany
            from metagpt.roles import (
                ProductManager, Architect, ProjectManager, 
                Engineer, QaEngineer
            )
            
            if progress_callback:
                await progress_callback(10, "Initializing MetaGPT company...")
            
            # Create software company
            company = SoftwareCompany()
            
            # Map agent roles to MetaGPT roles
            role_mapping = {
                AgentRole.PRODUCT_MANAGER: ProductManager,
                AgentRole.ARCHITECT: Architect,
                AgentRole.PROJECT_MANAGER: ProjectManager,
                AgentRole.ENGINEER: Engineer,
                AgentRole.QA_ENGINEER: QaEngineer
            }
            
            # Hire agents based on request
            team_roles = []
            for role in request.active_agents:
                if role in role_mapping:
                    team_roles.append(role_mapping[role]())
            
            company.hire(team_roles)
            
            if progress_callback:
                await progress_callback(20, "Starting MetaGPT generation...")
            
            # Enhanced requirement with context
            enhanced_requirement = self._enhance_requirement(request)
            
            # Execute in thread pool to avoid blocking
            result = await asyncio.get_event_loop().run_in_executor(
                None, 
                lambda: company.run_project(enhanced_requirement)
            )
            
            if progress_callback:
                await progress_callback(90, "Processing MetaGPT results...")
            
            # Process results
            artifacts = await self._process_metagpt_results(result, session_id)
            
            return {
                'success': True,
                'artifacts': artifacts,
                'session_id': session_id,
                'model_used': request.preferred_model.value
            }
            
        except Exception as e:
            logger.error(f"MetaGPT execution failed: {e}")
            raise MetaGPTException(f"Generation failed: {e}")
    
    def _enhance_requirement(self, request: GenerationRequest) -> str:
        """Enhance the requirement with additional context"""
        enhanced = f"""
Project Requirement:
{request.requirement}

Application Type: {request.app_type.value}
Target Technology Stack: {', '.join(request.tech_stack_preferences) if request.tech_stack_preferences else 'Modern web technologies'}
AI Model: {request.preferred_model.value} (AWS Bedrock)
Priority: {request.priority.value}

Additional Context:
{request.additional_requirements or 'None specified'}

Please generate a complete, production-ready application with:
1. Clean, well-documented code
2. Proper error handling
3. Security best practices
4. Scalable architecture
5. Comprehensive testing
6. Deployment configuration
"""
        return enhanced
    
    async def _process_metagpt_results(self, result: Any, session_id: str) -> List[Dict[str, Any]]:
        """Process MetaGPT results into artifacts"""
        artifacts = []
        
        try:
            # Get workspace path
            workspace_path = Path(settings.METAGPT_WORKSPACE) / session_id
            
            if workspace_path.exists():
                # Process generated files
                for file_path in workspace_path.rglob("*"):
                    if file_path.is_file() and not file_path.name.startswith('.'):
                        try:
                            content = file_path.read_text(encoding='utf-8')
                            
                            artifact = {
                                'id': f"{session_id}_{file_path.name}",
                                'name': file_path.name,
                                'type': self._determine_file_type(file_path),
                                'content': content,
                                'agent_role': 'metagpt',
                                'file_path': str(file_path.relative_to(workspace_path)),
                                'size': len(content),
                                'created_at': datetime.now().isoformat(),
                                'language': self._detect_language(file_path)
                            }
                            
                            artifacts.append(artifact)
                            
                        except Exception as e:
                            logger.warning(f"Failed to process file {file_path}: {e}")
            
            logger.info(f"Processed {len(artifacts)} artifacts from MetaGPT")
            return artifacts
            
        except Exception as e:
            logger.error(f"Failed to process MetaGPT results: {e}")
            return []
    
    def _determine_file_type(self, file_path: Path) -> str:
        """Determine file type based on extension"""
        extension = file_path.suffix.lower()
        
        type_mapping = {
            '.py': 'code',
            '.js': 'code',
            '.jsx': 'code',
            '.ts': 'code',
            '.tsx': 'code',
            '.html': 'code',
            '.css': 'code',
            '.scss': 'code',
            '.json': 'configuration',
            '.yaml': 'configuration',
            '.yml': 'configuration',
            '.toml': 'configuration',
            '.md': 'documentation',
            '.txt': 'documentation',
            '.rst': 'documentation',
            '.dockerfile': 'configuration',
            '.env': 'configuration'
        }
        
        return type_mapping.get(extension, 'other')
    
    def _detect_language(self, file_path: Path) -> Optional[str]:
        """Detect programming language from file extension"""
        extension = file_path.suffix.lower()
        
        language_mapping = {
            '.py': 'python',
            '.js': 'javascript',
            '.jsx': 'javascript',
            '.ts': 'typescript',
            '.tsx': 'typescript',
            '.html': 'html',
            '.css': 'css',
            '.scss': 'scss',
            '.json': 'json',
            '.yaml': 'yaml',
            '.yml': 'yaml',
            '.toml': 'toml',
            '.md': 'markdown',
            '.sql': 'sql',
            '.sh': 'bash',
            '.dockerfile': 'dockerfile'
        }
        
        return language_mapping.get(extension)
    
    def get_supported_roles(self) -> List[AgentRole]:
        """Get list of supported agent roles"""
        return [
            AgentRole.PRODUCT_MANAGER,
            AgentRole.ARCHITECT,
            AgentRole.PROJECT_MANAGER,
            AgentRole.ENGINEER,
            AgentRole.QA_ENGINEER
        ]
    
    def validate_request(self, request: GenerationRequest) -> List[str]:
        """Validate generation request"""
        errors = []
        
        # Check if MetaGPT is configured
        if not self.metagpt_configured:
            errors.append("MetaGPT not configured")
        
        # Validate agent roles
        supported_roles = self.get_supported_roles()
        for role in request.active_agents:
            if role not in supported_roles:
                errors.append(f"Unsupported agent role: {role}")
        
        # Validate requirement length
        if len(request.requirement) < 10:
            errors.append("Requirement too short (minimum 10 characters)")
        
        if len(request.requirement) > 50000:
            errors.append("Requirement too long (maximum 50,000 characters)")
        
        return errors