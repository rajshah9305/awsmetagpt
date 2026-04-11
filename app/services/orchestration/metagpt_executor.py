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
from app.models.schemas import AgentRole, GenerationRequest

logger = get_logger(__name__)

# Values copied from .env.example are not real keys — treat as unset
_PLACEHOLDER_MARKERS = (
    "your_openai_api_key_here",
    "your_anthropic_api_key_here",
    "your_api_key_here",
    "changeme",
    "replace_me",
)


def _effective_llm_api_key(raw: str) -> str:
    """Return stripped key if non-empty and not a template placeholder."""
    if not raw:
        return ""
    key = raw.strip()
    if len(key) < 8:
        return ""
    lower = key.lower()
    if lower in _PLACEHOLDER_MARKERS:
        return ""
    if "your_" in lower and "here" in lower:
        return ""
    return key


class MetaGPTExecutor:
    """Handles MetaGPT execution and configuration"""
    
    def __init__(self):
        self.metagpt_configured = False
        self._setup_error: Optional[str] = None
        try:
            self._setup_metagpt()
        except MetaGPTException as e:
            # Defer the error to request time so the server can still start
            self._setup_error = str(e)
            logger.warning(f"MetaGPT not configured at startup: {e}")
    
    def _setup_metagpt(self) -> None:
        """Initialize MetaGPT with proper configuration"""
        try:
            # Create MetaGPT config directory
            config_dir = Path(settings.METAGPT_CONFIG_DIR)
            if not config_dir.is_absolute():
                config_dir = Path.cwd() / config_dir
            config_dir.mkdir(parents=True, exist_ok=True)
            
            # Determine which API to use for MetaGPT
            # MetaGPT 0.8.1 doesn't support 'bedrock' directly
            # We'll use OpenAI or Anthropic API for MetaGPT agents
            api_type = None
            api_key = None
            model = None
            
            openai_key = _effective_llm_api_key(settings.OPENAI_API_KEY)
            anthropic_key = _effective_llm_api_key(settings.ANTHROPIC_API_KEY)

            if openai_key:
                api_type = "openai"
                api_key = openai_key
                model = "gpt-4"
                logger.info("Using OpenAI API for MetaGPT agents")
            elif anthropic_key:
                api_type = "anthropic"
                api_key = anthropic_key
                model = "claude-3-sonnet-20240229"
                logger.info("Using Anthropic API for MetaGPT agents")
            else:
                raise MetaGPTException(
                    "MetaGPT requires OPENAI_API_KEY or ANTHROPIC_API_KEY (direct API keys). "
                    "AWS Bedrock credentials alone do not configure MetaGPT agents. "
                    "Set one of these in .env and restart the server."
                )
            
            # Create MetaGPT configuration
            metagpt_config = {
                "llm": {
                    "api_type": api_type,
                    "model": model,
                    "api_key": api_key,
                    "max_tokens": 4000,
                    "temperature": 0.7
                }
            }
            
            config_file = config_dir / "config2.yaml"
            with open(config_file, 'w') as f:
                yaml.dump(metagpt_config, f, default_flow_style=False)
            
            # Set environment variables for MetaGPT
            os.environ["METAGPT_CONFIG_PATH"] = str(config_dir / "config2.yaml")
            if api_type == "openai" and api_key != "dummy-key-for-development":
                os.environ['OPENAI_API_KEY'] = api_key
            elif api_type == "anthropic":
                os.environ['ANTHROPIC_API_KEY'] = api_key
            
            # Create workspace directory
            workspace_path = Path(settings.METAGPT_WORKSPACE)
            if not workspace_path.is_absolute():
                workspace_path = Path.cwd() / workspace_path
            workspace_path.mkdir(parents=True, exist_ok=True)
            
            self.metagpt_configured = True
            logger.info(f"✅ MetaGPT configured with {api_type} API and model: {model}")
            
        except Exception as e:
            logger.error(f"Failed to setup MetaGPT: {e}")
            raise MetaGPTException(f"MetaGPT setup failed: {e}")

    def _run_metagpt_team_blocking(
        self,
        request: GenerationRequest,
        session_id: str,
        team_role_classes: List[type],
    ) -> Optional[Any]:
        """
        Run MetaGPT Team using the same sequence as upstream ``generate_repo``:
        invest → run_project(idea) → asyncio.run(company.run(n_round=...)).

        See: https://github.com/FoundationAgents/MetaGPT/blob/main/metagpt/software_company.py
        """
        from metagpt.config2 import config
        from metagpt.context import Context
        from metagpt.team import Team
        from metagpt.roles import Engineer

        if not team_role_classes:
            raise MetaGPTException(
                "No MetaGPT agents to run. Select at least one role (e.g. product_manager, engineer)."
            )

        workspace_root = Path(settings.METAGPT_WORKSPACE)
        if not workspace_root.is_absolute():
            workspace_root = Path.cwd() / workspace_root
        workspace_path = workspace_root / session_id
        workspace_path.mkdir(parents=True, exist_ok=True)

        project_name = f"app_{session_id}"
        config.update_via_cli(str(workspace_path), project_name, False, "", 0)
        ctx = Context(config=config)
        company = Team(context=ctx)

        roles_to_hire = []
        for cls in team_role_classes:
            if cls is Engineer:
                roles_to_hire.append(Engineer(n_borg=1, use_code_review=True))
            else:
                roles_to_hire.append(cls())
        company.hire(roles_to_hire)

        investment = 3.0
        if request.priority.value == "high":
            investment = 5.0
        elif request.priority.value == "critical":
            investment = 6.0

        n_round = min(max(request.timeout_minutes // 2, 3), 10)
        idea = self._enhance_requirement(request)

        # Match metagpt.software_company.generate_repo (FoundationAgents/MetaGPT)
        company.invest(investment)
        company.run_project(idea)
        asyncio.run(company.run(n_round=n_round))

        return ctx.repo
    
    async def execute_generation(
        self, 
        request: GenerationRequest, 
        session_id: str,
        progress_callback: Optional[callable] = None
    ) -> Dict[str, Any]:
        """Execute MetaGPT generation process"""
        if not self.metagpt_configured:
            raise MetaGPTException(self._setup_error or "MetaGPT not configured")
        
        try:
            # Log the selected model (MetaGPT uses OpenAI/Anthropic; Bedrock model is informational)
            logger.debug(f"Generation requested with Bedrock model: {request.preferred_model.value}")
            
            # Import MetaGPT (lazy import to avoid startup issues)
            try:
                from metagpt.roles import (
                    ProductManager,
                    Architect,
                    ProjectManager,
                    Engineer,
                    QaEngineer,
                )
            except ImportError as e:
                raise MetaGPTException(
                    f"MetaGPT package not installed. Run: pip install -e \".[metagpt]\" or pip install metagpt==0.8.1. Error: {e}"
                )
            
            if progress_callback:
                await progress_callback(10, "Initializing MetaGPT team...")
            
            # Map agent roles to MetaGPT roles (DevOps maps to Engineer; MetaGPT has no DevOps role)
            role_mapping = {
                AgentRole.PRODUCT_MANAGER: ProductManager,
                AgentRole.ARCHITECT: Architect,
                AgentRole.PROJECT_MANAGER: ProjectManager,
                AgentRole.ENGINEER: Engineer,
                AgentRole.QA_ENGINEER: QaEngineer,
                AgentRole.DEVOPS: Engineer,
            }
            # One hire per MetaGPT role class to avoid duplicate agents when e.g. Engineer + DevOps
            team_role_classes: List[type] = []
            seen_metagpt_classes = set()
            for role in request.active_agents:
                if role not in role_mapping:
                    continue
                cls = role_mapping[role]
                if cls in seen_metagpt_classes:
                    continue
                seen_metagpt_classes.add(cls)
                team_role_classes.append(cls)

            if not team_role_classes:
                raise MetaGPTException(
                    "No compatible agent roles selected. Include at least one: "
                    "product_manager, architect, project_manager, engineer, qa_engineer, or devops."
                )

            if progress_callback:
                await progress_callback(20, "Starting MetaGPT generation...")
            
            loop = asyncio.get_event_loop()

            def _blocking():
                return self._run_metagpt_team_blocking(request, session_id, team_role_classes)

            project_repo = await loop.run_in_executor(None, _blocking)
            
            if progress_callback:
                await progress_callback(90, "Processing MetaGPT results...")
            
            artifacts = await self._process_metagpt_results(session_id, project_repo=project_repo)
            
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
    
    def _workspace_roots_for_session(
        self, session_id: str, project_repo: Optional[Any] = None
    ) -> List[Path]:
        """Paths where MetaGPT may write output (session dir + optional ProjectRepo root)."""
        roots: List[Path] = []
        base = Path(settings.METAGPT_WORKSPACE) / session_id
        if not base.is_absolute():
            base = Path.cwd() / base
        roots.append(base.resolve())
        if project_repo is not None:
            try:
                wd = Path(project_repo.workdir).resolve()
                if wd not in roots:
                    roots.append(wd)
            except Exception as e:
                logger.debug(f"No project_repo.workdir: {e}")
        return roots

    async def _process_metagpt_results(
        self, session_id: str, project_repo: Optional[Any] = None
    ) -> List[Dict[str, Any]]:
        """Collect generated files from MetaGPT workspace(s)."""
        artifacts: List[Dict[str, Any]] = []
        seen_paths: set = set()

        try:
            for workspace_path in self._workspace_roots_for_session(session_id, project_repo):
                if not workspace_path.exists():
                    continue
                for file_path in workspace_path.rglob("*"):
                    if not file_path.is_file() or file_path.name.startswith('.'):
                        continue
                    try:
                        resolved = file_path.resolve()
                        if resolved in seen_paths:
                            continue
                        seen_paths.add(resolved)
                        content = file_path.read_text(encoding='utf-8')
                    except UnicodeDecodeError:
                        logger.warning(f"Skipping binary or non-UTF-8 file: {file_path}")
                        continue
                    except Exception as e:
                        logger.warning(f"Failed to read file {file_path}: {e}")
                        continue

                    try:
                        rel = str(file_path.relative_to(workspace_path))
                    except ValueError:
                        rel = file_path.name

                    artifact = {
                        'id': f"{session_id}_{rel.replace('/', '_')}",
                        'name': file_path.name,
                        'type': self._determine_file_type(file_path),
                        'content': content,
                        'agent_role': 'metagpt',
                        'file_path': rel,
                        'size': len(content),
                        'created_at': datetime.now().isoformat(),
                        'language': self._detect_language(file_path),
                    }
                    artifacts.append(artifact)

            logger.info(f"Processed {len(artifacts)} artifacts from MetaGPT workspace(s)")
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
            AgentRole.QA_ENGINEER,
            AgentRole.DEVOPS,
        ]
    
    def validate_request(self, request: GenerationRequest) -> List[str]:
        """Validate generation request"""
        errors = []
        
        # Check if MetaGPT is configured (needs OpenAI or Anthropic — not Bedrock alone)
        if not self.metagpt_configured:
            errors.append(
                self._setup_error
                or "MetaGPT is not configured. Set OPENAI_API_KEY or ANTHROPIC_API_KEY in .env and restart."
            )
        
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