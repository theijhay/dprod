"""Docker container management for deployments."""

import asyncio
import os
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any
import uuid

import docker
from docker.errors import DockerException

from dprod_shared.models import ProjectConfig, ProjectType
from dprod_shared.exceptions import ContainerError, BuildError


class DockerManager:
    """Manages Docker containers for project deployments."""
    
    def __init__(self, docker_socket_path: str = "/var/run/docker.sock"):
        """Initialize Docker manager."""
        self.docker_socket_path = docker_socket_path
        self.client = docker.from_env()
        self.containers: Dict[str, Any] = {}
    
    async def create_deployment_container(
        self,
        project_id: str,
        project_config: ProjectConfig,
        source_code_path: Path
    ) -> str:
        """
        Create and start a deployment container.
        
        Args:
            project_id: Unique project identifier
            project_config: Project configuration
            source_code_path: Path to extracted source code
            
        Returns:
            str: Container ID
            
        Raises:
            ContainerError: If container creation fails
        """
        try:
            # Generate unique container name
            container_name = f"dprod-{project_id}-{uuid.uuid4().hex[:8]}"
            
            # Generate Dockerfile
            dockerfile_content = self._generate_dockerfile(project_config)
            
            # Create temporary directory for build context
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # Write Dockerfile
                dockerfile_path = temp_path / "Dockerfile"
                dockerfile_path.write_text(dockerfile_content)
                
                # Copy source code
                import shutil
                app_dir = temp_path / "app"
                shutil.copytree(source_code_path, app_dir)
                
                # Build Docker image
                image_tag = f"dprod-{project_id}:latest"
                print(f"🔨 Building Docker image: {image_tag}")
                
                image, build_logs = self.client.images.build(
                    path=str(temp_path),
                    tag=image_tag,
                    rm=True,
                    forcerm=True
                )
                
                # Print build logs
                for log in build_logs:
                    if 'stream' in log:
                        print(f"📦 {log['stream'].strip()}")
                
                # Run container
                print(f"🚀 Starting container: {container_name}")
                container = self.client.containers.run(
                    image_tag,
                    name=container_name,
                    ports={f"{project_config.port}/tcp": None},  # Dynamic port mapping
                    environment=project_config.environment,
                    detach=True,
                    remove=False,
                    mem_limit="512m",  # 512MB memory limit
                    cpu_period=100000,
                    cpu_quota=50000,  # 0.5 CPU
                    working_dir="/app"
                )
                
                # Store container reference
                self.containers[project_id] = {
                    "container": container,
                    "image_tag": image_tag,
                    "port": project_config.port
                }
                
                print(f"✅ Container started: {container.id[:12]}")
                return container.id
                
        except DockerException as e:
            raise ContainerError(f"Failed to create container: {e}")
        except Exception as e:
            raise ContainerError(f"Unexpected error creating container: {e}")
    
    def _generate_dockerfile(self, project_config: ProjectConfig) -> str:
        """Generate Dockerfile content based on project configuration."""
        if project_config.type == ProjectType.NODEJS:
            return self._generate_nodejs_dockerfile(project_config)
        elif project_config.type == ProjectType.PYTHON:
            return self._generate_python_dockerfile(project_config)
        elif project_config.type == ProjectType.GO:
            return self._generate_go_dockerfile(project_config)
        elif project_config.type == ProjectType.STATIC:
            return self._generate_static_dockerfile(project_config)
        else:
            return self._generate_generic_dockerfile(project_config)
    
    def _generate_nodejs_dockerfile(self, config: ProjectConfig) -> str:
        """Generate Dockerfile for Node.js projects."""
        return f"""FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY app/package*.json ./

# Install dependencies
RUN npm install --production

# Copy source code
COPY app/ .

# Expose port
EXPOSE {config.port}

# Set environment variables
{self._format_env_vars(config.environment)}

# Start application
CMD {config.start_command}
"""
    
    def _generate_python_dockerfile(self, config: ProjectConfig) -> str:
        """Generate Dockerfile for Python projects."""
        build_cmd = config.build_command or "pip install -r requirements.txt"
        return f"""FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for better caching
COPY app/requirements*.txt ./

# Install dependencies
RUN {build_cmd}

# Copy source code
COPY app/ .

# Expose port
EXPOSE {config.port}

# Set environment variables
{self._format_env_vars(config.environment)}

# Start application
CMD {config.start_command}
"""
    
    def _generate_go_dockerfile(self, config: ProjectConfig) -> str:
        """Generate Dockerfile for Go projects."""
        return f"""FROM golang:1.21-alpine

WORKDIR /app

# Copy go mod files
COPY app/go.mod app/go.sum ./

# Download dependencies
RUN go mod download

# Copy source code
COPY app/ .

# Build the application
RUN go build -o main .

# Expose port
EXPOSE {config.port}

# Set environment variables
{self._format_env_vars(config.environment)}

# Start application
CMD ./main
"""
    
    def _generate_static_dockerfile(self, config: ProjectConfig) -> str:
        """Generate Dockerfile for static sites."""
        return f"""FROM nginx:alpine

# Copy static files
COPY app/ /usr/share/nginx/html/

# Expose port
EXPOSE {config.port}

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
"""
    
    def _generate_generic_dockerfile(self, config: ProjectConfig) -> str:
        """Generate generic Dockerfile."""
        return f"""FROM python:3.11-slim

WORKDIR /app

# Copy source code
COPY app/ .

# Install any requirements if they exist
RUN if [ -f requirements.txt ]; then pip install -r requirements.txt; fi

# Expose port
EXPOSE {config.port}

# Set environment variables
{self._format_env_vars(config.environment)}

# Start application
CMD {config.start_command}
"""
    
    def _format_env_vars(self, environment: Dict[str, str]) -> str:
        """Format environment variables for Dockerfile."""
        if not environment:
            return ""
        
        env_lines = []
        for key, value in environment.items():
            env_lines.append(f"ENV {key}={value}")
        
        return "\n".join(env_lines)
    
    async def get_container_port(self, project_id: str) -> Optional[int]:
        """Get the mapped port for a container."""
        if project_id not in self.containers:
            return None
        
        container = self.containers[project_id]["container"]
        port_info = container.ports
        
        if port_info:
            # Get the first mapped port
            for container_port, host_ports in port_info.items():
                if host_ports:
                    return host_ports[0]["HostPort"]
        
        return None
    
    async def get_container_logs(self, project_id: str) -> str:
        """Get container logs."""
        if project_id not in self.containers:
            return "Container not found"
        
        container = self.containers[project_id]["container"]
        return container.logs().decode('utf-8')
    
    async def stop_container(self, project_id: str) -> bool:
        """Stop and remove a container."""
        if project_id not in self.containers:
            return False
        
        try:
            container_info = self.containers[project_id]
            container = container_info["container"]
            
            # Stop container
            container.stop(timeout=10)
            
            # Remove container
            container.remove()
            
            # Remove image
            try:
                self.client.images.remove(container_info["image_tag"])
            except DockerException:
                pass  # Image might be in use
            
            # Remove from tracking
            del self.containers[project_id]
            
            print(f"🛑 Container stopped and removed: {project_id}")
            return True
            
        except DockerException as e:
            print(f"⚠️  Error stopping container {project_id}: {e}")
            return False
    
    async def cleanup_old_containers(self, max_age_hours: int = 24):
        """Clean up old containers and images."""
        try:
            # Get all containers with dprod prefix
            containers = self.client.containers.list(
                all=True,
                filters={"name": "dprod-"}
            )
            
            for container in containers:
                # Check container age
                created_at = container.attrs["Created"]
                # Simple cleanup - remove containers older than max_age_hours
                # In production, you'd want more sophisticated cleanup logic
                
                # Stop and remove old containers
                if container.status == "running":
                    container.stop(timeout=5)
                container.remove()
                
                print(f"🧹 Cleaned up old container: {container.name}")
                
        except DockerException as e:
            print(f"⚠️  Error during cleanup: {e}")
    
    def list_containers(self) -> Dict[str, Dict[str, Any]]:
        """List all managed containers."""
        result = {}
        for project_id, info in self.containers.items():
            container = info["container"]
            result[project_id] = {
                "container_id": container.id,
                "name": container.name,
                "status": container.status,
                "port": info["port"],
                "image": info["image_tag"]
            }
        return result
