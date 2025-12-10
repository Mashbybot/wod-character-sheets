"""Add disciplines table

Revision ID: 004
Revises: 003
Create Date: 2025-12-10

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade():
    # Create disciplines table
    op.create_table(
        'disciplines',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('character_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('level', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('powers', sa.Text(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('display_order', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['character_id'], ['vtm_characters.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_disciplines_id'), 'disciplines', ['id'], unique=False)

    # Migrate existing discipline data from individual fields to disciplines table
    # This will copy discipline_1 through discipline_5 from vtm_characters to the new disciplines table
    op.execute("""
        INSERT INTO disciplines (character_id, name, level, powers, description, display_order)
        SELECT
            id as character_id,
            discipline_1_name as name,
            COALESCE(discipline_1_level, 0) as level,
            discipline_1_powers as powers,
            discipline_1_description as description,
            0 as display_order
        FROM vtm_characters
        WHERE discipline_1_name IS NOT NULL AND discipline_1_name != ''
    """)

    op.execute("""
        INSERT INTO disciplines (character_id, name, level, powers, description, display_order)
        SELECT
            id as character_id,
            discipline_2_name as name,
            COALESCE(discipline_2_level, 0) as level,
            discipline_2_powers as powers,
            discipline_2_description as description,
            1 as display_order
        FROM vtm_characters
        WHERE discipline_2_name IS NOT NULL AND discipline_2_name != ''
    """)

    op.execute("""
        INSERT INTO disciplines (character_id, name, level, powers, description, display_order)
        SELECT
            id as character_id,
            discipline_3_name as name,
            COALESCE(discipline_3_level, 0) as level,
            discipline_3_powers as powers,
            discipline_3_description as description,
            2 as display_order
        FROM vtm_characters
        WHERE discipline_3_name IS NOT NULL AND discipline_3_name != ''
    """)

    op.execute("""
        INSERT INTO disciplines (character_id, name, level, powers, description, display_order)
        SELECT
            id as character_id,
            discipline_4_name as name,
            COALESCE(discipline_4_level, 0) as level,
            discipline_4_powers as powers,
            discipline_4_description as description,
            3 as display_order
        FROM vtm_characters
        WHERE discipline_4_name IS NOT NULL AND discipline_4_name != ''
    """)

    op.execute("""
        INSERT INTO disciplines (character_id, name, level, powers, description, display_order)
        SELECT
            id as character_id,
            discipline_5_name as name,
            COALESCE(discipline_5_level, 0) as level,
            discipline_5_powers as powers,
            discipline_5_description as description,
            4 as display_order
        FROM vtm_characters
        WHERE discipline_5_name IS NOT NULL AND discipline_5_name != ''
    """)

    # Note: We keep the old discipline columns for now in case we need to rollback
    # They can be removed in a future migration after confirming everything works


def downgrade():
    # Drop disciplines table
    op.drop_index(op.f('ix_disciplines_id'), table_name='disciplines')
    op.drop_table('disciplines')

    # Note: Old discipline columns remain in vtm_characters table
