"""Add Hunter: The Reckoning character tables

Revision ID: 002_add_htr_tables
Revises: 001_refactor_schema
Create Date: 2025-11-29

This migration:
1. Expands existing placeholder htr_characters table with full HTR5e fields
2. Creates HTR relationship tables (touchstones, advantages, flaws, xp_log_entries)
3. Maintains compatibility with existing VTM structure
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002_add_htr_tables'
down_revision = '001_refactor_schema'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create htr_touchstones table
    op.create_table(
        'htr_touchstones',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('character_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('display_order', sa.Integer(), server_default='0', nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['character_id'], ['htr_characters.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_htr_touchstones_id'), 'htr_touchstones', ['id'], unique=False)

    # Create htr_advantages table
    op.create_table(
        'htr_advantages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('character_id', sa.Integer(), nullable=False),
        sa.Column('type', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('dots', sa.Integer(), server_default='1', nullable=True),
        sa.Column('display_order', sa.Integer(), server_default='0', nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['character_id'], ['htr_characters.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_htr_advantages_id'), 'htr_advantages', ['id'], unique=False)

    # Create htr_flaws table
    op.create_table(
        'htr_flaws',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('character_id', sa.Integer(), nullable=False),
        sa.Column('type', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('dots', sa.Integer(), server_default='1', nullable=True),
        sa.Column('display_order', sa.Integer(), server_default='0', nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['character_id'], ['htr_characters.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_htr_flaws_id'), 'htr_flaws', ['id'], unique=False)

    # Create htr_xp_log_entries table
    op.create_table(
        'htr_xp_log_entries',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('character_id', sa.Integer(), nullable=False),
        sa.Column('date', sa.String(length=50), nullable=False),
        sa.Column('type', sa.String(length=10), nullable=False),
        sa.Column('amount', sa.Integer(), nullable=False),
        sa.Column('reason', sa.String(length=200), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['character_id'], ['htr_characters.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_htr_xp_log_entries_id'), 'htr_xp_log_entries', ['id'], unique=False)

    # Drop old placeholder columns from htr_characters
    op.drop_column('htr_characters', 'concept')
    op.drop_column('htr_characters', 'portrait_url')
    op.drop_column('htr_characters', 'character_data')

    # Add all new HTR character fields
    # Header / Chronicle Information
    op.add_column('htr_characters', sa.Column('cell', sa.String(length=100), nullable=True))
    op.add_column('htr_characters', sa.Column('chronicle', sa.String(length=100), nullable=True))

    # Identity
    op.add_column('htr_characters', sa.Column('drive', sa.String(length=50), nullable=True))
    op.add_column('htr_characters', sa.Column('age', sa.String(length=50), nullable=True))
    op.add_column('htr_characters', sa.Column('blood_type', sa.String(length=10), nullable=True))
    op.add_column('htr_characters', sa.Column('pronouns', sa.String(length=50), nullable=True))
    op.add_column('htr_characters', sa.Column('origin', sa.String(length=100), nullable=True))

    # Character Portraits (6 slots)
    op.add_column('htr_characters', sa.Column('portrait_face', sa.String(length=500), nullable=True))
    op.add_column('htr_characters', sa.Column('portrait_body', sa.String(length=500), nullable=True))
    op.add_column('htr_characters', sa.Column('portrait_hobby_1', sa.String(length=500), nullable=True))
    op.add_column('htr_characters', sa.Column('portrait_hobby_2', sa.String(length=500), nullable=True))
    op.add_column('htr_characters', sa.Column('portrait_hobby_3', sa.String(length=500), nullable=True))
    op.add_column('htr_characters', sa.Column('portrait_hobby_4', sa.String(length=500), nullable=True))
    op.add_column('htr_characters', sa.Column('alias', sa.String(length=100), nullable=True))

    # Attributes (1-5)
    op.add_column('htr_characters', sa.Column('strength', sa.Integer(), server_default='1', nullable=True))
    op.add_column('htr_characters', sa.Column('dexterity', sa.Integer(), server_default='1', nullable=True))
    op.add_column('htr_characters', sa.Column('stamina', sa.Integer(), server_default='1', nullable=True))
    op.add_column('htr_characters', sa.Column('charisma', sa.Integer(), server_default='1', nullable=True))
    op.add_column('htr_characters', sa.Column('manipulation', sa.Integer(), server_default='1', nullable=True))
    op.add_column('htr_characters', sa.Column('composure', sa.Integer(), server_default='1', nullable=True))
    op.add_column('htr_characters', sa.Column('intelligence', sa.Integer(), server_default='1', nullable=True))
    op.add_column('htr_characters', sa.Column('wits', sa.Integer(), server_default='1', nullable=True))
    op.add_column('htr_characters', sa.Column('resolve', sa.Integer(), server_default='1', nullable=True))

    # Skills (0-5)
    op.add_column('htr_characters', sa.Column('athletics', sa.Integer(), server_default='0', nullable=True))
    op.add_column('htr_characters', sa.Column('brawl', sa.Integer(), server_default='0', nullable=True))
    op.add_column('htr_characters', sa.Column('craft', sa.Integer(), server_default='0', nullable=True))
    op.add_column('htr_characters', sa.Column('drive_skill', sa.Integer(), server_default='0', nullable=True))
    op.add_column('htr_characters', sa.Column('firearms', sa.Integer(), server_default='0', nullable=True))
    op.add_column('htr_characters', sa.Column('larceny', sa.Integer(), server_default='0', nullable=True))
    op.add_column('htr_characters', sa.Column('melee', sa.Integer(), server_default='0', nullable=True))
    op.add_column('htr_characters', sa.Column('stealth', sa.Integer(), server_default='0', nullable=True))
    op.add_column('htr_characters', sa.Column('survival', sa.Integer(), server_default='0', nullable=True))
    op.add_column('htr_characters', sa.Column('animal_ken', sa.Integer(), server_default='0', nullable=True))
    op.add_column('htr_characters', sa.Column('etiquette', sa.Integer(), server_default='0', nullable=True))
    op.add_column('htr_characters', sa.Column('insight', sa.Integer(), server_default='0', nullable=True))
    op.add_column('htr_characters', sa.Column('intimidation', sa.Integer(), server_default='0', nullable=True))
    op.add_column('htr_characters', sa.Column('leadership', sa.Integer(), server_default='0', nullable=True))
    op.add_column('htr_characters', sa.Column('performance', sa.Integer(), server_default='0', nullable=True))
    op.add_column('htr_characters', sa.Column('persuasion', sa.Integer(), server_default='0', nullable=True))
    op.add_column('htr_characters', sa.Column('streetwise', sa.Integer(), server_default='0', nullable=True))
    op.add_column('htr_characters', sa.Column('subterfuge', sa.Integer(), server_default='0', nullable=True))
    op.add_column('htr_characters', sa.Column('academics', sa.Integer(), server_default='0', nullable=True))
    op.add_column('htr_characters', sa.Column('awareness', sa.Integer(), server_default='0', nullable=True))
    op.add_column('htr_characters', sa.Column('finance', sa.Integer(), server_default='0', nullable=True))
    op.add_column('htr_characters', sa.Column('investigation', sa.Integer(), server_default='0', nullable=True))
    op.add_column('htr_characters', sa.Column('medicine', sa.Integer(), server_default='0', nullable=True))
    op.add_column('htr_characters', sa.Column('occult', sa.Integer(), server_default='0', nullable=True))
    op.add_column('htr_characters', sa.Column('politics', sa.Integer(), server_default='0', nullable=True))
    op.add_column('htr_characters', sa.Column('science', sa.Integer(), server_default='0', nullable=True))
    op.add_column('htr_characters', sa.Column('technology', sa.Integer(), server_default='0', nullable=True))

    # Skill Specialties
    op.add_column('htr_characters', sa.Column('skill_specialties', sa.Text(), nullable=True))

    # Trackers
    op.add_column('htr_characters', sa.Column('danger_current', sa.Integer(), server_default='0', nullable=True))
    op.add_column('htr_characters', sa.Column('desperation_current', sa.Integer(), server_default='0', nullable=True))
    op.add_column('htr_characters', sa.Column('health_max', sa.Integer(), server_default='6', nullable=True))
    op.add_column('htr_characters', sa.Column('health_superficial', sa.Integer(), server_default='0', nullable=True))
    op.add_column('htr_characters', sa.Column('health_aggravated', sa.Integer(), server_default='0', nullable=True))
    op.add_column('htr_characters', sa.Column('willpower_max', sa.Integer(), server_default='5', nullable=True))
    op.add_column('htr_characters', sa.Column('willpower_superficial', sa.Integer(), server_default='0', nullable=True))
    op.add_column('htr_characters', sa.Column('willpower_aggravated', sa.Integer(), server_default='0', nullable=True))
    op.add_column('htr_characters', sa.Column('in_despair', sa.Boolean(), server_default='false', nullable=True))

    # Edges & Perks
    op.add_column('htr_characters', sa.Column('edge_config', sa.String(length=10), server_default='1e2p', nullable=True))
    op.add_column('htr_characters', sa.Column('edge_1_id', sa.String(length=50), nullable=True))
    op.add_column('htr_characters', sa.Column('edge_2_id', sa.String(length=50), nullable=True))
    op.add_column('htr_characters', sa.Column('selected_perks', sa.Text(), nullable=True))

    # Equipment
    op.add_column('htr_characters', sa.Column('equipment_weapon', sa.String(length=100), nullable=True))
    op.add_column('htr_characters', sa.Column('equipment_weapon_damage', sa.Integer(), server_default='0', nullable=True))
    op.add_column('htr_characters', sa.Column('equipment_armor_rating', sa.Integer(), server_default='0', nullable=True))
    op.add_column('htr_characters', sa.Column('equipment_notes', sa.Text(), nullable=True))

    # Experience Tracking
    op.add_column('htr_characters', sa.Column('exp_total', sa.Integer(), server_default='0', nullable=True))
    op.add_column('htr_characters', sa.Column('exp_available', sa.Integer(), server_default='0', nullable=True))
    op.add_column('htr_characters', sa.Column('exp_spent', sa.Integer(), server_default='0', nullable=True))

    # History & Notes
    op.add_column('htr_characters', sa.Column('first_encounter', sa.Text(), nullable=True))
    op.add_column('htr_characters', sa.Column('history', sa.Text(), nullable=True))
    op.add_column('htr_characters', sa.Column('notes', sa.Text(), nullable=True))
    op.add_column('htr_characters', sa.Column('current_mission', sa.Text(), nullable=True))

    # Character Creation
    op.add_column('htr_characters', sa.Column('creation_complete', sa.Boolean(), server_default='false', nullable=True))


def downgrade() -> None:
    # Drop HTR relationship tables
    op.drop_index(op.f('ix_htr_xp_log_entries_id'), table_name='htr_xp_log_entries')
    op.drop_table('htr_xp_log_entries')

    op.drop_index(op.f('ix_htr_flaws_id'), table_name='htr_flaws')
    op.drop_table('htr_flaws')

    op.drop_index(op.f('ix_htr_advantages_id'), table_name='htr_advantages')
    op.drop_table('htr_advantages')

    op.drop_index(op.f('ix_htr_touchstones_id'), table_name='htr_touchstones')
    op.drop_table('htr_touchstones')

    # Remove all added columns from htr_characters (in reverse order)
    op.drop_column('htr_characters', 'creation_complete')
    op.drop_column('htr_characters', 'current_mission')
    op.drop_column('htr_characters', 'notes')
    op.drop_column('htr_characters', 'history')
    op.drop_column('htr_characters', 'first_encounter')
    op.drop_column('htr_characters', 'exp_spent')
    op.drop_column('htr_characters', 'exp_available')
    op.drop_column('htr_characters', 'exp_total')
    op.drop_column('htr_characters', 'equipment_notes')
    op.drop_column('htr_characters', 'equipment_armor_rating')
    op.drop_column('htr_characters', 'equipment_weapon_damage')
    op.drop_column('htr_characters', 'equipment_weapon')
    op.drop_column('htr_characters', 'selected_perks')
    op.drop_column('htr_characters', 'edge_2_id')
    op.drop_column('htr_characters', 'edge_1_id')
    op.drop_column('htr_characters', 'edge_config')
    op.drop_column('htr_characters', 'in_despair')
    op.drop_column('htr_characters', 'willpower_aggravated')
    op.drop_column('htr_characters', 'willpower_superficial')
    op.drop_column('htr_characters', 'willpower_max')
    op.drop_column('htr_characters', 'health_aggravated')
    op.drop_column('htr_characters', 'health_superficial')
    op.drop_column('htr_characters', 'health_max')
    op.drop_column('htr_characters', 'desperation_current')
    op.drop_column('htr_characters', 'danger_current')
    op.drop_column('htr_characters', 'skill_specialties')
    op.drop_column('htr_characters', 'technology')
    op.drop_column('htr_characters', 'science')
    op.drop_column('htr_characters', 'politics')
    op.drop_column('htr_characters', 'occult')
    op.drop_column('htr_characters', 'medicine')
    op.drop_column('htr_characters', 'investigation')
    op.drop_column('htr_characters', 'finance')
    op.drop_column('htr_characters', 'awareness')
    op.drop_column('htr_characters', 'academics')
    op.drop_column('htr_characters', 'subterfuge')
    op.drop_column('htr_characters', 'streetwise')
    op.drop_column('htr_characters', 'persuasion')
    op.drop_column('htr_characters', 'performance')
    op.drop_column('htr_characters', 'leadership')
    op.drop_column('htr_characters', 'intimidation')
    op.drop_column('htr_characters', 'insight')
    op.drop_column('htr_characters', 'etiquette')
    op.drop_column('htr_characters', 'animal_ken')
    op.drop_column('htr_characters', 'survival')
    op.drop_column('htr_characters', 'stealth')
    op.drop_column('htr_characters', 'melee')
    op.drop_column('htr_characters', 'larceny')
    op.drop_column('htr_characters', 'firearms')
    op.drop_column('htr_characters', 'drive_skill')
    op.drop_column('htr_characters', 'craft')
    op.drop_column('htr_characters', 'brawl')
    op.drop_column('htr_characters', 'athletics')
    op.drop_column('htr_characters', 'resolve')
    op.drop_column('htr_characters', 'wits')
    op.drop_column('htr_characters', 'intelligence')
    op.drop_column('htr_characters', 'composure')
    op.drop_column('htr_characters', 'manipulation')
    op.drop_column('htr_characters', 'charisma')
    op.drop_column('htr_characters', 'stamina')
    op.drop_column('htr_characters', 'dexterity')
    op.drop_column('htr_characters', 'strength')
    op.drop_column('htr_characters', 'alias')
    op.drop_column('htr_characters', 'portrait_hobby_4')
    op.drop_column('htr_characters', 'portrait_hobby_3')
    op.drop_column('htr_characters', 'portrait_hobby_2')
    op.drop_column('htr_characters', 'portrait_hobby_1')
    op.drop_column('htr_characters', 'portrait_body')
    op.drop_column('htr_characters', 'portrait_face')
    op.drop_column('htr_characters', 'origin')
    op.drop_column('htr_characters', 'pronouns')
    op.drop_column('htr_characters', 'blood_type')
    op.drop_column('htr_characters', 'age')
    op.drop_column('htr_characters', 'drive')
    op.drop_column('htr_characters', 'chronicle')
    op.drop_column('htr_characters', 'cell')

    # Restore old placeholder columns
    op.add_column('htr_characters', sa.Column('character_data', sa.Text(), nullable=True))
    op.add_column('htr_characters', sa.Column('portrait_url', sa.String(length=500), nullable=True))
    op.add_column('htr_characters', sa.Column('concept', sa.String(length=200), nullable=True))
