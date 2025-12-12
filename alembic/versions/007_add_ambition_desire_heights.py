"""Add ambition and desire height columns to user_preferences

Revision ID: 007_add_ambition_desire_heights
Revises: 006_fix_textarea_heights
Create Date: 2025-12-12

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '007_add_ambition_desire_heights'
down_revision = '006_fix_textarea_heights'
branch_labels = None
depends_on = None


def upgrade():
    # Add ambition_height column
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name = 'user_preferences'
                AND column_name = 'ambition_height'
            ) THEN
                ALTER TABLE user_preferences ADD COLUMN ambition_height INTEGER;
            END IF;
        END $$;
    """)

    # Add desire_height column
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name = 'user_preferences'
                AND column_name = 'desire_height'
            ) THEN
                ALTER TABLE user_preferences ADD COLUMN desire_height INTEGER;
            END IF;
        END $$;
    """)


def downgrade():
    # Remove desire_height column
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name = 'user_preferences'
                AND column_name = 'desire_height'
            ) THEN
                ALTER TABLE user_preferences DROP COLUMN desire_height;
            END IF;
        END $$;
    """)

    # Remove ambition_height column
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name = 'user_preferences'
                AND column_name = 'ambition_height'
            ) THEN
                ALTER TABLE user_preferences DROP COLUMN ambition_height;
            END IF;
        END $$;
    """)
