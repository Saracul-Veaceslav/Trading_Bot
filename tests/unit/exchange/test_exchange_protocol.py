"""
Tests to verify that exchange implementations satisfy the Exchange protocol.
"""
import pytest
from typing import Dict, Any

from abidance.exchange.protocols import Exchange, ExchangeFactory
from abidance.exchange.binance import BinanceExchange
from abidance.exchange.factory import create_exchange


class TestExchangeProtocol:
    """Test suite to verify exchange implementations satisfy the Exchange protocol."""

    def test_binance_exchange_satisfies_protocol(self):
        """Test that BinanceExchange satisfies the Exchange protocol."""
        # Create a BinanceExchange instance with test credentials
        exchange = BinanceExchange(
            api_key="test_api_key",
            api_secret="test_api_secret",
            testnet=True
        )
        
        # Assert that the instance satisfies the Exchange protocol
        assert isinstance(exchange, Exchange)
    
    def test_create_exchange_factory_function(self):
        """Test that the create_exchange factory function satisfies ExchangeFactory."""
        # Define a wrapper class to adapt the create_exchange function to the ExchangeFactory protocol
        class ExchangeFactoryWrapper:
            def create_exchange(self, config: Dict[str, Any]) -> Exchange:
                return create_exchange(config)
        
        factory = ExchangeFactoryWrapper()
        
        # Assert that the factory satisfies the ExchangeFactory protocol
        assert isinstance(factory, ExchangeFactory)
    
    def test_create_exchange_returns_exchange_protocol(self):
        """Test that create_exchange returns an object satisfying the Exchange protocol."""
        # Create a minimal configuration for a testnet exchange
        config = {
            "exchange_id": "binance",
            "testnet": True,
            "api_key": "test_api_key",
            "api_secret": "test_api_secret"
        }
        
        # Create an exchange using the factory function
        exchange = create_exchange(config)
        
        # Assert that the created exchange satisfies the Exchange protocol
        assert isinstance(exchange, Exchange)


class TestExchangeImplementations:
    """Test suite to verify specific exchange implementation details."""
    
    def test_binance_exchange_attributes(self):
        """Test that BinanceExchange has the required attributes."""
        exchange = BinanceExchange(
            api_key="test_api_key",
            api_secret="test_api_secret",
            testnet=True
        )
        
        # Check required attributes
        assert hasattr(exchange, "exchange_id")
        assert exchange.exchange_id == "binance"
        assert hasattr(exchange, "testnet")
        assert exchange.testnet is True
        assert hasattr(exchange, "api_key")
        assert exchange.api_key == "test_api_key"
        assert hasattr(exchange, "api_secret")
        assert exchange.api_secret == "test_api_secret"
    
    def test_binance_exchange_methods(self):
        """Test that BinanceExchange has the required methods."""
        exchange = BinanceExchange(
            api_key="test_api_key",
            api_secret="test_api_secret",
            testnet=True
        )
        
        # Check required methods
        assert callable(getattr(exchange, "get_markets", None))
        assert callable(getattr(exchange, "get_ticker", None))
        assert callable(getattr(exchange, "get_ohlcv", None))
        assert callable(getattr(exchange, "get_balance", None))
        assert callable(getattr(exchange, "place_order", None))
        assert callable(getattr(exchange, "cancel_order", None))
        assert callable(getattr(exchange, "get_order_status", None))
        assert callable(getattr(exchange, "get_open_orders", None)) 