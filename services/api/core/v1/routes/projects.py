"""Project management endpoints."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ...db.database import get_db
from ...v1.auth.dependencies import get_current_user
from services.shared.core.models import Project, ProjectCreate, ProjectResponse, User

router = APIRouter()


@router.post("/", response_model=ProjectResponse)
async def create_project(
    project_data: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new project."""
    # Generate subdomain
    import re
    subdomain = re.sub(r'[^a-z0-9-]', '-', project_data.name.lower())
    subdomain = re.sub(r'-+', '-', subdomain).strip('-')
    
    # Ensure subdomain is unique
    counter = 1
    original_subdomain = subdomain
    while True:
        result = await db.execute(
            select(Project).where(Project.subdomain == subdomain)
        )
        if not result.scalar_one_or_none():
            break
        subdomain = f"{original_subdomain}-{counter}"
        counter += 1
    
    new_project = Project(
        user_id=current_user.id,
        name=project_data.name,
        subdomain=subdomain,
        type=project_data.type
    )
    
    db.add(new_project)
    await db.commit()
    await db.refresh(new_project)
    
    return ProjectResponse.from_orm(new_project)


@router.get("/", response_model=List[ProjectResponse])
async def list_projects(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List user's projects."""
    result = await db.execute(
        select(Project).where(Project.user_id == current_user.id)
    )
    projects = result.scalars().all()
    
    return [ProjectResponse.from_orm(project) for project in projects]


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific project."""
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
    
    return ProjectResponse.from_orm(project)


@router.delete("/{project_id}")
async def delete_project(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a project."""
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
    
    await db.delete(project)
    await db.commit()
    
    return {"message": "Project deleted successfully"}
