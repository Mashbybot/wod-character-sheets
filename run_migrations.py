#!/usr/bin/env python3
"""
Simple script to run Alembic migrations in Railway environment.
Usage: railway run python run_migrations.py
"""
import sys
from alembic.config import Config
from alembic import command

def main():
    try:
        print("Starting database migrations...")
        alembic_cfg = Config("alembic.ini")
        command.upgrade(alembic_cfg, "head")
        print("✅ Migrations completed successfully!")
        return 0
    except Exception as e:
        print(f"❌ Migration failed: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
