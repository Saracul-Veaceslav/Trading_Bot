"""
Unit tests for the trade repository implementation.

This module contains tests for the trade repository class, ensuring that
trade-specific queries and filtering operations work correctly.
"""
import pytest
from datetime import datetime, timezone, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from abidance.database.models import Base, Trade, Strategy
from abidance.database.repository.trade import TradeRepository
from abidance.trading.order import OrderSide


class TestTradeRepository:
    """Test suite for the trade repository implementation."""

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
        """Create a trade repository instance for testing."""
        return TradeRepository(session)

    @pytest.fixture
    def sample_trades(self, session):
        """Create sample trades for testing."""
        # Create a strategy
        strategy = Strategy(
            name="Test Strategy",
            parameters={"param1": "value1"}
        )
        session.add(strategy)
        session.flush()
        
        # Create timestamps for testing
        now = datetime.now(timezone.utc)
        yesterday = now - timedelta(days=1)
        two_days_ago = now - timedelta(days=2)
        
        # Create sample trades
        trades = [
            Trade(
                symbol="BTC/USD",
                side=OrderSide.BUY,
                amount=1.0,
                price=50000.0,
                timestamp=now,
                strategy_id=strategy.id
            ),
            Trade(
                symbol="ETH/USD",
                side=OrderSide.SELL,
                amount=10.0,
                price=3000.0,
                timestamp=yesterday,
                strategy_id=strategy.id
            ),
            Trade(
                symbol="BTC/USD",
                side=OrderSide.SELL,
                amount=0.5,
                price=51000.0,
                timestamp=two_days_ago,
                strategy_id=strategy.id
            )
        ]
        session.add_all(trades)
        session.commit()
        
        # Store the timestamps for later use
        self.now = now
        self.yesterday = yesterday
        self.two_days_ago = two_days_ago
        
        return trades

    def test_get_trades_by_symbol(self, repository, sample_trades):
        """
        Feature: Filtering trades by symbol
        
        Scenario: Retrieving trades for a specific symbol
          Given a repository with trades for different symbols
          When trades are filtered by a specific symbol
          Then only trades for that symbol should be returned
        """
        # Get trades for BTC/USD
        btc_trades = repository.get_trades_by_symbol("BTC/USD")
        
        # Verify only BTC/USD trades were returned
        assert len(btc_trades) == 2
        assert all(trade.symbol == "BTC/USD" for trade in btc_trades)
        
        # Get trades for ETH/USD
        eth_trades = repository.get_trades_by_symbol("ETH/USD")
        
        # Verify only ETH/USD trades were returned
        assert len(eth_trades) == 1
        assert eth_trades[0].symbol == "ETH/USD"
        
        # Get trades for a symbol with no trades
        ltc_trades = repository.get_trades_by_symbol("LTC/USD")
        
        # Verify no trades were returned
        assert len(ltc_trades) == 0

    def test_get_trades_by_date_range(self, repository, sample_trades):
        """
        Feature: Filtering trades by date range
        
        Scenario: Retrieving trades within a specific date range
          Given a repository with trades from different dates
          When trades are filtered by a date range
          Then only trades within that range should be returned
        """
        # Use the stored timestamps from the fixture
        now = self.now
        yesterday = self.yesterday
        two_days_ago = self.two_days_ago
        three_days_ago = two_days_ago - timedelta(days=1)
        
        # Get trades from the last day
        recent_trades = repository.get_trades_by_date_range(yesterday - timedelta(minutes=1), now + timedelta(minutes=1))
        
        # Verify only recent trades were returned
        assert len(recent_trades) == 2
        symbols = [t.symbol for t in recent_trades]
        assert "BTC/USD" in symbols
        assert "ETH/USD" in symbols
        
        # Get trades from two days ago to yesterday
        older_trades = repository.get_trades_by_date_range(two_days_ago - timedelta(minutes=1), yesterday + timedelta(minutes=1))
        
        # Verify only older trades were returned
        assert len(older_trades) == 2
        symbols = [t.symbol for t in older_trades]
        assert "BTC/USD" in symbols
        assert "ETH/USD" in symbols
        
        # Get trades from a range with no trades
        no_trades = repository.get_trades_by_date_range(three_days_ago, two_days_ago - timedelta(hours=1))
        
        # Verify no trades were returned
        assert len(no_trades) == 0

    def test_get_trades_by_strategy(self, repository, sample_trades, session):
        """
        Feature: Filtering trades by strategy
        
        Scenario: Retrieving trades for a specific strategy
          Given a repository with trades for different strategies
          When trades are filtered by a strategy ID
          Then only trades for that strategy should be returned
        """
        # Get the strategy ID from the first trade
        strategy_id = sample_trades[0].strategy_id
        
        # Create a new strategy with no trades
        new_strategy = Strategy(
            name="New Strategy",
            parameters={"param1": "value2"}
        )
        session.add(new_strategy)
        session.commit()
        
        # Get trades for the original strategy
        strategy_trades = repository.get_trades_by_strategy(strategy_id)
        
        # Verify all trades for the strategy were returned
        assert len(strategy_trades) == 3
        assert all(trade.strategy_id == strategy_id for trade in strategy_trades)
        
        # Get trades for the new strategy
        new_strategy_trades = repository.get_trades_by_strategy(new_strategy.id)
        
        # Verify no trades were returned
        assert len(new_strategy_trades) == 0

    def test_get_latest_trade_by_symbol(self, repository, sample_trades):
        """
        Feature: Retrieving the latest trade for a symbol
        
        Scenario: Getting the most recent trade for a specific symbol
          Given a repository with trades for a symbol from different times
          When the latest trade is requested for that symbol
          Then the most recent trade should be returned
        """
        # Get the latest BTC/USD trade
        latest_btc_trade = repository.get_latest_trade_by_symbol("BTC/USD")
        
        # Verify the latest trade was returned
        assert latest_btc_trade is not None
        assert latest_btc_trade.symbol == "BTC/USD"
        assert latest_btc_trade.side == OrderSide.BUY
        assert latest_btc_trade.price == 50000.0
        
        # Get the latest trade for a symbol with no trades
        latest_ltc_trade = repository.get_latest_trade_by_symbol("LTC/USD")
        
        # Verify no trade was returned
        assert latest_ltc_trade is None 