"""Add desire and ambition columns to htr_characters

Revision ID: 008_add_desire_ambition_to_htr
Revises: 007_add_ambition_desire_heights
Create Date: 2025-12-12

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '008_add_desire_ambition_to_htr'
down_revision = '007_add_ambition_desire_heights'
branch_labels = None
depends_on = None


def upgrade():
    # Add desire column
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name = 'htr_characters'
                AND column_name = 'desire'
            ) THEN
                ALTER TABLE htr_characters ADD COLUMN desire TEXT;
            END IF;
        END $$;
    """)

    # Add ambition column
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name = 'htr_characters'
                AND column_name = 'ambition'
            ) THEN
                ALTER TABLE htr_characters ADD COLUMN ambition TEXT;
            END IF;
        END $$;
    """)


def downgrade():
    # Remove ambition column
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name = 'htr_characters'
                AND column_name = 'ambition'
            ) THEN
                ALTER TABLE htr_characters DROP COLUMN ambition;
            END IF;
        END $$;
    """)

    # Remove desire column
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name = 'htr_characters'
                AND column_name = 'desire'
            ) THEN
                ALTER TABLE htr_characters DROP COLUMN desire;
            END IF;
        END $$;
    """)
