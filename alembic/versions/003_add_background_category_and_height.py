"""Add category and description_height to backgrounds

Revision ID: 003
Revises: 002
Create Date: 2025-12-10

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade():
    # Add category column to backgrounds table
    op.add_column('backgrounds', sa.Column('category', sa.String(length=20), nullable=True))

    # Add description_height column to backgrounds table
    op.add_column('backgrounds', sa.Column('description_height', sa.Integer(), nullable=True))

    # Set default values for existing rows
    op.execute("UPDATE backgrounds SET category = 'Background' WHERE category IS NULL")
    op.execute("UPDATE backgrounds SET description_height = 60 WHERE description_height IS NULL")

    # Make category non-nullable with default
    op.alter_column('backgrounds', 'category',
                    existing_type=sa.String(length=20),
                    nullable=False,
                    server_default='Background')


def downgrade():
    # Remove the columns
    op.drop_column('backgrounds', 'description_height')
    op.drop_column('backgrounds', 'category')
