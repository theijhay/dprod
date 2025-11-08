"""SQLAlchemy database models for Dprod."""

from datetime import datetime
from enum import Enum
from uuid import uuid4

from sqlalchemy import Column, DateTime, String, Text, Integer, Boolean, Numeric, Date
from sqlalchemy.dialects.postgresql import UUID as SQLUUID, JSONB
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


# AI Agent Models
class AIAgentDecision(Base):
    """AI Agent Decision tracking model."""
    __tablename__ = "ai_agent_decisions"

    id = Column(SQLUUID(as_uuid=True), primary_key=True, default=uuid4)
    agent_type = Column(String(50), nullable=False, index=True)
    project_id = Column(SQLUUID(as_uuid=True), nullable=True, index=True)
    deployment_id = Column(SQLUUID(as_uuid=True), nullable=True)
    
    # Input context
    input_context = Column(JSONB, nullable=False)
    tools_used = Column(JSONB)
    raw_agent_response = Column(Text)
    
    # Decision output
    parsed_decision = Column(JSONB, nullable=False)
    confidence_score = Column(Numeric(3, 2))
    decision_version = Column(String(20))
    
    # Verification tracking
    was_correct = Column(Boolean)
    user_override = Column(Boolean, default=False)
    override_reason = Column(Text)
    verification_source = Column(String(50))
    
    # Performance metrics
    processing_time_ms = Column(Integer)
    token_usage = Column(Integer)
    cost_estimate = Column(Numeric(10, 6))
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class ProjectPattern(Base):
    """Project Pattern knowledge base model."""
    __tablename__ = "project_patterns"

    id = Column(SQLUUID(as_uuid=True), primary_key=True, default=uuid4)
    pattern_name = Column(String(100), nullable=False)
    pattern_type = Column(String(50), nullable=False, index=True)
    
    # Detection signatures
    file_signatures = Column(JSONB)
    directory_patterns = Column(JSONB)
    config_patterns = Column(JSONB)
    
    # Deployment configuration
    suggested_config = Column(JSONB, nullable=False)
    resource_requirements = Column(JSONB)
    
    # Success tracking
    detection_count = Column(Integer, default=0)
    success_count = Column(Integer, default=0)
    success_rate = Column(Numeric(4, 3))
    avg_build_time = Column(Integer)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class AgentPerformance(Base):
    """Agent Performance metrics model."""
    __tablename__ = "agent_performance"

    id = Column(SQLUUID(as_uuid=True), primary_key=True, default=uuid4)
    agent_type = Column(String(50), nullable=False)
    date = Column(Date, nullable=False)
    
    # Usage metrics
    total_requests = Column(Integer, default=0)
    successful_requests = Column(Integer, default=0)
    failed_requests = Column(Integer, default=0)
    
    # Accuracy metrics
    correct_decisions = Column(Integer, default=0)
    incorrect_decisions = Column(Integer, default=0)
    accuracy_rate = Column(Numeric(4, 3))
    
    # Cost metrics
    total_tokens_used = Column(Integer, default=0)
    estimated_cost = Column(Numeric(10, 6), default=0)
    avg_tokens_per_request = Column(Integer)
    
    # Performance metrics
    avg_processing_time_ms = Column(Integer)
    p95_processing_time_ms = Column(Integer)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

