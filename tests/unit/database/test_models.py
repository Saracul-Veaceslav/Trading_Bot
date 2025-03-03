"""
Unit tests for database models.

This module contains tests for the database models, ensuring that they
correctly represent the domain entities and maintain data integrity.
"""
import pytest
from datetime import datetime, timezone
from sqlalchemy import create_engine, select, inspect
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from abidance.database.models import Base, Trade, Strategy, OHLCV
from abidance.trading.order import OrderSide, OrderType


class TestDatabaseModels:
    """Test suite for database models."""

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

    def test_trade_model_creation(self, session):
        """
        Feature: Trade model creation
        
        Scenario: Creating a valid trade record
          Given a database session
          When a new Trade record is created with valid data
          Then the record should be successfully saved to the database
          And the retrieved record should match the original data
        """
        # Create a new trade
        trade = Trade(
            symbol="BTC/USD",
            side=OrderSide.BUY,
            amount=1.0,
            price=50000.0,
            timestamp=datetime.now(timezone.utc)
        )
        
        # Add to session and commit
        session.add(trade)
        session.commit()
        
        # Query the trade
        result = session.execute(select(Trade).filter_by(id=trade.id)).scalar_one()
        
        # Verify the trade was saved correctly
        assert result.symbol == "BTC/USD"
        assert result.side == OrderSide.BUY
        assert result.amount == 1.0
        assert result.price == 50000.0
        assert result.timestamp is not None
        assert result.strategy_id is None
        
    def test_strategy_model_creation(self, session):
        """
        Feature: Strategy model creation
        
        Scenario: Creating a valid strategy record
          Given a database session
          When a new Strategy record is created with valid data
          Then the record should be successfully saved to the database
          And the retrieved record should match the original data
        """
        # Create a new strategy
        strategy = Strategy(
            name="SMA Crossover",
            parameters={"short_window": 10, "long_window": 50}
        )
        
        # Add to session and commit
        session.add(strategy)
        session.commit()
        
        # Query the strategy
        result = session.execute(select(Strategy).filter_by(id=strategy.id)).scalar_one()
        
        # Verify the strategy was saved correctly
        assert result.name == "SMA Crossover"
        assert result.parameters == {"short_window": 10, "long_window": 50}
        assert result.created_at is not None
        
    def test_ohlcv_model_creation(self, session):
        """
        Feature: OHLCV model creation
        
        Scenario: Creating a valid OHLCV record
          Given a database session
          When a new OHLCV record is created with valid data
          Then the record should be successfully saved to the database
          And the retrieved record should match the original data
        """
        # Create a new OHLCV record
        ohlcv = OHLCV(
            symbol="BTC/USD",
            timestamp=datetime.now(timezone.utc),
            open=50000.0,
            high=51000.0,
            low=49000.0,
            close=50500.0,
            volume=100.0
        )
        
        # Add to session and commit
        session.add(ohlcv)
        session.commit()
        
        # Query the OHLCV record
        result = session.execute(select(OHLCV).filter_by(id=ohlcv.id)).scalar_one()
        
        # Verify the OHLCV record was saved correctly
        assert result.symbol == "BTC/USD"
        assert result.timestamp is not None
        assert result.open == 50000.0
        assert result.high == 51000.0
        assert result.low == 49000.0
        assert result.close == 50500.0
        assert result.volume == 100.0
        
    def test_trade_strategy_relationship(self, session):
        """
        Feature: Trade-Strategy relationship
        
        Scenario: Creating trades associated with a strategy
          Given a database session
          When a Strategy is created with associated Trades
          Then the relationship between Strategy and Trades should be maintained
          And the trades should reference the correct strategy
        """
        # Create a new strategy
        strategy = Strategy(
            name="RSI Strategy",
            parameters={"oversold": 30, "overbought": 70}
        )
        session.add(strategy)
        session.flush()  # Flush to get the strategy ID
        
        # Create trades associated with the strategy
        trade1 = Trade(
            symbol="BTC/USD",
            side=OrderSide.BUY,
            amount=1.0,
            price=50000.0,
            timestamp=datetime.now(timezone.utc),
            strategy_id=strategy.id
        )
        
        trade2 = Trade(
            symbol="ETH/USD",
            side=OrderSide.SELL,
            amount=10.0,
            price=3000.0,
            timestamp=datetime.now(timezone.utc),
            strategy_id=strategy.id
        )
        
        session.add_all([trade1, trade2])
        session.commit()
        
        # Query the strategy with its trades
        result = session.execute(select(Strategy).filter_by(id=strategy.id)).scalar_one()
        
        # Verify the relationship
        assert len(result.trades) == 2
        assert any(t.symbol == "BTC/USD" and t.side == OrderSide.BUY for t in result.trades)
        assert any(t.symbol == "ETH/USD" and t.side == OrderSide.SELL for t in result.trades)
        
    def test_unique_ohlcv_constraint(self, session):
        """
        Feature: OHLCV unique constraint
        
        Scenario: Attempting to create duplicate OHLCV records
          Given a database session with an existing OHLCV record
          When a new OHLCV record with the same symbol and timestamp is created
          Then an integrity error should be raised
        """
        # Create a timestamp for testing
        timestamp = datetime.now(timezone.utc)
        
        # Create first OHLCV record
        ohlcv1 = OHLCV(
            symbol="BTC/USD",
            timestamp=timestamp,
            open=50000.0,
            high=51000.0,
            low=49000.0,
            close=50500.0,
            volume=100.0
        )
        session.add(ohlcv1)
        session.commit()
        
        # Create second OHLCV record with same symbol and timestamp
        ohlcv2 = OHLCV(
            symbol="BTC/USD",
            timestamp=timestamp,
            open=50100.0,
            high=51100.0,
            low=49100.0,
            close=50600.0,
            volume=110.0
        )
        session.add(ohlcv2)
        
        # Verify that an integrity error is raised
        with pytest.raises(IntegrityError):
            session.commit()
            
    def test_model_representations(self):
        """
        Feature: Model string representations
        
        Scenario: Creating model instances and checking their string representations
          Given model instances
          When the __repr__ method is called
          Then the string representation should contain key identifying information
        """
        # Create instances
        trade = Trade(
            symbol="BTC/USD",
            side=OrderSide.BUY,
            amount=1.0,
            price=50000.0,
            timestamp=datetime.now(timezone.utc)
        )
        
        strategy = Strategy(
            name="SMA Crossover",
            parameters={"short_window": 10, "long_window": 50}
        )
        
        ohlcv = OHLCV(
            symbol="BTC/USD",
            timestamp=datetime.now(timezone.utc),
            open=50000.0,
            high=51000.0,
            low=49000.0,
            close=50500.0,
            volume=100.0
        )
        
        # Check representations
        assert "Trade" in repr(trade)
        assert "BTC/USD" in repr(trade)
        
        assert "Strategy" in repr(strategy)
        assert "SMA Crossover" in repr(strategy)
        
        assert "OHLCV" in repr(ohlcv)
        assert "BTC/USD" in repr(ohlcv)
        
    def test_index_creation(self, engine):
        """
        Feature: Database index creation
        
        Scenario: Checking if indexes are properly created
          Given a database with models
          When inspecting the database schema
          Then the expected indexes should exist on the tables
        """
        inspector = inspect(engine)
        
        # Check OHLCV indexes
        ohlcv_indexes = inspector.get_indexes("ohlcv")
        assert any(idx["name"] == "idx_symbol_timestamp" for idx in ohlcv_indexes)
        
        # Check Trade indexes
        trade_indexes = inspector.get_indexes("trades")
        assert any(idx["column_names"] == ["symbol"] for idx in trade_indexes)
        assert any(idx["column_names"] == ["timestamp"] for idx in trade_indexes) 