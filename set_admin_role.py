#!/usr/bin/env python3
"""
Script to set a user's role to admin by Discord username or Discord ID
Usage: python set_admin_role.py
"""

import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add app directory to path
sys.path.insert(0, os.path.dirname(__file__))

from app.models_new import User

def get_database_url():
    """Get database URL from environment"""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("Error: DATABASE_URL environment variable not set")
        sys.exit(1)

    # Handle Railway PostgreSQL URL format
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)

    return database_url

def list_users(session):
    """List all users in the database"""
    users = session.query(User).all()
    if not users:
        print("\nNo users found in database.")
        return

    print("\n=== Current Users ===")
    print(f"{'ID':<6} {'Discord ID':<20} {'Username':<30} {'Role':<15}")
    print("-" * 75)
    for user in users:
        print(f"{user.id:<6} {user.discord_id:<20} {user.discord_username:<30} {user.role:<15}")
    print()

def set_admin_role(session, identifier):
    """Set a user's role to admin by Discord ID or username"""
    # Try to find user by Discord ID first
    user = session.query(User).filter(User.discord_id == identifier).first()

    # If not found, try by username (case-insensitive)
    if not user:
        user = session.query(User).filter(User.discord_username.ilike(identifier)).first()

    # If still not found, try by database ID
    if not user and identifier.isdigit():
        user = session.query(User).filter(User.id == int(identifier)).first()

    if not user:
        print(f"Error: User '{identifier}' not found")
        return False

    # Update role
    old_role = user.role
    user.role = "admin"
    session.commit()

    print(f"\n✓ Successfully updated user '{user.discord_username}'")
    print(f"  Discord ID: {user.discord_id}")
    print(f"  Role changed: {old_role} → admin")
    return True

def main():
    # Get database connection
    database_url = get_database_url()
    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # List all users
        list_users(session)

        # Prompt for user to update
        print("Enter the Discord ID, username, or database ID of the user to make admin")
        print("(or press Enter to exit): ", end="")
        identifier = input().strip()

        if not identifier:
            print("Exiting...")
            return

        # Set admin role
        if set_admin_role(session, identifier):
            print("\nUser role updated successfully!")
            print("The user will have unlimited character sheet creation on their next login.")

    except KeyboardInterrupt:
        print("\n\nOperation cancelled.")
    except Exception as e:
        print(f"\nError: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    main()
