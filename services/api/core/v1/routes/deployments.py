"""Deployment management endpoints."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ...db.database import get_db
from ...v1.auth.dependencies import get_current_user
from ...v1.services.deployment_service import DeploymentService
from services.shared.core.models import Project, Deployment, User
from services.shared.core.schemas import DeploymentCreate, DeploymentResponse

router = APIRouter()

# Note: deployment_service is created per-request to inject DB session
# deployment_service = DeploymentService()  # OLD: shared instance


@router.post("/projects/{project_id}", response_model=DeploymentResponse)
async def create_deployment(
    project_id: str,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new deployment for a project."""
    # Create deployment service with DB session for AI-enhanced detection
    deployment_service = DeploymentService(db_session=db)
    # Verify project ownership
    result = await db.execute(
        select(Project).where(
            Project.id == project_id,
            Project.user_id == current_user.id
        )
    )
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Read uploaded file
    content = await file.read()
    
    # Create deployment record
    new_deployment = Deployment(
        project_id=project.id,
        status="created"
    )
    
    db.add(new_deployment)
    await db.commit()
    await db.refresh(new_deployment)
    
    # Trigger actual deployment process
    try:
        deployment_info = await deployment_service.deploy_project(project, content)
        
        # Update deployment with results
        new_deployment.status = "live"
        new_deployment.url = deployment_info.get("url")
        new_deployment.container_id = deployment_info.get("container_id")
        
        await db.commit()
        await db.refresh(new_deployment)
        
    except Exception as e:
        # Update deployment with error
        new_deployment.status = "error"
        new_deployment.logs = str(e)
        
        await db.commit()
        await db.refresh(new_deployment)
    
    return DeploymentResponse.from_orm(new_deployment)


@router.get("/projects/{project_id}", response_model=List[DeploymentResponse])
async def list_deployments(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List deployments for a project."""
    # Verify project ownership
    result = await db.execute(
        select(Project).where(
            Project.id == project_id,
            Project.user_id == current_user.id
        )
    )
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Get deployments
    result = await db.execute(
        select(Deployment).where(Deployment.project_id == project_id)
    )
    deployments = result.scalars().all()
    
    return [DeploymentResponse.from_orm(deployment) for deployment in deployments]


@router.get("/{deployment_id}", response_model=DeploymentResponse)
async def get_deployment(
    deployment_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific deployment."""
    # Get deployment with project ownership check
    result = await db.execute(
        select(Deployment)
        .join(Project, Deployment.project_id == Project.id)
        .where(
            Deployment.id == deployment_id,
            Project.user_id == current_user.id
        )
    )
    deployment = result.scalar_one_or_none()
    
    if not deployment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deployment not found"
        )
    
    return DeploymentResponse.from_orm(deployment)


@router.get("/{deployment_id}/logs")
async def get_deployment_logs(
    deployment_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get deployment logs."""
    # Get deployment with project ownership check
    result = await db.execute(
        select(Deployment)
        .join(Project, Deployment.project_id == Project.id)
        .where(
            Deployment.id == deployment_id,
            Project.user_id == current_user.id
        )
    )
    deployment = result.scalar_one_or_none()
    
    if not deployment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deployment not found"
        )
    
    return {
        "deployment_id": deployment.id,
        "logs": deployment.logs or "No logs available"
    }
