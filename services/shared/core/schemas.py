"""Pydantic schemas for API validation and serialization."""

from datetime import datetime
from typing import Dict, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from .models import ProjectType, DeploymentStatus, UserStatus


# User Schemas
class UserBase(BaseModel):
    """Base user model."""
    email: str = Field(..., description="User email address")
    status: UserStatus = Field(default=UserStatus.ACTIVE, description="User status")


class UserCreate(UserBase):
    """User creation model."""
    pass


class UserResponse(UserBase):
    """User response model."""
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Project Schemas
class ProjectBase(BaseModel):
    """Base project model."""
    name: str = Field(..., min_length=1, max_length=50, description="Project name")
    subdomain: Optional[str] = Field(None, description="Project subdomain")
    custom_domain: Optional[str] = Field(None, description="Custom domain (premium feature)")


class ProjectCreate(ProjectBase):
    """Project creation model."""
    type: ProjectType = Field(default=ProjectType.UNKNOWN, description="Project type")


class ProjectResponse(ProjectBase):
    """Project response model."""
    id: UUID
    user_id: UUID
    type: ProjectType
    status: str
    url: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Deployment Schemas
class DeploymentBase(BaseModel):
    """Base deployment model."""
    status: DeploymentStatus = Field(default=DeploymentStatus.CREATED, description="Deployment status")
    commit_hash: Optional[str] = Field(None, description="Git commit hash")


class DeploymentCreate(DeploymentBase):
    """Deployment creation model."""
    project_id: UUID = Field(..., description="Project ID")


class DeploymentResponse(DeploymentBase):
    """Deployment response model."""
    id: UUID
    project_id: UUID
    logs: Optional[str] = None
    url: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Configuration Schemas
class ProjectConfig(BaseModel):
    """Project configuration for deployment."""
    type: ProjectType
    build_command: Optional[str] = None
    start_command: str
    port: int = Field(default=3000, description="Application port")
    environment: Dict[str, str] = Field(default_factory=dict, description="Environment variables")
    install_path: str = Field(default="/app", description="Container installation path")


class LogEntry(BaseModel):
    """Log entry model."""
    level: str = Field(..., description="Log level (info, warning, error, debug)")
    message: str = Field(..., description="Log message")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Log timestamp")
    deployment_id: UUID = Field(..., description="Deployment ID")
