#!/usr/bin/env python3
"""
Script to initialize the database for the Abidance Trading Bot API.
"""

import logging
import os
from abidance.database.models import Base, Trade, Strategy
from abidance.api.database import engine
from sqlalchemy.orm import Session
import random
from datetime import datetime, timedelta
from abidance.trading.order import OrderSide

# Configure logging
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/database_init.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("abidance.database")

def create_sample_data(db: Session):
    """Create sample data for testing."""
    # Create sample strategies
    strategies = [
        Strategy(
            id=1,
            name="sma_crossover",
            parameters={"fast_period": 10, "slow_period": 30}
        ),
        Strategy(
            id=2,
            name="rsi_strategy",
            parameters={"rsi_period": 14, "oversold": 30, "overbought": 70}
        )
    ]
    
    # Add strategies to database
    for strategy in strategies:
        db.add(strategy)
    
    # Create sample trades
    symbols = ["BTC/USDT", "ETH/USDT", "XRP/USDT"]
    sides = [OrderSide.BUY, OrderSide.SELL]
    
    # Generate trades for the last 7 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    trades = []
    current_date = start_date
    
    while current_date < end_date:
        # Generate 1-3 trades per day
        for _ in range(random.randint(1, 3)):
            symbol = random.choice(symbols)
            side = random.choice(sides)
            price = random.uniform(40000, 60000) if symbol == "BTC/USDT" else random.uniform(2000, 3000) if symbol == "ETH/USDT" else random.uniform(0.5, 1.5)
            amount = random.uniform(0.1, 1.0) if symbol == "BTC/USDT" else random.uniform(1.0, 10.0) if symbol == "ETH/USDT" else random.uniform(100, 1000)
            
            trade_time = current_date + timedelta(hours=random.randint(0, 23), minutes=random.randint(0, 59))
            
            trade = Trade(
                symbol=symbol,
                side=side,
                amount=amount,
                price=price,
                timestamp=trade_time,
                strategy_id=random.choice([1, 2])
            )
            trades.append(trade)
        
        current_date += timedelta(days=1)
    
    # Add trades to database
    for trade in trades:
        db.add(trade)
    
    # Commit changes
    db.commit()
    
    logger.info(f"Created {len(strategies)} strategies and {len(trades)} trades")

def main():
    """Initialize the database."""
    logger.info("Initializing database")
    
    try:
        # Create tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created")
        
        # Create session
        with Session(engine) as db:
            # Create sample data
            create_sample_data(db)
        
        logger.info("Database initialization complete")
    except Exception as e:
        logger.exception(f"Error initializing database: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    main() 