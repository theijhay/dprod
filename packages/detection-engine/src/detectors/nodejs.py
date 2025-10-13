"""Node.js project detector."""

import json
from pathlib import Path
from typing import Optional

from dprod_shared.models import ProjectConfig, ProjectType
from .base import BaseDetector


class NodeJSDetector(BaseDetector):
    """Detector for Node.js projects."""
    
    def __init__(self):
        super().__init__(ProjectType.NODEJS)
    
    def can_handle(self, project_path: Path) -> bool:
        """Check if this is a Node.js project."""
        package_json = self._find_file(project_path, "package.json")
        return package_json is not None
    
    def get_config(self, project_path: Path) -> ProjectConfig:
        """Get Node.js project configuration."""
        package_json_path = self._find_file(project_path, "package.json")
        if not package_json_path:
            raise ValueError("package.json not found")
        
        package_data = self._read_json_file(package_json_path)
        
        # Determine start command
        start_command = self._get_start_command(package_data)
        
        # Determine port
        port = self._get_port(package_data)
        
        # Get environment variables
        environment = self._get_environment(package_data)
        
        return ProjectConfig(
            type=ProjectType.NODEJS,
            build_command="npm install",
            start_command=start_command,
            port=port,
            environment=environment
        )
    
    def _get_start_command(self, package_data: dict) -> str:
        """Determine the start command from package.json."""
        scripts = package_data.get("scripts", {})
        
        # Priority order for start commands
        start_commands = ["start", "dev", "serve", "server"]
        
        for cmd in start_commands:
            if cmd in scripts:
                return f"npm run {cmd}"
        
        # Check for main file
        main_file = package_data.get("main", "index.js")
        if main_file:
            return f"node {main_file}"
        
        # Default fallback
        return "npm start"
    
    def _get_port(self, package_data: dict) -> int:
        """Determine the port from package.json or environment."""
        # Check for port in scripts
        scripts = package_data.get("scripts", {})
        for script in scripts.values():
            if isinstance(script, str) and "--port" in script:
                try:
                    # Extract port from --port 3000
                    parts = script.split()
                    port_index = parts.index("--port")
                    if port_index + 1 < len(parts):
                        return int(parts[port_index + 1])
                except (ValueError, IndexError):
                    pass
        
        # Check for PORT environment variable
        environment = package_data.get("environment", {})
        if "PORT" in environment:
            try:
                return int(environment["PORT"])
            except ValueError:
                pass
        
        # Default port for Node.js
        return 3000
    
    def _get_environment(self, package_data: dict) -> dict:
        """Get environment variables for the project."""
        environment = {
            "NODE_ENV": "production",
            "PORT": "3000"
        }
        
        # Add any custom environment variables from package.json
        if "environment" in package_data:
            environment.update(package_data["environment"])
        
        return environment
