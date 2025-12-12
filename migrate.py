#!/usr/bin/env python3
"""
Smart migration script that handles database/Alembic state mismatches.
Specifically handles the case where tables exist but Alembic tracking is missing.
"""
import sys
import subprocess
from sqlalchemy import create_engine, inspect, text
from app.database import DATABASE_URL

def check_table_exists(engine, table_name):
    """Check if a table exists in the database"""
    inspector = inspect(engine)
    return table_name in inspector.get_table_names()

def get_alembic_version(engine):
    """Get current Alembic version from database, returns None if table doesn't exist"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version_num FROM alembic_version")).fetchone()
            return result[0] if result else None
    except Exception:
        # Table doesn't exist or other error
        return None

def run_command(cmd):
    """Run a shell command and return success/failure"""
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    return result.returncode == 0

def main():
    print("🔍 Checking database migration state...")

    # Create engine to check database state
    engine = create_engine(DATABASE_URL)

    # Check if tables exist
    tables_exist = check_table_exists(engine, 'user_preferences')
    alembic_version = get_alembic_version(engine)

    print(f"   Tables exist: {tables_exist}")
    print(f"   Alembic version: {alembic_version or 'Not tracked'}")

    if tables_exist and not alembic_version:
        # Database has tables but Alembic doesn't know about them
        print("⚠️  Database has tables but Alembic tracking is missing!")
        print("   Stamping database to migration 001 (where tables were created)...")
        if run_command("python3 -m alembic stamp 001_refactor_schema"):
            print("✅ Successfully stamped database to 001_refactor_schema")
        else:
            print("❌ Failed to stamp database")
            return 1

    # Now run migrations normally
    print("📦 Running migrations...")
    if run_command("python3 -m alembic upgrade head"):
        print("✅ Migrations completed successfully")
        return 0
    else:
        print("❌ Migration failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
