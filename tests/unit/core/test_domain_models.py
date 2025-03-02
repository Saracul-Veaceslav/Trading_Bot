"""
Tests for the core domain models.

This module contains tests for the core domain entities used throughout the application.
"""

import pytest
from datetime import datetime
from dataclasses import FrozenInstanceError

from abidance.core.domain import (
    OrderSide,
    OrderType,
    SignalType,
    Position,
    Order,
    Signal,
    Candle,
    Trade
)


class TestOrderSide:
    """Tests for the OrderSide enum."""
    
    def test_order_side_values(self):
        """Test that OrderSide enum has the expected values."""
        assert OrderSide.BUY.value == "buy"
        assert OrderSide.SELL.value == "sell"
    
    def test_order_side_from_string(self):
        """Test that OrderSide can be created from string values."""
        assert OrderSide("buy") == OrderSide.BUY
        assert OrderSide("sell") == OrderSide.SELL
    
    def test_order_side_invalid_value(self):
        """Test that creating OrderSide with invalid value raises ValueError."""
        with pytest.raises(ValueError):
            OrderSide("invalid")


class TestOrderType:
    """Tests for the OrderType enum."""
    
    def test_order_type_values(self):
        """Test that OrderType enum has the expected values."""
        assert OrderType.MARKET.value == "market"
        assert OrderType.LIMIT.value == "limit"
        assert OrderType.STOP_LOSS.value == "stop_loss"
        assert OrderType.TAKE_PROFIT.value == "take_profit"
    
    def test_order_type_from_string(self):
        """Test that OrderType can be created from string values."""
        assert OrderType("market") == OrderType.MARKET
        assert OrderType("limit") == OrderType.LIMIT
        assert OrderType("stop_loss") == OrderType.STOP_LOSS
        assert OrderType("take_profit") == OrderType.TAKE_PROFIT
    
    def test_order_type_invalid_value(self):
        """Test that creating OrderType with invalid value raises ValueError."""
        with pytest.raises(ValueError):
            OrderType("invalid")


class TestSignalType:
    """Tests for the SignalType enum."""
    
    def test_signal_type_values(self):
        """Test that SignalType enum has the expected values."""
        assert SignalType.BUY.value == "buy"
        assert SignalType.SELL.value == "sell"
        assert SignalType.HOLD.value == "hold"
    
    def test_signal_type_from_string(self):
        """Test that SignalType can be created from string values."""
        assert SignalType("buy") == SignalType.BUY
        assert SignalType("sell") == SignalType.SELL
        assert SignalType("hold") == SignalType.HOLD
    
    def test_signal_type_invalid_value(self):
        """Test that creating SignalType with invalid value raises ValueError."""
        with pytest.raises(ValueError):
            SignalType("invalid")


class TestPosition:
    """Tests for the Position dataclass."""
    
    def test_position_creation(self):
        """Test that Position can be created with valid parameters."""
        timestamp = datetime.now()
        position = Position(
            symbol="BTC/USD",
            side=OrderSide.BUY,
            entry_price=50000.0,
            size=1.0,
            timestamp=timestamp,
            stop_loss=48000.0,
            take_profit=55000.0,
            position_id="pos123"
        )
        
        assert position.symbol == "BTC/USD"
        assert position.side == OrderSide.BUY
        assert position.entry_price == 50000.0
        assert position.size == 1.0
        assert position.timestamp == timestamp
        assert position.stop_loss == 48000.0
        assert position.take_profit == 55000.0
        assert position.position_id == "pos123"
    
    def test_position_optional_fields(self):
        """Test that Position can be created without optional fields."""
        timestamp = datetime.now()
        position = Position(
            symbol="BTC/USD",
            side=OrderSide.BUY,
            entry_price=50000.0,
            size=1.0,
            timestamp=timestamp
        )
        
        assert position.symbol == "BTC/USD"
        assert position.side == OrderSide.BUY
        assert position.entry_price == 50000.0
        assert position.size == 1.0
        assert position.timestamp == timestamp
        assert position.stop_loss is None
        assert position.take_profit is None
        assert position.position_id is None


