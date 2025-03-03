"""
Tests for the mock exchange implementation.

This module contains tests for the MockExchange class and related utilities.
"""
import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from abidance.testing.mock_exchange import MockExchange
from abidance.testing.mock_data import (
    generate_random_ohlcv,
    generate_trending_ohlcv,
    generate_pattern_ohlcv,
    _parse_timeframe
)
from abidance.trading.order import OrderSide, OrderType
from abidance.core.domain import Position


class TestMockExchange:
    """Tests for the MockExchange class."""
    
    @pytest.fixture
    def mock_exchange(self):
        """Create a mock exchange instance."""
        return MockExchange(initial_balance=10000.0)
    
    @pytest.fixture
    def sample_ohlcv_data(self):
        """Create sample OHLCV data."""
        start_date = datetime(2023, 1, 1)
        return generate_random_ohlcv(
            symbol="BTC/USDT",
            start_date=start_date,
            num_periods=100,
            timeframe="1h",
            base_price=50000.0,
            volatility=0.01,
            trend=0.0001,
            seed=42
        )
    
    def test_initialization(self, mock_exchange):
        """Test that the mock exchange initializes correctly."""
        assert mock_exchange.balance == 10000.0
        assert mock_exchange.positions == {}
        assert mock_exchange.orders == []
        assert mock_exchange._ohlcv_data == {}
        assert mock_exchange._current_price == {}
        
        # Check protocol attributes
        assert mock_exchange.exchange_id == "mock"
        assert mock_exchange.testnet is True
        assert mock_exchange.api_key is None
        assert mock_exchange.api_secret is None
    
    def test_set_ohlcv_data(self, mock_exchange, sample_ohlcv_data):
        """Test setting OHLCV data."""
        symbol = "BTC/USDT"
        mock_exchange.set_ohlcv_data(symbol, sample_ohlcv_data)
        
        # Check that data was stored
        assert symbol in mock_exchange._ohlcv_data
        assert len(mock_exchange._ohlcv_data[symbol]) == len(sample_ohlcv_data)
        
        # Check that current price was set to last close
        assert symbol in mock_exchange._current_price
        assert mock_exchange._current_price[symbol] == sample_ohlcv_data['close'].iloc[-1]
    
    def test_fetch_ohlcv(self, mock_exchange, sample_ohlcv_data):
        """Test fetching OHLCV data."""
        symbol = "BTC/USDT"
        mock_exchange.set_ohlcv_data(symbol, sample_ohlcv_data)
        
        # Test fetching all data
        result = mock_exchange.fetch_ohlcv(symbol, "1h")
        assert len(result) == len(sample_ohlcv_data)
        
        # Test with limit
        limit = 10
        result = mock_exchange.fetch_ohlcv(symbol, "1h", limit=limit)
        assert len(result) == limit
        
        # Test with since
        since = sample_ohlcv_data['timestamp'].iloc[50]
        result = mock_exchange.fetch_ohlcv(symbol, "1h", since=since)
        assert len(result) <= len(sample_ohlcv_data) - 50
        assert result['timestamp'].min() >= since
        
        # Test with invalid symbol
        with pytest.raises(ValueError):
            mock_exchange.fetch_ohlcv("INVALID/USDT", "1h")
    
    def test_create_market_order_buy(self, mock_exchange, sample_ohlcv_data):
        """Test creating a market buy order."""
        symbol = "BTC/USDT"
        mock_exchange.set_ohlcv_data(symbol, sample_ohlcv_data)
        
        initial_balance = mock_exchange.balance
        price = mock_exchange._current_price[symbol]
        amount = 0.1
        
        # Create buy order
        order = mock_exchange.create_market_order(symbol, OrderSide.BUY, amount)
        
        # Check order properties
        assert order['symbol'] == symbol
        assert order['side'] == OrderSide.BUY
        assert order['type'] == OrderType.MARKET
        assert order['amount'] == amount
        assert order['price'] == price
        assert order['status'] == 'closed'
        
        # Check that order was added to orders list
        assert len(mock_exchange.orders) == 1
        assert mock_exchange.orders[0] == order
        
        # Check that position was created
        assert symbol in mock_exchange.positions
        assert mock_exchange.positions[symbol].symbol == symbol
        assert mock_exchange.positions[symbol].side == OrderSide.BUY
        assert mock_exchange.positions[symbol].entry_price == price
        assert mock_exchange.positions[symbol].size == amount
        
        # Check that balance was updated
        assert mock_exchange.balance == initial_balance - (price * amount)
    
    def test_create_market_order_sell(self, mock_exchange, sample_ohlcv_data):
        """Test creating a market sell order."""
        symbol = "BTC/USDT"
        mock_exchange.set_ohlcv_data(symbol, sample_ohlcv_data)
        
        # First create a buy position
        price = mock_exchange._current_price[symbol]
        buy_amount = 0.2
        mock_exchange.create_market_order(symbol, OrderSide.BUY, buy_amount)
        
        initial_balance = mock_exchange.balance
        sell_amount = 0.1
        
        # Create sell order for part of the position
        order = mock_exchange.create_market_order(symbol, OrderSide.SELL, sell_amount)
        
        # Check order properties
        assert order['symbol'] == symbol
        assert order['side'] == OrderSide.SELL
        assert order['amount'] == sell_amount
        
        # Check that position was reduced
        assert symbol in mock_exchange.positions
        assert mock_exchange.positions[symbol].size == buy_amount - sell_amount
        
        # Check that balance was updated
        assert mock_exchange.balance == initial_balance + (price * sell_amount)
        
        # Sell the rest of the position
        mock_exchange.create_market_order(symbol, OrderSide.SELL, buy_amount - sell_amount)
        
        # Check that position was closed
        assert symbol not in mock_exchange.positions
    
    def test_sell_without_position(self, mock_exchange, sample_ohlcv_data):
        """Test that selling without a position raises an error."""
        symbol = "BTC/USDT"
        mock_exchange.set_ohlcv_data(symbol, sample_ohlcv_data)
        
        with pytest.raises(ValueError, match="Cannot sell without an existing position"):
            mock_exchange.create_market_order(symbol, OrderSide.SELL, 0.1)
    
    def test_get_markets(self, mock_exchange, sample_ohlcv_data):
        """Test getting available markets."""
        symbol1 = "BTC/USDT"
        symbol2 = "ETH/USDT"
        
        # Initially no markets
        assert mock_exchange.get_markets() == []
        
        # Add data for two symbols
        mock_exchange.set_ohlcv_data(symbol1, sample_ohlcv_data)
        mock_exchange.set_ohlcv_data(symbol2, sample_ohlcv_data)
        
        # Check markets
        markets = mock_exchange.get_markets()
        assert len(markets) == 2
        assert {'symbol': symbol1} in markets
        assert {'symbol': symbol2} in markets
    
    def test_get_ticker(self, mock_exchange, sample_ohlcv_data):
        """Test getting ticker data."""
        symbol = "BTC/USDT"
        mock_exchange.set_ohlcv_data(symbol, sample_ohlcv_data)
        
        ticker = mock_exchange.get_ticker(symbol)
        assert ticker['symbol'] == symbol
        assert ticker['last'] == sample_ohlcv_data['close'].iloc[-1]
        assert 'timestamp' in ticker
        
        # Test with invalid symbol
        with pytest.raises(ValueError):
            mock_exchange.get_ticker("INVALID/USDT")
    
    def test_get_ohlcv(self, mock_exchange, sample_ohlcv_data):
        """Test getting OHLCV data in list format."""
        symbol = "BTC/USDT"
        mock_exchange.set_ohlcv_data(symbol, sample_ohlcv_data)
        
        ohlcv_list = mock_exchange.get_ohlcv(symbol, "1h")
        assert len(ohlcv_list) == len(sample_ohlcv_data)
        assert len(ohlcv_list[0]) == 6  # timestamp, open, high, low, close, volume
    
    def test_get_balance(self, mock_exchange):
        """Test getting account balance."""
        balance = mock_exchange.get_balance()
        assert balance['total']['USD'] == 10000.0
    
    def test_cancel_order(self, mock_exchange, sample_ohlcv_data):
        """Test canceling an order."""
        symbol = "BTC/USDT"
        mock_exchange.set_ohlcv_data(symbol, sample_ohlcv_data)
        
        # Create an order
        order = mock_exchange.create_market_order(symbol, OrderSide.BUY, 0.1)
        order_id = order['id']
        
        # Try to cancel (should fail because order is already closed)
        result = mock_exchange.cancel_order(order_id)
        assert 'error' in result
        
        # Test with invalid order ID
        result = mock_exchange.cancel_order("invalid_id")
        assert 'error' in result
    
    def test_get_order_status(self, mock_exchange, sample_ohlcv_data):
        """Test getting order status."""
        symbol = "BTC/USDT"
        mock_exchange.set_ohlcv_data(symbol, sample_ohlcv_data)
        
        # Create an order
        order = mock_exchange.create_market_order(symbol, OrderSide.BUY, 0.1)
        order_id = order['id']
        
        # Get status
        status = mock_exchange.get_order_status(order_id)
        assert status == order
        
        # Test with invalid order ID
        result = mock_exchange.get_order_status("invalid_id")
        assert 'error' in result
    
    def test_get_open_orders(self, mock_exchange, sample_ohlcv_data):
        """Test getting open orders."""
        symbol = "BTC/USDT"
        mock_exchange.set_ohlcv_data(symbol, sample_ohlcv_data)
        
        # Create an order (market orders are immediately closed)
        mock_exchange.create_market_order(symbol, OrderSide.BUY, 0.1)
        
        # Should be no open orders
        open_orders = mock_exchange.get_open_orders()
        assert len(open_orders) == 0
        
        # Manually add an open order
        open_order = {
            'id': 'open_order_1',
            'symbol': symbol,
            'side': OrderSide.BUY,
            'type': OrderType.LIMIT,
            'amount': 0.1,
            'price': 45000.0,
            'timestamp': datetime.now(),
            'status': 'open'
        }
        mock_exchange.orders.append(open_order)
        
        # Now should have one open order
        open_orders = mock_exchange.get_open_orders()
        assert len(open_orders) == 1
        assert open_orders[0] == open_order
        
        # Filter by symbol
        open_orders = mock_exchange.get_open_orders(symbol)
        assert len(open_orders) == 1
        
        open_orders = mock_exchange.get_open_orders("ETH/USDT")
        assert len(open_orders) == 0


