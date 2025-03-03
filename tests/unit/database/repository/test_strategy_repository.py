"""
Unit tests for the strategy repository implementation.

This module contains tests for the strategy repository class, ensuring that
strategy-specific queries and filtering operations work correctly.
"""
import pytest
from datetime import datetime, timezone, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from abidance.database.models import Base, Strategy, Trade
from abidance.database.repository.strategy import StrategyRepository
from abidance.trading.order import OrderSide


class TestStrategyRepository:
    """Test suite for the strategy repository implementation."""

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
        """Create a strategy repository instance for testing."""
        return StrategyRepository(session)

    @pytest.fixture
    def sample_strategies(self, session):
        """Create sample strategies for testing."""
        # Create timestamps for testing
        now = datetime.now(timezone.utc)
        yesterday = now - timedelta(days=1)
        
        # Create sample strategies
        strategies = [
            Strategy(
                name="SMA Crossover",
                parameters={"short_window": 10, "long_window": 50},
                created_at=now
            ),
            Strategy(
                name="RSI Strategy",
                parameters={"oversold": 30, "overbought": 70},
                created_at=yesterday
            ),
            Strategy(
                name="MACD Strategy",
                parameters={"fast_period": 12, "slow_period": 26, "signal_period": 9},
                created_at=yesterday - timedelta(days=1)
            )
        ]
        session.add_all(strategies)
        session.commit()
        
        # Store the timestamps for later use
        self.now = now
        self.yesterday = yesterday
        
        # Add some trades to the first strategy
        trades = [
            Trade(
                symbol="BTC/USD",
                side=OrderSide.BUY,
                amount=1.0,
                price=50000.0,
                timestamp=now,
                strategy_id=strategies[0].id
            ),
            Trade(
                symbol="ETH/USD",
                side=OrderSide.SELL,
                amount=10.0,
                price=3000.0,
                timestamp=yesterday,
                strategy_id=strategies[0].id
            )
        ]
        session.add_all(trades)
        session.commit()
        
        return strategies

    def test_get_by_name(self, repository, sample_strategies):
        """
        Feature: Finding strategies by name
        
        Scenario: Retrieving a strategy by its name
          Given a repository with multiple strategies
          When a strategy is searched for by name
          Then the correct strategy should be returned
        """
        # Get strategy by name
        strategy = repository.get_by_name("SMA Crossover")
        
        # Verify the correct strategy was returned
        assert strategy is not None
        assert strategy.name == "SMA Crossover"
        assert strategy.parameters == {"short_window": 10, "long_window": 50}
        
        # Try to get a nonexistent strategy
        nonexistent = repository.get_by_name("Nonexistent Strategy")
        
        # Verify None was returned
        assert nonexistent is None

    def test_get_strategies_by_date_range(self, repository, sample_strategies):
        """
        Feature: Filtering strategies by creation date
        
        Scenario: Retrieving strategies created within a date range
          Given a repository with strategies created on different dates
          When strategies are filtered by a date range
          Then only strategies created within that range should be returned
        """
        # Use the stored timestamps from the fixture
        now = self.now
        yesterday = self.yesterday
        two_days_ago = yesterday - timedelta(days=1)
        three_days_ago = two_days_ago - timedelta(days=1)
        
        # Get strategies from the last day
        recent_strategies = repository.get_strategies_by_date_range(yesterday - timedelta(minutes=1), now + timedelta(minutes=1))
        
        # Verify only recent strategies were returned
        assert len(recent_strategies) == 2
        assert any(strategy.name == "SMA Crossover" for strategy in recent_strategies)
        assert any(strategy.name == "RSI Strategy" for strategy in recent_strategies)
        
        # Get strategies from three days ago to yesterday
        older_strategies = repository.get_strategies_by_date_range(three_days_ago, yesterday + timedelta(minutes=1))
        
        # Verify only older strategies were returned
        assert len(older_strategies) == 2
        assert any(strategy.name == "RSI Strategy" for strategy in older_strategies)
        assert any(strategy.name == "MACD Strategy" for strategy in older_strategies)

    def test_get_strategies_with_trades(self, repository, sample_strategies):
        """
        Feature: Finding strategies with trades
        
        Scenario: Retrieving strategies that have associated trades
          Given a repository with strategies, some with trades
          When strategies with trades are requested
          Then only strategies with trades should be returned
        """
        # Get strategies with trades
        strategies_with_trades = repository.get_strategies_with_trades()
        
        # Verify only strategies with trades were returned
        assert len(strategies_with_trades) == 1
        assert strategies_with_trades[0].name == "SMA Crossover"
        
        # Add a trade to another strategy
        trade = Trade(
            symbol="LTC/USD",
            side=OrderSide.BUY,
            amount=5.0,
            price=200.0,
            timestamp=datetime.now(timezone.utc),
            strategy_id=sample_strategies[1].id
        )
        repository._session.add(trade)
        repository._session.commit()
        
        # Get strategies with trades again
        updated_strategies_with_trades = repository.get_strategies_with_trades()
        
        # Verify both strategies with trades are returned
        assert len(updated_strategies_with_trades) == 2
        strategy_names = [s.name for s in updated_strategies_with_trades]
        assert "SMA Crossover" in strategy_names
        assert "RSI Strategy" in strategy_names

    def test_get_strategies_by_parameter(self, repository, sample_strategies):
        """
        Feature: Finding strategies by parameter
        
        Scenario: Retrieving strategies that have a specific parameter
          Given a repository with strategies with different parameters
          When strategies are filtered by a parameter name
          Then only strategies with that parameter should be returned
        """
        # Get strategies with the 'oversold' parameter
        oversold_strategies = repository.get_strategies_by_parameter("oversold")
        
        # Verify only strategies with the parameter were returned
        assert len(oversold_strategies) == 1
        assert oversold_strategies[0].name == "RSI Strategy"
        
        # Get strategies with the 'short_window' parameter
        short_window_strategies = repository.get_strategies_by_parameter("short_window")
        
        # Verify only strategies with the parameter were returned
        assert len(short_window_strategies) == 1
        assert short_window_strategies[0].name == "SMA Crossover"
        
        # Get strategies with a nonexistent parameter
        nonexistent_param_strategies = repository.get_strategies_by_parameter("nonexistent")
        
        # Verify no strategies were returned
        assert len(nonexistent_param_strategies) == 0 