"""initial schema

Revision ID: 20251029_0001
Revises: 
Create Date: 2025-10-29 07:15:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "20251029_0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("api_key", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_api_key", "users", ["api_key"], unique=True)

    op.create_table(
        "projects",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("subdomain", sa.String(length=63), nullable=True),
        sa.Column("type", sa.String(length=20), nullable=False, server_default="unknown"),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="active"),
        sa.Column("url", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_projects_user_id", "projects", ["user_id"], unique=False)
    op.create_index("ix_projects_subdomain", "projects", ["subdomain"], unique=True)

    op.create_table(
        "deployments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="created"),
        sa.Column("commit_hash", sa.String(length=40), nullable=True),
        sa.Column("logs", sa.Text(), nullable=True),
        sa.Column("url", sa.String(length=255), nullable=True),
        sa.Column("container_id", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_deployments_project_id", "deployments", ["project_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_deployments_project_id", table_name="deployments")
    op.drop_table("deployments")
    op.drop_index("ix_projects_subdomain", table_name="projects")
    op.drop_index("ix_projects_user_id", table_name="projects")
    op.drop_table("projects")
    op.drop_index("ix_users_api_key", table_name="users")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")


