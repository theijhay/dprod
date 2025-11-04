"""add password hash to users

Revision ID: 20251103_0001
Revises: 20251029_0001
Create Date: 2025-11-03 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "20251103_0001"
down_revision: Union[str, None] = "20251029_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add password_hash column to users table."""
    # Add password_hash column as nullable first
    op.add_column(
        "users",
        sa.Column("password_hash", sa.String(length=255), nullable=True)
    )
    
    # Set a default hash for existing users (they'll need to reset password)
    # This is a hash of "ChangeMe123!" - users should change this immediately
    default_hash = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqYr4tCJKW"
    op.execute(f"UPDATE users SET password_hash = '{default_hash}' WHERE password_hash IS NULL")
    
    # Now make it non-nullable
    op.alter_column("users", "password_hash", nullable=False)


def downgrade() -> None:
    """Remove password_hash column from users table."""
    op.drop_column("users", "password_hash")
