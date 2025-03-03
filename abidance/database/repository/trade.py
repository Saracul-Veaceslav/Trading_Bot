"""
Trade repository implementation.

This module provides a repository for trade operations, including
trade-specific queries and filtering operations.
"""
from datetime import datetime
from typing import List, Optional
from sqlalchemy import select, desc, func

from abidance.database.models import Trade
from .base import BaseRepository


class TradeRepository(BaseRepository[Trade]):
    """Repository for trade operations."""
    
    def __init__(self, session):
        """
        Initialize the trade repository with a database session.
        
        Args:
            session: SQLAlchemy session
        """
        super().__init__(session, Trade)
    
    def get_trades_by_symbol(self, symbol: str) -> List[Trade]:
        """
        Get all trades for a symbol.
        
        Args:
            symbol: Trading symbol (e.g., "BTC/USD")
            
        Returns:
            List of trades for the symbol
        """
        return self._session.execute(
            select(Trade).where(Trade.symbol == symbol)
        ).scalars().all()
    
    def get_trades_by_date_range(self, 
                               start_date: datetime,
                               end_date: datetime) -> List[Trade]:
        """
        Get trades within a date range.
        
        Args:
            start_date: Start date (inclusive)
            end_date: End date (inclusive)
            
        Returns:
            List of trades within the date range
        """
        # Use >= and <= for inclusive range
        return self._session.execute(
            select(Trade).where(
                Trade.timestamp >= start_date,
                Trade.timestamp <= end_date
            )
        ).scalars().all()
    
    def get_trades_by_strategy(self, strategy_id: int) -> List[Trade]:
        """
        Get all trades for a strategy.
        
        Args:
            strategy_id: Strategy ID
            
        Returns:
            List of trades for the strategy
        """
        return self._session.execute(
            select(Trade).where(Trade.strategy_id == strategy_id)
        ).scalars().all()
    
    def get_latest_trade_by_symbol(self, symbol: str) -> Optional[Trade]:
        """
        Get the most recent trade for a symbol.
        
        Args:
            symbol: Trading symbol (e.g., "BTC/USD")
            
        Returns:
            The most recent trade for the symbol, or None if no trades exist
        """
        return self._session.execute(
            select(Trade)
            .where(Trade.symbol == symbol)
            .order_by(desc(Trade.timestamp))
            .limit(1)
        ).scalar_one_or_none() 