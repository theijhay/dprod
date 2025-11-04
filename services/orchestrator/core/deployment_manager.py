"""Deployment manager that orchestrates the complete deployment process."""

import asyncio
import tempfile
import tarfile
import shutil
from pathlib import Path
from typing import Dict, Any, Optional

from services.shared.core.models import Project
from services.shared.core.schemas import ProjectConfig
from services.shared.core.exceptions import DeploymentError, BuildError
from .docker_manager import DockerManager


class DeploymentManager:
    """Manages the complete deployment lifecycle."""
    
    def __init__(self):
        """Initialize deployment manager."""
        self.docker_manager = DockerManager()
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
            detection_engine: Project detection engine
            
        Returns:
            Dict containing deployment information
        """
        try:
            print(f"🚀 Starting deployment for project: {project.name}")
            
            # Create temporary directory for build context
            with tempfile.TemporaryDirectory() as temp_dir:
                build_context = Path(temp_dir)
                
                # Extract source code
                await self._extract_source_code(source_code, build_context)
                
                # Detect project type and generate config
                config = detection_engine.detect_project(build_context)
                if not config:
                    raise DeploymentError("Could not detect project type")
                
                print(f"📋 Project config: {config}")
                
                # Build Docker image
                image_id = await self.docker_manager.build_image(
                    project, source_code, config, build_context
                )
                
                # Run container
                container_id = await self.docker_manager.run_container(
                    project, image_id, config
                )
                
                # Get container info
                container_info = await self.docker_manager.get_container_info(container_id)
                
                # Generate URL - always use Dprod's default domain for free users
                subdomain = getattr(project, 'subdomain', None) or project.name.lower().replace('_', '-')
                
                # Generate URL based on environment
                import os
                is_development = os.getenv('NODE_ENV', 'development') != 'production'
                
                if is_development:
                    # Development: use localhost with port
                    if container_info.get("ports"):
                        first_port = list(container_info["ports"].values())[0]
                        url = f"http://localhost:{first_port}"
                    else:
                        url = f"http://localhost:3000"
                else:
                    # Production: Dprod's default domain (free tier)
                    url = f"https://{subdomain}.dprod.app"
                
                # Store deployment info
                deployment_info = {
                    "project_id": str(project.id),
                    "container_id": container_id,
                    "image_id": image_id,
                    "status": "live",
                    "url": url,
                    "ports": container_info.get("ports", {}),
                    "created_at": container_info.get("created"),
                    "config": config.dict()
                }
                
                self.active_deployments[str(project.id)] = deployment_info
                
                print(f"✅ Deployment successful: {deployment_info['url']}")
                return deployment_info
                
        except Exception as e:
            print(f"❌ Deployment failed: {e}")
            raise DeploymentError(f"Deployment failed: {e}")
    
    async def get_deployment_status(self, project_id: str) -> Dict[str, Any]:
        """Get deployment status for a project."""
        if project_id not in self.active_deployments:
            return {"status": "not_found", "project_id": project_id}
        
        deployment = self.active_deployments[project_id]
        container_id = deployment["container_id"]
        
        try:
            container_info = await self.docker_manager.get_container_info(container_id)
            deployment["status"] = container_info["status"]
            deployment["ports"] = container_info["ports"]
            
            return deployment
            
        except Exception as e:
            return {
                "status": "error",
                "project_id": project_id,
                "error": str(e)
            }
    
    async def get_deployment_logs(self, project_id: str) -> str:
        """Get deployment logs for a project."""
        if project_id not in self.active_deployments:
            return f"No deployment found for project {project_id}"
        
        deployment = self.active_deployments[project_id]
        container_id = deployment["container_id"]
        
        try:
            logs = await self.docker_manager.get_container_logs(container_id)
            return logs
            
        except Exception as e:
            return f"Failed to get logs: {e}"
    
    async def stop_deployment(self, project_id: str) -> bool:
        """Stop a deployment."""
        if project_id not in self.active_deployments:
            return False
        
        deployment = self.active_deployments[project_id]
        container_id = deployment["container_id"]
        
        try:
            success = await self.docker_manager.stop_container(container_id)
            if success:
                del self.active_deployments[project_id]
            return success
            
        except Exception as e:
            print(f"❌ Failed to stop deployment: {e}")
            return False
    
    async def list_deployments(self) -> Dict[str, Dict[str, Any]]:
        """List all active deployments."""
        return self.active_deployments.copy()
    
    async def health_check(self, project_id: str) -> bool:
        """Perform health check on a deployment."""
        if project_id not in self.active_deployments:
            return False
        
        deployment = self.active_deployments[project_id]
        container_id = deployment["container_id"]
        
        try:
            container_info = await self.docker_manager.get_container_info(container_id)
            return container_info["status"] == "running"
            
        except Exception:
            return False
    
    async def _extract_source_code(self, source_code: bytes, target_dir: Path) -> None:
        """Extract compressed source code to target directory."""
        try:
            # Write compressed data to temporary file
            with tempfile.NamedTemporaryFile(suffix='.tar.gz', delete=False) as temp_file:
                temp_file.write(source_code)
                temp_file_path = temp_file.name
            
            # Extract tar.gz file
            with tarfile.open(temp_file_path, 'r:gz') as tar:
                tar.extractall(target_dir)
            
            # Clean up temporary file
            Path(temp_file_path).unlink()
            
        except Exception as e:
            raise BuildError(f"Failed to extract source code: {e}")