"""
File management for sandboxes
"""

import json
import mimetypes
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from app.core.logging import get_logger
from app.core.exceptions import SandboxException
from app.core.config_clean import settings

logger = get_logger(__name__)


class SandboxFileManager:
    """Manages files within sandboxes"""
    
    def __init__(self, sandbox_id: str):
        self.sandbox_id = sandbox_id
        self.files: Dict[str, Dict] = {}
        self.project_type: Optional[str] = None
    
    async def write_files(self, artifacts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Write multiple files to sandbox"""
        results = {
            'success': True,
            'files_written': 0,
            'errors': [],
            'project_type': None
        }
        
        try:
            # Validate file count
            if len(artifacts) > settings.files.MAX_FILES_PER_SESSION:
                raise SandboxException(f"Too many files: {len(artifacts)} (max: {settings.files.MAX_FILES_PER_SESSION})")
            
            # Write each file
            for artifact in artifacts:
                try:
                    await self._write_single_file(artifact)
                    results['files_written'] += 1
                except Exception as e:
                    error_msg = f"Failed to write {artifact.get('name', 'unknown')}: {str(e)}"
                    results['errors'].append(error_msg)
                    logger.error(error_msg)
            
            # Detect project type
            self.project_type = self._detect_project_type()
            results['project_type'] = self.project_type
            
            logger.info(f"Wrote {results['files_written']} files to sandbox {self.sandbox_id}")
            
        except Exception as e:
            results['success'] = False
            results['errors'].append(str(e))
            logger.error(f"Failed to write files to sandbox {self.sandbox_id}: {e}")
        
        return results
    
    async def _write_single_file(self, artifact: Dict[str, Any]):
        """Write a single file to sandbox"""
        # Validate artifact
        required_fields = ['name', 'content']
        for field in required_fields:
            if field not in artifact:
                raise SandboxException(f"Artifact missing required field: {field}")
        
        file_name = artifact['name']
        content = artifact['content']
        
        # Validate file size
        if len(content) > settings.files.MAX_FILE_SIZE:
            raise SandboxException(f"File {file_name} too large: {len(content)} bytes")
        
        # Sanitize file name
        safe_name = self._sanitize_filename(file_name)
        
        # Determine file path
        file_path = self._determine_file_path(safe_name, artifact)
        
        # Store file info
        file_info = {
            'name': safe_name,
            'path': file_path,
            'content': content,
            'size': len(content),
            'type': artifact.get('type', 'unknown'),
            'language': artifact.get('language'),
            'created_at': datetime.now().isoformat(),
            'mime_type': mimetypes.guess_type(safe_name)[0]
        }
        
        self.files[file_path] = file_info
        
        # In real implementation, this would write to E2B sandbox
        logger.debug(f"Wrote file {file_path} ({len(content)} bytes) to sandbox {self.sandbox_id}")
    
    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for security"""
        # Remove dangerous characters
        dangerous_chars = ['..', '/', '\\', ':', '*', '?', '"', '<', '>', '|']
        safe_name = filename
        
        for char in dangerous_chars:
            safe_name = safe_name.replace(char, '_')
        
        # Ensure reasonable length
        if len(safe_name) > 255:
            name_part, ext = safe_name.rsplit('.', 1) if '.' in safe_name else (safe_name, '')
            safe_name = name_part[:250] + ('.' + ext if ext else '')
        
        return safe_name
    
    def _determine_file_path(self, filename: str, artifact: Dict) -> str:
        """Determine appropriate file path"""
        # Use provided path if available
        if 'file_path' in artifact and artifact['file_path']:
            return artifact['file_path']
        
        # Determine based on file type and name
        name_lower = filename.lower()
        file_type = artifact.get('type', 'unknown')
        language = artifact.get('language')
        
        # Root level files
        root_files = [
            'readme.md', 'package.json', 'requirements.txt', 'dockerfile',
            'docker-compose.yml', '.gitignore', 'makefile', 'setup.py'
        ]
        
        if name_lower in root_files:
            return filename
        
        # Determine directory based on type and language
        if file_type == 'documentation':
            if 'readme' in name_lower:
                return filename
            return f"docs/{filename}"
        
        elif file_type == 'configuration':
            if name_lower.endswith(('.json', '.yaml', '.yml', '.toml', '.ini')):
                return f"config/{filename}"
            return filename
        
        elif file_type == 'code':
            if language == 'python':
                if 'test' in name_lower:
                    return f"tests/{filename}"
                return f"src/{filename}"
            
            elif language in ['javascript', 'typescript']:
                if 'test' in name_lower or 'spec' in name_lower:
                    return f"tests/{filename}"
                elif filename.endswith(('.jsx', '.tsx')):
                    return f"src/components/{filename}"
                elif filename.endswith(('.js', '.ts')):
                    return f"src/{filename}"
                return f"src/{filename}"
            
            elif language == 'html':
                return f"public/{filename}"
            
            elif language == 'css':
                return f"src/styles/{filename}"
        
        # Default to src directory
        return f"src/{filename}"
    
    def _detect_project_type(self) -> Optional[str]:
        """Detect project type based on files"""
        file_names = [info['name'].lower() for info in self.files.values()]
        
        # React project
        if 'package.json' in file_names:
            package_json = next((f for f in self.files.values() if f['name'].lower() == 'package.json'), None)
            if package_json:
                try:
                    content = json.loads(package_json['content'])
                    dependencies = content.get('dependencies', {})
                    if 'react' in dependencies:
                        return 'react'
                    elif 'vue' in dependencies:
                        return 'vue'
                    elif 'angular' in dependencies:
                        return 'angular'
                    elif 'express' in dependencies:
                        return 'node'
                    else:
                        return 'javascript'
                except json.JSONDecodeError:
                    pass
        
        # Python project
        if 'requirements.txt' in file_names or 'setup.py' in file_names:
            return 'python'
        
        # Check for specific frameworks
        has_jsx = any(f['name'].endswith(('.jsx', '.tsx')) for f in self.files.values())
        if has_jsx:
            return 'react'
        
        has_py = any(f['name'].endswith('.py') for f in self.files.values())
        if has_py:
            return 'python'
        
        has_js = any(f['name'].endswith(('.js', '.ts')) for f in self.files.values())
        if has_js:
            return 'javascript'
        
        return 'unknown'
    
    def get_file(self, file_path: str) -> Optional[Dict]:
        """Get file information"""
        return self.files.get(file_path)
    
    def get_all_files(self) -> List[Dict]:
        """Get all files"""
        return list(self.files.values())
    
    def get_files_by_type(self, file_type: str) -> List[Dict]:
        """Get files by type"""
        return [f for f in self.files.values() if f.get('type') == file_type]
    
    def get_project_structure(self) -> Dict[str, Any]:
        """Get project structure"""
        structure = {}
        
        for file_path, file_info in self.files.items():
            parts = file_path.split('/')
            current = structure
            
            # Build nested structure
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]
            
            # Add file
            current[parts[-1]] = {
                'type': 'file',
                'size': file_info['size'],
                'language': file_info.get('language'),
                'mime_type': file_info.get('mime_type')
            }
        
        return structure
    
    def get_entry_points(self) -> List[str]:
        """Get potential entry points for the application"""
        entry_points = []
        
        # Common entry point files
        common_entries = [
            'index.html', 'index.js', 'index.ts', 'index.jsx', 'index.tsx',
            'main.py', 'app.py', 'server.js', 'server.ts',
            'package.json'  # For npm scripts
        ]
        
        for file_info in self.files.values():
            if file_info['name'].lower() in common_entries:
                entry_points.append(file_info['path'])
        
        return entry_points
    
    def get_run_commands(self) -> List[str]:
        """Get suggested run commands based on project type"""
        commands = []
        
        if self.project_type == 'react':
            commands.extend(['npm start', 'yarn start', 'npm run dev'])
        elif self.project_type == 'vue':
            commands.extend(['npm run serve', 'yarn serve', 'npm run dev'])
        elif self.project_type == 'angular':
            commands.extend(['ng serve', 'npm start'])
        elif self.project_type == 'node':
            commands.extend(['npm start', 'node server.js', 'node index.js'])
        elif self.project_type == 'python':
            # Look for main files
            main_files = [f for f in self.files.values() 
                         if f['name'].lower() in ['main.py', 'app.py', 'run.py']]
            if main_files:
                commands.extend([f"python {f['name']}" for f in main_files])
            else:
                commands.append('python -m http.server 8000')
        elif self.project_type == 'javascript':
            commands.extend(['node index.js', 'npm start'])
        
        # Add generic commands
        if not commands:
            commands.extend(['python -m http.server 8000', 'npx serve .'])
        
        return commands
    
    def get_statistics(self) -> Dict:
        """Get file statistics"""
        total_files = len(self.files)
        total_size = sum(f['size'] for f in self.files.values())
        
        type_counts = {}
        language_counts = {}
        
        for file_info in self.files.values():
            # Count by type
            file_type = file_info.get('type', 'unknown')
            type_counts[file_type] = type_counts.get(file_type, 0) + 1
            
            # Count by language
            language = file_info.get('language')
            if language:
                language_counts[language] = language_counts.get(language, 0) + 1
        
        return {
            'total_files': total_files,
            'total_size_bytes': total_size,
            'project_type': self.project_type,
            'type_distribution': type_counts,
            'language_distribution': language_counts,
            'entry_points': self.get_entry_points(),
            'suggested_commands': self.get_run_commands()
        }