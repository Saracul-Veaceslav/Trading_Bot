"""
Exchange factory module for creating exchange instances.

This module provides factory functions for creating exchange instances
based on configuration parameters.
"""
from typing import Any, Dict


from .base import Exchange
from .binance import BinanceExchange


def create_exchange(config: Dict[str, Any]) -> Exchange:
    """
    Create an exchange instance from configuration.

    Args:
        config: Exchange configuration dictionary with parameters like:
               - exchange_id: Identifier for the exchange
               - api_key: API key for authentication
               - api_secret: API secret for authentication
               - testnet: Whether to use testnet/sandbox
               - Additional exchange-specific parameters

    Returns:
        Exchange instance

    Raises:
        ValueError: If the exchange_id is not supported
    """
    exchange_id = config.get("exchange_id")
    api_key = config.get("api_key")
    api_secret = config.get("api_secret")
    testnet = config.get("testnet", False)

    # Remove known parameters to isolate exchange-specific ones
    known_params = ["exchange_id", "api_key", "api_secret", "testnet"]
    kwargs = {k: v for k, v in config.items() if k not in known_params}

    if exchange_id == "binance":
        return BinanceExchange(
            api_key=api_key,
            api_secret=api_secret,
            testnet=testnet,
            **kwargs
        )
    raise ValueError(f"Unsupported exchange: {exchange_id}")
