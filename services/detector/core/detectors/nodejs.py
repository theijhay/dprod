"""Node.js project detector."""

import json
from pathlib import Path
from typing import Dict, Any

from .base import BaseDetector
from services.shared.core.models import ProjectType
from services.shared.core.schemas import ProjectConfig


class NodeJSDetector(BaseDetector):
    """Detector for Node.js projects."""
    
    def __init__(self):
        super().__init__(ProjectType.NODEJS)
    
    def can_handle(self, project_path: Path) -> bool:
        """Check if this is a Node.js project."""
        package_json = project_path / "package.json"
        return package_json.exists()
    
    def get_config(self, project_path: Path) -> ProjectConfig:
        """Generate configuration for Node.js project."""
        package_json_path = project_path / "package.json"
        
        # Default configuration
        config = ProjectConfig(
            type=ProjectType.NODEJS,
            build_command="npm ci --only=production",
            start_command="npm start",
            port=3000,
            environment={"NODE_ENV": "production"},
            install_path="/app"
        )
        
        # Try to read package.json for better configuration
        if package_json_path.exists():
            try:
                with open(package_json_path, 'r') as f:
                    package_data = json.load(f)
                
                # Detect NestJS project
                dependencies = package_data.get("dependencies", {})
                dev_dependencies = package_data.get("devDependencies", {})
                is_nestjs = "@nestjs/core" in dependencies or "@nestjs/core" in dev_dependencies
                
                # Update build and start commands based on project type
                scripts = package_data.get("scripts", {})
                
                if is_nestjs:
                    # NestJS requires build step and runs built code
                    config.build_command = "npm install && npm run build"
                    if "start:prod" in scripts:
                        config.start_command = scripts["start:prod"]
                    else:
                        config.start_command = "node dist/main"
                else:
                    # Standard Node.js app
                    if "build" in scripts:
                        # Has a build step
                        config.build_command = "npm install && npm run build"
                    
                    # Update start command if available
                    if "start" in scripts:
                        config.start_command = scripts["start"]
                    elif "dev" in scripts:
                        config.start_command = scripts["dev"]
                
                # Check for specific port in package.json
                if "port" in package_data:
                    config.port = int(package_data["port"])
                
                # Add custom environment variables
                if "dprod" in package_data:
                    dprod_config = package_data["dprod"]
                    if "port" in dprod_config:
                        config.port = int(dprod_config["port"])
                    if "environment" in dprod_config:
                        config.environment.update(dprod_config["environment"])
                
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                print(f"Warning: Could not parse package.json: {e}")
        
        return config