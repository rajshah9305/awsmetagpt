"""
Process management for sandboxes
"""

import asyncio
import uuid
from typing import Dict, List, Optional, Callable
from datetime import datetime

from app.core.logging import get_logger
from app.core.exceptions import SandboxExecutionException
from .models import ProcessInfo, ProcessState

logger = get_logger(__name__)


class ProcessManager:
    """Manages processes within sandboxes"""
    
    def __init__(self, sandbox_id: str):
        self.sandbox_id = sandbox_id
        self.processes: Dict[str, ProcessInfo] = {}
        self.output_callbacks: Dict[str, List[Callable]] = {}
    
    async def start_process(
        self, 
        command: str, 
        working_dir: str = "/home/user",
        env: Optional[Dict[str, str]] = None
    ) -> str:
        """Start a new process"""
        process_id = str(uuid.uuid4())
        
        try:
            # Create process info
            process_info = ProcessInfo(
                id=process_id,
                command=command,
                state=ProcessState.STARTING
            )
            
            self.processes[process_id] = process_info
            
            # Start the actual process (this would integrate with E2B)
            # For now, we'll simulate the process execution
            await self._execute_process(process_info, working_dir, env)
            
            logger.info(f"Started process {process_id} in sandbox {self.sandbox_id}")
            return process_id
            
        except Exception as e:
            logger.error(f"Failed to start process in sandbox {self.sandbox_id}: {e}")
            if process_id in self.processes:
                self.processes[process_id].state = ProcessState.FAILED
            raise SandboxExecutionException(f"Process start failed: {e}")
    
    async def _execute_process(
        self, 
        process_info: ProcessInfo, 
        working_dir: str,
        env: Optional[Dict[str, str]]
    ):
        """Execute the process (placeholder for E2B integration)"""
        try:
            process_info.state = ProcessState.RUNNING
            process_info.started_at = datetime.now()
            
            # This is where we would integrate with E2B's process execution
            # For now, simulate based on command type
            if "npm start" in process_info.command or "yarn start" in process_info.command:
                await self._simulate_dev_server(process_info)
            elif "python" in process_info.command:
                await self._simulate_python_execution(process_info)
            elif "build" in process_info.command:
                await self._simulate_build_process(process_info)
            else:
                await self._simulate_generic_process(process_info)
                
        except Exception as e:
            process_info.state = ProcessState.FAILED
            process_info.completed_at = datetime.now()
            process_info.add_stderr(f"Process failed: {str(e)}")
            raise
    
    async def _simulate_dev_server(self, process_info: ProcessInfo):
        """Simulate development server process"""
        process_info.add_stdout("Starting development server...")
        await asyncio.sleep(1)
        
        process_info.add_stdout("Webpack compiled successfully")
        process_info.add_stdout("Local: http://localhost:3000")
        process_info.add_stdout("On Your Network: http://192.168.1.100:3000")
        
        # Simulate long-running server
        # In real implementation, this would be handled by E2B
        await asyncio.sleep(0.1)  # Just to yield control
    
    async def _simulate_python_execution(self, process_info: ProcessInfo):
        """Simulate Python script execution"""
        process_info.add_stdout("Python 3.11.0 (main, Oct 24 2022, 18:26:48)")
        await asyncio.sleep(0.5)
        
        process_info.add_stdout("Installing dependencies...")
        await asyncio.sleep(1)
        
        process_info.add_stdout("Running application...")
        process_info.add_stdout("Application started successfully")
        
        # Complete the process
        process_info.state = ProcessState.COMPLETED
        process_info.completed_at = datetime.now()
        process_info.exit_code = 0
    
    async def _simulate_build_process(self, process_info: ProcessInfo):
        """Simulate build process"""
        process_info.add_stdout("Starting build process...")
        await asyncio.sleep(0.5)
        
        process_info.add_stdout("Compiling TypeScript...")
        await asyncio.sleep(1)
        
        process_info.add_stdout("Bundling assets...")
        await asyncio.sleep(1)
        
        process_info.add_stdout("Build completed successfully")
        
        process_info.state = ProcessState.COMPLETED
        process_info.completed_at = datetime.now()
        process_info.exit_code = 0
    
    async def _simulate_generic_process(self, process_info: ProcessInfo):
        """Simulate generic process execution"""
        process_info.add_stdout(f"Executing: {process_info.command}")
        await asyncio.sleep(1)
        
        process_info.add_stdout("Process completed")
        
        process_info.state = ProcessState.COMPLETED
        process_info.completed_at = datetime.now()
        process_info.exit_code = 0
    
    async def stop_process(self, process_id: str) -> bool:
        """Stop a running process"""
        process_info = self.processes.get(process_id)
        if not process_info:
            return False
        
        if process_info.state != ProcessState.RUNNING:
            return False
        
        try:
            # In real implementation, this would send SIGTERM to the E2B process
            process_info.state = ProcessState.KILLED
            process_info.completed_at = datetime.now()
            process_info.exit_code = -1
            process_info.add_stdout("Process terminated by user")
            
            logger.info(f"Stopped process {process_id} in sandbox {self.sandbox_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to stop process {process_id}: {e}")
            return False
    
    def get_process(self, process_id: str) -> Optional[ProcessInfo]:
        """Get process information"""
        return self.processes.get(process_id)
    
    def get_all_processes(self) -> List[ProcessInfo]:
        """Get all processes"""
        return list(self.processes.values())
    
    def get_running_processes(self) -> List[ProcessInfo]:
        """Get all running processes"""
        return [p for p in self.processes.values() if p.state == ProcessState.RUNNING]
    
    def get_process_logs(self, process_id: str, lines: int = 100) -> Optional[Dict]:
        """Get process logs"""
        process_info = self.processes.get(process_id)
        if not process_info:
            return None
        
        return {
            'process_id': process_id,
            'command': process_info.command,
            'state': process_info.state.value,
            'started_at': process_info.started_at.isoformat(),
            'completed_at': process_info.completed_at.isoformat() if process_info.completed_at else None,
            'exit_code': process_info.exit_code,
            'output': process_info.get_recent_output(lines)
        }
    
    def add_output_callback(self, process_id: str, callback: Callable):
        """Add callback for process output"""
        if process_id not in self.output_callbacks:
            self.output_callbacks[process_id] = []
        self.output_callbacks[process_id].append(callback)
    
    def _notify_output_callbacks(self, process_id: str, output_type: str, line: str):
        """Notify output callbacks"""
        callbacks = self.output_callbacks.get(process_id, [])
        for callback in callbacks:
            try:
                callback(process_id, output_type, line)
            except Exception as e:
                logger.error(f"Error in output callback: {e}")
    
    async def cleanup_completed_processes(self, max_age_hours: int = 24):
        """Clean up old completed processes"""
        cutoff_time = datetime.now().timestamp() - (max_age_hours * 3600)
        
        processes_to_remove = []
        for process_id, process_info in self.processes.items():
            if (process_info.state in [ProcessState.COMPLETED, ProcessState.FAILED, ProcessState.KILLED] and
                process_info.completed_at and
                process_info.completed_at.timestamp() < cutoff_time):
                processes_to_remove.append(process_id)
        
        for process_id in processes_to_remove:
            del self.processes[process_id]
            if process_id in self.output_callbacks:
                del self.output_callbacks[process_id]
        
        if processes_to_remove:
            logger.info(f"Cleaned up {len(processes_to_remove)} old processes in sandbox {self.sandbox_id}")
    
    def get_statistics(self) -> Dict:
        """Get process statistics"""
        total_processes = len(self.processes)
        state_counts = {}
        
        for state in ProcessState:
            state_counts[state.value] = len([p for p in self.processes.values() if p.state == state])
        
        return {
            'total_processes': total_processes,
            'state_distribution': state_counts,
            'running_processes': len(self.get_running_processes())
        }