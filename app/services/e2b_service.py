"""
Clean E2B service using modular components
"""

from typing import Dict, List, Optional, Any

from app.core.logging import get_logger
from app.core.exceptions import SandboxException
from .sandbox import SandboxManager, SandboxConfig

logger = get_logger(__name__)


class E2BService:
    """Clean E2B service interface"""
    
    def __init__(self):
        self.sandbox_manager = SandboxManager()
    
    async def create_sandbox(self, session_id: str, template: str = "base") -> str:
        """Create a new sandbox for the session"""
        config = SandboxConfig(template_id=template)
        return await self.sandbox_manager.create_sandbox(session_id, config)
    
    async def write_files(self, session_id: str, artifacts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Write files to the session's sandbox"""
        sandbox_id = self.sandbox_manager.get_sandbox_by_session(session_id)
        if not sandbox_id:
            # Create sandbox if it doesn't exist
            sandbox_id = await self.create_sandbox(session_id)
        
        return await self.sandbox_manager.write_files(sandbox_id, artifacts)
    
    async def run_application(self, session_id: str, command: Optional[str] = None) -> Dict[str, Any]:
        """Run application in the session's sandbox"""
        sandbox_id = self.sandbox_manager.get_sandbox_by_session(session_id)
        if not sandbox_id:
            raise SandboxException(f"No sandbox found for session {session_id}")
        
        return await self.sandbox_manager.run_application(sandbox_id, command)
    
    async def stop_application(self, session_id: str) -> bool:
        """Stop application in the session's sandbox"""
        sandbox_id = self.sandbox_manager.get_sandbox_by_session(session_id)
        if not sandbox_id:
            return False
        
        return await self.sandbox_manager.stop_application(sandbox_id)
    
    async def get_logs(self, session_id: str, lines: int = 100) -> Dict[str, Any]:
        """Get logs from the session's sandbox"""
        sandbox_id = self.sandbox_manager.get_sandbox_by_session(session_id)
        if not sandbox_id:
            raise SandboxException(f"No sandbox found for session {session_id}")
        
        return await self.sandbox_manager.get_logs(sandbox_id, lines=lines)
    
    def get_sandbox_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get sandbox information for the session"""
        sandbox_id = self.sandbox_manager.get_sandbox_by_session(session_id)
        if not sandbox_id:
            return None
        
        return self.sandbox_manager.get_sandbox_info(sandbox_id)
    
    async def cleanup_session(self, session_id: str) -> bool:
        """Clean up sandbox for the session"""
        sandbox_id = self.sandbox_manager.get_sandbox_by_session(session_id)
        if not sandbox_id:
            return False
        
        return await self.sandbox_manager.cleanup_sandbox(sandbox_id)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get E2B service statistics"""
        return self.sandbox_manager.get_statistics()


# Global instance
e2b_service = E2BService()