class TestOrder:
    """Tests for the Order dataclass."""
    
    def test_order_creation(self):
        """Test that Order can be created with valid parameters."""
        timestamp = datetime.now()
        order = Order(
            symbol="BTC/USD",
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            price=50000.0,
            size=1.0,
            timestamp=timestamp,
            order_id="ord123"
        )
        
        assert order.symbol == "BTC/USD"
        assert order.side == OrderSide.BUY
        assert order.order_type == OrderType.LIMIT
        assert order.price == 50000.0
        assert order.size == 1.0
        assert order.timestamp == timestamp
        assert order.order_id == "ord123"
    
    def test_order_optional_fields(self):
        """Test that Order can be created without optional fields."""
        timestamp = datetime.now()
        order = Order(
            symbol="BTC/USD",
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            price=None,
            size=1.0,
            timestamp=timestamp
        )
        
        assert order.symbol == "BTC/USD"
        assert order.side == OrderSide.BUY
        assert order.order_type == OrderType.MARKET
        assert order.price is None
        assert order.size == 1.0
        assert order.timestamp == timestamp
        assert order.order_id is None


class TestSignal:
    """Tests for the Signal dataclass."""
    
    def test_signal_creation(self):
        """Test that Signal can be created with valid parameters."""
        timestamp = datetime.now()
        signal = Signal(
            symbol="BTC/USD",
            signal_type=SignalType.BUY,
            price=50000.0,
            timestamp=timestamp,
            confidence=0.85,
            metadata={"strategy": "sma_crossover"}
        )
        
        assert signal.symbol == "BTC/USD"
        assert signal.signal_type == SignalType.BUY
        assert signal.price == 50000.0
        assert signal.timestamp == timestamp
        assert signal.confidence == 0.85
        assert signal.metadata == {"strategy": "sma_crossover"}
    
    def test_signal_optional_fields(self):
        """Test that Signal can be created without optional fields."""
        timestamp = datetime.now()
        signal = Signal(
            symbol="BTC/USD",
            signal_type=SignalType.BUY,
            price=50000.0,
            timestamp=timestamp
        )
        
        assert signal.symbol == "BTC/USD"
        assert signal.signal_type == SignalType.BUY
        assert signal.price == 50000.0
        assert signal.timestamp == timestamp
        assert signal.confidence is None
        assert signal.metadata is None


class TestCandle:
    """Tests for the Candle dataclass."""
    
    def test_candle_creation(self):
        """Test that Candle can be created with valid parameters."""
        timestamp = datetime.now()
        candle = Candle(
            symbol="BTC/USD",
            timestamp=timestamp,
            open=50000.0,
            high=51000.0,
            low=49000.0,
            close=50500.0,
            volume=10.5
        )
        
        assert candle.symbol == "BTC/USD"
        assert candle.timestamp == timestamp
        assert candle.open == 50000.0
        assert candle.high == 51000.0
        assert candle.low == 49000.0
        assert candle.close == 50500.0
        assert candle.volume == 10.5


class TestTrade:
    """Tests for the Trade dataclass."""
    
    def test_trade_creation(self):
        """Test that Trade can be created with valid parameters."""
        timestamp = datetime.now()
        trade = Trade(
            symbol="BTC/USD",
            side=OrderSide.BUY,
            price=50000.0,
            size=1.0,
            timestamp=timestamp,
            trade_id="trade123",
            fee=25.0,
            fee_currency="USD"
        )
        
        assert trade.symbol == "BTC/USD"
        assert trade.side == OrderSide.BUY
        assert trade.price == 50000.0
        assert trade.size == 1.0
        assert trade.timestamp == timestamp
        assert trade.trade_id == "trade123"
        assert trade.fee == 25.0
        assert trade.fee_currency == "USD"
    
    def test_trade_optional_fields(self):
        """Test that Trade can be created without optional fields."""
        timestamp = datetime.now()
        trade = Trade(
            symbol="BTC/USD",
            side=OrderSide.BUY,
            price=50000.0,
            size=1.0,
            timestamp=timestamp
        )
        
        assert trade.symbol == "BTC/USD"
        assert trade.side == OrderSide.BUY
        assert trade.price == 50000.0
        assert trade.size == 1.0
        assert trade.timestamp == timestamp
        assert trade.trade_id is None
        assert trade.fee is None
        assert trade.fee_currency is None 