class TestMockData:
    """Tests for the mock data generation utilities."""
    
    def test_parse_timeframe(self):
        """Test parsing timeframe strings."""
        assert _parse_timeframe("1m") == timedelta(minutes=1)
        assert _parse_timeframe("5m") == timedelta(minutes=5)
        assert _parse_timeframe("1h") == timedelta(hours=1)
        assert _parse_timeframe("4h") == timedelta(hours=4)
        assert _parse_timeframe("1d") == timedelta(days=1)
        assert _parse_timeframe("1w") == timedelta(weeks=1)
        
        # Test invalid formats
        with pytest.raises(ValueError):
            _parse_timeframe("")
        
        with pytest.raises(ValueError):
            _parse_timeframe("m")
        
        with pytest.raises(ValueError):
            _parse_timeframe("1x")
    
    def test_generate_random_ohlcv(self):
        """Test generating random OHLCV data."""
        symbol = "BTC/USDT"
        start_date = datetime(2023, 1, 1)
        num_periods = 100
        
        # Test with default parameters
        df = generate_random_ohlcv(symbol, start_date, num_periods=num_periods)
        
        # Check DataFrame structure
        assert len(df) == num_periods
        assert set(df.columns) == {'timestamp', 'open', 'high', 'low', 'close', 'volume'}
        
        # Check data integrity
        assert (df['high'] >= df['open']).all()
        assert (df['high'] >= df['close']).all()
        assert (df['low'] <= df['open']).all()
        assert (df['low'] <= df['close']).all()
        assert (df['volume'] > 0).all()
        
        # Check timestamps
        assert df['timestamp'].iloc[0] == start_date
        assert df['timestamp'].iloc[-1] == start_date + timedelta(hours=num_periods-1)
        
        # Test with end_date
        end_date = start_date + timedelta(hours=50)
        df = generate_random_ohlcv(symbol, start_date, end_date=end_date, num_periods=num_periods)
        assert len(df) == 51  # 0 to 50 inclusive
        
        # Test with seed for reproducibility
        df1 = generate_random_ohlcv(symbol, start_date, num_periods=10, seed=42)
        df2 = generate_random_ohlcv(symbol, start_date, num_periods=10, seed=42)
        pd.testing.assert_frame_equal(df1, df2)
    
    def test_generate_trending_ohlcv(self):
        """Test generating OHLCV data with trends."""
        symbol = "BTC/USDT"
        start_date = datetime(2023, 1, 1)
        num_periods = 100
        
        # Define custom trend changes
        trend_changes = [
            (0, 0.01),    # Strong uptrend
            (50, -0.01),  # Strong downtrend
        ]
        
        df = generate_trending_ohlcv(
            symbol, 
            start_date, 
            num_periods=num_periods,
            trend_changes=trend_changes,
            seed=42
        )
        
        # Check DataFrame structure
        assert len(df) == num_periods
        
        # Check trend direction (prices should generally increase in first half, decrease in second)
        first_half_price_change = df.iloc[49]['close'] - df.iloc[0]['close']
        second_half_price_change = df.iloc[-1]['close'] - df.iloc[50]['close']
        
        assert first_half_price_change > 0  # Uptrend
        assert second_half_price_change < 0  # Downtrend
    
    def test_generate_pattern_ohlcv(self):
        """Test generating OHLCV data with patterns."""
        symbol = "BTC/USDT"
        start_date = datetime(2023, 1, 1)
        num_periods = 100
        
        # Test different patterns
        patterns = ['double_top', 'head_shoulders', 'cup_and_handle']
        
        for pattern in patterns:
            df = generate_pattern_ohlcv(
                symbol,
                pattern,
                start_date,
                num_periods=num_periods,
                seed=42
            )
            
            # Check DataFrame structure
            assert len(df) == num_periods
            assert set(df.columns) == {'timestamp', 'open', 'high', 'low', 'close', 'volume'}


# Feature: Mock Exchange Framework
# 
#   As a trading strategy developer
#   I want a mock exchange for testing
#   So that I can test strategies without connecting to real exchanges
# 
#   Scenario: Creating and executing market orders
#     Given a mock exchange with initial balance of 10000
#     And OHLCV data for "BTC/USDT" with current price of 50000
#     When I create a market buy order for 0.1 BTC
#     Then a new position should be created with size 0.1
#     And the balance should be reduced by 5000
#     When I create a market sell order for 0.1 BTC
#     Then the position should be closed
#     And the balance should be restored to 10000
# 
#   Scenario: Generating and using mock market data
#     Given I need to test a strategy with specific market conditions
#     When I generate random OHLCV data with a seed
#     Then the data should be deterministic and reproducible
#     When I generate data with a specific trend pattern
#     Then the price movement should follow the expected trend
#     And I should be able to use this data with the mock exchange 