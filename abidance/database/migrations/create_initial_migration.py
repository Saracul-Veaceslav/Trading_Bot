"""
Script to generate the initial database migration.

This script creates the initial migration version for the database schema.
It should be run once to initialize the migration history.
"""
import sys
import subprocess
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the models to ensure they are registered with SQLAlchemy
# pylint: disable=unused-import,wrong-import-position
from abidance.database.models import Base


def create_initial_migration():
    """Create the initial database migration."""
    # Get the path to the alembic.ini file
    alembic_ini_path = Path(__file__).parent.parent / "alembic.ini"

    # Get the path to the migrations directory
    migrations_dir = Path(__file__).parent

    # Run alembic revision --autogenerate
    result = subprocess.run(
        [
            "alembic",
            "-c",
            str(alembic_ini_path),
            "revision",
            "--autogenerate",
            "-m",
            "Initial migration"
        ],
        cwd=migrations_dir.parent,
        capture_output=True,
        text=True,
        check=False
    )

    if result.returncode != 0:
        print(f"Error creating initial migration: {result.stderr}")
        sys.exit(1)

    print(f"Initial migration created successfully: {result.stdout}")

    # Check if any migration files were created
    versions_dir = migrations_dir / "versions"
    migration_files = list(versions_dir.glob("*.py"))

    if not migration_files:
        print("No migration files were created. Check the alembic configuration.")
        sys.exit(1)

    print(f"Created migration file: {migration_files[-1].name}")


if __name__ == "__main__":
    create_initial_migration()
