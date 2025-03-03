"""
Unit tests for the base repository implementation.

This module contains tests for the base repository class, ensuring that
CRUD operations, error handling, and transaction management work correctly.
"""
import pytest
from datetime import datetime, timezone
from sqlalchemy import create_engine, select, inspect
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, NoResultFound

from abidance.database.models import Base, Trade
from abidance.database.repository.base import BaseRepository
from abidance.trading.order import OrderSide


class TestBaseRepository:
    """Test suite for the base repository implementation."""

    @pytest.fixture
    def engine(self):
        """Create an in-memory SQLite database for testing."""
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        return engine

    @pytest.fixture
    def session(self, engine):
        """Create a new database session for a test."""
        with Session(engine) as session:
            yield session

    @pytest.fixture
    def repository(self, session):
        """Create a base repository instance for testing."""
        return BaseRepository(session, Trade)

    def test_add_entity(self, repository):
        """
        Feature: Adding entities to the repository
        
        Scenario: Adding a new entity to the repository
          Given a repository instance
          When a new entity is added
          Then the entity should be persisted in the database
          And the entity should have an ID assigned
        """
        # Create a new trade
        trade = Trade(
            symbol="BTC/USD",
            side=OrderSide.BUY,
            amount=1.0,
            price=50000.0,
            timestamp=datetime.now(timezone.utc)
        )
        
        # Add the trade to the repository
        result = repository.add(trade)
        
        # Verify the trade was added successfully
        assert result.id is not None
        assert result.symbol == "BTC/USD"
        assert result.side == OrderSide.BUY
        
        # Verify the trade exists in the database
        db_trade = repository._session.get(Trade, result.id)
        assert db_trade is not None
        assert db_trade.symbol == "BTC/USD"

    def test_get_by_id(self, repository, session):
        """
        Feature: Retrieving entities by ID
        
        Scenario: Retrieving an existing entity by ID
          Given a repository with an existing entity
          When the entity is retrieved by its ID
          Then the correct entity should be returned
        """
        # Create and add a trade
        trade = Trade(
            symbol="ETH/USD",
            side=OrderSide.SELL,
            amount=2.0,
            price=3000.0,
            timestamp=datetime.now(timezone.utc)
        )
        session.add(trade)
        session.commit()
        
        # Get the trade by ID
        result = repository.get_by_id(trade.id)
        
        # Verify the correct trade was retrieved
        assert result is not None
        assert result.id == trade.id
        assert result.symbol == "ETH/USD"
        assert result.side == OrderSide.SELL
        assert result.amount == 2.0

    def test_get_by_id_nonexistent(self, repository):
        """
        Feature: Retrieving nonexistent entities
        
        Scenario: Attempting to retrieve a nonexistent entity
          Given a repository
          When a nonexistent entity ID is provided
          Then None should be returned
        """
        # Try to get a nonexistent trade
        result = repository.get_by_id(999)
        
        # Verify None was returned
        assert result is None

    def test_list_entities(self, repository, session):
        """
        Feature: Listing all entities
        
        Scenario: Listing all entities in the repository
          Given a repository with multiple entities
          When all entities are listed
          Then all entities should be returned in a list
        """
        # Create and add multiple trades
        trades = [
            Trade(
                symbol="BTC/USD",
                side=OrderSide.BUY,
                amount=1.0,
                price=50000.0,
                timestamp=datetime.now(timezone.utc)
            ),
            Trade(
                symbol="ETH/USD",
                side=OrderSide.SELL,
                amount=2.0,
                price=3000.0,
                timestamp=datetime.now(timezone.utc)
            ),
            Trade(
                symbol="LTC/USD",
                side=OrderSide.BUY,
                amount=10.0,
                price=200.0,
                timestamp=datetime.now(timezone.utc)
            )
        ]
        session.add_all(trades)
        session.commit()
        
        # List all trades
        results = repository.list()
        
        # Verify all trades were returned
        assert len(results) == 3
        symbols = [t.symbol for t in results]
        assert "BTC/USD" in symbols
        assert "ETH/USD" in symbols
        assert "LTC/USD" in symbols

    def test_delete_entity(self, repository, session):
        """
        Feature: Deleting entities
        
        Scenario: Deleting an existing entity
          Given a repository with an existing entity
          When the entity is deleted by its ID
          Then the entity should be removed from the database
          And the delete operation should return True
        """
        # Create and add a trade
        trade = Trade(
            symbol="XRP/USD",
            side=OrderSide.SELL,
            amount=100.0,
            price=1.0,
            timestamp=datetime.now(timezone.utc)
        )
        session.add(trade)
        session.commit()
        
        # Delete the trade
        result = repository.delete(trade.id)
        
        # Verify the trade was deleted
        assert result is True
        assert repository.get_by_id(trade.id) is None

    def test_delete_nonexistent_entity(self, repository):
        """
        Feature: Deleting nonexistent entities
        
        Scenario: Attempting to delete a nonexistent entity
          Given a repository
          When a nonexistent entity ID is provided for deletion
          Then the delete operation should return False
        """
        # Try to delete a nonexistent trade
        result = repository.delete(999)
        
        # Verify the operation returned False
        assert result is False

    def test_transaction_rollback(self, repository, session):
        """
        Feature: Transaction rollback
        
        Scenario: Rolling back a transaction on error
          Given a repository with an existing entity
          When an operation fails and causes a rollback
          Then no changes should be persisted to the database
        """
        # Create and add an initial trade
        initial_trade = Trade(
            symbol="BTC/USD",
            side=OrderSide.BUY,
            amount=1.0,
            price=50000.0,
            timestamp=datetime.now(timezone.utc)
        )
        session.add(initial_trade)
        session.commit()
        
        # Count initial trades
        initial_count = len(repository.list())
        
        # Create a custom repository method that will cause a transaction to fail
        def transaction_with_error():
            with repository.transaction() as tx_session:
                # Add a valid trade
                trade = Trade(
                    symbol="ETH/USD",
                    side=OrderSide.SELL,
                    amount=2.0,
                    price=3000.0,
                    timestamp=datetime.now(timezone.utc)
                )
                tx_session.add(trade)
                
                # Force an error
                raise ValueError("Forced error to test rollback")
        
        # Execute the transaction and expect it to fail
        try:
            transaction_with_error()
        except ValueError:
            # Expected exception
            pass
        
        # Verify no trades were added (rollback occurred)
        final_count = len(repository.list())
        assert final_count == initial_count 