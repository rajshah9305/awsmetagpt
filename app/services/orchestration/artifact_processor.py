"""
Artifact processing and management
"""

import json
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from app.core.logging import get_logger
from app.core.exceptions import OrchestrationException
from app.core.config import settings

logger = get_logger(__name__)


class ArtifactProcessor:
    """Processes and manages generated artifacts"""
    
    def __init__(self):
        self.artifacts_cache: Dict[str, Dict] = {}
        self.workspace_base = Path(settings.METAGPT_WORKSPACE)
    
    def process_artifacts(self, session_id: str, raw_artifacts: List[Dict]) -> List[Dict]:
        """Process raw artifacts into standardized format"""
        processed_artifacts = []
        
        for artifact in raw_artifacts:
            try:
                processed = self._process_single_artifact(session_id, artifact)
                if processed:
                    processed_artifacts.append(processed)
                    self.artifacts_cache[processed['id']] = processed
            except Exception as e:
                logger.error(f"Failed to process artifact: {e}")
        
        logger.info(f"Processed {len(processed_artifacts)} artifacts for session {session_id}")
        return processed_artifacts
    
    def _process_single_artifact(self, session_id: str, artifact: Dict) -> Optional[Dict]:
        """Process a single artifact"""
        # Validate required fields
        required_fields = ['name', 'content', 'type']
        for field in required_fields:
            if field not in artifact:
                logger.warning(f"Artifact missing required field: {field}")
                return None
        
        # Generate unique ID
        content_hash = hashlib.md5(artifact['content'].encode()).hexdigest()[:8]
        artifact_id = f"{session_id}_{artifact['name']}_{content_hash}"
        
        # Standardize artifact
        processed = {
            'id': artifact_id,
            'session_id': session_id,
            'name': artifact['name'],
            'type': artifact['type'],
            'content': artifact['content'],
            'agent_role': artifact.get('agent_role', 'unknown'),
            'file_path': artifact.get('file_path', artifact['name']),
            'size': len(artifact['content']),
            'created_at': artifact.get('created_at', datetime.now().isoformat()),
            'language': artifact.get('language'),
            'dependencies': artifact.get('dependencies', []),
            'metadata': self._extract_metadata(artifact)
        }
        
        # Validate content
        if not self._validate_content(processed):
            logger.warning(f"Invalid content in artifact {artifact_id}")
            return None
        
        # Enhance with additional information
        processed = self._enhance_artifact(processed)
        
        return processed
    
    def _extract_metadata(self, artifact: Dict) -> Dict:
        """Extract metadata from artifact"""
        metadata = {}
        
        # Extract from content based on type
        content = artifact['content']
        artifact_type = artifact['type']
        
        if artifact_type == 'code':
            metadata.update(self._analyze_code(content, artifact.get('language')))
        elif artifact_type == 'configuration':
            metadata.update(self._analyze_config(content, artifact['name']))
        elif artifact_type == 'documentation':
            metadata.update(self._analyze_documentation(content))
        
        return metadata
    
    def _analyze_code(self, content: str, language: Optional[str]) -> Dict:
        """Analyze code content"""
        metadata = {
            'lines_of_code': len(content.splitlines()),
            'character_count': len(content),
            'language': language
        }
        
        # Language-specific analysis
        if language == 'python':
            metadata.update(self._analyze_python_code(content))
        elif language in ['javascript', 'typescript']:
            metadata.update(self._analyze_js_code(content))
        
        return metadata
    
    def _analyze_python_code(self, content: str) -> Dict:
        """Analyze Python code"""
        metadata = {}
        
        # Count imports
        import_lines = [line for line in content.splitlines() if line.strip().startswith(('import ', 'from '))]
        metadata['import_count'] = len(import_lines)
        
        # Count functions and classes
        function_count = content.count('def ')
        class_count = content.count('class ')
        metadata['function_count'] = function_count
        metadata['class_count'] = class_count
        
        # Check for common patterns
        if 'async def' in content:
            metadata['has_async'] = True
        if 'pytest' in content or 'unittest' in content:
            metadata['has_tests'] = True
        
        return metadata
    
    def _analyze_js_code(self, content: str) -> Dict:
        """Analyze JavaScript/TypeScript code"""
        metadata = {}
        
        # Count imports/requires
        import_lines = [line for line in content.splitlines() 
                       if 'import ' in line or 'require(' in line]
        metadata['import_count'] = len(import_lines)
        
        # Count functions
        function_count = content.count('function ') + content.count('=>')
        metadata['function_count'] = function_count
        
        # Check for frameworks
        if 'react' in content.lower():
            metadata['framework'] = 'react'
        elif 'vue' in content.lower():
            metadata['framework'] = 'vue'
        elif 'angular' in content.lower():
            metadata['framework'] = 'angular'
        
        return metadata
    
    def _analyze_config(self, content: str, filename: str) -> Dict:
        """Analyze configuration files"""
        metadata = {'config_type': 'unknown'}
        
        if filename.endswith('.json'):
            try:
                data = json.loads(content)
                metadata['config_type'] = 'json'
                metadata['key_count'] = len(data) if isinstance(data, dict) else 0
            except json.JSONDecodeError:
                pass
        elif filename.endswith(('.yaml', '.yml')):
            metadata['config_type'] = 'yaml'
        elif filename.endswith('.env'):
            metadata['config_type'] = 'environment'
            env_vars = [line for line in content.splitlines() 
                       if '=' in line and not line.strip().startswith('#')]
            metadata['env_var_count'] = len(env_vars)
        
        return metadata
    
    def _analyze_documentation(self, content: str) -> Dict:
        """Analyze documentation content"""
        lines = content.splitlines()
        
        metadata = {
            'line_count': len(lines),
            'word_count': len(content.split()),
            'character_count': len(content)
        }
        
        # Count headers (markdown)
        header_count = len([line for line in lines if line.strip().startswith('#')])
        metadata['header_count'] = header_count
        
        # Check for code blocks
        code_block_count = content.count('```')
        metadata['code_block_count'] = code_block_count // 2
        
        return metadata
    
    def _validate_content(self, artifact: Dict) -> bool:
        """Validate artifact content"""
        # Check size limits
        if artifact['size'] > settings.MAX_FILE_SIZE:
            logger.warning(f"Artifact {artifact['id']} exceeds size limit")
            return False
        
        # Check for suspicious content
        content = artifact['content'].lower()
        suspicious_patterns = ['<script>', 'eval(', 'exec(', 'system(']
        
        for pattern in suspicious_patterns:
            if pattern in content:
                logger.warning(f"Suspicious pattern '{pattern}' found in artifact {artifact['id']}")
                return False
        
        return True
    
    def _enhance_artifact(self, artifact: Dict) -> Dict:
        """Enhance artifact with additional information"""
        # Add file extension if missing
        if '.' not in artifact['name']:
            extension = self._get_extension_for_type(artifact['type'], artifact.get('language'))
            if extension:
                artifact['name'] += extension
        
        # Add project structure information
        artifact['project_path'] = self._determine_project_path(artifact)
        
        # Add quality score
        artifact['quality_score'] = self._calculate_quality_score(artifact)
        
        return artifact
    
    def _get_extension_for_type(self, artifact_type: str, language: Optional[str]) -> Optional[str]:
        """Get file extension for artifact type and language"""
        if artifact_type == 'code':
            language_extensions = {
                'python': '.py',
                'javascript': '.js',
                'typescript': '.ts',
                'html': '.html',
                'css': '.css'
            }
            return language_extensions.get(language)
        elif artifact_type == 'configuration':
            return '.json'
        elif artifact_type == 'documentation':
            return '.md'
        
        return None
    
    def _determine_project_path(self, artifact: Dict) -> str:
        """Determine appropriate project path for artifact"""
        name = artifact['name'].lower()
        artifact_type = artifact['type']
        language = artifact.get('language')
        
        # Common project structure patterns
        if artifact_type == 'documentation':
            if 'readme' in name:
                return '/'
            else:
                return '/docs/'
        elif artifact_type == 'configuration':
            if name in ['package.json', 'requirements.txt', 'dockerfile']:
                return '/'
            else:
                return '/config/'
        elif artifact_type == 'code':
            if language == 'python':
                if 'test' in name:
                    return '/tests/'
                else:
                    return '/src/'
            elif language in ['javascript', 'typescript']:
                if 'test' in name or 'spec' in name:
                    return '/tests/'
                elif name.endswith(('.jsx', '.tsx')):
                    return '/src/components/'
                else:
                    return '/src/'
        
        return '/src/'
    
    def _calculate_quality_score(self, artifact: Dict) -> float:
        """Calculate quality score for artifact"""
        score = 0.5  # Base score
        
        metadata = artifact.get('metadata', {})
        
        # Size-based scoring
        size = artifact['size']
        if 100 <= size <= 10000:  # Reasonable size
            score += 0.1
        elif size > 50000:  # Too large
            score -= 0.1
        
        # Content-based scoring
        if artifact['type'] == 'code':
            # Has comments
            if '#' in artifact['content'] or '//' in artifact['content']:
                score += 0.1
            
            # Has proper structure
            if metadata.get('function_count', 0) > 0:
                score += 0.1
            
            # Has imports (indicates dependencies)
            if metadata.get('import_count', 0) > 0:
                score += 0.1
        
        elif artifact['type'] == 'documentation':
            # Has headers
            if metadata.get('header_count', 0) > 0:
                score += 0.1
            
            # Reasonable length
            word_count = metadata.get('word_count', 0)
            if 50 <= word_count <= 5000:
                score += 0.1
        
        return min(1.0, max(0.0, score))
    
    def get_artifact(self, artifact_id: str) -> Optional[Dict]:
        """Get artifact by ID"""
        return self.artifacts_cache.get(artifact_id)
    
    def get_session_artifacts(self, session_id: str) -> List[Dict]:
        """Get all artifacts for a session"""
        return [artifact for artifact in self.artifacts_cache.values() 
                if artifact.get('session_id') == session_id]
    
    def save_artifacts_to_disk(self, session_id: str, artifacts: List[Dict]) -> str:
        """Save artifacts to disk and return workspace path"""
        workspace_path = self.workspace_base / session_id
        workspace_path.mkdir(parents=True, exist_ok=True)
        
        for artifact in artifacts:
            try:
                file_path = workspace_path / artifact['name']
                file_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(artifact['content'])
                
                logger.debug(f"Saved artifact {artifact['id']} to {file_path}")
                
            except Exception as e:
                logger.error(f"Failed to save artifact {artifact['id']}: {e}")
        
        return str(workspace_path)
    
    def get_statistics(self) -> Dict:
        """Get artifact statistics"""
        total_artifacts = len(self.artifacts_cache)
        
        type_counts = {}
        language_counts = {}
        total_size = 0
        
        for artifact in self.artifacts_cache.values():
            # Count by type
            artifact_type = artifact['type']
            type_counts[artifact_type] = type_counts.get(artifact_type, 0) + 1
            
            # Count by language
            language = artifact.get('language')
            if language:
                language_counts[language] = language_counts.get(language, 0) + 1
            
            # Total size
            total_size += artifact['size']
        
        return {
            'total_artifacts': total_artifacts,
            'type_distribution': type_counts,
            'language_distribution': language_counts,
            'total_size_bytes': total_size,
            'average_size_bytes': total_size / total_artifacts if total_artifacts > 0 else 0
        }