"""
E2B Sandbox service for live code execution and preview
"""

import asyncio
import logging
from typing import Dict, List, Optional
from datetime import datetime
import json

from app.core.config import settings

logger = logging.getLogger(__name__)

class E2BService:
    """Service for managing E2B sandboxes and code execution"""

    def __init__(self):
        self.active_sandboxes: Dict[str, Dict] = {}

    async def create_sandbox(self, generation_id: str) -> Optional[str]:
        """Create a new E2B sandbox for a generation"""
        try:
            # Import E2B dynamically to avoid issues if not installed
            from e2b import Sandbox
            
            if not settings.E2B_API_KEY:
                logger.warning("E2B API key not configured")
                return None

            # Create sandbox with proper configuration
            sandbox = Sandbox(
                template=settings.E2B_TEMPLATE_ID,
                api_key=settings.E2B_API_KEY,
                metadata={"generation_id": generation_id},
                timeout=600  # 10 minutes
            )

            # Store sandbox info
            self.active_sandboxes[generation_id] = {
                "sandbox": sandbox,
                "created_at": datetime.now(),
                "files": [],
                "status": "ready",
                "url": None,
                "process": None
            }

            logger.info(f"✅ E2B sandbox created for generation {generation_id}")
            return generation_id

        except Exception as e:
            logger.error(f"Failed to create E2B sandbox: {e}")
            return None

    async def write_files(self, generation_id: str, artifacts: List[Dict]) -> bool:
        """Write generated artifacts to the sandbox"""
        if generation_id not in self.active_sandboxes:
            logger.error(f"Sandbox not found for generation {generation_id}")
            return False

        try:
            sandbox_info = self.active_sandboxes[generation_id]
            sandbox = sandbox_info["sandbox"]

            for artifact in artifacts:
                filename = artifact.get("file_path", artifact.get("name", "unknown.txt"))
                content = artifact.get("content", "")
                
                if not content:
                    continue

                # Ensure proper file path
                if not filename.startswith("/"):
                    filename = f"/home/user/{filename}"

                # Create directory if needed
                dir_path = "/".join(filename.split("/")[:-1])
                if dir_path and dir_path != "/home/user":
                    sandbox.filesystem.make_dir(dir_path)

                # Write file to sandbox (synchronous call)
                sandbox.filesystem.write(filename, content)
                sandbox_info["files"].append(filename)
                
                logger.info(f"📄 Created file: {filename}")

            return True

        except Exception as e:
            logger.error(f"Failed to write files to sandbox: {e}")
            return False

    async def run_application(self, generation_id: str) -> Optional[str]:
        """Run the generated application in the sandbox"""
        if generation_id not in self.active_sandboxes:
            return None

        try:
            sandbox_info = self.active_sandboxes[generation_id]
            sandbox = sandbox_info["sandbox"]
            files = sandbox_info["files"]

            # Detect project type and run accordingly
            project_type = self._detect_project_type(files)
            
            if project_type == "react":
                return await self._run_react_app(sandbox, sandbox_info)
            elif project_type == "python":
                return await self._run_python_app(sandbox, sandbox_info)
            elif project_type == "html":
                return await self._run_html_app(sandbox, sandbox_info)
            elif project_type == "node":
                return await self._run_node_app(sandbox, sandbox_info)
            else:
                # Default: create a simple preview
                return await self._run_default_preview(sandbox, sandbox_info, files)

        except Exception as e:
            logger.error(f"Failed to run application in sandbox: {e}")
            return None

    async def _run_react_app(self, sandbox, sandbox_info: Dict) -> Optional[str]:
        """Run a React application"""
        try:
            # Check if package.json exists
            package_json_exists = sandbox.filesystem.exists("/home/user/package.json")
            
            if not package_json_exists:
                # Create a basic package.json for React
                package_json = {
                    "name": "generated-app",
                    "version": "1.0.0",
                    "scripts": {
                        "start": "react-scripts start",
                        "build": "react-scripts build"
                    },
                    "dependencies": {
                        "react": "^18.0.0",
                        "react-dom": "^18.0.0",
                        "react-scripts": "5.0.1"
                    }
                }
                sandbox.filesystem.write("/home/user/package.json", json.dumps(package_json, indent=2))

            # Install dependencies
            install_process = sandbox.process.start("cd /home/user && npm install")
            install_process.wait()

            # Start the React app
            start_process = sandbox.process.start("cd /home/user && npm start")
            sandbox_info["process"] = start_process
            sandbox_info["status"] = "running"

            # Get the URL (React typically runs on port 3000)
            url = f"https://{sandbox.get_hostname(3000)}"
            sandbox_info["url"] = url
            
            return url

        except Exception as e:
            logger.error(f"Failed to run React app: {e}")
            return None

    async def _run_python_app(self, sandbox, sandbox_info: Dict) -> Optional[str]:
        """Run a Python application (typically with Streamlit or Flask)"""
        try:
            # Check for main Python file
            main_files = ["/home/user/app.py", "/home/user/main.py", "/home/user/streamlit_app.py"]
            main_file = None
            
            for file_path in main_files:
                if sandbox.filesystem.exists(file_path):
                    main_file = file_path
                    break
            
            if not main_file:
                # Create a simple Streamlit app
                main_file = "/home/user/app.py"
                streamlit_code = self._generate_streamlit_app(sandbox_info["files"])
                sandbox.filesystem.write(main_file, streamlit_code)

            # Install required packages
            requirements = ["streamlit", "pandas", "numpy"]
            install_cmd = f"pip install {' '.join(requirements)}"
            install_process = sandbox.process.start(install_cmd)
            install_process.wait()

            # Start Streamlit app
            start_process = sandbox.process.start(f"streamlit run {main_file} --server.port 8501 --server.address 0.0.0.0")
            sandbox_info["process"] = start_process
            sandbox_info["status"] = "running"

            # Get the URL (Streamlit runs on port 8501)
            url = f"https://{sandbox.get_hostname(8501)}"
            sandbox_info["url"] = url
            
            return url

        except Exception as e:
            logger.error(f"Failed to run Python app: {e}")
            return None

    async def _run_html_app(self, sandbox, sandbox_info: Dict) -> Optional[str]:
        """Run an HTML application with a simple HTTP server"""
        try:
            # Start a simple HTTP server
            start_process = sandbox.process.start("cd /home/user && python -m http.server 8000")
            sandbox_info["process"] = start_process
            sandbox_info["status"] = "running"

            # Get the URL
            url = f"https://{sandbox.get_hostname(8000)}"
            sandbox_info["url"] = url
            
            return url

        except Exception as e:
            logger.error(f"Failed to run HTML app: {e}")
            return None

    async def _run_node_app(self, sandbox, sandbox_info: Dict) -> Optional[str]:
        """Run a Node.js application"""
        try:
            # Check if package.json exists
            package_json_exists = sandbox.filesystem.exists("/home/user/package.json")
            
            if not package_json_exists:
                # Create a basic package.json
                package_json = {
                    "name": "generated-app",
                    "version": "1.0.0",
                    "main": "index.js",
                    "scripts": {
                        "start": "node index.js"
                    },
                    "dependencies": {
                        "express": "^4.18.0"
                    }
                }
                sandbox.filesystem.write("/home/user/package.json", json.dumps(package_json, indent=2))

            # Install dependencies
            install_process = sandbox.process.start("cd /home/user && npm install")
            install_process.wait()

            # Start the Node app
            start_process = sandbox.process.start("cd /home/user && npm start")
            sandbox_info["process"] = start_process
            sandbox_info["status"] = "running"

            # Get the URL (assuming Express runs on port 3000)
            url = f"https://{sandbox.get_hostname(3000)}"
            sandbox_info["url"] = url
            
            return url

        except Exception as e:
            logger.error(f"Failed to run Node app: {e}")
            return None

    async def _run_default_preview(self, sandbox, sandbox_info: Dict, files: List[str]) -> Optional[str]:
        """Create a default preview for any type of files"""
        try:
            # Create a simple Streamlit app to display files
            streamlit_code = self._generate_streamlit_app(files)
            sandbox.filesystem.write("/home/user/preview_app.py", streamlit_code)

            # Install Streamlit
            install_process = sandbox.process.start("pip install streamlit")
            install_process.wait()

            # Start Streamlit app
            start_process = sandbox.process.start("streamlit run /home/user/preview_app.py --server.port 8501 --server.address 0.0.0.0")
            sandbox_info["process"] = start_process
            sandbox_info["status"] = "running"

            # Get the URL
            url = f"https://{sandbox.get_hostname(8501)}"
            sandbox_info["url"] = url
            
            return url

        except Exception as e:
            logger.error(f"Failed to run default preview: {e}")
            return None

    def _detect_project_type(self, files: List[str]) -> str:
        """Detect the type of project based on files"""
        file_names = [f.split("/")[-1].lower() for f in files]
        
        if "package.json" in file_names and any(f.endswith(('.jsx', '.tsx')) for f in file_names):
            return "react"
        elif "package.json" in file_names:
            return "node"
        elif any(f.endswith('.py') for f in file_names):
            return "python"
        elif any(f.endswith('.html') for f in file_names):
            return "html"
        else:
            return "unknown"

    def _generate_streamlit_app(self, files: List[str]) -> str:
        """Generate a Streamlit app to display the generated files"""
        return f'''
import streamlit as st
import os

st.title("Generated Application Preview")
st.write("This is a preview of the generated application files.")

# List all files
files = {files}

# Create tabs for each file
if files:
    tabs = st.tabs([os.path.basename(f) for f in files[:10]])  # Limit to 10 tabs
    
    for i, (tab, file_path) in enumerate(zip(tabs, files[:10])):
        with tab:
            st.subheader(f"📄 {{os.path.basename(file_path)}}")
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Determine file type for syntax highlighting
                if file_path.endswith(('.py', '.js', '.jsx', '.ts', '.tsx', '.html', '.css', '.json')):
                    st.code(content, language=file_path.split('.')[-1])
                else:
                    st.text(content)
                    
            except Exception as e:
                st.error(f"Could not read file: {{e}}")
else:
    st.info("No files found in the generated application.")

st.sidebar.title("File Explorer")
for file_path in files:
    st.sidebar.text(f"📄 {{os.path.basename(file_path)}}")
'''

    async def stop_application(self, generation_id: str) -> bool:
        """Stop the running application"""
        if generation_id not in self.active_sandboxes:
            return False

        try:
            sandbox_info = self.active_sandboxes[generation_id]
            process = sandbox_info.get("process")
            
            if process:
                process.kill()
                sandbox_info["process"] = None
                sandbox_info["status"] = "stopped"
                sandbox_info["url"] = None
                
            logger.info(f"✅ Stopped application for generation {generation_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to stop application: {e}")
            return False

    async def get_logs(self, generation_id: str) -> List[str]:
        """Get logs from the running application"""
        if generation_id not in self.active_sandboxes:
            return []

        try:
            sandbox_info = self.active_sandboxes[generation_id]
            process = sandbox_info.get("process")
            
            if not process:
                return ["No running process found"]

            # Get recent logs
            logs = []
            try:
                # Try to get stdout/stderr (synchronous calls)
                stdout = process.stdout
                stderr = process.stderr
                
                if stdout:
                    logs.extend(str(stdout).split('\n'))
                if stderr:
                    logs.extend(str(stderr).split('\n'))
                    
            except Exception:
                logs.append("Could not retrieve process logs")

            return [log for log in logs if log.strip()]

        except Exception as e:
            logger.error(f"Failed to get logs: {e}")
            return [f"Error retrieving logs: {str(e)}"]

    async def cleanup_sandbox(self, generation_id: str) -> bool:
        """Clean up and terminate the sandbox"""
        if generation_id not in self.active_sandboxes:
            return False

        try:
            sandbox_info = self.active_sandboxes[generation_id]
            sandbox = sandbox_info["sandbox"]
            
            # Stop any running processes
            await self.stop_application(generation_id)
            
            # Close the sandbox
            sandbox.close()
            
            # Remove from active sandboxes
            del self.active_sandboxes[generation_id]
            
            logger.info(f"✅ Cleaned up sandbox for generation {generation_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to cleanup sandbox: {e}")
            return False

    def get_sandbox_info(self, generation_id: str) -> Optional[Dict]:
        """Get sandbox information"""
        return self.active_sandboxes.get(generation_id)

# Global service instance
e2b_service = E2BService()