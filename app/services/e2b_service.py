"""
E2B Sandbox service for live code execution and preview
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

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

            # Create sandbox
            sandbox = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: Sandbox.create(
                    api_key=settings.E2B_API_KEY,
                    metadata={"generation_id": generation_id},
                    timeout=600  # 10 minutes
                )
            )

            # Store sandbox info
            self.active_sandboxes[generation_id] = {
                "sandbox": sandbox,
                "created_at": datetime.now(),
                "files": [],
                "status": "ready"
            }

            logger.info(f"✅ E2B sandbox created for generation {generation_id}")
            return generation_id

        except Exception as e:
            logger.error(f"Failed to create E2B sandbox: {e}")
            return None

    async def write_files(self, generation_id: str, artifacts: List[Dict]) -> bool:
        """Write generated artifacts to the sandbox"""
        if generation_id not in self.active_sandboxes:
            return False

        try:
            sandbox = self.active_sandboxes[generation_id]["sandbox"]

            for artifact in artifacts:
                filename = self._get_filename_from_artifact(artifact)

                # Write file to sandbox
                await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: sandbox.files.write(filename, artifact["content"])
                )

                self.active_sandboxes[generation_id]["files"].append(filename)
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
            sandbox = self.active_sandboxes[generation_id]["sandbox"]

            # Create a simple Streamlit app to display the artifacts
            streamlit_code = self._generate_streamlit_app(
                self.active_sandboxes[generation_id]["files"]
            )

            # Write and run the Streamlit app
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: sandbox.files.write('app.py', streamlit_code)
            )

            # Install required packages
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: sandbox.commands.run('pip install streamlit')
            )

            # Start the application
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: sandbox.commands.run('streamlit run app.py --server.port 8501 --server.headless true --server.runOnSave false &')
            )

            # Get the preview URL
            hostname = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: sandbox.get_host(8501)
            )

            preview_url = f"https://{hostname}"
            logger.info(f"✅ Application running at: {preview_url}")

            return preview_url

        except Exception as e:
            logger.error(f"Failed to run application: {e}")
            return None

    async def stop_application(self, generation_id: str) -> bool:
        """Stop the running application"""
        if generation_id not in self.active_sandboxes:
            return False

        try:
            sandbox = self.active_sandboxes[generation_id]["sandbox"]

            # Kill any running processes
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: sandbox.commands.run('pkill -f streamlit')
            )

            logger.info(f"🛑 Application stopped for generation {generation_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to stop application: {e}")
            return False

    async def get_logs(self, generation_id: str) -> List[str]:
        """Get logs from the sandbox"""
        if generation_id not in self.active_sandboxes:
            return []

        try:
            sandbox = self.active_sandboxes[generation_id]["sandbox"]

            # This is a simplified log retrieval - in practice you'd want to
            # capture stdout/stderr from the running processes
            logs = ["Sandbox initialized", "Files created successfully"]

            if self.active_sandboxes[generation_id]["status"] == "running":
                logs.append("Application is running")

            return logs

        except Exception as e:
            logger.error(f"Failed to get logs: {e}")
            return []

    async def cleanup_sandbox(self, generation_id: str) -> bool:
        """Clean up and close the sandbox"""
        if generation_id not in self.active_sandboxes:
            return True

        try:
            sandbox = self.active_sandboxes[generation_id]["sandbox"]

            # Close the sandbox
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: sandbox.kill()
            )

            # Remove from active sandboxes
            del self.active_sandboxes[generation_id]

            logger.info(f"🧹 Sandbox cleaned up for generation {generation_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to cleanup sandbox: {e}")
            return False

    def _get_filename_from_artifact(self, artifact: Dict) -> str:
        """Get appropriate filename from artifact"""
        import re
        name = artifact.get("name", "").lower().replace(" ", "_")

        extension_map = {
            'product requirements document': 'requirements.md',
            'system architecture design': 'architecture.md',
            'project plan & timeline': 'project_plan.md',
            'technical implementation': 'implementation.md',
            'test strategy & cases': 'test_strategy.md',
            'deployment & infrastructure': 'deployment.md'
        }

        return extension_map.get(artifact.get("name", "").toLowerCase(), f"{name}.md")

    def _generate_streamlit_app(self, files: List[str]) -> str:
        """Generate a simple Streamlit app to display artifacts"""
        return f'''import streamlit as st

st.title("🚀 Generated Application Documentation")
st.write("This application was generated by AI agents!")

st.header("Generated Documentation")

# Display files
files_created = {files!r}

for filename in files_created:
    try:
        with open(filename, 'r') as f:
            content = f.read()

        with st.expander(f"📄 {{filename}}"):
            if filename.endswith('.md'):
                st.markdown(content)
            else:
                st.code(content, language='text')
    except Exception as e:
        st.error(f"Error reading {{filename}}: {{e}}")

st.success("✅ Documentation generated successfully!")
'''

# Global instance
e2b_service = E2BService()