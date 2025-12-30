"""add performance indexes

Revision ID: 010_add_performance_indexes
Revises: 009_add_user_roles
Create Date: 2024-12-30

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '010_add_performance_indexes'
down_revision = '009_add_user_roles'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # VTM Character indexes
    op.create_index('ix_vtm_characters_user_id', 'vtm_characters', ['user_id'])
    op.create_index('ix_vtm_characters_chronicle', 'vtm_characters', ['chronicle'])
    op.create_index('ix_vtm_characters_created_at', 'vtm_characters', ['created_at'])
    op.create_index('ix_vtm_characters_updated_at', 'vtm_characters', ['updated_at'])

    # HTR Character indexes
    op.create_index('ix_htr_characters_user_id', 'htr_characters', ['user_id'])
    op.create_index('ix_htr_characters_chronicle', 'htr_characters', ['chronicle'])
    op.create_index('ix_htr_characters_created_at', 'htr_characters', ['created_at'])
    op.create_index('ix_htr_characters_updated_at', 'htr_characters', ['updated_at'])

    # Touchstone indexes (for faster joins)
    op.create_index('ix_touchstones_character_id', 'touchstones', ['character_id'])
    op.create_index('ix_htr_touchstones_character_id', 'htr_touchstones', ['character_id'])

    # Background/Advantage/Flaw indexes
    op.create_index('ix_backgrounds_character_id', 'backgrounds', ['character_id'])
    op.create_index('ix_htr_advantages_character_id', 'htr_advantages', ['character_id'])
    op.create_index('ix_htr_flaws_character_id', 'htr_flaws', ['character_id'])

    # Discipline/Edge/Perk indexes
    op.create_index('ix_disciplines_character_id', 'disciplines', ['character_id'])
    op.create_index('ix_htr_edges_character_id', 'htr_edges', ['character_id'])
    op.create_index('ix_htr_perks_edge_id', 'htr_perks', ['edge_id'])

    # XP Log indexes
    op.create_index('ix_vtm_xp_log_character_id', 'vtm_xp_log', ['character_id'])
    op.create_index('ix_htr_xp_log_character_id', 'htr_xp_log', ['character_id'])

    # Equipment indexes
    op.create_index('ix_htr_equipment_character_id', 'htr_equipment', ['character_id'])


def downgrade() -> None:
    # Drop all indexes in reverse order
    op.drop_index('ix_htr_equipment_character_id', table_name='htr_equipment')

    op.drop_index('ix_htr_xp_log_character_id', table_name='htr_xp_log')
    op.drop_index('ix_vtm_xp_log_character_id', table_name='vtm_xp_log')

    op.drop_index('ix_htr_perks_edge_id', table_name='htr_perks')
    op.drop_index('ix_htr_edges_character_id', table_name='htr_edges')
    op.drop_index('ix_disciplines_character_id', table_name='disciplines')

    op.drop_index('ix_htr_flaws_character_id', table_name='htr_flaws')
    op.drop_index('ix_htr_advantages_character_id', table_name='htr_advantages')
    op.drop_index('ix_backgrounds_character_id', table_name='backgrounds')

    op.drop_index('ix_htr_touchstones_character_id', table_name='htr_touchstones')
    op.drop_index('ix_touchstones_character_id', table_name='touchstones')

    op.drop_index('ix_htr_characters_updated_at', table_name='htr_characters')
    op.drop_index('ix_htr_characters_created_at', table_name='htr_characters')
    op.drop_index('ix_htr_characters_chronicle', table_name='htr_characters')
    op.drop_index('ix_htr_characters_user_id', table_name='htr_characters')

    op.drop_index('ix_vtm_characters_updated_at', table_name='vtm_characters')
    op.drop_index('ix_vtm_characters_created_at', table_name='vtm_characters')
    op.drop_index('ix_vtm_characters_chronicle', table_name='vtm_characters')
    op.drop_index('ix_vtm_characters_user_id', table_name='vtm_characters')
