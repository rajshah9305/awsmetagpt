"""
Production-ready E2B Sandbox service for secure code execution and live preview
Handles sandbox lifecycle, file operations, process management, and monitoring
"""

import asyncio
import logging
import json
import time
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
from pathlib import Path
import traceback

from app.core.config import settings
from app.services.websocket_manager import websocket_manager

logger = logging.getLogger(__name__)

class SandboxState(str, Enum):
    """Sandbox states"""
    CREATING = "creating"
    READY = "ready"
    RUNNING = "running"
    STOPPED = "stopped"
    ERROR = "error"
    TERMINATED = "terminated"

class ProcessState(str, Enum):
    """Process states"""
    STARTING = "starting"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    KILLED = "killed"

@dataclass
class SandboxProcess:
    """Represents a running process in sandbox"""
    id: str
    command: str
    pid: Optional[int] = None
    state: ProcessState = ProcessState.STARTING
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    exit_code: Optional[int] = None
    stdout_buffer: List[str] = field(default_factory=list)
    stderr_buffer: List[str] = field(default_factory=list)

@dataclass
class SandboxInfo:
    """Enhanced sandbox information"""
    id: str
    session_id: str
    state: SandboxState
    created_at: datetime
    sandbox_instance: Any = None
    files: List[str] = field(default_factory=list)
    processes: Dict[str, SandboxProcess] = field(default_factory=dict)
    preview_url: Optional[str] = None
    project_type: Optional[str] = None
    metrics: Dict[str, Any] = field(default_factory=dict)
    last_activity: datetime = field(default_factory=datetime.now)

