"""Drop denormalized discipline columns and deprecated HTR edge columns

Revision ID: 012_drop_denormalized_columns
Revises: 011_add_audit_logs
Create Date: 2026-02-08

Migration 004 migrated discipline data into the disciplines table but kept the
old individual columns on vtm_characters as a safety net. Now that all code reads
from the disciplines relationship table, these columns can be dropped.

Similarly, the legacy edge_config/edge_1_id/edge_2_id/selected_perks columns on
htr_characters were superseded by the htr_edges and htr_perks tables and are no
longer referenced by any code.
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '012_drop_denormalized_columns'
down_revision = '011_add_audit_logs'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Drop denormalized discipline columns from vtm_characters
    # Data lives in the disciplines table (migrated in 004)
    for i in range(1, 6):
        op.drop_column('vtm_characters', f'discipline_{i}_name')
        op.drop_column('vtm_characters', f'discipline_{i}_level')
        op.drop_column('vtm_characters', f'discipline_{i}_powers')
        op.drop_column('vtm_characters', f'discipline_{i}_description')

    # Drop deprecated HTR edge columns from htr_characters
    # Data lives in htr_edges and htr_perks tables
    op.drop_column('htr_characters', 'edge_config')
    op.drop_column('htr_characters', 'edge_1_id')
    op.drop_column('htr_characters', 'edge_2_id')
    op.drop_column('htr_characters', 'selected_perks')


def downgrade() -> None:
    # Re-add deprecated HTR edge columns
    op.add_column('htr_characters', sa.Column('selected_perks', sa.Text(), nullable=True))
    op.add_column('htr_characters', sa.Column('edge_2_id', sa.String(length=50), nullable=True))
    op.add_column('htr_characters', sa.Column('edge_1_id', sa.String(length=50), nullable=True))
    op.add_column('htr_characters', sa.Column('edge_config', sa.String(length=10), server_default='1e2p', nullable=True))

    # Re-add denormalized discipline columns
    for i in range(1, 6):
        op.add_column('vtm_characters', sa.Column(f'discipline_{i}_description', sa.Text(), nullable=True))
        op.add_column('vtm_characters', sa.Column(f'discipline_{i}_powers', sa.Text(), nullable=True))
        op.add_column('vtm_characters', sa.Column(f'discipline_{i}_level', sa.Integer(), nullable=True))
        op.add_column('vtm_characters', sa.Column(f'discipline_{i}_name', sa.String(length=100), nullable=True))

    # Note: downgrade re-creates the columns but does NOT repopulate data.
    # If you need the data back, restore from a database backup.
