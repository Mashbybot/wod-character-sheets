"""Update HTR edges to support unlimited selection

Revision ID: 003
Revises: 002
Create Date: 2025-11-29

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade():
    """
    Update HTR character edges system:
    - Remove edge_config column (no longer needed - no fixed limits)
    - Remove edge_1_id and edge_2_id columns
    - Add selected_edges column (JSON array of edge IDs)
    - Keep selected_perks column (already exists)
    """

    # Add new selected_edges column
    op.add_column('htr_characters', sa.Column('selected_edges', sa.Text(), nullable=True))

    # Migrate existing data: convert edge_1_id and edge_2_id to selected_edges array
    # This SQL will create a JSON array from the old edge_1_id and edge_2_id columns
    op.execute("""
        UPDATE htr_characters
        SET selected_edges =
            CASE
                WHEN edge_1_id IS NOT NULL AND edge_2_id IS NOT NULL THEN
                    '["' || edge_1_id || '","' || edge_2_id || '"]'
                WHEN edge_1_id IS NOT NULL THEN
                    '["' || edge_1_id || '"]'
                WHEN edge_2_id IS NOT NULL THEN
                    '["' || edge_2_id || '"]'
                ELSE
                    '[]'
            END
    """)

    # Drop old columns
    op.drop_column('htr_characters', 'edge_config')
    op.drop_column('htr_characters', 'edge_1_id')
    op.drop_column('htr_characters', 'edge_2_id')


def downgrade():
    """
    Rollback changes:
    - Add back edge_config, edge_1_id, edge_2_id columns
    - Remove selected_edges column
    """

    # Add back old columns
    op.add_column('htr_characters', sa.Column('edge_2_id', sa.String(50), nullable=True))
    op.add_column('htr_characters', sa.Column('edge_1_id', sa.String(50), nullable=True))
    op.add_column('htr_characters', sa.Column('edge_config', sa.String(10), nullable=True, server_default='1e2p'))

    # Attempt to migrate data back (this is lossy if more than 2 edges selected)
    op.execute("""
        UPDATE htr_characters
        SET
            edge_1_id = CASE
                WHEN selected_edges IS NOT NULL AND selected_edges != '[]' THEN
                    REPLACE(REPLACE(REPLACE(selected_edges, '[', ''), ']', ''), '"', '')
                ELSE NULL
            END,
            edge_config = '1e2p'
    """)

    # Drop new column
    op.drop_column('htr_characters', 'selected_edges')
