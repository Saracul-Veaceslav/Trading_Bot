#!/usr/bin/env python
"""
Script to insert and query sample data in the database.
"""
import os
from datetime import datetime, timezone
import json
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

# Import the database models
from abidance.database.models import Base, Trade, Strategy, OHLCV
from abidance.trading.order import OrderSide

# Database path
DB_PATH = os.path.join('data', 'abidance.db')
DB_URL = f"sqlite:///{DB_PATH}"

def insert_sample_data():
    """Insert sample data into the database."""
    engine = create_engine(DB_URL)
    
    with Session(engine) as session:
        # Insert a sample strategy
        strategy = Strategy(
            name="SMA Crossover",
            parameters=json.dumps({
                "fast_period": 10,
                "slow_period": 30,
                "volume_factor": 1.5
            }),
            created_at=datetime.now(timezone.utc)
        )
        session.add(strategy)
        session.flush()  # Flush to get the strategy ID
        
        # Insert sample OHLCV data
        ohlcv_data = [
            OHLCV(
                symbol="BTC/USDT",
                timestamp=datetime(2023, 3, 1, 0, 0, 0, tzinfo=timezone.utc),
                open=23000.0,
                high=23500.0,
                low=22800.0,
                close=23200.0,
                volume=1000.0
            ),
            OHLCV(
                symbol="BTC/USDT",
                timestamp=datetime(2023, 3, 1, 1, 0, 0, tzinfo=timezone.utc),
                open=23200.0,
                high=23700.0,
                low=23100.0,
                close=23600.0,
                volume=1200.0
            ),
            OHLCV(
                symbol="ETH/USDT",
                timestamp=datetime(2023, 3, 1, 0, 0, 0, tzinfo=timezone.utc),
                open=1600.0,
                high=1650.0,
                low=1580.0,
                close=1630.0,
                volume=500.0
            )
        ]
        session.add_all(ohlcv_data)
        
        # Insert sample trades
        trades = [
            Trade(
                symbol="BTC/USDT",
                side=OrderSide.BUY.name,
                amount=0.1,
                price=23200.0,
                timestamp=datetime(2023, 3, 1, 0, 30, 0, tzinfo=timezone.utc),
                strategy_id=strategy.id
            ),
            Trade(
                symbol="BTC/USDT",
                side=OrderSide.SELL.name,
                amount=0.1,
                price=23600.0,
                timestamp=datetime(2023, 3, 1, 1, 30, 0, tzinfo=timezone.utc),
                strategy_id=strategy.id
            ),
            Trade(
                symbol="ETH/USDT",
                side=OrderSide.BUY.name,
                amount=1.0,
                price=1630.0,
                timestamp=datetime(2023, 3, 1, 0, 45, 0, tzinfo=timezone.utc),
                strategy_id=strategy.id
            )
        ]
        session.add_all(trades)
        
        # Commit the transaction
        session.commit()
    
    print("Sample data inserted successfully.")

def query_data():
    """Query and display data from the database."""
    engine = create_engine(DB_URL)
    
    with Session(engine) as session:
        # Query strategies
        strategies = session.execute(select(Strategy)).scalars().all()
        print("\nStrategies:")
        for strategy in strategies:
            print(f"ID: {strategy.id}, Name: {strategy.name}, "
                  f"Parameters: {strategy.parameters}, "
                  f"Created At: {strategy.created_at}")
        
        # Query OHLCV data
        ohlcv_data = session.execute(select(OHLCV)).scalars().all()
        print("\nOHLCV Data:")
        for ohlcv in ohlcv_data:
            print(f"Symbol: {ohlcv.symbol}, Timestamp: {ohlcv.timestamp}, "
                  f"Open: {ohlcv.open}, High: {ohlcv.high}, "
                  f"Low: {ohlcv.low}, Close: {ohlcv.close}, "
                  f"Volume: {ohlcv.volume}")
        
        # Query trades
        trades = session.execute(select(Trade)).scalars().all()
        print("\nTrades:")
        for trade in trades:
            print(f"Symbol: {trade.symbol}, Side: {trade.side}, "
                  f"Amount: {trade.amount}, Price: {trade.price}, "
                  f"Timestamp: {trade.timestamp}, "
                  f"Strategy ID: {trade.strategy_id}")
        
        # Query trades for a specific strategy
        if strategies:
            strategy_id = strategies[0].id
            strategy_trades = session.execute(
                select(Trade).where(Trade.strategy_id == strategy_id)
            ).scalars().all()
            
            print(f"\nTrades for Strategy ID {strategy_id}:")
            for trade in strategy_trades:
                print(f"Symbol: {trade.symbol}, Side: {trade.side}, "
                      f"Amount: {trade.amount}, Price: {trade.price}, "
                      f"Timestamp: {trade.timestamp}")

def main():
    """Main function to insert and query sample data."""
    # Insert sample data
    insert_sample_data()
    
    # Query and display data
    query_data()

if __name__ == "__main__":
    main() 