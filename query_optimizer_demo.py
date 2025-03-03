#!/usr/bin/env python
"""
Script to demonstrate the QueryOptimizer class.
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

# Import the database models and QueryOptimizer
from abidance.database.models import Base
from abidance.database.queries import QueryOptimizer

# Database path
DB_PATH = os.path.join('data', 'abidance.db')
DB_URL = f"sqlite:///{DB_PATH}"

def main():
    """Main function to demonstrate the QueryOptimizer class."""
    # Create engine and session
    engine = create_engine(DB_URL)
    session = Session(engine)
    
    # Create a QueryOptimizer instance
    optimizer = QueryOptimizer(session)
    
    # Get trade statistics for BTC/USDT
    print("\nTrade Statistics for BTC/USDT:")
    try:
        stats = optimizer.get_trade_statistics("BTC/USDT")
        for key, value in stats.items():
            print(f"{key}: {value}")
    except Exception as e:
        print(f"Error getting trade statistics: {e}")
    
    # Get OHLCV data with indicators for BTC/USDT
    print("\nOHLCV Data with Indicators for BTC/USDT:")
    try:
        ohlcv_with_indicators = optimizer.get_ohlcv_with_indicators(
            symbol="BTC/USDT",
            window=14  # Using window parameter instead of indicators
        )
        if ohlcv_with_indicators.empty:
            print("No data found.")
        else:
            print(ohlcv_with_indicators)
    except Exception as e:
        print(f"Error getting OHLCV data with indicators: {e}")
    
    # Get strategy performance for SMA Crossover (using ID 1)
    print("\nStrategy Performance for SMA Crossover (ID: 1):")
    try:
        performance = optimizer.get_strategy_performance(
            strategy_id=1  # Using strategy_id instead of strategy_name
        )
        if not performance:
            print("No performance data found.")
        else:
            for key, value in performance.items():
                print(f"{key}: {value}")
    except Exception as e:
        print(f"Error getting strategy performance: {e}")
    
    # Get aggregated OHLCV data for BTC/USDT
    print("\nAggregated OHLCV Data for BTC/USDT (Daily):")
    try:
        aggregated_ohlcv = optimizer.get_aggregated_ohlcv(
            symbol="BTC/USDT",
            interval="1d"
        )
        if aggregated_ohlcv.empty:
            print("No data found.")
        else:
            print(aggregated_ohlcv)
    except Exception as e:
        print(f"Error getting aggregated OHLCV data: {e}")
    
    # Close the session
    session.close()

if __name__ == "__main__":
    main() 