"""Deployment service that integrates detection engine and orchestrator."""

import asyncio
from pathlib import Path
from typing import Dict, Any

from services.shared.core.models import Project, Deployment, DeploymentStatus
from services.shared.core.exceptions import DeploymentError

# Import our services
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../../..'))
from services.detector.core.detector import ProjectDetector
from services.orchestrator.core.deployment_manager import DeploymentManager


class DeploymentService:
    """Service that orchestrates the complete deployment process."""
    
    def __init__(self):
        """Initialize deployment service."""
        self.detector = ProjectDetector()
        self.deployment_manager = DeploymentManager()
    
    async def deploy_project(
        self,
        project: Project,
        source_code: bytes
    ) -> Dict[str, Any]:
        """
        Deploy a project from source code.
        
        Args:
            project: Project database model
            source_code: Compressed source code bytes
            
        Returns:
            Dict containing deployment information
        """
        try:
            print(f"🚀 Starting deployment for project: {project.name}")
            
            # Deploy using the deployment manager
            deployment_info = await self.deployment_manager.deploy_project(
                project=project,
                source_code=source_code,
                detection_engine=self.detector
            )
            
            return deployment_info
            
        except Exception as e:
            print(f"❌ Deployment failed: {e}")
            raise DeploymentError(f"Deployment failed: {e}")
    
    async def get_deployment_status(self, project_id: str) -> Dict[str, Any]:
        """Get deployment status for a project."""
        return await self.deployment_manager.get_deployment_status(project_id)
    
    async def get_deployment_logs(self, project_id: str) -> str:
        """Get deployment logs for a project."""
        return await self.deployment_manager.get_deployment_logs(project_id)
    
    async def stop_deployment(self, project_id: str) -> bool:
        """Stop a deployment."""
        return await self.deployment_manager.stop_deployment(project_id)
    
    async def list_deployments(self) -> Dict[str, Dict[str, Any]]:
        """List all active deployments."""
        return await self.deployment_manager.list_deployments()
    
    async def health_check(self, project_id: str) -> bool:
        """Perform health check on a deployment."""
        return await self.deployment_manager.health_check(project_id)
