"""add user roles

Revision ID: 009
Revises: 008
Create Date: 2024-12-30

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '009'
down_revision = '008'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add role column to users table
    op.add_column('users', sa.Column('role', sa.String(20), server_default='player', nullable=False))

    # Create index on role for faster queries
    op.create_index('ix_users_role', 'users', ['role'])

    # Optionally: Set storyteller role for existing STORYTELLER_DISCORD_ID
    # This would need to be done manually or via a data migration script


def downgrade() -> None:
    # Remove index and column
    op.drop_index('ix_users_role', table_name='users')
    op.drop_column('users', 'role')
