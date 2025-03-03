"""
Unit tests for database migrations.

This module contains tests for the database migration system, ensuring that
migrations can be applied and reverted correctly.
"""
import os
import tempfile
import subprocess
import shutil
from pathlib import Path

import pytest
from sqlalchemy import create_engine, inspect
# pylint: disable=unused-import
from sqlalchemy import text
from sqlalchemy.orm import Session

# pylint: disable=unused-import
from abidance.database.models import Base


class TestDatabaseMigrations:
    """Test suite for database migrations."""

    @pytest.fixture
    def temp_db_path(self):
        """Create a temporary database file for testing migrations."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as temp_file:
            temp_db_path = temp_file.name
            yield temp_db_path
            # Clean up the temporary file after the test
            if os.path.exists(temp_db_path):
                os.unlink(temp_db_path)

    @pytest.fixture
    def alembic_config_path(self):
        """Get the path to the alembic.ini file."""
        return Path(__file__).parent.parent.parent.parent / 'abidance' / 'database' / 'alembic.ini'

    @pytest.fixture
    def migrations_dir(self):
        """Get the path to the migrations directory."""
        return Path(__file__).parent.parent.parent.parent / 'abidance' / 'database' / 'migrations'

    def test_migration_initialization(self, temp_db_path, alembic_config_path, migrations_dir):
        """Test that migrations can be initialized and applied to a new database."""
        # Create a database URL for the temporary database
        db_url = f"sqlite:///{temp_db_path}"

        # Create a new engine connected to the temporary database
        engine = create_engine(db_url)

        # Check that the database is empty
        inspector = inspect(engine)
        assert not inspector.get_table_names(), "Database should be empty initially"

        # Run the migration command
        env = os.environ.copy()
        env["PYTHONPATH"] = str(Path(__file__).parent.parent.parent.parent)
        env["DATABASE_URL"] = db_url

        # Create a custom alembic.ini with the temporary database URL
        temp_alembic_ini = os.path.join(os.path.dirname(temp_db_path), "alembic.ini")
        
        # Copy the alembic.ini file to the temporary directory
        shutil.copy(alembic_config_path, temp_alembic_ini)
        
        # Modify the database URL in the copied file
        with open(temp_alembic_ini, "r", encoding="utf-8") as src_file:
            content = src_file.read()
            # Replace the database URL
            content = content.replace(
                "sqlalchemy.url = sqlite:///abidance.db",
                f"sqlalchemy.url = {db_url}"
            )

        with open(temp_alembic_ini, "w", encoding="utf-8") as dest_file:
            dest_file.write(content)

        # Run alembic upgrade head
        result = subprocess.run(
            ["alembic", "-c", temp_alembic_ini, "upgrade", "head"],
            cwd=migrations_dir.parent,
            env=env,
            capture_output=True,
            text=True,
            check=False
        )

        # Check that the command was successful
        assert result.returncode == 0, f"Migration failed: {result.stderr}"

        # Check that the tables were created
        inspector = inspect(engine)
        tables = inspector.get_table_names()

        # Verify that our model tables exist
        assert "trades" in tables, "Trades table should be created by migrations"
        assert "strategies" in tables, "Strategies table should be created by migrations"
        assert "ohlcv" in tables, "OHLCV table should be created by migrations"

        # Verify that alembic_version table exists
        assert "alembic_version" in tables, "Alembic version table should be created"

        # Check that we can downgrade
        result = subprocess.run(
            ["alembic", "-c", temp_alembic_ini, "downgrade", "base"],
            cwd=migrations_dir.parent,
            env=env,
            capture_output=True,
            text=True,
            check=False
        )

        # Check that the command was successful
        assert result.returncode == 0, f"Downgrade failed: {result.stderr}"

        # Check that only the alembic_version table remains
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        assert len(tables) <= 1, "All tables except alembic_version should be removed"

        # Clean up the temporary alembic.ini
        os.unlink(temp_alembic_ini)

    def test_migration_idempotency(self, temp_db_path, alembic_config_path, migrations_dir):
        """Test that migrations are idempotent and can be applied multiple times."""
        # Create a database URL for the temporary database
        db_url = f"sqlite:///{temp_db_path}"

        # Create a new engine connected to the temporary database
        engine = create_engine(db_url)

        # Create a custom alembic.ini with the temporary database URL
        temp_alembic_ini = os.path.join(os.path.dirname(temp_db_path), "alembic.ini")
        
        # Copy the alembic.ini file to the temporary directory
        shutil.copy(alembic_config_path, temp_alembic_ini)
        
        # Modify the database URL in the copied file
        with open(temp_alembic_ini, "r", encoding="utf-8") as src_file:
            content = src_file.read()
            # Replace the database URL
            content = content.replace(
                "sqlalchemy.url = sqlite:///abidance.db",
                f"sqlalchemy.url = {db_url}"
            )

        with open(temp_alembic_ini, "w", encoding="utf-8") as dest_file:
            dest_file.write(content)

        env = os.environ.copy()
        env["PYTHONPATH"] = str(Path(__file__).parent.parent.parent.parent)
        env["DATABASE_URL"] = db_url

        # Run alembic upgrade head
        result1 = subprocess.run(
            ["alembic", "-c", temp_alembic_ini, "upgrade", "head"],
            cwd=migrations_dir.parent,
            env=env,
            capture_output=True,
            text=True,
            check=False
        )

        # Check that the command was successful
        assert result1.returncode == 0, f"First migration failed: {result1.stderr}"

        # Run alembic upgrade head again
        result2 = subprocess.run(
            ["alembic", "-c", temp_alembic_ini, "upgrade", "head"],
            cwd=migrations_dir.parent,
            env=env,
            capture_output=True,
            text=True,
            check=False
        )

        # Check that the command was successful
        assert result2.returncode == 0, f"Second migration failed: {result2.stderr}"

        # Check that the database structure is the same
        inspector = inspect(engine)
        tables = inspector.get_table_names()

        # Verify that our model tables exist
        assert "trades" in tables, "Trades table should be created by migrations"
        assert "strategies" in tables, "Strategies table should be created by migrations"
        assert "ohlcv" in tables, "OHLCV table should be created by migrations"

        # Clean up the temporary alembic.ini
        os.unlink(temp_alembic_ini)
