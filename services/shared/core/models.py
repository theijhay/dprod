"""SQLAlchemy database models for Dprod."""

from datetime import datetime
from enum import Enum
from uuid import uuid4

from sqlalchemy import Column, DateTime, String, Text
from sqlalchemy.dialects.postgresql import UUID as SQLUUID
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


# Enums
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


# SQLAlchemy Database Models
class User(Base):
    """User database model."""
    __tablename__ = "users"

    id = Column(SQLUUID(as_uuid=True), primary_key=True, default=uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
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
