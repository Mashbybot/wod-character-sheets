"""Fix textarea height columns in user_preferences

Revision ID: 006_fix_textarea_heights
Revises: 005_add_textarea_heights
Create Date: 2025-12-12

This migration ensures the textarea height columns exist in the user_preferences table.
It uses IF NOT EXISTS to safely add columns even if migration 005 partially failed.
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '006_fix_textarea_heights'
down_revision = '005_add_textarea_heights'
branch_labels = None
depends_on = None


def upgrade():
    # Use raw SQL with IF NOT EXISTS to safely add columns
    # This will work even if the columns were partially added

    # Check and add history_in_life_height
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name = 'user_preferences'
                AND column_name = 'history_in_life_height'
            ) THEN
                ALTER TABLE user_preferences ADD COLUMN history_in_life_height INTEGER;
            END IF;
        END $$;
    """)

    # Check and add after_death_height
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name = 'user_preferences'
                AND column_name = 'after_death_height'
            ) THEN
                ALTER TABLE user_preferences ADD COLUMN after_death_height INTEGER;
            END IF;
        END $$;
    """)

    # Check and add notes_height
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name = 'user_preferences'
                AND column_name = 'notes_height'
            ) THEN
                ALTER TABLE user_preferences ADD COLUMN notes_height INTEGER;
            END IF;
        END $$;
    """)


def downgrade():
    # Only drop columns if they exist
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name = 'user_preferences'
                AND column_name = 'notes_height'
            ) THEN
                ALTER TABLE user_preferences DROP COLUMN notes_height;
            END IF;
        END $$;
    """)

    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name = 'user_preferences'
                AND column_name = 'after_death_height'
            ) THEN
                ALTER TABLE user_preferences DROP COLUMN after_death_height;
            END IF;
        END $$;
    """)

    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name = 'user_preferences'
                AND column_name = 'history_in_life_height'
            ) THEN
                ALTER TABLE user_preferences DROP COLUMN history_in_life_height;
            END IF;
        END $$;
    """)
