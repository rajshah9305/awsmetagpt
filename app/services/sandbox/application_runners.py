"""
Application runners for different project types
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
import asyncio

from app.core.logging import get_logger
from app.core.exceptions import SandboxExecutionException
from .process_manager import ProcessManager
from .file_manager import SandboxFileManager

logger = get_logger(__name__)


class ApplicationRunner(ABC):
    """Abstract base class for application runners"""
    
    def __init__(self, sandbox_id: str, process_manager: ProcessManager, file_manager: SandboxFileManager):
        self.sandbox_id = sandbox_id
        self.process_manager = process_manager
        self.file_manager = file_manager
    
    @abstractmethod
    async def can_run(self) -> bool:
        """Check if this runner can handle the project"""
        pass
    
    @abstractmethod
    async def install_dependencies(self) -> str:
        """Install project dependencies"""
        pass
    
    @abstractmethod
    async def start_application(self) -> str:
        """Start the application"""
        pass
    
    @abstractmethod
    async def build_application(self) -> str:
        """Build the application"""
        pass
    
    @abstractmethod
    def get_preview_url(self) -> Optional[str]:
        """Get preview URL for the application"""
        pass
    
    @abstractmethod
    def get_supported_commands(self) -> List[str]:
        """Get list of supported commands"""
        pass


class ReactRunner(ApplicationRunner):
    """Runner for React applications"""
    
    async def can_run(self) -> bool:
        """Check if this is a React project"""
        package_json = self.file_manager.get_file('package.json')
        if not package_json:
            return False
        
        try:
            import json
            content = json.loads(package_json['content'])
            dependencies = content.get('dependencies', {})
            return 'react' in dependencies
        except (json.JSONDecodeError, KeyError):
            return False
    
    async def install_dependencies(self) -> str:
        """Install npm dependencies"""
        logger.info(f"Installing React dependencies in sandbox {self.sandbox_id}")
        
        # Check if package-lock.json exists
        has_package_lock = self.file_manager.get_file('package-lock.json') is not None
        has_yarn_lock = self.file_manager.get_file('yarn.lock') is not None
        
        if has_yarn_lock:
            command = "yarn install"
        elif has_package_lock:
            command = "npm ci"
        else:
            command = "npm install"
        
        process_id = await self.process_manager.start_process(
            command=command,
            working_dir="/home/user/app"
        )
        
        return process_id
    
    async def start_application(self) -> str:
        """Start React development server"""
        logger.info(f"Starting React application in sandbox {self.sandbox_id}")
        
        # Try different start commands
        package_json = self.file_manager.get_file('package.json')
        if package_json:
            try:
                import json
                content = json.loads(package_json['content'])
                scripts = content.get('scripts', {})
                
                if 'dev' in scripts:
                    command = "npm run dev"
                elif 'start' in scripts:
                    command = "npm start"
                else:
                    command = "npx react-scripts start"
            except (json.JSONDecodeError, KeyError):
                command = "npm start"
        else:
            command = "npm start"
        
        process_id = await self.process_manager.start_process(
            command=command,
            working_dir="/home/user/app",
            env={"PORT": "3000", "BROWSER": "none"}
        )
        
        return process_id
    
    async def build_application(self) -> str:
        """Build React application"""
        logger.info(f"Building React application in sandbox {self.sandbox_id}")
        
        process_id = await self.process_manager.start_process(
            command="npm run build",
            working_dir="/home/user/app"
        )
        
        return process_id
    
    def get_preview_url(self) -> Optional[str]:
        """Get preview URL"""
        return f"https://{self.sandbox_id}.e2b.dev:3000"
    
    def get_supported_commands(self) -> List[str]:
        """Get supported commands"""
        return [
            "npm install",
            "yarn install", 
            "npm start",
            "yarn start",
            "npm run dev",
            "npm run build",
            "npm test"
        ]


class PythonRunner(ApplicationRunner):
    """Runner for Python applications"""
    
    async def can_run(self) -> bool:
        """Check if this is a Python project"""
        has_requirements = self.file_manager.get_file('requirements.txt') is not None
        has_setup_py = self.file_manager.get_file('setup.py') is not None
        has_py_files = len(self.file_manager.get_files_by_type('code')) > 0
        
        return has_requirements or has_setup_py or has_py_files
    
    async def install_dependencies(self) -> str:
        """Install Python dependencies"""
        logger.info(f"Installing Python dependencies in sandbox {self.sandbox_id}")
        
        requirements_file = self.file_manager.get_file('requirements.txt')
        if requirements_file:
            command = "pip install -r requirements.txt"
        else:
            command = "pip install flask fastapi uvicorn"  # Common dependencies
        
        process_id = await self.process_manager.start_process(
            command=command,
            working_dir="/home/user/app"
        )
        
        return process_id
    
    async def start_application(self) -> str:
        """Start Python application"""
        logger.info(f"Starting Python application in sandbox {self.sandbox_id}")
        
        # Look for main files
        main_files = ['main.py', 'app.py', 'run.py', 'server.py']
        main_file = None
        
        for filename in main_files:
            if self.file_manager.get_file(filename):
                main_file = filename
                break
        
        if main_file:
            # Check if it's a web framework
            file_info = self.file_manager.get_file(main_file)
            content = file_info['content'].lower()
            
            if 'fastapi' in content or 'uvicorn' in content:
                command = f"uvicorn {main_file.replace('.py', '')}:app --host 0.0.0.0 --port 8000"
            elif 'flask' in content:
                command = f"python {main_file}"
            else:
                command = f"python {main_file}"
        else:
            # Default to simple HTTP server
            command = "python -m http.server 8000"
        
        process_id = await self.process_manager.start_process(
            command=command,
            working_dir="/home/user/app",
            env={"PYTHONPATH": "/home/user/app"}
        )
        
        return process_id
    
    async def build_application(self) -> str:
        """Build Python application (usually not needed)"""
        logger.info(f"Building Python application in sandbox {self.sandbox_id}")
        
        # For Python, we might just run tests or linting
        process_id = await self.process_manager.start_process(
            command="python -m py_compile *.py",
            working_dir="/home/user/app"
        )
        
        return process_id
    
    def get_preview_url(self) -> Optional[str]:
        """Get preview URL"""
        return f"https://{self.sandbox_id}.e2b.dev:8000"
    
    def get_supported_commands(self) -> List[str]:
        """Get supported commands"""
        return [
            "pip install -r requirements.txt",
            "python main.py",
            "python app.py",
            "python -m http.server 8000",
            "uvicorn main:app --host 0.0.0.0 --port 8000",
            "flask run"
        ]


class NodeRunner(ApplicationRunner):
    """Runner for Node.js applications"""
    
    async def can_run(self) -> bool:
        """Check if this is a Node.js project"""
        package_json = self.file_manager.get_file('package.json')
        if not package_json:
            return False
        
        try:
            import json
            content = json.loads(package_json['content'])
            dependencies = content.get('dependencies', {})
            
            # Check for Node.js specific packages (not React/Vue/Angular)
            node_packages = ['express', 'koa', 'fastify', 'hapi', 'socket.io']
            return any(pkg in dependencies for pkg in node_packages)
        except (json.JSONDecodeError, KeyError):
            return False
    
    async def install_dependencies(self) -> str:
        """Install npm dependencies"""
        logger.info(f"Installing Node.js dependencies in sandbox {self.sandbox_id}")
        
        has_package_lock = self.file_manager.get_file('package-lock.json') is not None
        has_yarn_lock = self.file_manager.get_file('yarn.lock') is not None
        
        if has_yarn_lock:
            command = "yarn install"
        elif has_package_lock:
            command = "npm ci"
        else:
            command = "npm install"
        
        process_id = await self.process_manager.start_process(
            command=command,
            working_dir="/home/user/app"
        )
        
        return process_id
    
    async def start_application(self) -> str:
        """Start Node.js application"""
        logger.info(f"Starting Node.js application in sandbox {self.sandbox_id}")
        
        package_json = self.file_manager.get_file('package.json')
        if package_json:
            try:
                import json
                content = json.loads(package_json['content'])
                scripts = content.get('scripts', {})
                
                if 'dev' in scripts:
                    command = "npm run dev"
                elif 'start' in scripts:
                    command = "npm start"
                else:
                    # Look for main file
                    main = content.get('main', 'index.js')
                    command = f"node {main}"
            except (json.JSONDecodeError, KeyError):
                command = "node index.js"
        else:
            command = "node index.js"
        
        process_id = await self.process_manager.start_process(
            command=command,
            working_dir="/home/user/app",
            env={"PORT": "3000"}
        )
        
        return process_id
    
    async def build_application(self) -> str:
        """Build Node.js application"""
        logger.info(f"Building Node.js application in sandbox {self.sandbox_id}")
        
        process_id = await self.process_manager.start_process(
            command="npm run build",
            working_dir="/home/user/app"
        )
        
        return process_id
    
    def get_preview_url(self) -> Optional[str]:
        """Get preview URL"""
        return f"https://{self.sandbox_id}.e2b.dev:3000"
    
    def get_supported_commands(self) -> List[str]:
        """Get supported commands"""
        return [
            "npm install",
            "yarn install",
            "npm start",
            "npm run dev",
            "node index.js",
            "node server.js"
        ]


class StaticRunner(ApplicationRunner):
    """Runner for static HTML/CSS/JS applications"""
    
    async def can_run(self) -> bool:
        """Check if this is a static project"""
        has_html = any(f['name'].endswith('.html') for f in self.file_manager.get_all_files())
        has_no_package_json = self.file_manager.get_file('package.json') is None
        
        return has_html and has_no_package_json
    
    async def install_dependencies(self) -> str:
        """No dependencies to install for static sites"""
        logger.info(f"No dependencies to install for static site in sandbox {self.sandbox_id}")
        
        # Just create a dummy completed process
        process_id = await self.process_manager.start_process(
            command="echo 'No dependencies required for static site'",
            working_dir="/home/user/app"
        )
        
        return process_id
    
    async def start_application(self) -> str:
        """Start static file server"""
        logger.info(f"Starting static file server in sandbox {self.sandbox_id}")
        
        process_id = await self.process_manager.start_process(
            command="python -m http.server 8000",
            working_dir="/home/user/app"
        )
        
        return process_id
    
    async def build_application(self) -> str:
        """No build needed for static sites"""
        logger.info(f"No build required for static site in sandbox {self.sandbox_id}")
        
        process_id = await self.process_manager.start_process(
            command="echo 'No build required for static site'",
            working_dir="/home/user/app"
        )
        
        return process_id
    
    def get_preview_url(self) -> Optional[str]:
        """Get preview URL"""
        return f"https://{self.sandbox_id}.e2b.dev:8000"
    
    def get_supported_commands(self) -> List[str]:
        """Get supported commands"""
        return [
            "python -m http.server 8000",
            "npx serve .",
            "php -S 0.0.0.0:8000"
        ]


class ApplicationRunnerFactory:
    """Factory for creating appropriate application runners"""
    
    @staticmethod
    def create_runner(
        sandbox_id: str, 
        process_manager: ProcessManager, 
        file_manager: SandboxFileManager
    ) -> ApplicationRunner:
        """Create appropriate runner based on project type"""
        
        runners = [
            ReactRunner(sandbox_id, process_manager, file_manager),
            PythonRunner(sandbox_id, process_manager, file_manager),
            NodeRunner(sandbox_id, process_manager, file_manager),
            StaticRunner(sandbox_id, process_manager, file_manager)
        ]
        
        return runners  # Return all runners for now
    
    @staticmethod
    async def get_best_runner(
        sandbox_id: str,
        process_manager: ProcessManager,
        file_manager: SandboxFileManager
    ) -> ApplicationRunner:
        """Get the best runner for the project"""
        
        runners = [
            ReactRunner(sandbox_id, process_manager, file_manager),
            PythonRunner(sandbox_id, process_manager, file_manager), 
            NodeRunner(sandbox_id, process_manager, file_manager),
            StaticRunner(sandbox_id, process_manager, file_manager)
        ]
        
        # Test each runner
        for runner in runners:
            if await runner.can_run():
                logger.info(f"Selected {runner.__class__.__name__} for sandbox {sandbox_id}")
                return runner
        
        # Default to static runner
        logger.info(f"No specific runner found, using StaticRunner for sandbox {sandbox_id}")
        return StaticRunner(sandbox_id, process_manager, file_manager)