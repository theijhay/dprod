"""Deployment orchestration and management."""

import asyncio
import tempfile
import uuid
from pathlib import Path
from typing import Optional, Dict, Any
import tarfile
import io

from dprod_shared.models import Project, ProjectConfig, Deployment, DeploymentStatus
from dprod_shared.exceptions import DeploymentError, ProjectDetectionError

from .docker_manager import DockerManager


class DeploymentManager:
    """Manages the complete deployment lifecycle."""
    
    def __init__(self, docker_socket_path: str = "/var/run/docker.sock"):
        """Initialize deployment manager."""
        self.docker_manager = DockerManager(docker_socket_path)
        self.active_deployments: Dict[str, Dict[str, Any]] = {}
    
    async def deploy_project(
        self,
        project: Project,
        source_code: bytes,
        detection_engine
    ) -> Dict[str, Any]:
        """
        Deploy a project from source code.
        
        Args:
            project: Project database model
            source_code: Compressed source code bytes
            detection_engine: Project detection engine instance
            
        Returns:
            Dict containing deployment information
        """
        deployment_id = str(uuid.uuid4())
        
        try:
            print(f"🚀 Starting deployment for project: {project.name}")
            
            # Extract source code
            source_path = await self._extract_source_code(source_code, deployment_id)
            
            # Detect project configuration
            print("🔍 Detecting project configuration...")
            project_config = detection_engine.detect(source_path)
            
            # Update project type if detected
            if project_config.type != "unknown":
                project.type = project_config.type
            
            # Create Docker container
            print("🐳 Creating deployment container...")
            container_id = await self.docker_manager.create_deployment_container(
                project.id,
                project_config,
                source_path
            )
            
            # Get container port
            container_port = await self.docker_manager.get_container_port(project.id)
            
            # Generate deployment URL
            deployment_url = f"http://localhost:{container_port}"
            
            # Store deployment info
            deployment_info = {
                "deployment_id": deployment_id,
                "project_id": project.id,
                "container_id": container_id,
                "url": deployment_url,
                "port": container_port,
                "status": DeploymentStatus.LIVE,
                "config": project_config
            }
            
            self.active_deployments[project.id] = deployment_info
            
            print(f"✅ Deployment successful!")
            print(f"🔗 URL: {deployment_url}")
            print(f"📦 Container: {container_id[:12]}")
            
            return deployment_info
            
        except Exception as e:
            print(f"❌ Deployment failed: {e}")
            
            # Cleanup on failure
            if project.id in self.active_deployments:
                await self.docker_manager.stop_container(project.id)
                del self.active_deployments[project.id]
            
            raise DeploymentError(f"Deployment failed: {e}")
    
    async def _extract_source_code(self, source_code: bytes, deployment_id: str) -> Path:
        """Extract compressed source code to temporary directory."""
        try:
            # Create temporary directory
            temp_dir = Path(tempfile.gettempdir()) / "dprod" / deployment_id
            temp_dir.mkdir(parents=True, exist_ok=True)
            
            # Extract tar.gz
            with tarfile.open(fileobj=io.BytesIO(source_code), mode='r:gz') as tar:
                tar.extractall(path=temp_dir)
            
            # Find the extracted project directory
            # Usually it's the first directory in the temp dir
            extracted_dirs = [d for d in temp_dir.iterdir() if d.is_dir()]
            if not extracted_dirs:
                raise DeploymentError("No project directory found in source code")
            
            project_dir = extracted_dirs[0]
            print(f"📁 Extracted project to: {project_dir}")
            
            return project_dir
            
        except Exception as e:
            raise DeploymentError(f"Failed to extract source code: {e}")
    
    async def get_deployment_status(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Get deployment status for a project."""
        return self.active_deployments.get(project_id)
    
    async def get_deployment_logs(self, project_id: str) -> str:
        """Get deployment logs for a project."""
        if project_id not in self.active_deployments:
            return "Deployment not found"
        
        try:
            return await self.docker_manager.get_container_logs(project_id)
        except Exception as e:
            return f"Error retrieving logs: {e}"
    
    async def stop_deployment(self, project_id: str) -> bool:
        """Stop a deployment."""
        if project_id not in self.active_deployments:
            return False
        
        try:
            success = await self.docker_manager.stop_container(project_id)
            if success:
                del self.active_deployments[project_id]
            return success
        except Exception as e:
            print(f"⚠️  Error stopping deployment {project_id}: {e}")
            return False
    
    async def list_deployments(self) -> Dict[str, Dict[str, Any]]:
        """List all active deployments."""
        return self.active_deployments.copy()
    
    async def cleanup_old_deployments(self, max_age_hours: int = 24):
        """Clean up old deployments."""
        await self.docker_manager.cleanup_old_containers(max_age_hours)
        
        # Also clean up our tracking
        # In a real implementation, you'd check actual container ages
        print("🧹 Cleaned up old deployments")
    
    async def health_check(self, project_id: str) -> bool:
        """Perform health check on a deployment."""
        if project_id not in self.active_deployments:
            return False
        
        try:
            # Get container status
            containers = self.docker_manager.list_containers()
            if project_id in containers:
                container_info = containers[project_id]
                return container_info["status"] == "running"
            
            return False
        except Exception as e:
            print(f"⚠️  Health check failed for {project_id}: {e}")
            return False
