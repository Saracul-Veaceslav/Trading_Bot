# Database Migration System

This directory contains the database migration system for the Abidance trading bot. The migration system is built using Alembic, a lightweight database migration tool for SQLAlchemy.

## Overview

Database migrations allow for versioned, incremental changes to the database schema. This is essential for:

1. Tracking schema changes over time
2. Applying changes consistently across different environments
3. Rolling back changes if needed
4. Collaborating with other developers

## Directory Structure

- `env.py`: Alembic environment configuration
- `script.py.mako`: Template for migration scripts
- `versions/`: Directory containing individual migration versions
- `create_initial_migration.py`: Script to create the initial migration
- `migration_manager.py`: Utility script for managing migrations

## Usage

### Creating a New Migration

When you make changes to the database models in `abidance/database/models.py`, you need to create a new migration to apply those changes to the database.

```bash
python -m abidance.database.migrations.migration_manager create "Description of changes"
```

This will create a new migration file in the `versions/` directory.

### Upgrading the Database

To apply all pending migrations to the database:

```bash
python -m abidance.database.migrations.migration_manager upgrade
```

To upgrade to a specific revision:

```bash
python -m abidance.database.migrations.migration_manager upgrade --revision <revision_id>
```

### Downgrading the Database

To revert the most recent migration:

```bash
python -m abidance.database.migrations.migration_manager downgrade
```

To downgrade multiple revisions:

```bash
python -m abidance.database.migrations.migration_manager downgrade --revision -3
```

To downgrade to a specific revision:

```bash
python -m abidance.database.migrations.migration_manager downgrade --revision <revision_id>
```

### Viewing Migration History

To view the migration history:

```bash
python -m abidance.database.migrations.migration_manager history
```

### Checking Current Migration Version

To check the current migration version:

```bash
python -m abidance.database.migrations.migration_manager current
```

## Best Practices

1. **Always create migrations for schema changes**: Never modify the database schema directly.
2. **Test migrations before applying to production**: Run migrations in a test environment first.
3. **Keep migrations small and focused**: Each migration should make a small, focused change.
4. **Include both upgrade and downgrade paths**: Always implement both the upgrade and downgrade functions.
5. **Use meaningful migration messages**: The migration message should clearly describe the changes.
6. **Review migration files before committing**: Ensure the generated migration does what you expect.

## Troubleshooting

### Migration Conflicts

If you encounter conflicts between migrations (e.g., two developers created migrations for the same model), you may need to merge the migrations manually. This typically involves:

1. Identifying the conflicting changes
2. Creating a new migration that combines the changes
3. Adjusting the dependencies between migrations

### Failed Migrations

If a migration fails, you can:

1. Fix the issue in the migration file
2. Run the migration again
3. If necessary, downgrade to a previous version and then upgrade again

### Database Out of Sync

If the database schema is out of sync with the migrations, you may need to:

1. Create a new migration that brings the schema in line with the current state
2. Mark the migration as applied without running it (`alembic stamp <revision>`)

## Further Reading

- [Alembic Documentation](https://alembic.sqlalchemy.org/en/latest/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/en/14/) 