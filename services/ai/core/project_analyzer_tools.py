"""Project Analyzer Tools - Utilities for analyzing project structure and configuration."""

import json
from pathlib import Path
from typing import Dict, List


# Key configuration files to look for
KEY_CONFIG_FILES = [
    'package.json',
    'requirements.txt',
    'pyproject.toml',
    'go.mod',
    'Cargo.toml',
    'composer.json',
    'Gemfile',
    'pom.xml',
    'build.gradle',
    'next.config.js',
    'next.config.mjs',
    'tsconfig.json',
    'vite.config.js',
    'vite.config.ts',
    'Dockerfile',
    'docker-compose.yml',
    '.env.example',
    'README.md'
]


class ProjectAnalyzerTools:
    """Tools for analyzing project structure and configuration."""
    
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        
    async def analyze_project_structure(self, scan_depth: int = 2) -> Dict:
        """Analyze project directory structure."""
        structure = {
            'root_files': [],
            'directories': [],
            'key_files_found': [],
            'total_size_kb': 0
        }
        
        if not self.project_path.exists():
            return structure
        
        # Scan top-level files and directories
        for item in self.project_path.iterdir():
            try:
                if item.is_file():
                    structure['root_files'].append(item.name)
                    structure['total_size_kb'] += item.stat().st_size / 1024
                    
                    # Check if it's a key configuration file
                    if item.name in KEY_CONFIG_FILES:
                        structure['key_files_found'].append(item.name)
                elif item.is_dir() and not item.name.startswith('.'):
                    structure['directories'].append(item.name)
            except (PermissionError, OSError):
                continue
                
        return structure
    
    async def read_configuration_files(self, file_paths: List[str]) -> Dict:
        """Read and parse configuration files."""
        config_data = {}
        
        for file_path in file_paths:
            full_path = self.project_path / file_path
            if full_path.exists() and full_path.is_file():
                try:
                    content = full_path.read_text(encoding='utf-8')
                    
                    # Parse based on file type
                    if file_path == 'package.json':
                        config_data[file_path] = json.loads(content)
                    elif file_path == 'requirements.txt':
                        config_data[file_path] = self._parse_requirements(content)
                    elif file_path == 'pyproject.toml':
                        config_data[file_path] = content  # Store raw for now
                    else:
                        config_data[file_path] = content[:5000]  # Limit size
                        
                except Exception as e:
                    config_data[file_path] = {'error': str(e)}
                    
        return config_data
    
    async def detect_framework_patterns(self) -> Dict:
        """Detect framework-specific patterns."""
        patterns = {
            'detected_frameworks': [],
            'build_tools': [],
            'indicators': []
        }
        
        # Check for Next.js patterns
        if await self._is_nextjs_project():
            patterns['detected_frameworks'].append('nextjs')
            patterns['indicators'].append('Next.js project detected')
        
        # Check for React patterns
        if await self._is_react_project():
            patterns['detected_frameworks'].append('react')
            patterns['indicators'].append('React project detected')
            
        # Check for Django patterns
        if await self._is_django_project():
            patterns['detected_frameworks'].append('django')
            patterns['indicators'].append('Django project detected')
        
        # Check for Express patterns
        if await self._is_express_project():
            patterns['detected_frameworks'].append('express')
            patterns['indicators'].append('Express.js project detected')
            
        return patterns
    
    async def suggest_build_configuration(self, project_analysis: Dict) -> Dict:
        """Suggest optimal build configuration."""
        config = {
            'build_steps': [],
            'dependencies': [],
            'environment_variables': {},
            'estimated_duration': 0
        }
        
        frameworks = project_analysis.get('detected_frameworks', [])
        config_files = project_analysis.get('config_files', {})
        
        # Next.js configuration
        if 'nextjs' in frameworks:
            config['build_steps'] = [
                {'command': 'npm install', 'purpose': 'Install dependencies'},
                {'command': 'npm run build', 'purpose': 'Build Next.js application'}
            ]
            config['environment_variables'] = {
                'NODE_ENV': 'production',
                'PORT': '3000'
            }
            config['estimated_duration'] = 180
            
        # React configuration
        elif 'react' in frameworks:
            config['build_steps'] = [
                {'command': 'npm install', 'purpose': 'Install dependencies'},
                {'command': 'npm run build', 'purpose': 'Build React application'}
            ]
            config['environment_variables'] = {
                'NODE_ENV': 'production',
                'PORT': '3000'
            }
            config['estimated_duration'] = 120
            
        # Django configuration
        elif 'django' in frameworks:
            config['build_steps'] = [
                {'command': 'pip install -r requirements.txt', 'purpose': 'Install dependencies'},
                {'command': 'python manage.py collectstatic --noinput', 'purpose': 'Collect static files'},
                {'command': 'python manage.py migrate', 'purpose': 'Run migrations'}
            ]
            config['environment_variables'] = {
                'DJANGO_SETTINGS_MODULE': 'project.settings',
                'PYTHONUNBUFFERED': '1',
                'PORT': '8000'
            }
            config['estimated_duration'] = 120
        
        # Express configuration
        elif 'express' in frameworks:
            config['build_steps'] = [
                {'command': 'npm install', 'purpose': 'Install dependencies'}
            ]
            config['environment_variables'] = {
                'NODE_ENV': 'production',
                'PORT': '3000'
            }
            config['estimated_duration'] = 60
            
        return config
    
    async def _is_nextjs_project(self) -> bool:
        """Check if project is a Next.js project."""
        next_config_files = ['next.config.js', 'next.config.mjs', 'next.config.ts']
        for config_file in next_config_files:
            if (self.project_path / config_file).exists():
                return True
        
        # Check package.json for next dependency
        pkg_path = self.project_path / 'package.json'
        if pkg_path.exists():
            try:
                pkg = json.loads(pkg_path.read_text())
                deps = {**pkg.get('dependencies', {}), **pkg.get('devDependencies', {})}
                return 'next' in deps
            except:
                pass
        
        return False
    
    async def _is_react_project(self) -> bool:
        """Check if project is a React project."""
        pkg_path = self.project_path / 'package.json'
        if pkg_path.exists():
            try:
                pkg = json.loads(pkg_path.read_text())
                deps = {**pkg.get('dependencies', {}), **pkg.get('devDependencies', {})}
                return 'react' in deps
            except:
                pass
        return False
    
    async def _is_django_project(self) -> bool:
        """Check if project is a Django project."""
        manage_py = self.project_path / 'manage.py'
        if manage_py.exists():
            return True
        
        # Check requirements.txt
        req_path = self.project_path / 'requirements.txt'
        if req_path.exists():
            try:
                content = req_path.read_text().lower()
                return 'django' in content
            except:
                pass
        
        return False
    
    async def _is_express_project(self) -> bool:
        """Check if project is an Express.js project."""
        pkg_path = self.project_path / 'package.json'
        if pkg_path.exists():
            try:
                pkg = json.loads(pkg_path.read_text())
                deps = {**pkg.get('dependencies', {}), **pkg.get('devDependencies', {})}
                return 'express' in deps
            except:
                pass
        return False
    
    def _parse_requirements(self, content: str) -> str:
        """Parse requirements.txt content."""
        # For now, just return the content as-is
        # In future, we can parse versions, etc.
        return content
