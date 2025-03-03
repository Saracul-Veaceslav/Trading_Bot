"""
Strategy repository implementation.

This module provides a repository for strategy operations, including
strategy-specific queries and filtering operations.
"""
from datetime import datetime
from typing import List, Optional
from sqlalchemy import select, func, exists

from abidance.database.models import Strategy, Trade
from .base import BaseRepository


class StrategyRepository(BaseRepository[Strategy]):
    """Repository for strategy operations."""
    
    def __init__(self, session):
        """
        Initialize the strategy repository with a database session.
        
        Args:
            session: SQLAlchemy session
        """
        super().__init__(session, Strategy)
    
    def get_by_name(self, name: str) -> Optional[Strategy]:
        """
        Get a strategy by name.
        
        Args:
            name: Strategy name
            
        Returns:
            The strategy if found, None otherwise
        """
        return self._session.execute(
            select(Strategy).where(Strategy.name == name)
        ).scalar_one_or_none()
    
    def get_strategies_by_date_range(self, 
                                   start_date: datetime,
                                   end_date: datetime) -> List[Strategy]:
        """
        Get strategies created within a date range.
        
        Args:
            start_date: Start date (inclusive)
            end_date: End date (inclusive)
            
        Returns:
            List of strategies created within the date range
        """
        # Use >= and <= for inclusive range
        return self._session.execute(
            select(Strategy).where(
                Strategy.created_at >= start_date,
                Strategy.created_at <= end_date
            )
        ).scalars().all()
    
    def get_strategies_with_trades(self) -> List[Strategy]:
        """
        Get strategies that have associated trades.
        
        Returns:
            List of strategies with at least one trade
        """
        return self._session.execute(
            select(Strategy).where(
                exists().where(Trade.strategy_id == Strategy.id)
            )
        ).scalars().all()
    
    def get_strategies_by_parameter(self, parameter_name: str) -> List[Strategy]:
        """
        Get strategies that have a specific parameter.
        
        Args:
            parameter_name: Parameter name to search for
            
        Returns:
            List of strategies with the specified parameter
        """
        # Using JSON containment operator to check if the parameter exists
        # This is SQLite-compatible using the JSON1 extension
        return self._session.execute(
            select(Strategy).where(
                func.json_extract(Strategy.parameters, f"$.{parameter_name}") != None
            )
        ).scalars().all() 