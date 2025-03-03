"""
Data generators for property-based testing.

This module provides generators for creating test data for property-based testing
of trading strategies and other components.
"""
from typing import Any, Dict, List, Optional
from hypothesis import strategies as st
from hypothesis.strategies import SearchStrategy
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


@st.composite
def generate_ohlcv_data(
    draw: Any,
    min_length: int = 100,
    max_length: int = 200,  # Reduced from 1000 to avoid health check issues
    min_price: float = 1.0,
    max_price: float = 1000.0,
    volatility: float = 0.02
) -> pd.DataFrame:
    """
    Generate random OHLCV data for property-based testing.

    Args:
        draw: Hypothesis draw function
        min_length: Minimum number of candles
        max_length: Maximum number of candles
        min_price: Minimum price
        max_price: Maximum price
        volatility: Price volatility factor

    Returns:
        DataFrame with OHLCV data
    """
    length = draw(st.integers(min_length, max_length))

    # Generate timestamps
    start_date = draw(st.datetimes(
        min_value=datetime(2010, 1, 1),
        max_value=datetime(2024, 1, 1)
    ))
    timestamps = [
        start_date + timedelta(hours=i)
        for i in range(length)
    ]

    # Generate prices with random walk
    base_price = draw(st.floats(min_price, max_price))
    prices = [base_price]

    for _ in range(length - 1):
        change = draw(st.floats(-volatility, volatility))
        new_price = max(min_price, prices[-1] * (1 + change))
        prices.append(new_price)

    # Generate OHLCV data
    data = []
    for i, close_price in enumerate(prices):
        # Generate realistic OHLCV values
        open_price = prices[i-1] if i > 0 else close_price
        high_price = max(open_price, close_price) * (1 + abs(draw(st.floats(0, 0.005))))
        low_price = min(open_price, close_price) * (1 - abs(draw(st.floats(0, 0.005))))
        volume = draw(st.floats(100, 10000))

        data.append({
            'timestamp': timestamps[i],
            'open': open_price,
            'high': high_price,
            'low': low_price,
            'close': close_price,
            'volume': volume
        })

    return pd.DataFrame(data)


@st.composite
def generate_strategy_parameters(draw: Any) -> Dict[str, Any]:
    """
    Generate random strategy parameters for testing.

    Args:
        draw: Hypothesis draw function

    Returns:
        Dictionary of strategy parameters
    """
    # Generate SMA strategy parameters
    short_window = draw(st.integers(5, 20))
    long_window = draw(st.integers(short_window + 5, short_window + 50))

    return {
        'short_window': short_window,
        'long_window': long_window
    }


@st.composite
def generate_market_data(
    draw: Any,
    min_symbols: int = 1,
    max_symbols: int = 5,
    min_length: int = 100,
    max_length: int = 200  # Reduced from 1000 to avoid health check issues
) -> Dict[str, pd.DataFrame]:
    """
    Generate market data for multiple symbols.

    Args:
        draw: Hypothesis draw function
        min_symbols: Minimum number of symbols
        max_symbols: Maximum number of symbols
        min_length: Minimum number of candles per symbol
        max_length: Maximum number of candles per symbol

    Returns:
        Dictionary mapping symbol names to OHLCV DataFrames
    """
    num_symbols = draw(st.integers(min_symbols, max_symbols))

    # Generate symbol names
    base_currencies = draw(st.lists(
        st.sampled_from(['BTC', 'ETH', 'XRP', 'LTC', 'ADA', 'DOT', 'SOL']),
        min_size=num_symbols,
        max_size=num_symbols,
        unique=True
    ))
    quote_currency = draw(st.sampled_from(['USDT', 'USD', 'USDC']))
    symbols = [f"{base}/{quote_currency}" for base in base_currencies]

    # Generate data for each symbol
    market_data = {}
    for symbol in symbols:
        data = draw(generate_ohlcv_data(
            min_length=min_length,
            max_length=max_length
        ))
        market_data[symbol] = data

    return market_data


@st.composite
def generate_order_book_data(
    draw: Any,
    min_depth: int = 5,
    max_depth: int = 20,
    min_price: float = 1.0,
    max_price: float = 1000.0
) -> Dict[str, List[Dict[str, float]]]:
    """
    Generate order book data for testing.

    Args:
        draw: Hypothesis draw function
        min_depth: Minimum number of levels in the order book
        max_depth: Maximum number of levels in the order book
        min_price: Minimum price
        max_price: Maximum price

    Returns:
        Dictionary with 'bids' and 'asks' lists
    """
    # Generate base price
    base_price = draw(st.floats(min_price, max_price))

    # Generate depth
    depth = draw(st.integers(min_depth, max_depth))

    # Generate bids (buy orders, below base price)
    bids = []
    for i in range(depth):
        price = base_price * (1 - 0.001 * (i + 1))
        size = draw(st.floats(0.1, 10.0))
        bids.append({'price': price, 'size': size})

    # Generate asks (sell orders, above base price)
    asks = []
    for i in range(depth):
        price = base_price * (1 + 0.001 * (i + 1))
        size = draw(st.floats(0.1, 10.0))
        asks.append({'price': price, 'size': size})

    return {
        'bids': sorted(bids, key=lambda x: x['price'], reverse=True),
        'asks': sorted(asks, key=lambda x: x['price'])
    }


@st.composite
def generate_trade_data(
    draw: Any,
    min_trades: int = 10,
    max_trades: int = 50,  # Reduced from 100 to avoid health check issues
    min_price: float = 1.0,
    max_price: float = 1000.0
) -> pd.DataFrame:
    """
    Generate trade data for testing.

    Args:
        draw: Hypothesis draw function
        min_trades: Minimum number of trades
        max_trades: Maximum number of trades
        min_price: Minimum price
        max_price: Maximum price

    Returns:
        DataFrame with trade data
    """
    num_trades = draw(st.integers(min_trades, max_trades))

    # Generate timestamps
    start_date = draw(st.datetimes(
        min_value=datetime(2010, 1, 1),
        max_value=datetime(2024, 1, 1)
    ))

    # Generate trades
    trades = []
    for i in range(num_trades):
        timestamp = start_date + timedelta(seconds=i)
        price = draw(st.floats(min_price, max_price))
        size = draw(st.floats(0.001, 10.0))
        side = draw(st.sampled_from(['buy', 'sell']))

        trades.append({
            'timestamp': timestamp,
            'price': price,
            'size': size,
            'side': side
        })

    return pd.DataFrame(trades)