"""
Main sandbox management system
"""

import asyncio
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

from app.core.logging import get_logger
from app.core.exceptions import SandboxException, SandboxCreationException, SandboxExecutionException
from app.core.config import settings
from .models import SandboxInfo, SandboxState, SandboxConfig
from .process_manager import ProcessManager
from .file_manager import SandboxFileManager
from .application_runners import ApplicationRunnerFactory

logger = get_logger(__name__)


class SandboxManager:
    """Main sandbox management system"""
    
    def __init__(self):
        self.sandboxes: Dict[str, SandboxInfo] = {}
        self.process_managers: Dict[str, ProcessManager] = {}
        self.file_managers: Dict[str, SandboxFileManager] = {}
        self.cleanup_task = None
        self._background_tasks_started = False
    
    def _start_background_tasks(self):
        """Start background maintenance tasks"""
        if not self._background_tasks_started:
            try:
                if not self.cleanup_task:
                    self.cleanup_task = asyncio.create_task(self._cleanup_loop())
                self._background_tasks_started = True
            except RuntimeError:
                # No event loop running, tasks will be started when needed
                pass
    
    async def create_sandbox(self, session_id: str, config: Optional[SandboxConfig] = None) -> str:
        """Create a new sandbox"""
        # Start background tasks if not already started
        if not self._background_tasks_started:
            self._start_background_tasks()
            
        sandbox_id = f"sb_{session_id}_{str(uuid.uuid4())[:8]}"
        
        try:
            # Use default config if none provided
            if not config:
                config = SandboxConfig(
                    template_id=settings.E2B_TEMPLATE_ID,
                    cpu_limit=settings.E2B_CPU_LIMIT,
                    memory_limit=settings.E2B_MEMORY_LIMIT,
                    timeout=settings.E2B_TIMEOUT
                )
            
            # Create sandbox info
            sandbox_info = SandboxInfo(
                id=sandbox_id,
                session_id=session_id,
                state=SandboxState.CREATING
            )
            
            # Initialize managers
            process_manager = ProcessManager(sandbox_id)
            file_manager = SandboxFileManager(sandbox_id)
            
            # Store references
            self.sandboxes[sandbox_id] = sandbox_info
            self.process_managers[sandbox_id] = process_manager
            self.file_managers[sandbox_id] = file_manager
            
            # Simulate E2B sandbox creation
            await self._create_e2b_sandbox(sandbox_info, config)
            
            sandbox_info.state = SandboxState.READY
            sandbox_info.update_activity()
            
            logger.info(f"Created sandbox {sandbox_id} for session {session_id}")
            return sandbox_id
            
        except Exception as e:
            logger.error(f"Failed to create sandbox for session {session_id}: {e}")
            # Cleanup on failure
            if sandbox_id in self.sandboxes:
                await self._cleanup_sandbox(sandbox_id)
            raise SandboxCreationException(f"Sandbox creation failed: {e}")
    
    async def _create_e2b_sandbox(self, sandbox_info: SandboxInfo, config: SandboxConfig):
        """Create actual E2B sandbox using real E2B API"""
        try:
            # Check if E2B is enabled and configured
            if not settings.ENABLE_E2B or not settings.E2B_API_KEY:
                logger.warning(f"E2B not configured, using simulated sandbox for {sandbox_info.id}")
                # Fallback to simulation
                await asyncio.sleep(0.5)
                sandbox_info.sandbox_instance = {
                    'id': sandbox_info.id,
                    'template': config.template_id,
                    'status': 'simulated',
                    'url': f"https://simulated-{sandbox_info.id}.local"
                }
                sandbox_info.preview_url = f"https://simulated-{sandbox_info.id}.local"
                return
            
            logger.debug(f"Creating real E2B sandbox {sandbox_info.id} with config: {config.to_dict()}")
            
            # Import E2B SDK
            from e2b import Sandbox
            
            # Create actual E2B sandbox with configuration
            sandbox = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: Sandbox(
                    template=config.template_id,
                    api_key=settings.E2B_API_KEY,
                    timeout=config.timeout,
                    metadata={
                        'session_id': sandbox_info.session_id,
                        'sandbox_id': sandbox_info.id
                    }
                )
            )
            
            # Store the actual E2B sandbox instance
            sandbox_info.sandbox_instance = sandbox
            
            # Get the sandbox URL (E2B provides this)
            sandbox_info.preview_url = f"https://{sandbox.get_host(3000)}" if hasattr(sandbox, 'get_host') else None
            
            logger.info(f"✅ Real E2B sandbox {sandbox_info.id} created successfully")
            
        except ImportError as e:
            logger.error(f"E2B SDK not available: {e}")
            raise SandboxCreationException(f"E2B SDK not installed: {e}")
        except Exception as e:
            logger.error(f"Failed to create E2B sandbox {sandbox_info.id}: {e}")
            raise SandboxCreationException(f"E2B sandbox creation failed: {e}")
    
    async def write_files(self, sandbox_id: str, artifacts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Write files to sandbox"""
        sandbox_info = self.sandboxes.get(sandbox_id)
        if not sandbox_info:
            raise SandboxException(f"Sandbox {sandbox_id} not found")
        
        if sandbox_info.state != SandboxState.READY:
            raise SandboxException(f"Sandbox {sandbox_id} not ready (state: {sandbox_info.state})")
        
        try:
            file_manager = self.file_managers[sandbox_id]
            result = await file_manager.write_files(artifacts)
            
            # Update sandbox info
            sandbox_info.files = [f['path'] for f in file_manager.get_all_files()]
            sandbox_info.project_type = file_manager.project_type
            sandbox_info.update_activity()
            
            logger.info(f"Wrote {result['files_written']} files to sandbox {sandbox_id}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to write files to sandbox {sandbox_id}: {e}")
            raise SandboxException(f"File write failed: {e}")
    
    async def run_application(self, sandbox_id: str, command: Optional[str] = None) -> Dict[str, Any]:
        """Run application in sandbox"""
        sandbox_info = self.sandboxes.get(sandbox_id)
        if not sandbox_info:
            raise SandboxException(f"Sandbox {sandbox_id} not found")
        
        try:
            process_manager = self.process_managers[sandbox_id]
            file_manager = self.file_managers[sandbox_id]
            
            # Get appropriate runner
            runner = await ApplicationRunnerFactory.get_best_runner(
                sandbox_id, process_manager, file_manager
            )
            
            sandbox_info.state = SandboxState.RUNNING
            
            # Install dependencies first
            install_process_id = await runner.install_dependencies()
            
            # Wait for installation to complete (simplified)
            await asyncio.sleep(2)
            
            # Start application
            if command:
                # Use custom command
                run_process_id = await process_manager.start_process(
                    command=command,
                    working_dir="/home/user/app"
                )
            else:
                # Use runner's default command
                run_process_id = await runner.start_application()
            
            # Update sandbox info
            sandbox_info.preview_url = runner.get_preview_url()
            sandbox_info.update_activity()
            
            result = {
                'success': True,
                'install_process_id': install_process_id,
                'run_process_id': run_process_id,
                'preview_url': sandbox_info.preview_url,
                'supported_commands': runner.get_supported_commands()
            }
            
            logger.info(f"Started application in sandbox {sandbox_id}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to run application in sandbox {sandbox_id}: {e}")
            sandbox_info.state = SandboxState.ERROR
            raise SandboxExecutionException(f"Application run failed: {e}")
    
    async def stop_application(self, sandbox_id: str) -> bool:
        """Stop running application"""
        sandbox_info = self.sandboxes.get(sandbox_id)
        if not sandbox_info:
            return False
        
        try:
            process_manager = self.process_managers[sandbox_id]
            
            # Stop all running processes
            running_processes = process_manager.get_running_processes()
            stopped_count = 0
            
            for process in running_processes:
                if await process_manager.stop_process(process.id):
                    stopped_count += 1
            
            sandbox_info.state = SandboxState.STOPPED
            sandbox_info.update_activity()
            
            logger.info(f"Stopped {stopped_count} processes in sandbox {sandbox_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to stop application in sandbox {sandbox_id}: {e}")
            return False
    
    async def get_logs(self, sandbox_id: str, process_id: Optional[str] = None, lines: int = 100) -> Dict[str, Any]:
        """Get logs from sandbox"""
        sandbox_info = self.sandboxes.get(sandbox_id)
        if not sandbox_info:
            raise SandboxException(f"Sandbox {sandbox_id} not found")
        
        try:
            process_manager = self.process_managers[sandbox_id]
            
            if process_id:
                # Get logs for specific process
                logs = process_manager.get_process_logs(process_id, lines)
                if not logs:
                    raise SandboxException(f"Process {process_id} not found")
                return logs
            else:
                # Get logs for all processes
                all_processes = process_manager.get_all_processes()
                logs = {
                    'sandbox_id': sandbox_id,
                    'processes': [
                        process_manager.get_process_logs(p.id, lines)
                        for p in all_processes
                    ]
                }
                return logs
                
        except Exception as e:
            logger.error(f"Failed to get logs from sandbox {sandbox_id}: {e}")
            raise SandboxException(f"Log retrieval failed: {e}")
    
    def get_sandbox_info(self, sandbox_id: str) -> Optional[Dict[str, Any]]:
        """Get sandbox information"""
        sandbox_info = self.sandboxes.get(sandbox_id)
        if not sandbox_info:
            return None
        
        process_manager = self.process_managers.get(sandbox_id)
        file_manager = self.file_managers.get(sandbox_id)
        
        return {
            'id': sandbox_info.id,
            'session_id': sandbox_info.session_id,
            'state': sandbox_info.state.value,
            'created_at': sandbox_info.created_at.isoformat(),
            'last_activity': sandbox_info.last_activity.isoformat(),
            'preview_url': sandbox_info.preview_url,
            'project_type': sandbox_info.project_type,
            'file_count': len(sandbox_info.files),
            'process_count': sandbox_info.get_process_count(),
            'running_processes': len(sandbox_info.get_running_processes()),
            'resource_usage': sandbox_info.resource_usage,
            'process_stats': process_manager.get_statistics() if process_manager else {},
            'file_stats': file_manager.get_statistics() if file_manager else {}
        }
    
    def get_sandbox_by_session(self, session_id: str) -> Optional[str]:
        """Get sandbox ID by session ID"""
        for sandbox_id, sandbox_info in self.sandboxes.items():
            if sandbox_info.session_id == session_id:
                return sandbox_id
        return None
    
    async def cleanup_sandbox(self, sandbox_id: str) -> bool:
        """Clean up a sandbox"""
        try:
            await self._cleanup_sandbox(sandbox_id)
            logger.info(f"Cleaned up sandbox {sandbox_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to cleanup sandbox {sandbox_id}: {e}")
            return False
    
    async def _cleanup_sandbox(self, sandbox_id: str):
        """Internal cleanup method"""
        # Stop all processes
        if sandbox_id in self.process_managers:
            process_manager = self.process_managers[sandbox_id]
            running_processes = process_manager.get_running_processes()
            for process in running_processes:
                await process_manager.stop_process(process.id)
        
        # Close E2B sandbox if it's a real instance
        if sandbox_id in self.sandboxes:
            sandbox_info = self.sandboxes[sandbox_id]
            if sandbox_info.sandbox_instance:
                try:
                    # Check if it's a real E2B Sandbox object
                    if hasattr(sandbox_info.sandbox_instance, 'close'):
                        logger.debug(f"Closing real E2B sandbox {sandbox_id}")
                        await asyncio.get_event_loop().run_in_executor(
                            None,
                            sandbox_info.sandbox_instance.close
                        )
                        logger.info(f"✅ E2B sandbox {sandbox_id} closed successfully")
                except Exception as e:
                    logger.warning(f"Failed to close E2B sandbox {sandbox_id}: {e}")
        
        # Remove from all collections
        self.sandboxes.pop(sandbox_id, None)
        self.process_managers.pop(sandbox_id, None)
        self.file_managers.pop(sandbox_id, None)
        
        logger.debug(f"Sandbox {sandbox_id} cleaned up")
    
    async def _cleanup_loop(self):
        """Background cleanup loop"""
        while True:
            try:
                await asyncio.sleep(1800)  # Run every 30 minutes
                await self._cleanup_inactive_sandboxes()
            except Exception as e:
                logger.error(f"Cleanup loop error: {e}")
    
    async def _cleanup_inactive_sandboxes(self):
        """Clean up inactive sandboxes"""
        cutoff_time = datetime.now() - timedelta(hours=2)  # 2 hours
        
        sandboxes_to_cleanup = []
        for sandbox_id, sandbox_info in self.sandboxes.items():
            if (sandbox_info.last_activity < cutoff_time and
                sandbox_info.state in [SandboxState.STOPPED, SandboxState.ERROR]):
                sandboxes_to_cleanup.append(sandbox_id)
        
        for sandbox_id in sandboxes_to_cleanup:
            await self._cleanup_sandbox(sandbox_id)
        
        if sandboxes_to_cleanup:
            logger.info(f"Cleaned up {len(sandboxes_to_cleanup)} inactive sandboxes")
    
    def get_all_sandboxes(self) -> List[Dict[str, Any]]:
        """Get all sandboxes"""
        return [self.get_sandbox_info(sandbox_id) for sandbox_id in self.sandboxes.keys()]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get sandbox statistics"""
        total_sandboxes = len(self.sandboxes)
        state_counts = {}
        
        for state in SandboxState:
            state_counts[state.value] = len([s for s in self.sandboxes.values() if s.state == state])
        
        total_processes = sum(len(pm.processes) for pm in self.process_managers.values())
        running_processes = sum(len(pm.get_running_processes()) for pm in self.process_managers.values())
        
        return {
            'total_sandboxes': total_sandboxes,
            'state_distribution': state_counts,
            'total_processes': total_processes,
            'running_processes': running_processes,
            'active_sessions': len(set(s.session_id for s in self.sandboxes.values()))
        }


# Global instance
sandbox_manager = SandboxManager()