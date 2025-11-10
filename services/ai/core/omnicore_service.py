"""OmniCoreAgent integration for dprod AI operations."""
from omnicoreagent import (
    OmniAgent,
    MemoryRouter,
    EventRouter,
    ToolRegistry,
    Tool
)
from typing import Dict, Any, Optional
import os
import asyncio
import json
import re


class DprodOmniAgentService:
    """
    OmniCoreAgent service for dprod AI operations.
    
    This service integrates OmniCoreAgent to provide:
    - Intelligent project analysis with custom tools
    - Multi-tier memory management
    - Real-time event streaming
    - Production-ready AI operations
    """
    
    def __init__(self, db_session):
        """
        Initialize OmniAgent service.
        
        Args:
            db_session: Database session for dprod operations
        """
        self.db_session = db_session
        self.tool_registry = None
        self.memory_router = None
        self.event_router = None
        self.agent = None
        
    def _create_tool_registry(self):
        """Create and register all dprod AI tools."""
        try:
            registry = ToolRegistry()
            
            # Register dprod-specific tools
            self._register_project_analysis_tools(registry)
            self._register_deployment_tools(registry)
            self._register_optimization_tools(registry)
            
            return registry
        except Exception as e:
            raise Exception(f"Failed to create tool registry: {e}")
    
    def _register_project_analysis_tools(self, registry):
        """Register project analysis tools."""
        
        @registry.register_tool("analyze_project_structure")
        def analyze_project_structure(project_path: str) -> str:
            """
            Analyze project directory structure and identify key files.
            
            Args:
                project_path: Path to the project directory
                
            Returns:
                JSON string with project structure analysis
            """
            from services.ai.core.project_analyzer_tools import ProjectAnalyzerTools
            
            tools = ProjectAnalyzerTools(project_path)
            structure = asyncio.run(tools.analyze_project_structure())
            return json.dumps(structure, indent=2)
        
        @registry.register_tool("detect_framework")
        def detect_framework(project_path: str) -> str:
            """
            Detect the framework used in the project.
            
            Args:
                project_path: Path to the project directory
                
            Returns:
                Detected framework name with confidence score
            """
            from services.ai.core.project_analyzer_tools import ProjectAnalyzerTools
            
            tools = ProjectAnalyzerTools(project_path)
            patterns = asyncio.run(tools.detect_framework_patterns("auto"))
            return json.dumps(patterns, indent=2)
        
        @registry.register_tool("read_config_files")
        def read_config_files(project_path: str, files: str) -> str:
            """
            Read and parse configuration files from project.
            
            Args:
                project_path: Path to the project directory
                files: Comma-separated list of config files to read
                
            Returns:
                JSON string with parsed config file contents
            """
            from services.ai.core.project_analyzer_tools import ProjectAnalyzerTools
            
            tools = ProjectAnalyzerTools(project_path)
            file_list = [f.strip() for f in files.split(",")]
            configs = asyncio.run(tools.read_configuration_files(file_list))
            return json.dumps(configs, indent=2)
        
        @registry.register_tool("suggest_build_config")
        def suggest_build_config(project_analysis: str) -> str:
            """
            Suggest optimal build configuration based on project analysis.
            
            Args:
                project_analysis: JSON string of project analysis data
                
            Returns:
                JSON string with suggested build configuration
            """
            from services.ai.core.project_analyzer_tools import ProjectAnalyzerTools
            
            analysis = json.loads(project_analysis)
            tools = ProjectAnalyzerTools("")
            config = asyncio.run(tools.suggest_build_configuration(analysis))
            return json.dumps(config, indent=2)
    
    def _register_deployment_tools(self, registry):
        """Register deployment monitoring and management tools."""
        
        @registry.register_tool("get_deployment_status")
        def get_deployment_status(deployment_id: str) -> str:
            """
            Get current status of a deployment.
            
            Args:
                deployment_id: UUID of the deployment
                
            Returns:
                JSON string with deployment status
            """
            from services.shared.core.models import Deployment
            
            deployment = self.db_session.query(Deployment).filter_by(
                id=deployment_id
            ).first()
            
            if not deployment:
                return json.dumps({"error": "Deployment not found"})
            
            return json.dumps({
                "id": str(deployment.id),
                "status": deployment.status,
                "url": deployment.url,
                "created_at": str(deployment.created_at)
            })
        
        @registry.register_tool("validate_deployment_outcome")
        def validate_deployment_outcome(deployment_id: str) -> str:
            """
            Validate if deployment was successful and record outcome.
            
            Args:
                deployment_id: UUID of the deployment
                
            Returns:
                Validation result with success/failure status
            """
            from services.shared.core.models import Deployment
            import requests
            
            deployment = self.db_session.query(Deployment).filter_by(
                id=deployment_id
            ).first()
            
            if not deployment:
                return json.dumps({"error": "Deployment not found"})
            
            # Check if deployment URL is accessible
            try:
                response = requests.get(deployment.url, timeout=10)
                is_successful = response.status_code == 200
                
                return json.dumps({
                    "deployment_id": str(deployment.id),
                    "is_successful": is_successful,
                    "status_code": response.status_code,
                    "message": "Deployment is accessible" if is_successful else "Deployment failed health check"
                })
            except Exception as e:
                return json.dumps({
                    "deployment_id": str(deployment.id),
                    "is_successful": False,
                    "error": str(e),
                    "message": "Deployment health check failed"
                })
    
    def _register_optimization_tools(self, registry):
        """Register resource optimization tools."""
        
        @registry.register_tool("analyze_resource_usage")
        def analyze_resource_usage(deployment_id: str) -> str:
            """
            Analyze resource usage for a deployment using Docker stats.
            
            Args:
                deployment_id: UUID of the deployment
                
            Returns:
                Resource usage analysis with optimization suggestions
            """
            from services.shared.core.models import Deployment, Project
            import docker
            
            try:
                # Get deployment from database with project info
                deployment = self.db_session.query(Deployment).filter_by(
                    id=deployment_id
                ).first()
                
                if not deployment:
                    return json.dumps({"error": "Deployment not found"})
                
                # Get project info
                project = self.db_session.query(Project).filter_by(
                    id=deployment.project_id
                ).first()
                
                if not project:
                    return json.dumps({"error": "Project not found"})
                
                # Connect to Docker
                client = docker.from_env()
                
                # Find container by project_id label (set by docker_manager.py)
                containers = client.containers.list(
                    filters={"label": f"project_id={deployment.project_id}"}
                )
                
                if not containers:
                    # Fallback: try by project name
                    containers = client.containers.list(
                        filters={"label": f"project={project.name}"}
                    )
                
                if not containers:
                    return json.dumps({
                        "error": "Container not found",
                        "deployment_id": deployment_id,
                        "project_id": str(deployment.project_id),
                        "project_name": project.name,
                        "hint": "Container may have stopped or not yet started"
                    })
                
                # Use the first matching container (should only be one per project)
                container = containers[0]
                
                # Get container stats (stream=False for single snapshot)
                stats = container.stats(stream=False)
                
                # Calculate CPU percentage
                cpu_delta = stats['cpu_stats']['cpu_usage']['total_usage'] - \
                           stats['precpu_stats']['cpu_usage']['total_usage']
                system_delta = stats['cpu_stats']['system_cpu_usage'] - \
                              stats['precpu_stats']['system_cpu_usage']
                cpu_count = stats['cpu_stats']['online_cpus']
                cpu_percent = (cpu_delta / system_delta) * cpu_count * 100.0 if system_delta > 0 else 0.0
                
                # Calculate Memory usage
                memory_usage = stats['memory_stats']['usage']
                memory_limit = stats['memory_stats']['limit']
                memory_percent = (memory_usage / memory_limit) * 100.0 if memory_limit > 0 else 0.0
                memory_usage_mb = memory_usage / (1024 * 1024)
                memory_limit_mb = memory_limit / (1024 * 1024)
                
                # Network I/O
                network_stats = stats.get('networks', {})
                network_rx_mb = sum(net['rx_bytes'] for net in network_stats.values()) / (1024 * 1024)
                network_tx_mb = sum(net['tx_bytes'] for net in network_stats.values()) / (1024 * 1024)
                
                # Block I/O
                block_stats = stats.get('blkio_stats', {}).get('io_service_bytes_recursive', [])
                block_read_mb = sum(item['value'] for item in block_stats if item['op'] == 'Read') / (1024 * 1024) if block_stats else 0
                block_write_mb = sum(item['value'] for item in block_stats if item['op'] == 'Write') / (1024 * 1024) if block_stats else 0
                
                # Generate AI-powered suggestions
                suggestions = []
                
                # CPU optimization
                if cpu_percent < 10:
                    suggestions.append(f"Low CPU usage ({cpu_percent:.1f}%) - Consider reducing CPU allocation to save costs")
                elif cpu_percent > 80:
                    suggestions.append(f"High CPU usage ({cpu_percent:.1f}%) - Consider increasing CPU allocation for better performance")
                else:
                    suggestions.append(f"CPU usage is optimal ({cpu_percent:.1f}%)")
                
                # Memory optimization
                if memory_percent < 30:
                    suggestions.append(f"Low memory usage ({memory_percent:.1f}%) - Consider reducing memory limit from {memory_limit_mb:.0f}MB")
                elif memory_percent > 85:
                    suggestions.append(f"High memory usage ({memory_percent:.1f}%) - Consider increasing memory limit to prevent OOM")
                else:
                    suggestions.append(f"Memory usage is optimal ({memory_percent:.1f}%)")
                
                # Network usage insights
                if network_rx_mb + network_tx_mb > 100:
                    suggestions.append(f"High network activity ({network_rx_mb + network_tx_mb:.1f}MB transferred) - Consider CDN for static assets")
                
                return json.dumps({
                    "deployment_id": deployment_id,
                    "container_name": container.name,
                    "status": container.status,
                    "cpu": {
                        "usage_percent": round(cpu_percent, 2),
                        "cpu_count": cpu_count,
                        "status": "high" if cpu_percent > 80 else "low" if cpu_percent < 10 else "optimal"
                    },
                    "memory": {
                        "usage_mb": round(memory_usage_mb, 2),
                        "limit_mb": round(memory_limit_mb, 2),
                        "usage_percent": round(memory_percent, 2),
                        "status": "high" if memory_percent > 85 else "low" if memory_percent < 30 else "optimal"
                    },
                    "network": {
                        "rx_mb": round(network_rx_mb, 2),
                        "tx_mb": round(network_tx_mb, 2),
                        "total_mb": round(network_rx_mb + network_tx_mb, 2)
                    },
                    "disk_io": {
                        "read_mb": round(block_read_mb, 2),
                        "write_mb": round(block_write_mb, 2)
                    },
                    "suggestions": suggestions,
                    "cost_optimization": {
                        "current_cost_estimate": f"${(memory_limit_mb / 1024) * 0.01:.4f}/hour",
                        "potential_savings": f"${(memory_limit_mb / 1024) * 0.01 * 0.3:.4f}/hour" if memory_percent < 30 else "None"
                    }
                }, indent=2)
                
            except docker.errors.DockerException as e:
                return json.dumps({
                    "error": "Docker connection failed",
                    "message": str(e),
                    "deployment_id": deployment_id
                })
            except Exception as e:
                return json.dumps({
                    "error": "Failed to analyze resource usage",
                    "message": str(e),
                    "deployment_id": deployment_id
                })
    
    async def create_project_analyzer_agent(self):
        """Create the main project analyzer agent with OmniCoreAgent."""
        try:
            # Initialize tool registry
            self.tool_registry = self._create_tool_registry()
        except Exception as e:
            print(f"Failed to initialize tool registry: {e}")
            return None
        
        # Initialize memory and event routers
        self.memory_router = MemoryRouter(
            memory_store_type=os.getenv("OMNI_MEMORY_TYPE", "in_memory")
        )
        self.event_router = EventRouter(
            event_store_type=os.getenv("OMNI_EVENT_TYPE", "in_memory")
        )
        
        # Create OmniAgent
        agent = OmniAgent(
            name="dprod_project_analyzer",
            system_instruction="""You are an expert DevOps AI agent for dprod, 
a zero-configuration deployment platform. Your role is to:

1. Analyze software projects to detect frameworks and technologies
2. Suggest optimal build and deployment configurations
3. Validate deployment outcomes and learn from results
4. Optimize resource allocation for deployments

Use the available tools to gather project information, analyze patterns,
and make intelligent deployment decisions. Always provide confidence scores
and explain your reasoning.

When analyzing a project:
1. First use analyze_project_structure to understand the directory layout
2. Then use detect_framework to identify the technology stack
3. Read relevant config files (package.json, requirements.txt, etc.)
4. Finally suggest_build_config with your recommendations

Provide responses in JSON format with:
- detected_framework: The framework name
- confidence_score: 0.0 to 1.0 confidence level
- project_type: nodejs, python, go, static, etc.
- build_configuration: Build commands and steps
- runtime_configuration: Start command, port, env vars
- resource_requirements: CPU, memory estimates
- detected_issues: Any problems found
- optimization_suggestions: Recommendations""",
            
            model_config={
                "provider": os.getenv("LLM_PROVIDER", "openai"),
                "model": os.getenv("LLM_MODEL", "gpt-4o-mini"),
                "temperature": 0.1  # Low temperature for consistent results
            },
            
            agent_config={
                "tool_call_timeout": 60,
                "max_steps": 15,
                "request_limit": 0,  # Unlimited for production
                "total_tokens_limit": 0,  # Unlimited for production
                "memory_results_limit": 10,
                "memory_similarity_threshold": 0.7,
                "enable_tools_knowledge_base": True,  # Semantic tool search
                "tools_results_limit": 10
            },
            
            # Our custom dprod tools
            local_tools=self.tool_registry,
            
            # Embedding for semantic memory
            embedding_config={
                "provider": os.getenv("EMBEDDING_PROVIDER", "openai"),
                "model": "text-embedding-3-small",
                "dimensions": 1536
            },
            
            # Memory and events
            memory_router=self.memory_router,
            event_router=self.event_router
        )
        
        await agent.initialize()
        self.agent = agent
        return agent
    
    async def analyze_project(
        self, 
        project_path: str,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze a project using OmniCoreAgent.
        
        Args:
            project_path: Path to the project
            session_id: Optional session ID for memory continuity
            
        Returns:
            Analysis results with framework detection and config
        """
        if not self.agent:
            agent = await self.create_project_analyzer_agent()
            if not agent:
                raise Exception("Failed to create OmniAgent. Package not installed.")
        
        query = f"""Analyze the project at: {project_path}

Please:
1. Analyze the project structure using analyze_project_structure tool
2. Detect the framework using detect_framework tool
3. Read relevant config files (package.json, requirements.txt, pyproject.toml, etc.)
4. Suggest optimal build configuration using suggest_build_config

Provide a comprehensive analysis with:
- Detected framework (with confidence score 0.0-1.0)
- Project type (nodejs, python, go, static, etc.)
- Build configuration (commands, dependencies)
- Runtime configuration (start command, port, env vars)
- Resource requirements (CPU, memory estimates)
- Any detected issues or warnings
- Optimization suggestions

Return your response as valid JSON."""
        
        result = await self.agent.run(
            query=query,
            session_id=session_id
        )
        
        return result
    
    def parse_omniagent_response(self, omni_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse OmniAgent response into dprod format.
        
        Args:
            omni_result: Raw result from OmniAgent
            
        Returns:
            Parsed analysis in dprod format
        """
        # Extract the final answer from OmniAgent
        answer = omni_result.get("final_answer", "")
        
        # Try to extract JSON from the response
        json_match = re.search(r'\{.*\}', answer, re.DOTALL)
        if json_match:
            try:
                parsed = json.loads(json_match.group())
                # Add metadata from OmniAgent
                parsed["tokens_used"] = omni_result.get("total_tokens", 0)
                parsed["cost_usd"] = omni_result.get("total_cost", 0.0)
                return parsed
            except json.JSONDecodeError:
                pass
        
        # Fallback: extract key information from text
        return {
            "detected_framework": self._extract_framework(answer),
            "confidence_score": self._extract_confidence(answer),
            "project_type": self._extract_project_type(answer),
            "analysis": answer,
            "tokens_used": omni_result.get("total_tokens", 0),
            "cost_usd": omni_result.get("total_cost", 0.0)
        }
    
    def _extract_framework(self, text: str) -> str:
        """Extract framework name from text."""
        frameworks = [
            "nextjs", "react", "express", "django", "flask", 
            "fastapi", "vue", "angular", "go", "static"
        ]
        text_lower = text.lower()
        for framework in frameworks:
            if framework in text_lower:
                return framework
        return "unknown"
    
    def _extract_confidence(self, text: str) -> float:
        """Extract confidence score from text."""
        # Look for patterns like "confidence: 0.95" or "95%"
        patterns = [
            r"confidence[:\s]+(\d+\.?\d*)",
            r"(\d+\.?\d*)%?\s*confidence",
            r"score[:\s]+(\d+\.?\d*)"
        ]
        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                value = float(match.group(1))
                # Normalize percentage to 0-1 range
                return value / 100 if value > 1 else value
        return 0.5  # Default medium confidence
    
    def _extract_project_type(self, text: str) -> str:
        """Extract project type from text."""
        types = ["nodejs", "python", "go", "static", "java", "ruby"]
        text_lower = text.lower()
        for ptype in types:
            if ptype in text_lower:
                return ptype
        return "unknown"
