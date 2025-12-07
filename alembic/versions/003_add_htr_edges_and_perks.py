"""Add HTR Edges and Perks tables

Revision ID: 003_add_htr_edges_and_perks
Revises: 002_add_htr_tables
Create Date: 2025-12-07

This migration:
1. Creates HTREdge table for tracking character edges
2. Creates HTRPerk table for tracking character perks
3. Replaces the old edge_config/edge_1_id/edge_2_id/selected_perks system with flexible relationships
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '003_add_htr_edges_and_perks'
down_revision = '002_add_htr_tables'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create htr_edges table
    op.create_table(
        'htr_edges',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('character_id', sa.Integer(), nullable=False),
        sa.Column('edge_id', sa.String(length=100), nullable=False),
        sa.Column('display_order', sa.Integer(), server_default='0', nullable=True),
        sa.ForeignKeyConstraint(['character_id'], ['htr_characters.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_htr_edges_id'), 'htr_edges', ['id'], unique=False)

    # Create htr_perks table
    op.create_table(
        'htr_perks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('character_id', sa.Integer(), nullable=False),
        sa.Column('edge_id', sa.String(length=100), nullable=False),
        sa.Column('perk_id', sa.String(length=100), nullable=False),
        sa.Column('display_order', sa.Integer(), server_default='0', nullable=True),
        sa.ForeignKeyConstraint(['character_id'], ['htr_characters.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_htr_perks_id'), 'htr_perks', ['id'], unique=False)

    # Migrate existing data from old edge/perk system to new tables
    # This will be handled by a separate data migration script if needed


def downgrade() -> None:
    # Drop new tables
    op.drop_index(op.f('ix_htr_perks_id'), table_name='htr_perks')
    op.drop_table('htr_perks')
    op.drop_index(op.f('ix_htr_edges_id'), table_name='htr_edges')
    op.drop_table('htr_edges')
