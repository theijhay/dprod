"""add_ai_agent_infrastructure

Revision ID: 076ae3b5902b
Revises: 20251103_0001
Create Date: 2025-11-08 08:29:25.094387

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '076ae3b5902b'
down_revision: Union[str, None] = '20251103_0001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # AI Agent Decisions Table
    op.create_table(
        'ai_agent_decisions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('agent_type', sa.String(50), nullable=False),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('projects.id', ondelete='CASCADE')),
        sa.Column('deployment_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('deployments.id', ondelete='CASCADE'), nullable=True),
        
        # Input context
        sa.Column('input_context', postgresql.JSONB, nullable=False),
        sa.Column('tools_used', postgresql.JSONB),
        sa.Column('raw_agent_response', sa.Text),
        
        # Decision output
        sa.Column('parsed_decision', postgresql.JSONB, nullable=False),
        sa.Column('confidence_score', sa.Numeric(3, 2)),
        sa.Column('decision_version', sa.String(20)),
        
        # Verification tracking
        sa.Column('was_correct', sa.Boolean),
        sa.Column('user_override', sa.Boolean, default=False),
        sa.Column('override_reason', sa.Text),
        sa.Column('verification_source', sa.String(50)),
        
        # Performance metrics
        sa.Column('processing_time_ms', sa.Integer),
        sa.Column('token_usage', sa.Integer),
        sa.Column('cost_estimate', sa.Numeric(10, 6)),
        
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), onupdate=sa.text('now()'))
    )
    
    # Create indexes for ai_agent_decisions
    op.create_index('ix_ai_agent_decisions_agent_type', 'ai_agent_decisions', ['agent_type'])
    op.create_index('ix_ai_agent_decisions_project_id', 'ai_agent_decisions', ['project_id'])
    op.create_index('ix_ai_agent_decisions_created_at', 'ai_agent_decisions', ['created_at'])
    
    # Project Patterns Knowledge Base
    op.create_table(
        'project_patterns',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('pattern_name', sa.String(100), nullable=False),
        sa.Column('pattern_type', sa.String(50), nullable=False),
        
        # Detection signatures
        sa.Column('file_signatures', postgresql.JSONB),
        sa.Column('directory_patterns', postgresql.JSONB),
        sa.Column('config_patterns', postgresql.JSONB),
        
        # Deployment configuration
        sa.Column('suggested_config', postgresql.JSONB, nullable=False),
        sa.Column('resource_requirements', postgresql.JSONB),
        
        # Success tracking
        sa.Column('detection_count', sa.Integer, default=0),
        sa.Column('success_count', sa.Integer, default=0),
        sa.Column('success_rate', sa.Numeric(4, 3)),
        sa.Column('avg_build_time', sa.Integer),
        
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), onupdate=sa.text('now()'))
    )
    
    # Create indexes for project_patterns
    op.create_index('ix_project_patterns_pattern_type', 'project_patterns', ['pattern_type'])
    op.create_index('ix_project_patterns_success_rate', 'project_patterns', ['success_rate'])
    
    # Agent Performance Metrics
    op.create_table(
        'agent_performance',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('agent_type', sa.String(50), nullable=False),
        sa.Column('date', sa.Date, nullable=False),
        
        # Usage metrics
        sa.Column('total_requests', sa.Integer, default=0),
        sa.Column('successful_requests', sa.Integer, default=0),
        sa.Column('failed_requests', sa.Integer, default=0),
        
        # Accuracy metrics
        sa.Column('correct_decisions', sa.Integer, default=0),
        sa.Column('incorrect_decisions', sa.Integer, default=0),
        sa.Column('accuracy_rate', sa.Numeric(4, 3)),
        
        # Cost metrics
        sa.Column('total_tokens_used', sa.Integer, default=0),
        sa.Column('estimated_cost', sa.Numeric(10, 4), default=0),
        sa.Column('avg_tokens_per_request', sa.Integer),
        
        # Performance metrics
        sa.Column('avg_processing_time_ms', sa.Integer),
        sa.Column('p95_processing_time_ms', sa.Integer),
        
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'))
    )
    
    # Create unique constraint for agent_performance
    op.create_index('ix_agent_performance_agent_date', 'agent_performance', ['agent_type', 'date'], unique=True)


def downgrade() -> None:
    op.drop_table('agent_performance')
    op.drop_table('project_patterns')
    op.drop_table('ai_agent_decisions')
