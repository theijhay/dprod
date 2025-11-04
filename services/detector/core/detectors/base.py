"""Base class for project detectors."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

from services.shared.core.models import ProjectType
from services.shared.core.schemas import ProjectConfig


class BaseDetector(ABC):
    """Base class for all project detectors."""
    
    def __init__(self, project_type: ProjectType):
        """Initialize detector with project type."""
        self.project_type = project_type
    
    @abstractmethod
    def can_handle(self, project_path: Path) -> bool:
        """
        Check if this detector can handle the project.
        
        Args:
            project_path: Path to the project directory
            
        Returns:
            True if this detector can handle the project
        """
        pass
    
    @abstractmethod
    def get_config(self, project_path: Path) -> ProjectConfig:
        """
        Generate project configuration.
        
        Args:
            project_path: Path to the project directory
            
        Returns:
            ProjectConfig for the project
        """
        pass
    
    def generate_dockerfile(self, config: ProjectConfig) -> str:
        """
        Generate Dockerfile content for the project.
        
        Args:
            config: Project configuration
            
        Returns:
            Dockerfile content as string
        """
        dockerfile = f"""FROM {self._get_base_image(config.type)}

WORKDIR {config.install_path}

# Copy package files first for better caching
{self._get_copy_commands(config.type)}

# Install dependencies
{self._get_install_commands(config.type)}

# Copy source code
COPY . .

# Expose port
EXPOSE {config.port}

# Set environment variables
{self._get_env_commands(config.environment)}

# Start command
CMD {config.start_command}
"""
        return dockerfile
    
    def _get_base_image(self, project_type: ProjectType) -> str:
        """Get base Docker image for project type."""
        images = {
            ProjectType.NODEJS: "node:18",  # Use the available local image
            ProjectType.PYTHON: "python:3.11-slim",
            ProjectType.GO: "golang:1.21-alpine",
            ProjectType.STATIC: "nginx:alpine"
        }
        return images.get(project_type, "alpine:latest")
    
    def _get_copy_commands(self, project_type: ProjectType) -> str:
        """Get COPY commands for package files."""
        commands = {
            ProjectType.NODEJS: "COPY package*.json ./",
            ProjectType.PYTHON: "COPY requirements*.txt pyproject.toml setup.py* ./",
            ProjectType.GO: "COPY go.mod go.sum ./",
            ProjectType.STATIC: ""
        }
        return commands.get(project_type, "")
    
    def _get_install_commands(self, project_type: ProjectType) -> str:
        """Get install commands for dependencies."""
        commands = {
            ProjectType.NODEJS: "RUN npm install --only=production",
            ProjectType.PYTHON: "RUN pip install --no-cache-dir -r requirements.txt",
            ProjectType.GO: "RUN go mod download",
            ProjectType.STATIC: ""
        }
        return commands.get(project_type, "")
    
    def _get_env_commands(self, environment: dict) -> str:
        """Get ENV commands for environment variables."""
        if not environment:
            return ""
        
        env_lines = []
        for key, value in environment.items():
            env_lines.append(f"ENV {key}={value}")
        
        return "\n".join(env_lines)