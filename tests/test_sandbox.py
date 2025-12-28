"""
Tests for sandbox system
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock

from app.services.sandbox.sandbox_manager import SandboxManager
from app.services.sandbox.process_manager import ProcessManager
from app.services.sandbox.file_manager import SandboxFileManager
from app.services.sandbox.models import SandboxState, ProcessState, SandboxConfig


class TestSandboxManager:
    """Test sandbox manager functionality"""
    
    def setup_method(self):
        self.manager = SandboxManager()
    
    @pytest.mark.asyncio
    async def test_create_sandbox(self):
        """Test creating a sandbox"""
        session_id = "test_session"
        sandbox_id = await self.manager.create_sandbox(session_id)
        
        assert sandbox_id.startswith("sb_test_session_")
        assert sandbox_id in self.manager.sandboxes
        
        sandbox_info = self.manager.sandboxes[sandbox_id]
        assert sandbox_info.session_id == session_id
        assert sandbox_info.state == SandboxState.READY
    
    @pytest.mark.asyncio
    async def test_write_files(self):
        """Test writing files to sandbox"""
        session_id = "test_session"
        sandbox_id = await self.manager.create_sandbox(session_id)
        
        artifacts = [
            {
                "name": "test.py",
                "content": "print('hello world')",
                "type": "code",
                "language": "python"
            }
        ]
        
        result = await self.manager.write_files(sandbox_id, artifacts)
        
        assert result["success"] is True
        assert result["files_written"] == 1
        
        sandbox_info = self.manager.sandboxes[sandbox_id]
        assert len(sandbox_info.files) == 1
    
    def test_get_sandbox_by_session(self):
        """Test getting sandbox by session ID"""
        # No sandbox initially
        result = self.manager.get_sandbox_by_session("nonexistent")
        assert result is None


class TestProcessManager:
    """Test process manager functionality"""
    
    def setup_method(self):
        self.manager = ProcessManager("test_sandbox")
    
    @pytest.mark.asyncio
    async def test_start_process(self):
        """Test starting a process"""
        process_id = await self.manager.start_process("echo 'hello'")
        
        assert process_id in self.manager.processes
        process_info = self.manager.processes[process_id]
        assert process_info.command == "echo 'hello'"
        assert process_info.state in [ProcessState.RUNNING, ProcessState.COMPLETED]
    
    @pytest.mark.asyncio
    async def test_stop_process(self):
        """Test stopping a process"""
        process_id = await self.manager.start_process("sleep 10")
        
        # Give it a moment to start
        await asyncio.sleep(0.1)
        
        success = await self.manager.stop_process(process_id)
        assert success is True
        
        process_info = self.manager.processes[process_id]
        assert process_info.state == ProcessState.KILLED
    
    def test_get_process_logs(self):
        """Test getting process logs"""
        # Create a mock process
        from app.services.sandbox.models import ProcessInfo
        process = ProcessInfo(
            id="test_process",
            command="echo 'test'"
        )
        process.add_stdout("test output")
        process.add_stderr("test error")
        
        self.manager.processes["test_process"] = process
        
        logs = self.manager.get_process_logs("test_process")
        assert logs is not None
        assert logs["process_id"] == "test_process"
        assert "test output" in logs["output"]["stdout"]
        assert "test error" in logs["output"]["stderr"]


class TestFileManager:
    """Test file manager functionality"""
    
    def setup_method(self):
        self.manager = SandboxFileManager("test_sandbox")
    
    @pytest.mark.asyncio
    async def test_write_files(self):
        """Test writing files"""
        artifacts = [
            {
                "name": "app.py",
                "content": "from flask import Flask\napp = Flask(__name__)",
                "type": "code",
                "language": "python"
            },
            {
                "name": "requirements.txt",
                "content": "flask==2.0.1",
                "type": "configuration"
            }
        ]
        
        result = await self.manager.write_files(artifacts)
        
        assert result["success"] is True
        assert result["files_written"] == 2
        assert result["project_type"] == "python"
    
    def test_detect_project_type(self):
        """Test project type detection"""
        # Test Python project
        self.manager.files = {
            "requirements.txt": {
                "name": "requirements.txt",
                "content": "flask==2.0.1",
                "type": "configuration"
            }
        }
        
        project_type = self.manager._detect_project_type()
        assert project_type == "python"
    
    def test_get_run_commands(self):
        """Test getting run commands"""
        self.manager.project_type = "python"
        self.manager.files = {
            "main.py": {
                "name": "main.py",
                "content": "print('hello')",
                "type": "code"
            }
        }
        
        commands = self.manager.get_run_commands()
        assert "python main.py" in commands
    
    def test_sanitize_filename(self):
        """Test filename sanitization"""
        # Test dangerous characters
        unsafe_name = "../../../etc/passwd"
        safe_name = self.manager._sanitize_filename(unsafe_name)
        assert ".." not in safe_name
        assert "/" not in safe_name
        
        # Test long filename
        long_name = "a" * 300 + ".txt"
        safe_name = self.manager._sanitize_filename(long_name)
        assert len(safe_name) <= 255
        assert safe_name.endswith(".txt")


class TestApplicationRunners:
    """Test application runners"""
    
    def setup_method(self):
        self.process_manager = ProcessManager("test_sandbox")
        self.file_manager = SandboxFileManager("test_sandbox")
    
    @pytest.mark.asyncio
    async def test_react_runner_detection(self):
        """Test React runner detection"""
        from app.services.sandbox.application_runners import ReactRunner
        
        # Mock package.json with React
        self.file_manager.files = {
            "package.json": {
                "name": "package.json",
                "content": '{"dependencies": {"react": "^18.0.0"}}',
                "type": "configuration"
            }
        }
        
        runner = ReactRunner("test_sandbox", self.process_manager, self.file_manager)
        can_run = await runner.can_run()
        assert can_run is True
    
    @pytest.mark.asyncio
    async def test_python_runner_detection(self):
        """Test Python runner detection"""
        from app.services.sandbox.application_runners import PythonRunner
        
        # Mock requirements.txt
        self.file_manager.files = {
            "requirements.txt": {
                "name": "requirements.txt",
                "content": "flask==2.0.1",
                "type": "configuration"
            }
        }
        
        runner = PythonRunner("test_sandbox", self.process_manager, self.file_manager)
        can_run = await runner.can_run()
        assert can_run is True


@pytest.mark.asyncio
class TestSandboxIntegration:
    """Integration tests for sandbox system"""
    
    async def test_complete_sandbox_workflow(self):
        """Test complete sandbox workflow"""
        manager = SandboxManager()
        
        # Create sandbox
        session_id = "integration_test"
        sandbox_id = await manager.create_sandbox(session_id)
        
        # Write files
        artifacts = [
            {
                "name": "app.py",
                "content": "print('Hello from sandbox!')",
                "type": "code",
                "language": "python"
            }
        ]
        
        write_result = await manager.write_files(sandbox_id, artifacts)
        assert write_result["success"] is True
        
        # Run application
        run_result = await manager.run_application(sandbox_id)
        assert run_result["success"] is True
        
        # Get logs
        logs = await manager.get_logs(sandbox_id)
        assert "sandbox_id" in logs
        
        # Stop application
        stop_result = await manager.stop_application(sandbox_id)
        assert stop_result is True
        
        # Cleanup
        cleanup_result = await manager.cleanup_sandbox(sandbox_id)
        assert cleanup_result is True


if __name__ == "__main__":
    pytest.main([__file__])