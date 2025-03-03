"""
Database migration manager.

This module provides utility functions for managing database migrations,
including creating new migrations, upgrading, and downgrading the database.
"""
import sys
import argparse
import subprocess
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))


def get_alembic_config_path():
    """Get the path to the alembic.ini file."""
    return Path(__file__).parent.parent / "alembic.ini"


def get_migrations_dir():
    """Get the path to the migrations directory."""
    return Path(__file__).parent


def create_migration(message):
    """Create a new migration with the given message."""
    alembic_ini_path = get_alembic_config_path()
    migrations_dir = get_migrations_dir()

    result = subprocess.run(
        [
            "alembic",
            "-c",
            str(alembic_ini_path),
            "revision",
            "--autogenerate",
            "-m",
            message
        ],
        cwd=migrations_dir.parent,
        capture_output=True,
        text=True,
        check=False
    )

    if result.returncode != 0:
        print(f"Error creating migration: {result.stderr}")
        return False

    print(f"Migration created successfully: {result.stdout}")
    return True


def upgrade_database(revision="head"):
    """Upgrade the database to the specified revision."""
    alembic_ini_path = get_alembic_config_path()
    migrations_dir = get_migrations_dir()

    result = subprocess.run(
        [
            "alembic",
            "-c",
            str(alembic_ini_path),
            "upgrade",
            revision
        ],
        cwd=migrations_dir.parent,
        capture_output=True,
        text=True,
        check=False
    )

    if result.returncode != 0:
        print(f"Error upgrading database: {result.stderr}")
        return False

    print(f"Database upgraded successfully: {result.stdout}")
    return True


def downgrade_database(revision="-1"):
    """Downgrade the database by the specified number of revisions."""
    alembic_ini_path = get_alembic_config_path()
    migrations_dir = get_migrations_dir()

    result = subprocess.run(
        [
            "alembic",
            "-c",
            str(alembic_ini_path),
            "downgrade",
            revision
        ],
        cwd=migrations_dir.parent,
        capture_output=True,
        text=True,
        check=False
    )

    if result.returncode != 0:
        print(f"Error downgrading database: {result.stderr}")
        return False

    print(f"Database downgraded successfully: {result.stdout}")
    return True


def show_history():
    """Show the migration history."""
    alembic_ini_path = get_alembic_config_path()
    migrations_dir = get_migrations_dir()

    result = subprocess.run(
        [
            "alembic",
            "-c",
            str(alembic_ini_path),
            "history",
            "--verbose"
        ],
        cwd=migrations_dir.parent,
        capture_output=True,
        text=True,
        check=False
    )

    if result.returncode != 0:
        print(f"Error showing history: {result.stderr}")
        return False

    print(f"Migration history:\n{result.stdout}")
    return True


def show_current():
    """Show the current migration version."""
    alembic_ini_path = get_alembic_config_path()
    migrations_dir = get_migrations_dir()

    result = subprocess.run(
        [
            "alembic",
            "-c",
            str(alembic_ini_path),
            "current"
        ],
        cwd=migrations_dir.parent,
        capture_output=True,
        text=True,
        check=False
    )

    if result.returncode != 0:
        print(f"Error showing current version: {result.stderr}")
        return False

    print(f"Current migration version:\n{result.stdout}")
    return True


def main():
    """Main entry point for the migration manager."""
    parser = argparse.ArgumentParser(description="Database migration manager")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Create migration command
    create_parser = subparsers.add_parser("create", help="Create a new migration")
    create_parser.add_argument("message", help="Migration message")

    # Upgrade command
    upgrade_parser = subparsers.add_parser("upgrade", help="Upgrade the database")
    upgrade_parser.add_argument("--revision", default="head", help="Revision to upgrade to")

    # Downgrade command
    downgrade_parser = subparsers.add_parser("downgrade", help="Downgrade the database")
    downgrade_parser.add_argument(
        "--revision",
        default="-1",
        help="Revisions to downgrade"
    )

    # History command
    subparsers.add_parser("history", help="Show migration history")

    # Current command
    subparsers.add_parser("current", help="Show current migration version")

    args = parser.parse_args()

    if args.command == "create":
        create_migration(args.message)
    elif args.command == "upgrade":
        upgrade_database(args.revision)
    elif args.command == "downgrade":
        downgrade_database(args.revision)
    elif args.command == "history":
        show_history()
    elif args.command == "current":
        show_current()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
