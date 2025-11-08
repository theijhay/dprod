"""AI-powered project analyzer agent for intelligent project detection and deployment configuration."""

from typing import Dict, Any, Optional
from .ai_logger import AILogger

import json
import time
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from .ai_logger import AILogger


class ProjectAnalyzerAgent:
    """
    AI-powered project analyzer that intelligently detects project types
    and generates optimal deployment configurations.
    """
    
    def __init__(self, db_session: AsyncSession, use_ai: bool = True):
        self.db_session = db_session
        self.use_ai = use_ai
        self.logger = AILogger(db_session)
        
    async def analyze_project(
        self,
        project_path: str,
        project_id: str,
        deployment_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze a project and generate deployment configuration.
        
        Args:
            project_path: Path to the project directory
            project_id: Project ID for tracking
            deployment_id: Optional deployment ID
            
        Returns:
            Dict containing detected configuration and metadata
        """
        start_time = time.time()

        # Gather project information using tools
        input_context = await self._gather_project_context(project_path)
        
        # Run AI analysis (or fallback to rule-based)
        if self.use_ai:
            analysis_result = await self._ai_analyze(input_context)
        else:
            analysis_result = await self._rule_based_analyze(input_context)
        
        # Log the decision
        processing_time = int((time.time() - start_time) * 1000)
        
        decision_id = await self.logger.log_agent_decision(
            agent_type="project_analyzer",
            project_id=project_id,
            deployment_id=deployment_id,
            input_context=input_context,
            tools_used=analysis_result.get('tools_used', []),
            raw_response=json.dumps(analysis_result.get('raw_response', {})),
            parsed_decision=analysis_result['decision'],
            confidence=analysis_result.get('confidence_score', 0.0),
            processing_time=processing_time,
            token_usage=analysis_result.get('token_usage', 0)
        )
        
        # Add decision ID to result for tracking
        analysis_result['decision']['decision_id'] = decision_id
        
        return analysis_result['decision']
    
    async def verify_decision(
        self,
        decision_id: str,
        was_correct: bool,
        verification_source: str = "manual"
    ):
        """Verify if an AI decision was correct."""
        await self.logger.log_decision_verification(
            decision_id=decision_id,
            was_correct=was_correct,
            verification_source=verification_source
        )
    
    async def _gather_project_context(self, project_path: str) -> Dict[str, Any]:
        """Gather comprehensive project context using analysis tools."""
        from .project_analyzer_tools import ProjectAnalyzerTools
        
        tools = ProjectAnalyzerTools(project_path)
        
        context = {
            'project_path': project_path,
            'structure': await tools.analyze_project_structure(),
            'config_files': await tools.read_configuration_files([
                'package.json',
                'requirements.txt',
                'pyproject.toml',
                'go.mod',
                'Cargo.toml',
                'composer.json',
                'next.config.js',
                'tsconfig.json',
                'Dockerfile'
            ]),
            'framework_patterns': await tools.detect_framework_patterns(),
        }
        
        return context
    
    async def _ai_analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Use AI agent to analyze the project.
        This is a placeholder for OpenAI/Claude/OmniCore integration.
        """
        # TODO: Integrate with actual AI service (OmniCore provider)
        # For now, I use enhanced rule-based analysis with AI-like structure
        return await self._rule_based_analyze(context)
    
    async def _rule_based_analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhanced rule-based analysis that mimics AI output structure.
        This provides the foundation for AI integration.
        """
        from .project_analyzer_tools import ProjectAnalyzerTools
        
        tools = ProjectAnalyzerTools(context['project_path'])
        
        # Detect framework
        detected_framework = "unknown"
        confidence = 0.5
        tools_used = ["file_scanner", "config_reader", "pattern_detector"]
        
        config_files = context.get('config_files', {})
        structure = context.get('structure', {})
        framework_patterns = context.get('framework_patterns', {})
        
        # Next.js Detection
        if 'next.config.js' in structure.get('key_files_found', []) or \
           'next.config.mjs' in structure.get('key_files_found', []):
            detected_framework = "nextjs"
            confidence = 0.95
        # React Detection
        elif 'package.json' in config_files:
            pkg = config_files['package.json']
            if isinstance(pkg, dict):
                deps = {**pkg.get('dependencies', {}), **pkg.get('devDependencies', {})}
                if 'react' in deps and 'react-scripts' in deps:
                    detected_framework = "react-cra"
                    confidence = 0.90
                elif 'react' in deps and 'vite' in deps:
                    detected_framework = "react-vite"
                    confidence = 0.90
                elif 'express' in deps:
                    detected_framework = "express"
                    confidence = 0.85
        # Python Detection
        elif 'requirements.txt' in config_files or 'pyproject.toml' in config_files:
            reqs = config_files.get('requirements.txt', '')
            if 'django' in reqs.lower():
                detected_framework = "django"
                confidence = 0.90
            elif 'flask' in reqs.lower():
                detected_framework = "flask"
                confidence = 0.90
            elif 'fastapi' in reqs.lower():
                detected_framework = "fastapi"
                confidence = 0.90
            else:
                detected_framework = "python"
                confidence = 0.75
        # Static Site Detection
        elif 'index.html' in structure.get('root_files', []):
            detected_framework = "static"
            confidence = 0.80
        
        # Generate configuration based on detected framework
        build_config = await tools.suggest_build_configuration({
            'detected_frameworks': [detected_framework],
            'config_files': config_files
        })
        
        decision = {
            'detected_framework': detected_framework,
            'confidence_score': confidence,
            'build_configuration': build_config.get('build_steps', []),
            'runtime_configuration': {
                'start_command': self._get_start_command(detected_framework, config_files),
                'expected_port': self._get_default_port(detected_framework),
                'health_check_path': '/',
                'environment_variables': build_config.get('environment_variables', {})
            },
            'resource_requirements': {
                'cpu': 0.5,
                'memory_mb': 512,
                'estimated_build_time': build_config.get('estimated_duration', 120)
            },
            'detected_issues': [],
            'optimization_suggestions': []
        }
        
        return {
            'decision': decision,
            'confidence_score': confidence,
            'tools_used': tools_used,
            'token_usage': 0,  # No tokens for rule-based
            'raw_response': decision
        }
    
    def _get_start_command(self, framework: str, config_files: Dict) -> str:
        """Get the appropriate start command for the framework."""
        commands = {
            'nextjs': 'npm start',
            'react-cra': 'npm start',
            'react-vite': 'npm run preview',
            'express': 'node index.js',
            'django': 'python manage.py runserver 0.0.0.0:8000',
            'flask': 'python app.py',
            'fastapi': 'uvicorn main:app --host 0.0.0.0 --port 8000',
            'python': 'python main.py',
            'static': 'python -m http.server 8000'
        }
        
        # Check package.json for custom start script
        if 'package.json' in config_files:
            pkg = config_files.get('package.json', {})
            if isinstance(pkg, dict):
                scripts = pkg.get('scripts', {})
                if 'start' in scripts:
                    return 'npm start'
        
        return commands.get(framework, 'npm start')
    
    def _get_default_port(self, framework: str) -> int:
        """Get the default port for the framework."""
        ports = {
            'nextjs': 3000,
            'react-cra': 3000,
            'react-vite': 4173,
            'express': 3000,
            'django': 8000,
            'flask': 5000,
            'fastapi': 8000,
            'python': 8000,
            'static': 8000
        }
        return ports.get(framework, 3000)
