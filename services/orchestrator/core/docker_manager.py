"""Docker container management for deployments."""

import asyncio
import docker
import uuid
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

from services.shared.core.models import Project
from services.shared.core.schemas import ProjectConfig
from services.shared.core.exceptions import ContainerError, ResourceLimitError


class DockerManager:
    """Manages Docker containers for deployments."""
    
    def __init__(self):
        """Initialize Docker manager."""
        try:
            # Use the correct Docker client configuration
            self.client = docker.DockerClient(base_url='unix://var/run/docker.sock')
            self.client.ping()  # Test connection
            
            self.docker_available = True
            print("✅ Docker connection established")
            
        except Exception as e:
            print(f"❌ Failed to connect to Docker: {e}")
            print("   Please ensure Docker is running and accessible")
            raise ContainerError(f"Failed to connect to Docker: {e}")
    
    async def build_image(
        self, 
        project: Project, 
        source_code: bytes, 
        config: ProjectConfig,
        build_context: Path
    ) -> str:
        """
        Build Docker image for the project.
        
        Args:
            project: Project database model
            source_code: Compressed source code bytes
            config: Project configuration
            build_context: Path to build context
            
        Returns:
            Image ID
        """
        try:
            print(f"🐳 Building Docker image for {project.name}")
            
            # Generate unique image name
            image_name = f"dprod-{project.name.lower()}-{uuid.uuid4().hex[:8]}"
            image_tag = f"{image_name}:latest"
            
            # Generate Dockerfile
            dockerfile_content = self._generate_dockerfile(config)
            dockerfile_path = build_context / "Dockerfile"
            
            with open(dockerfile_path, 'w') as f:
                f.write(dockerfile_content)
            
            # Build image
            print(f"📦 Building image: {image_tag}")
            image, build_logs = self.client.images.build(
                path=str(build_context),
                tag=image_tag,
                rm=True,
                forcerm=True,
                labels={"dprod": "true", "project": project.name}
            )
            
            print(f"✅ Image built successfully: {image.id}")
            return image.id
            
        except Exception as e:
            print(f"❌ Failed to build image: {e}")
            raise ContainerError(f"Image build failed: {e}")
    
    async def run_container(
        self, 
        project: Project, 
        image_id: str, 
        config: ProjectConfig
    ) -> str:
        """
        Run container from the built image.
        
        Args:
            project: Project database model
            image_id: Docker image ID
            config: Project configuration
            
        Returns:
            Container ID
        """
        try:
            print(f"🚀 Starting container for {project.name}")
            
            # Generate unique container name
            container_name = f"dprod-{project.name.lower()}-{uuid.uuid4().hex[:8]}"
            
            # Container configuration
            container_config = {
                "image": image_id,
                "name": container_name,
                "ports": {f"{config.port}/tcp": None},  # Random port mapping
                "environment": config.environment,
                "detach": True,
                "remove": False,
                "mem_limit": "512m",  # 512MB memory limit
                "cpu_period": 100000,
                "cpu_quota": 50000,  # 50% CPU limit
                "labels": {
                    "dprod": "true",
                    "project": project.name,
                    "project_id": str(project.id)
                }
            }
            
            # Run container
            container = self.client.containers.run(**container_config)
            
            print(f"✅ Container started: {container.id}")
            return container.id
            
        except Exception as e:
            print(f"❌ Failed to start container: {e}")
            raise ContainerError(f"Container start failed: {e}")
    
    async def get_container_info(self, container_id: str) -> Dict[str, Any]:
        """Get container information."""
        try:
            container = self.client.containers.get(container_id)
            
            # Get port mappings
            ports = {}
            if container.attrs.get("NetworkSettings", {}).get("Ports"):
                for container_port, host_ports in container.attrs["NetworkSettings"]["Ports"].items():
                    if host_ports:
                        ports[container_port] = host_ports[0]["HostPort"]
            
            return {
                "id": container.id,
                "name": container.name,
                "status": container.status,
                "ports": ports,
                "created": container.attrs["Created"],
                "image": container.attrs["Config"]["Image"]
            }
            
        except Exception as e:
            raise ContainerError(f"Failed to get container info: {e}")
    
    async def stop_container(self, container_id: str) -> bool:
        """Stop and remove container."""
        try:
            container = self.client.containers.get(container_id)
            container.stop()
            container.remove()
            print(f"✅ Container stopped and removed: {container_id}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to stop container: {e}")
            return False
    
    async def get_container_logs(self, container_id: str) -> str:
        """Get container logs."""
        try:
            container = self.client.containers.get(container_id)
            logs = container.logs().decode('utf-8')
            return logs
            
        except Exception as e:
            raise ContainerError(f"Failed to get container logs: {e}")
    
    async def list_containers(self) -> List[Dict[str, Any]]:
        """List all Dprod containers."""
        try:
            containers = self.client.containers.list(
                all=True,
                filters={"label": "dprod=true"}
            )
            
            container_list = []
            for container in containers:
                container_list.append({
                    "id": container.id,
                    "name": container.name,
                    "status": container.status,
                    "image": container.attrs["Config"]["Image"],
                    "created": container.attrs["Created"]
                })
            
            return container_list
            
        except Exception as e:
            raise ContainerError(f"Failed to list containers: {e}")
    
    def _generate_dockerfile(self, config: ProjectConfig) -> str:
        """Generate Dockerfile content."""
        if config.type.value == "static":
            return f"""FROM nginx:alpine

# Copy static files
COPY . /usr/share/nginx/html

# Copy nginx configuration
RUN echo 'server {{' > /etc/nginx/conf.d/default.conf && \\
    echo '    listen 80;' >> /etc/nginx/conf.d/default.conf && \\
    echo '    server_name localhost;' >> /etc/nginx/conf.d/default.conf && \\
    echo '    root /usr/share/nginx/html;' >> /etc/nginx/conf.d/default.conf && \\
    echo '    index index.html index.htm;' >> /etc/nginx/conf.d/default.conf && \\
    echo '    location / {{' >> /etc/nginx/conf.d/default.conf && \\
    echo '        try_files $uri $uri/ /index.html;' >> /etc/nginx/conf.d/default.conf && \\
    echo '    }}' >> /etc/nginx/conf.d/default.conf && \\
    echo '}}' >> /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
"""
        else:
            # Get base image
            base_images = {
                "nodejs": "node:18",  # Use the available local image
                "python": "python:3.11-slim", 
                "go": "golang:1.21-alpine",
                "unknown": "alpine:latest"
            }
            base_image = base_images.get(config.type.value, "alpine:latest")
            
            # Get copy commands
            copy_commands = {
                "nodejs": "COPY package*.json ./",
                "python": "COPY requirements*.txt pyproject.toml setup.py* ./",
                "go": "COPY go.mod go.sum ./"
            }
            copy_cmd = copy_commands.get(config.type.value, "")
            
            # Get install commands
            install_commands = {
                "nodejs": "RUN npm install --only=production",
                "python": "RUN pip install --no-cache-dir -r requirements.txt",
                "go": "RUN go mod download"
            }
            install_cmd = install_commands.get(config.type.value, "")
            
            # Environment variables
            env_vars = ""
            if config.environment:
                for key, value in config.environment.items():
                    env_vars += f"ENV {key}={value}\n"
            
            return f"""FROM {base_image}

WORKDIR {config.install_path}

# Copy package files first for better caching
{copy_cmd}

# Install dependencies
{install_cmd}

# Copy source code
COPY . .

# Expose port
EXPOSE {config.port}

# Set environment variables
{env_vars}

# Start command
CMD {config.start_command}
"""