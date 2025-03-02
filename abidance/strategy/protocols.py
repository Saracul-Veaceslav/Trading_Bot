"""
Strategy protocols module defining interfaces for trading strategies.

This module provides Protocol classes that define the interfaces for trading strategies.
These protocols enable structural typing and dependency inversion, allowing high-level
modules to depend on abstractions rather than concrete implementations.
"""

from typing import Protocol, runtime_checkable, Dict, List, Any, Optional
import pandas as pd

from abidance.core.domain import SignalType
from abidance.trading.order import Order


@runtime_checkable
class Strategy(Protocol):
    """Protocol defining the interface for trading strategies."""
    
    name: str
    symbols: List[str]
    timeframe: str
    parameters: Dict[str, Any]
    is_running: bool
    
    def initialize(self) -> None:
        """
        Initialize the strategy before running.
        
        This method is called once before the strategy starts running.
        It should set up any resources or state needed by the strategy.
        """
        ...
    
    def analyze(self, symbol: str, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze market data and compute indicators.
        
        Args:
            symbol: The market symbol
            data: OHLCV data as a pandas DataFrame
            
        Returns:
            Dictionary with analysis results
        """
        ...
    
    def generate_signals(self, symbol: str, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate trading signals based on analysis results.
        
        Args:
            symbol: The market symbol
            analysis: Analysis results from the analyze method
            
        Returns:
            List of signal dictionaries
        """
        ...
    
    def create_order(self, signal: Dict[str, Any]) -> Optional[Order]:
        """
        Create an order based on a signal.
        
        Args:
            signal: Signal dictionary
            
        Returns:
            Order object or None if no order should be created
        """
        ...
    
    def update(self, symbol: str, data: pd.DataFrame) -> List[Order]:
        """
        Update the strategy with new market data.
        
        This method is called periodically with new market data.
        It runs the analysis, generates signals, and creates orders.
        
        Args:
            symbol: The market symbol
            data: OHLCV data as a pandas DataFrame
            
        Returns:
            List of orders to execute
        """
        ...
    
    def start(self) -> None:
        """Start the strategy."""
        ...
    
    def stop(self) -> None:
        """Stop the strategy."""
        ...
    
    def get_state(self) -> Dict[str, Any]:
        """
        Get the current state of the strategy.
        
        Returns:
            Dictionary with the current state
        """
        ...
    
    def set_state(self, state: Dict[str, Any]) -> None:
        """
        Set the state of the strategy.
        
        Args:
            state: Dictionary with the state to set
        """
        ...


@runtime_checkable
class StrategyFactory(Protocol):
    """Protocol defining the interface for strategy factories."""
    
    def create_strategy(self, config: Dict[str, Any]) -> Strategy:
        """
        Create a strategy instance from configuration.
        
        Args:
            config: Strategy configuration dictionary
            
        Returns:
            Strategy instance
        """
        ... 