"""Core data models for Dprod."""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field
from sqlalchemy import Column, DateTime, String, Text, Boolean, Integer
from sqlalchemy.dialects.postgresql import UUID as SQLUUID
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class ProjectType(str, Enum):
    """Supported project types."""
    NODEJS = "nodejs"
    PYTHON = "python"
    GO = "go"
    STATIC = "static"
    UNKNOWN = "unknown"


class DeploymentStatus(str, Enum):
    """Deployment status states."""
    CREATED = "created"
    BUILDING = "building"
    DEPLOYING = "deploying"
    LIVE = "live"
    ERROR = "error"
    STOPPED = "stopped"


class UserStatus(str, Enum):
    """User account status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


# Pydantic Models for API
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


# SQLAlchemy Models
class User(Base):
    """User database model."""
    __tablename__ = "users"

    id = Column(SQLUUID(as_uuid=True), primary_key=True, default=uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    api_key = Column(String(64), unique=True, nullable=False, index=True)
    status = Column(String(20), default=UserStatus.ACTIVE.value, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class Project(Base):
    """Project database model."""
    __tablename__ = "projects"

    id = Column(SQLUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(SQLUUID(as_uuid=True), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    subdomain = Column(String(63), unique=True, nullable=True, index=True)
    type = Column(String(20), default=ProjectType.UNKNOWN.value, nullable=False)
    status = Column(String(20), default="active", nullable=False)
    url = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class Deployment(Base):
    """Deployment database model."""
    __tablename__ = "deployments"

    id = Column(SQLUUID(as_uuid=True), primary_key=True, default=uuid4)
    project_id = Column(SQLUUID(as_uuid=True), nullable=False, index=True)
    status = Column(String(20), default=DeploymentStatus.CREATED.value, nullable=False)
    commit_hash = Column(String(40), nullable=True)
    logs = Column(Text, nullable=True)
    url = Column(String(255), nullable=True)
    container_id = Column(String(64), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
