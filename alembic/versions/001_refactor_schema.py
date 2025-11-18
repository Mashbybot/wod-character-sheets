"""Refactor character schema - add separate tables for touchstones, backgrounds, XP log, and user preferences

Revision ID: 001_refactor_schema
Revises: 
Create Date: 2025-01-16

This migration:
1. Creates new tables (touchstones, backgrounds, xp_log_entries, user_preferences)
2. Migrates existing data from old column format to new tables
3. Removes old redundant columns from vtm_characters
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = '001_refactor_schema'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create user_preferences table
    op.create_table(
        'user_preferences',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('column_widths_above', sa.String(length=50), server_default='30,35,35', nullable=True),
        sa.Column('column_widths_below', sa.String(length=50), server_default='33,33,34', nullable=True),
        sa.Column('theme', sa.String(length=20), server_default='dark', nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
    op.create_index(op.f('ix_user_preferences_id'), 'user_preferences', ['id'], unique=False)
    
    # Create touchstones table
    op.create_table(
        'touchstones',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('character_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('conviction', sa.Text(), nullable=True),
        sa.Column('display_order', sa.Integer(), server_default='0', nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['character_id'], ['vtm_characters.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_touchstones_id'), 'touchstones', ['id'], unique=False)
    
    # Create backgrounds table
    op.create_table(
        'backgrounds',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('character_id', sa.Integer(), nullable=False),
        sa.Column('type', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('dots', sa.Integer(), server_default='0', nullable=True),
        sa.Column('display_order', sa.Integer(), server_default='0', nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['character_id'], ['vtm_characters.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_backgrounds_id'), 'backgrounds', ['id'], unique=False)
    
    # Create xp_log_entries table
    op.create_table(
        'xp_log_entries',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('character_id', sa.Integer(), nullable=False),
        sa.Column('date', sa.String(length=50), nullable=False),
        sa.Column('type', sa.String(length=10), nullable=False),
        sa.Column('amount', sa.Integer(), nullable=False),
        sa.Column('reason', sa.String(length=200), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['character_id'], ['vtm_characters.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_xp_log_entries_id'), 'xp_log_entries', ['id'], unique=False)
    
    # Add new columns to vtm_characters if they don't exist
    # (This handles migration from existing schema)
    conn = op.get_bind()
    
    # Check if columns exist before adding
    columns_to_add = [
        ('sire', sa.String(length=100)),
        ('bane_custom', sa.String(length=200)),
        ('compulsion_custom', sa.String(length=200)),
        ('humanity_stained', sa.Integer(), {'server_default': '0'}),
        ('alias', sa.String(length=100)),
        ('portrait_face', sa.String(length=500)),
        ('portrait_body', sa.String(length=500)),
        ('portrait_hobby_1', sa.String(length=500)),
        ('portrait_hobby_2', sa.String(length=500)),
        ('portrait_hobby_3', sa.String(length=500)),
        ('portrait_hobby_4', sa.String(length=500)),
        ('chronicle_tenet_1', sa.String(length=200)),
        ('chronicle_tenet_2', sa.String(length=200)),
        ('chronicle_tenet_3', sa.String(length=200)),
        ('chronicle_tenet_4', sa.String(length=200)),
        ('chronicle_tenet_5', sa.String(length=200)),
    ]
    
    for column_info in columns_to_add:
        column_name = column_info[0]
        column_type = column_info[1]
        kwargs = column_info[2] if len(column_info) > 2 else {}
        
        # Check if column exists
        inspector = sa.inspect(conn)
        columns = [col['name'] for col in inspector.get_columns('vtm_characters')]
        
        if column_name not in columns:
            op.add_column('vtm_characters', sa.Column(column_name, column_type, **kwargs))
    
    # Migrate data from old columns to new tables
    # This is done via SQL to handle existing data
    
    # Migrate touchstones (if old columns exist)
    if 'touchstone_1_name' in columns:
        conn.execute(text("""
            INSERT INTO touchstones (character_id, name, description, conviction, display_order)
            SELECT id, touchstone_1_name, touchstone_1_description, touchstone_1_conviction, 0
            FROM vtm_characters
            WHERE touchstone_1_name IS NOT NULL AND touchstone_1_name != ''
        """))
        
        conn.execute(text("""
            INSERT INTO touchstones (character_id, name, description, conviction, display_order)
            SELECT id, touchstone_2_name, touchstone_2_description, touchstone_2_conviction, 1
            FROM vtm_characters
            WHERE touchstone_2_name IS NOT NULL AND touchstone_2_name != ''
        """))
        
        conn.execute(text("""
            INSERT INTO touchstones (character_id, name, description, conviction, display_order)
            SELECT id, touchstone_3_name, touchstone_3_description, touchstone_3_conviction, 2
            FROM vtm_characters
            WHERE touchstone_3_name IS NOT NULL AND touchstone_3_name != ''
        """))
        
        conn.execute(text("""
            INSERT INTO touchstones (character_id, name, description, conviction, display_order)
            SELECT id, touchstone_4_name, touchstone_4_description, touchstone_4_conviction, 3
            FROM vtm_characters
            WHERE touchstone_4_name IS NOT NULL AND touchstone_4_name != ''
        """))
        
        conn.execute(text("""
            INSERT INTO touchstones (character_id, name, description, conviction, display_order)
            SELECT id, touchstone_5_name, touchstone_5_description, touchstone_5_conviction, 4
            FROM vtm_characters
            WHERE touchstone_5_name IS NOT NULL AND touchstone_5_name != ''
        """))
    
    # Migrate backgrounds (if old columns exist)
    if 'background_type_1' in columns:
        for i in range(1, 7):
            conn.execute(text(f"""
                INSERT INTO backgrounds (character_id, type, description, dots, display_order)
                SELECT id, background_type_{i}, background_description_{i}, 0, {i-1}
                FROM vtm_characters
                WHERE background_type_{i} IS NOT NULL AND background_type_{i} != ''
            """))
    
    # Note: XP log migration would require parsing JSON if xp_log column exists
    # For now, we'll skip this as the old schema didn't have xp_log
    
    # Drop old columns after migration
    columns_to_drop = [
        'touchstone_1_name', 'touchstone_1_description', 'touchstone_1_conviction',
        'touchstone_2_name', 'touchstone_2_description', 'touchstone_2_conviction',
        'touchstone_3_name', 'touchstone_3_description', 'touchstone_3_conviction',
        'touchstone_4_name', 'touchstone_4_description', 'touchstone_4_conviction',
        'touchstone_5_name', 'touchstone_5_description', 'touchstone_5_conviction',
        'background_type_1', 'background_description_1',
        'background_type_2', 'background_description_2',
        'background_type_3', 'background_description_3',
        'background_type_4', 'background_description_4',
        'background_type_5', 'background_description_5',
        'background_type_6', 'background_description_6',
        'portrait_url',  # Replaced by portrait_face, portrait_body, etc.
        'chronicle_tenets',  # Replaced by chronicle_tenet_1-5
        'bane_severity',  # Calculated from blood_potency, not stored
        'blood_surge', 'mend_amount', 'power_bonus', 'rouse_reroll', 
        'feeding_penalty', 'bane_severity_bp',  # All calculated, not stored
    ]
    
    for column_name in columns_to_drop:
        if column_name in columns:
            try:
                op.drop_column('vtm_characters', column_name)
            except:
                pass  # Column doesn't exist, continue


def downgrade() -> None:
    """Downgrade not supported for this migration - too complex to reverse data migration"""
    raise NotImplementedError("Downgrade not supported for schema refactoring. Please restore from backup if needed.")
