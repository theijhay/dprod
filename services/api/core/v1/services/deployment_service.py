"""Deployment service that integrates detection engine and orchestrator."""

import asyncio
from pathlib import Path
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from services.shared.core.models import Project, Deployment, DeploymentStatus
from services.shared.core.exceptions import DeploymentError

# Import our services
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../../..'))
from services.detector.core.detector import ProjectDetector
from services.detector.core.ai_detector import AIEnhancedDetector
from services.orchestrator.core.deployment_manager import DeploymentManager
from services.orchestrator.core.sqs_deployment_manager import SQSDeploymentManager


class DeploymentService:
    """Service that orchestrates the complete deployment process."""
    
    def __init__(self, db_session: Optional[AsyncSession] = None):
        """
        Initialize deployment service.
        
        Args:
            db_session: Optional database session for AI-enhanced detection
        """
        self.db_session = db_session
        
        # Use AI-enhanced detector if:
        # 1. DB session is available
        # 2. AI_ENABLED environment variable is true
        ai_enabled = os.getenv("AI_ENABLED", "false").lower() == "true"
        
        if db_session and ai_enabled:
            print("🤖 AI-enhanced detection enabled")
            self.detector = AIEnhancedDetector(db_session)
            self.use_ai = True
        else:
            if not ai_enabled:
                print("ℹ️  AI detection disabled (set AI_ENABLED=true to enable)")
            print("🔍 Using rule-based detection")
            self.detector = ProjectDetector()
            self.use_ai = False
            
        # Choose deployment manager based on environment
        # Use SQS-based manager if SQS_QUEUE_URL is set (production)
        # Otherwise use local Docker manager (development)
        self.sqs_queue_url = os.getenv("SQS_QUEUE_URL")
        if self.sqs_queue_url:
            print("📥 Using SQS-based deployment (production mode)")
            self.deployment_manager = SQSDeploymentManager()
        else:
            print("🐳 Using local Docker deployment (development mode)")
            # Defer creating DeploymentManager (requires local Docker) until used
            self.deployment_manager = None
    
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
            
            # Lazily create the local deployment manager if needed
            if self.deployment_manager is None:
                self.deployment_manager = DeploymentManager()

            # Deploy using the deployment manager (SQS or local Docker)
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
