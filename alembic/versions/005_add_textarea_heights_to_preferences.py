"""Add textarea height columns to user_preferences

Revision ID: 005_add_textarea_heights
Revises: 004_add_disciplines_table
Create Date: 2025-12-11

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '005_add_textarea_heights'
down_revision = '004_add_disciplines_table'
branch_labels = None
depends_on = None


def upgrade():
    # Add textarea height columns to user_preferences table
    op.add_column('user_preferences', sa.Column('history_in_life_height', sa.Integer(), nullable=True))
    op.add_column('user_preferences', sa.Column('after_death_height', sa.Integer(), nullable=True))
    op.add_column('user_preferences', sa.Column('notes_height', sa.Integer(), nullable=True))


def downgrade():
    # Remove textarea height columns
    op.drop_column('user_preferences', 'notes_height')
    op.drop_column('user_preferences', 'after_death_height')
    op.drop_column('user_preferences', 'history_in_life_height')
