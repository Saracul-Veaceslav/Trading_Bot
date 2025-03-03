"""
Base repository implementation.

This module provides a generic base repository class that can be used
to implement the repository pattern for any SQLAlchemy model.
"""
from typing import Generic, TypeVar, List, Optional, Type
from contextlib import contextmanager
from sqlalchemy.orm import Session
from sqlalchemy import select, delete

T = TypeVar('T')


class BaseRepository(Generic[T]):
    """Base repository implementation."""

    def __init__(self, session: Session, model: Type[T]):
        """
        Initialize the repository with a database session and model class.

        Args:
            session: SQLAlchemy session
            model: SQLAlchemy model class
        """
        self._session = session
        self._model = model

    @contextmanager
    def transaction(self):
        """
        Context manager for database transactions.

        This ensures that operations are committed on success and
        rolled back on error.

        Yields:
            The session for use within the transaction
        """
        # Get the current transaction or create a new one
        try:
            # Yield the session for use in the with block
            yield self._session
            # If we get here, commit the transaction
            self._session.commit()
        except Exception:
            # If an exception occurs, roll back the transaction
            self._session.rollback()
            # Re-raise the exception
            raise

    def add(self, entity: T) -> T:
        """
        Add a new entity to the database.

        Args:
            entity: Entity to add

        Returns:
            The added entity with its ID populated
        """
        with self.transaction() as session:
            session.add(entity)
        return entity

    def get_by_id(self, entity_id: int) -> Optional[T]:
        """
        Get entity by ID.

        Args:
            entity_id: Entity ID

        Returns:
            The entity if found, None otherwise
        """
        return self._session.get(self._model, entity_id)

    def list(self) -> List[T]:
        """
        List all entities.

        Returns:
            List of all entities
        """
        return self._session.execute(
            select(self._model)
        ).scalars().all()

    def delete(self, entity_id: int) -> bool:
        """
        Delete entity by ID.

        Args:
            entity_id: Entity ID

        Returns:
            True if the entity was deleted, False if it didn't exist
        """
        with self.transaction() as session:
            result = session.execute(
                delete(self._model).where(self._model.id == entity_id)
            )
        return result.rowcount > 0
