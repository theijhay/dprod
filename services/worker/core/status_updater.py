"""Database status updater for deployment jobs."""
import logging
from typing import Optional, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, update

# Import shared models
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))
from services.shared.core.models import Deployment

from .config import config

logger = logging.getLogger(__name__)


class StatusUpdater:
    """Update deployment status in database."""
    
    def __init__(self):
        """Initialize database connection."""
        self.engine = create_async_engine(
            config.DATABASE_URL,
            echo=False,
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10
        )
        self.async_session = sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
    
    async def update_status(
        self,
        deployment_id: str,
        status: str,
        additional_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Update deployment status.
        
        Args:
            deployment_id: Deployment ID
            status: New status
            additional_data: Additional data to update
            
        Returns:
            True if successful
        """
        try:
            async with self.async_session() as session:
                # Get deployment
                result = await session.execute(
                    select(Deployment).where(Deployment.id == deployment_id)
                )
                deployment = result.scalar_one_or_none()
                
                if not deployment:
                    logger.error(f"❌ Deployment not found: {deployment_id}")
                    return False
                
                # Update status
                deployment.status = status
                deployment.updated_at = datetime.utcnow()
                
                # Update additional data
                if additional_data:
                    for key, value in additional_data.items():
                        if hasattr(deployment, key):
                            setattr(deployment, key, value)
                
                await session.commit()
                logger.info(f"✅ Status updated: {deployment_id} -> {status}")
                return True
                
        except Exception as e:
            logger.error(f"❌ Error updating status: {e}", exc_info=True)
            return False
    
    async def update_build_started(self, deployment_id: str) -> bool:
        """Mark deployment as building.
        
        Args:
            deployment_id: Deployment ID
            
        Returns:
            True if successful
        """
        return await self.update_status(
            deployment_id,
            'building',
            {'build_started_at': datetime.utcnow()}
        )
    
    async def update_build_completed(
        self,
        deployment_id: str,
        image_id: str
    ) -> bool:
        """Mark build as completed.
        
        Args:
            deployment_id: Deployment ID
            image_id: Docker image ID
            
        Returns:
            True if successful
        """
        return await self.update_status(
            deployment_id,
            'deploying',
            {
                'image_id': image_id,
                'build_completed_at': datetime.utcnow()
            }
        )
    
    async def update_deployment_running(
        self,
        deployment_id: str,
        container_id: str,
        url: Optional[str] = None
    ) -> bool:
        """Mark deployment as running.
        
        Args:
            deployment_id: Deployment ID
            container_id: Container ID
            url: Application URL
            
        Returns:
            True if successful
        """
        data = {
            'container_id': container_id,
            'deployed_at': datetime.utcnow()
        }
        if url:
            data['url'] = url
        
        return await self.update_status(deployment_id, 'running', data)
    
    async def update_deployment_failed(
        self,
        deployment_id: str,
        error_message: str
    ) -> bool:
        """Mark deployment as failed.
        
        Args:
            deployment_id: Deployment ID
            error_message: Error message
            
        Returns:
            True if successful
        """
        return await self.update_status(
            deployment_id,
            'failed',
            {
                'error': error_message,
                'failed_at': datetime.utcnow()
            }
        )
    
    async def add_build_log(
        self,
        deployment_id: str,
        log_message: str
    ) -> bool:
        """Add build log entry.
        
        Args:
            deployment_id: Deployment ID
            log_message: Log message
            
        Returns:
            True if successful
        """
        try:
            async with self.async_session() as session:
                result = await session.execute(
                    select(Deployment).where(Deployment.id == deployment_id)
                )
                deployment = result.scalar_one_or_none()
                
                if not deployment:
                    return False
                
                # Append to build logs
                if not deployment.build_logs:
                    deployment.build_logs = []
                
                deployment.build_logs.append({
                    'timestamp': datetime.utcnow().isoformat(),
                    'message': log_message,
                    'worker_id': config.WORKER_ID
                })
                
                await session.commit()
                return True
                
        except Exception as e:
            logger.error(f"❌ Error adding build log: {e}")
            return False
    
    async def cleanup(self):
        """Cleanup database connections."""
        await self.engine.dispose()