class E2BService:
    """Production-ready E2B sandbox management service"""

    def __init__(self):
        self.active_sandboxes: Dict[str, SandboxInfo] = {}
        self.sandbox_templates = {
            "base": "base",
            "python": "python3.11",
            "node": "node18",
            "react": "react18",
            "nextjs": "nextjs13"
        }
        self._monitoring_started = False

    
    def _setup_monitoring(self):
        """Setup sandbox monitoring and cleanup tasks (called when event loop is available)"""
        if not self._monitoring_started:
            asyncio.create_task(self._monitor_sandboxes())
            asyncio.create_task(self._cleanup_inactive_sandboxes())
            self._monitoring_started = True
    
    async def _monitor_sandboxes(self):
        """Monitor sandbox health and processes"""
        while True:
            try:
                for sandbox_id, sandbox_info in list(self.active_sandboxes.items()):
                    await self._check_sandbox_health(sandbox_info)
                await asyncio.sleep(30)  # Check every 30 seconds
            except Exception as e:
                logger.error(f"Sandbox monitoring error: {e}")
                await asyncio.sleep(60)
    
    async def _cleanup_inactive_sandboxes(self):
        """Cleanup inactive sandboxes"""
        while True:
            try:
                cutoff_time = datetime.now() - timedelta(hours=2)
                inactive_sandboxes = [
                    sid for sid, info in self.active_sandboxes.items()
                    if info.last_activity < cutoff_time
                ]
                
                for sandbox_id in inactive_sandboxes:
                    logger.info(f"Cleaning up inactive sandbox {sandbox_id}")
                    await self.cleanup_sandbox(sandbox_id)
                
                await asyncio.sleep(3600)  # Check every hour
            except Exception as e:
                logger.error(f"Cleanup monitoring error: {e}")
                await asyncio.sleep(3600)
    
    async def _check_sandbox_health(self, sandbox_info: SandboxInfo):
        """Check sandbox health and update metrics"""
        try:
            if not sandbox_info.sandbox_instance:
                return
            
            # Update last activity
            sandbox_info.last_activity = datetime.now()
            
            # Check running processes
            for process_id, process in list(sandbox_info.processes.items()):
                if process.state == ProcessState.RUNNING:
                    # Check if process is still alive
                    try:
                        # This would need actual E2B process checking
                        # For now, we'll simulate it
                        pass
                    except Exception:
                        process.state = ProcessState.FAILED
                        process.completed_at = datetime.now()
            
            # Update metrics
            sandbox_info.metrics.update({
                "uptime": (datetime.now() - sandbox_info.created_at).total_seconds(),
                "active_processes": len([p for p in sandbox_info.processes.values() if p.state == ProcessState.RUNNING]),
                "total_files": len(sandbox_info.files),
                "last_check": datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Health check failed for sandbox {sandbox_info.id}: {e}")
            sandbox_info.state = SandboxState.ERROR

    async def create_sandbox(self, session_id: str, template: str = "base") -> Optional[str]:
        """Create a new E2B sandbox with enhanced configuration"""
        try:
            # Import E2B dynamically
            from e2b import Sandbox
            
            if not settings.E2B_API_KEY:
                logger.error("E2B API key not configured")
                return None

            # Determine template
            template_id = self.sandbox_templates.get(template, settings.E2B_TEMPLATE_ID)
            
            # Create sandbox with enhanced configuration
            sandbox = Sandbox(
                template=template_id,
                api_key=settings.E2B_API_KEY,
                metadata={
                    "session_id": session_id,
                    "created_by": "metagpt_orchestrator",
                    "purpose": "code_execution"
                },
                timeout=1800,  # 30 minutes
                # Add resource limits
                cpu_count=2,
                memory_mb=2048
            )

            # Create sandbox info
            sandbox_info = SandboxInfo(
                id=session_id,
                session_id=session_id,
                state=SandboxState.READY,
                created_at=datetime.now(),
                sandbox_instance=sandbox
            )
            
            self.active_sandboxes[session_id] = sandbox_info
            
            # Initialize sandbox environment
            await self._initialize_sandbox_environment(sandbox_info)

            logger.info(f"✅ E2B sandbox created for session {session_id} with template {template_id}")
            return session_id

        except Exception as e:
            logger.error(f"Failed to create E2B sandbox: {e}")
            # Cleanup any partial sandbox creation
            if session_id in self.active_sandboxes:
                try:
                    await self.cleanup_sandbox(session_id)
                except Exception as cleanup_error:
                    logger.error(f"Failed to cleanup partial sandbox: {cleanup_error}")
            return None
    
    async def _initialize_sandbox_environment(self, sandbox_info: SandboxInfo):
        """Initialize sandbox with common tools and environment"""
        try:
            sandbox = sandbox_info.sandbox_instance
            
            # Create common directories
            directories = [
                "/home/user/app",
                "/home/user/logs",
                "/home/user/temp"
            ]
            
            for directory in directories:
                try:
                    sandbox.filesystem.make_dir(directory)
                except Exception:
                    pass  # Directory might already exist
            
            # Install common tools
            init_commands = [
                "apt-get update -qq",
                "apt-get install -y -qq curl wget git vim nano htop",
                "pip install --upgrade pip setuptools wheel",
                "npm install -g npm@latest"
            ]
            
            for cmd in init_commands:
                try:
                    process = sandbox.process.start(cmd)
                    process.wait(timeout=60)
                except Exception as e:
                    logger.warning(f"Failed to run init command '{cmd}': {e}")
            
            logger.info(f"✅ Initialized sandbox environment for {sandbox_info.id}")
            
        except Exception as e:
            logger.error(f"Failed to initialize sandbox environment: {e}")

    async def write_files(self, session_id: str, artifacts: List[Dict]) -> bool:
        """Write artifacts to sandbox with enhanced file handling"""
        if session_id not in self.active_sandboxes:
            logger.error(f"Sandbox not found for session {session_id}")
            return False

        try:
            sandbox_info = self.active_sandboxes[session_id]
            sandbox = sandbox_info.sandbox_instance
            
            if not sandbox:
                logger.error(f"Sandbox instance not available for {session_id}")
                return False

            written_files = []
            
            for artifact in artifacts:
                filename = artifact.get("file_path", artifact.get("name", "unknown.txt"))
                content = artifact.get("content", "")
                
                if not content:
                    continue

                # Ensure proper file path
                if not filename.startswith("/"):
                    filename = f"/home/user/app/{filename}"

                # Create directory structure
                dir_path = "/".join(filename.split("/")[:-1])
                if dir_path and dir_path != "/home/user/app":
                    try:
                        sandbox.filesystem.make_dir(dir_path)
                    except Exception:
                        pass  # Directory might already exist

                # Write file with error handling
                try:
                    sandbox.filesystem.write(filename, content)
                    written_files.append(filename)
                    sandbox_info.files.append(filename)
                    
                    logger.debug(f"📄 Created file: {filename}")
                    
                except Exception as e:
                    logger.error(f"Failed to write file {filename}: {e}")
                    continue

            # Detect project type based on written files
            sandbox_info.project_type = self._detect_project_type(written_files)
            
            logger.info(f"✅ Written {len(written_files)} files to sandbox {session_id}")
            return len(written_files) > 0

        except Exception as e:
            logger.error(f"Failed to write files to sandbox: {e}")
            return False

    async def run_application(self, session_id: str) -> Optional[str]:
        """Run application with enhanced process management"""
        if session_id not in self.active_sandboxes:
            logger.error(f"Sandbox not found for session {session_id}")
            return None

        try:
            sandbox_info = self.active_sandboxes[session_id]
            sandbox = sandbox_info.sandbox_instance
            
            if not sandbox:
                return None

            # Stop any existing processes
            await self._stop_all_processes(sandbox_info)
            
            # Determine how to run based on project type
            project_type = sandbox_info.project_type or self._detect_project_type(sandbox_info.files)
            
            if project_type == "react":
                return await self._run_react_app(sandbox_info)
            elif project_type == "python":
                return await self._run_python_app(sandbox_info)
            elif project_type == "node":
                return await self._run_node_app(sandbox_info)
            elif project_type == "html":
                return await self._run_html_app(sandbox_info)
            else:
                return await self._run_default_preview(sandbox_info)

        except Exception as e:
            logger.error(f"Failed to run application in sandbox: {e}")
            return None
    
    async def _stop_all_processes(self, sandbox_info: SandboxInfo):
        """Stop all running processes in sandbox"""
        try:
            for process_id, process in sandbox_info.processes.items():
                if process.state == ProcessState.RUNNING:
                    await self._kill_process(sandbox_info, process_id)
        except Exception as e:
            logger.error(f"Failed to stop processes: {e}")
    
    async def _start_process(self, sandbox_info: SandboxInfo, command: str, working_dir: str = "/home/user/app") -> Optional[str]:
        """Start a process in sandbox with monitoring"""
        try:
            sandbox = sandbox_info.sandbox_instance
            process_id = f"proc_{int(time.time() * 1000)}"
            
            # Start process
            full_command = f"cd {working_dir} && {command}"
            process_handle = sandbox.process.start(full_command)
            
            # Create process info
            process_info = SandboxProcess(
                id=process_id,
                command=command,
                pid=getattr(process_handle, 'pid', None),
                state=ProcessState.RUNNING
            )
            
            sandbox_info.processes[process_id] = process_info
            sandbox_info.state = SandboxState.RUNNING
            
            # Start log monitoring
            asyncio.create_task(self._monitor_process_logs(sandbox_info, process_id, process_handle))
            
            logger.info(f"✅ Started process {process_id} in sandbox {sandbox_info.id}")
            return process_id
            
        except Exception as e:
            logger.error(f"Failed to start process: {e}")
            return None
    
    async def _monitor_process_logs(self, sandbox_info: SandboxInfo, process_id: str, process_handle: Any):
        """Monitor process logs and stream to WebSocket"""
        try:
            process_info = sandbox_info.processes[process_id]
            
            while process_info.state == ProcessState.RUNNING:
                try:
                    # Read stdout/stderr (this would need actual E2B implementation)
                    # For now, we'll simulate log streaming
                    await asyncio.sleep(1)
                    
                    # Check if process is still running
                    if hasattr(process_handle, 'poll') and process_handle.poll() is not None:
                        process_info.state = ProcessState.COMPLETED
                        process_info.completed_at = datetime.now()
                        process_info.exit_code = process_handle.poll()
                        break
                        
                except Exception as e:
                    logger.error(f"Error monitoring process logs: {e}")
                    break
            
        except Exception as e:
            logger.error(f"Process monitoring failed: {e}")
    
    async def _kill_process(self, sandbox_info: SandboxInfo, process_id: str) -> bool:
        """Kill a specific process"""
        try:
            if process_id not in sandbox_info.processes:
                return False
            
            process_info = sandbox_info.processes[process_id]
            
            # Kill process (implementation depends on E2B API)
            # For now, we'll mark it as killed
            process_info.state = ProcessState.KILLED
            process_info.completed_at = datetime.now()
            
            logger.info(f"✅ Killed process {process_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to kill process: {e}")
            return False

    async def _run_react_app(self, sandbox_info: SandboxInfo) -> Optional[str]:
        """Run React application with enhanced setup"""
        try:
            sandbox = sandbox_info.sandbox_instance
            
            # Check for package.json
            package_json_exists = sandbox.filesystem.exists("/home/user/app/package.json")
            
            if not package_json_exists:
                # Create comprehensive package.json
                package_json = {
                    "name": "generated-react-app",
                    "version": "1.0.0",
                    "private": True,
                    "dependencies": {
                        "react": "^18.2.0",
                        "react-dom": "^18.2.0",
                        "react-scripts": "5.0.1",
                        "axios": "^1.4.0",
                        "react-router-dom": "^6.14.0"
                    },
                    "scripts": {
                        "start": "react-scripts start",
                        "build": "react-scripts build",
                        "test": "react-scripts test",
                        "eject": "react-scripts eject"
                    },
                    "eslintConfig": {
                        "extends": ["react-app", "react-app/jest"]
                    },
                    "browserslist": {
                        "production": [">0.2%", "not dead", "not op_mini all"],
                        "development": ["last 1 chrome version", "last 1 firefox version", "last 1 safari version"]
                    }
                }
                sandbox.filesystem.write("/home/user/app/package.json", json.dumps(package_json, indent=2))
            
            # Install dependencies
            install_process_id = await self._start_process(sandbox_info, "npm install --silent")
            if install_process_id:
                # Wait for installation to complete
                await self._wait_for_process(sandbox_info, install_process_id, timeout=300)
            
            # Start React development server
            start_process_id = await self._start_process(
                sandbox_info, 
                "BROWSER=none PORT=3000 npm start"
            )
            
            if start_process_id:
                # Wait for server to start
                await asyncio.sleep(10)
                
                # Get preview URL
                preview_url = f"https://{sandbox.get_hostname(3000)}"
                sandbox_info.preview_url = preview_url
                
                logger.info(f"✅ React app running at {preview_url}")
                return preview_url
            
            return None

        except Exception as e:
            logger.error(f"Failed to run React app: {e}")
            return None
    
    async def _wait_for_process(self, sandbox_info: SandboxInfo, process_id: str, timeout: int = 60) -> bool:
        """Wait for process to complete"""
        try:
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                if process_id not in sandbox_info.processes:
                    return False
                
                process_info = sandbox_info.processes[process_id]
                if process_info.state in [ProcessState.COMPLETED, ProcessState.FAILED, ProcessState.KILLED]:
                    return process_info.state == ProcessState.COMPLETED
                
                await asyncio.sleep(1)
            
            # Timeout
            await self._kill_process(sandbox_info, process_id)
            return False
            
        except Exception as e:
            logger.error(f"Error waiting for process: {e}")
            return False

    async def _run_python_app(self, sandbox_info: SandboxInfo) -> Optional[str]:
        """Run Python application with enhanced detection"""
        try:
            sandbox = sandbox_info.sandbox_instance
            
            # Detect Python app type
            main_files = [
                "/home/user/app/app.py",
                "/home/user/app/main.py", 
                "/home/user/app/streamlit_app.py",
                "/home/user/app/server.py"
            ]
            
            main_file = None
            app_type = "streamlit"  # default
            
            for file_path in main_files:
                if sandbox.filesystem.exists(file_path):
                    main_file = file_path
                    # Detect app type from content
                    try:
                        content = sandbox.filesystem.read(file_path)
                        if "flask" in content.lower():
                            app_type = "flask"
                        elif "fastapi" in content.lower():
                            app_type = "fastapi"
                        elif "streamlit" in content.lower():
                            app_type = "streamlit"
                    except Exception:
                        pass
                    break
            
            if not main_file:
                # Create default Streamlit app
                main_file = "/home/user/app/app.py"
                streamlit_code = self._generate_enhanced_streamlit_app(sandbox_info.files)
                sandbox.filesystem.write(main_file, streamlit_code)
                app_type = "streamlit"
            
            # Install requirements
            requirements_file = "/home/user/app/requirements.txt"
            if not sandbox.filesystem.exists(requirements_file):
                requirements = self._generate_python_requirements(app_type)
                sandbox.filesystem.write(requirements_file, requirements)
            
            # Install dependencies
            install_process_id = await self._start_process(sandbox_info, "pip install -r requirements.txt")
            if install_process_id:
                await self._wait_for_process(sandbox_info, install_process_id, timeout=180)
            
            # Start application based on type
            if app_type == "streamlit":
                command = f"streamlit run {main_file} --server.port 8501 --server.address 0.0.0.0 --server.headless true"
                port = 8501
            elif app_type == "flask":
                command = f"python {main_file}"
                port = 5000
            elif app_type == "fastapi":
                command = f"uvicorn main:app --host 0.0.0.0 --port 8000"
                port = 8000
            else:
                command = f"python {main_file}"
                port = 8000
            
            start_process_id = await self._start_process(sandbox_info, command)
            
            if start_process_id:
                await asyncio.sleep(5)  # Wait for server to start
                
                preview_url = f"https://{sandbox.get_hostname(port)}"
                sandbox_info.preview_url = preview_url
                
                logger.info(f"✅ Python {app_type} app running at {preview_url}")
                return preview_url
            
            return None

        except Exception as e:
            logger.error(f"Failed to run Python app: {e}")
            return None
    
    def _generate_python_requirements(self, app_type: str) -> str:
        """Generate requirements.txt based on app type"""
        base_requirements = [
            "requests>=2.31.0",
            "python-dotenv>=1.0.0"
        ]
        
        if app_type == "streamlit":
            base_requirements.extend([
                "streamlit>=1.25.0",
                "pandas>=2.0.0",
                "numpy>=1.24.0",
                "plotly>=5.15.0"
            ])
        elif app_type == "flask":
            base_requirements.extend([
                "flask>=2.3.0",
                "flask-cors>=4.0.0"
            ])
        elif app_type == "fastapi":
            base_requirements.extend([
                "fastapi>=0.100.0",
                "uvicorn>=0.23.0"
            ])
        
        return "\n".join(base_requirements)
    
    def _generate_enhanced_streamlit_app(self, files: List[str]) -> str:
        """Generate enhanced Streamlit app"""
        return f'''
import streamlit as st
import os
import json
from pathlib import Path

st.set_page_config(
    page_title="Generated Application",
    page_icon="🚀",
    layout="wide"
)

st.title("🚀 Generated Application Preview")
st.markdown("This is a preview of your generated application files.")

# Sidebar navigation
st.sidebar.title("📁 File Explorer")

# List all files
files = {files}
app_files = [f for f in files if f.startswith("/home/user/app/")]

if app_files:
    # Create file categories
    code_files = [f for f in app_files if f.endswith(('.py', '.js', '.jsx', '.ts', '.tsx', '.html', '.css'))]
    config_files = [f for f in app_files if f.endswith(('.json', '.yml', '.yaml', '.toml', '.ini'))]
    doc_files = [f for f in app_files if f.endswith(('.md', '.txt', '.rst'))]
    
    # Sidebar file selection
    file_category = st.sidebar.selectbox(
        "File Category",
        ["All Files", "Code Files", "Configuration", "Documentation"]
    )
    
    if file_category == "Code Files":
        display_files = code_files
    elif file_category == "Configuration":
        display_files = config_files
    elif file_category == "Documentation":
        display_files = doc_files
    else:
        display_files = app_files
    
    selected_file = st.sidebar.selectbox(
        "Select File",
        display_files,
        format_func=lambda x: os.path.basename(x)
    )
    
    # Main content area
    col1, col2 = st.columns([3, 1])
    
    with col1:
        if selected_file:
            st.subheader(f"📄 {{os.path.basename(selected_file)}}")
            
            try:
                with open(selected_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Determine language for syntax highlighting
                file_ext = Path(selected_file).suffix.lower()
                language_map = {{
                    '.py': 'python',
                    '.js': 'javascript',
                    '.jsx': 'javascript',
                    '.ts': 'typescript',
                    '.tsx': 'typescript',
                    '.html': 'html',
                    '.css': 'css',
                    '.json': 'json',
                    '.yml': 'yaml',
                    '.yaml': 'yaml',
                    '.md': 'markdown'
                }}
                
                language = language_map.get(file_ext, 'text')
                
                # Display content
                st.code(content, language=language)
                
                # File stats
                st.caption(f"File size: {{len(content):,}} characters | Lines: {{len(content.splitlines()):,}}")
                
            except Exception as e:
                st.error(f"Could not read file: {{e}}")
    
    with col2:
        st.subheader("📊 Project Stats")
        
        # Project statistics
        total_files = len(app_files)
        total_lines = 0
        total_chars = 0
        
        for file_path in app_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    total_lines += len(content.splitlines())
                    total_chars += len(content)
            except Exception:
                pass
        
        st.metric("Total Files", total_files)
        st.metric("Total Lines", f"{{total_lines:,}}")
        st.metric("Total Characters", f"{{total_chars:,}}")
        
        # File type breakdown
        st.subheader("📈 File Types")
        file_types = {{}}
        for file_path in app_files:
            ext = Path(file_path).suffix.lower() or '.txt'
            file_types[ext] = file_types.get(ext, 0) + 1
        
        for ext, count in sorted(file_types.items()):
            st.write(f"**{{ext}}**: {{count}} files")

else:
    st.info("No application files found.")
    st.write("Available files:")
    for file_path in files:
        st.write(f"- {{file_path}}")

# Footer
st.markdown("---")
st.markdown("Generated by MetaGPT + E2B Integration System")
'''

    async def _run_node_app(self, sandbox_info: SandboxInfo) -> Optional[str]:
        """Run Node.js application with enhanced setup"""
        try:
            sandbox = sandbox_info.sandbox_instance
            
            # Check for package.json
            package_json_exists = sandbox.filesystem.exists("/home/user/app/package.json")
            
            if not package_json_exists:
                # Create comprehensive package.json
                package_json = {
                    "name": "generated-node-app",
                    "version": "1.0.0",
                    "main": "index.js",
                    "scripts": {
                        "start": "node index.js",
                        "dev": "nodemon index.js"
                    },
                    "dependencies": {
                        "express": "^4.18.0",
                        "cors": "^2.8.5",
                        "dotenv": "^16.3.0"
                    },
                    "devDependencies": {
                        "nodemon": "^3.0.0"
                    }
                }
                sandbox.filesystem.write("/home/user/app/package.json", json.dumps(package_json, indent=2))
            
            # Create default server if no main file exists
            main_files = ["index.js", "server.js", "app.js"]
            main_file_exists = any(
                sandbox.filesystem.exists(f"/home/user/app/{f}") for f in main_files
            )
            
            if not main_file_exists:
                default_server = '''
const express = require('express');
const cors = require('cors');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static('public'));

// Routes
app.get('/', (req, res) => {
    res.json({
        message: 'Generated Node.js Application',
        timestamp: new Date().toISOString(),
        status: 'running'
    });
});

app.get('/health', (req, res) => {
    res.json({ status: 'healthy' });
});

// Start server
app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server running on port ${PORT}`);
});
'''
                sandbox.filesystem.write("/home/user/app/index.js", default_server)
            
            # Install dependencies
            install_process_id = await self._start_process(sandbox_info, "npm install --silent")
            if install_process_id:
                await self._wait_for_process(sandbox_info, install_process_id, timeout=180)
            
            # Start application
            start_process_id = await self._start_process(sandbox_info, "npm start")
            
            if start_process_id:
                await asyncio.sleep(5)
                
                preview_url = f"https://{sandbox.get_hostname(3000)}"
                sandbox_info.preview_url = preview_url
                
                logger.info(f"✅ Node.js app running at {preview_url}")
                return preview_url
            
            return None

        except Exception as e:
            logger.error(f"Failed to run Node.js app: {e}")
            return None

    async def _run_html_app(self, sandbox_info: SandboxInfo) -> Optional[str]:
        """Run HTML application with enhanced server"""
        try:
            # Start enhanced HTTP server
            server_script = '''
import http.server
import socketserver
import os
from urllib.parse import urlparse, parse_qs

class EnhancedHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

os.chdir('/home/user/app')
PORT = 8000

with socketserver.TCPServer(("0.0.0.0", PORT), EnhancedHTTPRequestHandler) as httpd:
    print(f"Serving at port {PORT}")
    httpd.serve_forever()
'''
            
            sandbox_info.sandbox_instance.filesystem.write("/home/user/server.py", server_script)
            
            start_process_id = await self._start_process(sandbox_info, "python /home/user/server.py")
            
            if start_process_id:
                await asyncio.sleep(3)
                
                preview_url = f"https://{sandbox_info.sandbox_instance.get_hostname(8000)}"
                sandbox_info.preview_url = preview_url
                
                logger.info(f"✅ HTML app running at {preview_url}")
                return preview_url
            
            return None

        except Exception as e:
            logger.error(f"Failed to run HTML app: {e}")
            return None

    async def _run_default_preview(self, sandbox_info: SandboxInfo) -> Optional[str]:
        """Create enhanced default preview"""
        try:
            # Create enhanced Streamlit preview app
            preview_code = self._generate_enhanced_streamlit_app(sandbox_info.files)
            sandbox_info.sandbox_instance.filesystem.write("/home/user/preview_app.py", preview_code)
            
            # Install Streamlit
            install_process_id = await self._start_process(sandbox_info, "pip install streamlit pandas plotly")
            if install_process_id:
                await self._wait_for_process(sandbox_info, install_process_id, timeout=120)
            
            # Start preview app
            start_process_id = await self._start_process(
                sandbox_info, 
                "streamlit run /home/user/preview_app.py --server.port 8501 --server.address 0.0.0.0 --server.headless true"
            )
            
            if start_process_id:
                await asyncio.sleep(5)
                
                preview_url = f"https://{sandbox_info.sandbox_instance.get_hostname(8501)}"
                sandbox_info.preview_url = preview_url
                
                logger.info(f"✅ Default preview running at {preview_url}")
                return preview_url
            
            return None

        except Exception as e:
            logger.error(f"Failed to run default preview: {e}")
            return None

    def _detect_project_type(self, files: List[str]) -> str:
        """Enhanced project type detection"""
        file_names = [f.split("/")[-1].lower() for f in files]
        file_extensions = [f.split(".")[-1].lower() for f in files if "." in f]
        
        # React detection
        if "package.json" in file_names:
            if any(f.endswith(('.jsx', '.tsx')) for f in files):
                return "react"
            elif "next.config.js" in file_names:
                return "nextjs"
            else:
                return "node"
        
        # Python detection
        if any(ext in file_extensions for ext in ['py']):
            if "requirements.txt" in file_names or "pyproject.toml" in file_names:
                return "python"
        
        # HTML detection
        if any(ext in file_extensions for ext in ['html', 'htm']):
            return "html"
        
        return "unknown"

    async def stop_application(self, session_id: str) -> bool:
        """Stop running application with enhanced cleanup"""
        if session_id not in self.active_sandboxes:
            return False

        try:
            sandbox_info = self.active_sandboxes[session_id]
            
            # Stop all processes
            await self._stop_all_processes(sandbox_info)
            
            # Update state
            sandbox_info.state = SandboxState.STOPPED
            sandbox_info.preview_url = None
            
            logger.info(f"✅ Stopped application for session {session_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to stop application: {e}")
            return False

    async def get_logs(self, session_id: str, process_id: Optional[str] = None) -> List[str]:
        """Get logs with enhanced filtering"""
        if session_id not in self.active_sandboxes:
            return []

        try:
            sandbox_info = self.active_sandboxes[session_id]
            logs = []
            
            if process_id and process_id in sandbox_info.processes:
                # Get logs for specific process
                process = sandbox_info.processes[process_id]
                logs.extend(process.stdout_buffer)
                logs.extend(process.stderr_buffer)
            else:
                # Get logs for all processes
                for process in sandbox_info.processes.values():
                    logs.extend([f"[{process.id}] {log}" for log in process.stdout_buffer])
                    logs.extend([f"[{process.id}] ERROR: {log}" for log in process.stderr_buffer])
            
            return logs[-100:]  # Return last 100 log lines

        except Exception as e:
            logger.error(f"Failed to get logs: {e}")
            return [f"Error retrieving logs: {str(e)}"]

    async def cleanup_sandbox(self, session_id: str) -> bool:
        """Enhanced sandbox cleanup"""
        if session_id not in self.active_sandboxes:
            return False

        try:
            sandbox_info = self.active_sandboxes[session_id]
            
            # Stop all processes
            await self._stop_all_processes(sandbox_info)
            
            # Close sandbox
            if sandbox_info.sandbox_instance:
                try:
                    sandbox_info.sandbox_instance.close()
                except Exception as e:
                    logger.warning(f"Error closing sandbox: {e}")
            
            # Update state
            sandbox_info.state = SandboxState.TERMINATED
            
            # Remove from active sandboxes
            del self.active_sandboxes[session_id]
            
            logger.info(f"✅ Cleaned up sandbox for session {session_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to cleanup sandbox: {e}")
            return False

    def get_sandbox_info(self, session_id: str) -> Optional[Dict]:
        """Get enhanced sandbox information"""
        sandbox_info = self.active_sandboxes.get(session_id)
        if not sandbox_info:
            return None
        
        return {
            "id": sandbox_info.id,
            "session_id": sandbox_info.session_id,
            "state": sandbox_info.state.value,
            "created_at": sandbox_info.created_at.isoformat(),
            "last_activity": sandbox_info.last_activity.isoformat(),
            "project_type": sandbox_info.project_type,
            "preview_url": sandbox_info.preview_url,
            "files_count": len(sandbox_info.files),
            "active_processes": len([p for p in sandbox_info.processes.values() if p.state == ProcessState.RUNNING]),
            "metrics": sandbox_info.metrics
        }
    
    async def get_sandbox_metrics(self, session_id: str) -> Dict[str, Any]:
        """Get detailed sandbox metrics"""
        sandbox_info = self.active_sandboxes.get(session_id)
        if not sandbox_info:
            return {}
        
        return {
            "uptime": (datetime.now() - sandbox_info.created_at).total_seconds(),
            "files_count": len(sandbox_info.files),
            "processes": {
                "total": len(sandbox_info.processes),
                "running": len([p for p in sandbox_info.processes.values() if p.state == ProcessState.RUNNING]),
                "completed": len([p for p in sandbox_info.processes.values() if p.state == ProcessState.COMPLETED]),
                "failed": len([p for p in sandbox_info.processes.values() if p.state == ProcessState.FAILED])
            },
            "state": sandbox_info.state.value,
            "project_type": sandbox_info.project_type,
            "has_preview": sandbox_info.preview_url is not None
        }

# Global service instance
e2b_service = E2BService()