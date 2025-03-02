"""
Base strategy module defining the abstract Strategy interface.
"""
from abc import ABC, abstractmethod
import logging
from typing import Any, Dict, List, Optional, Union

import pandas as pd

from ..trading.order import Order


class Strategy(ABC):
    """
    Abstract base class for trading strategies.
    
    All strategy implementations must inherit from this class and implement
    its abstract methods to provide a consistent interface.
    """
    
    def __init__(self, name: str, symbols: List[str], timeframe: str = '1h', 
                 parameters: Optional[Dict[str, Any]] = None):
        """
        Initialize the strategy.
        
        Args:
            name: Strategy name
            symbols: List of symbols to trade
            timeframe: Timeframe for analysis
            parameters: Strategy-specific parameters
        """
        self.name = name
        self.symbols = symbols
        self.timeframe = timeframe
        self.parameters = parameters or {}
        self.logger = logging.getLogger(f"{__name__}.{name}")
        
        # State tracking
        self.is_running = False
        self.last_update_time = None
        self.state: Dict[str, Any] = {}
    
    @abstractmethod
    def initialize(self) -> None:
        """
        Initialize the strategy before running.
        
        This method is called once before the strategy starts running.
        It should set up any resources or state needed by the strategy.
        """
        pass
    
    @abstractmethod
    def analyze(self, symbol: str, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze market data and generate signals.
        
        Args:
            symbol: The market symbol
            data: OHLCV data as a pandas DataFrame
            
        Returns:
            Dictionary with analysis results
        """
        pass
    
    @abstractmethod
    def generate_signals(self, symbol: str, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate trading signals based on analysis.
        
        Args:
            symbol: The market symbol
            analysis: Analysis results from the analyze method
            
        Returns:
            List of signal dictionaries
        """
        pass
    
    def create_order(self, signal: Dict[str, Any]) -> Optional[Order]:
        """
        Create an order based on a signal.
        
        Args:
            signal: Signal dictionary
            
        Returns:
            Order object or None if no order should be created
        """
        # Default implementation - override in subclasses for custom logic
        self.logger.info(f"Creating order from signal: {signal}")
        
        # This is a stub - in a real implementation, this would create an Order object
        return None
    
    def update(self, symbol: str, data: pd.DataFrame) -> List[Order]:
        """
        Update the strategy with new data and generate orders.
        
        This is the main entry point for strategy execution.
        
        Args:
            symbol: The market symbol
            data: OHLCV data as a pandas DataFrame
            
        Returns:
            List of orders to execute
        """
        if symbol not in self.symbols:
            self.logger.warning(f"Symbol {symbol} not in strategy symbols list")
            return []
        
        # Analyze the data
        analysis = self.analyze(symbol, data)
        
        # Generate signals
        signals = self.generate_signals(symbol, analysis)
        
        # Create orders from signals
        orders = []
        for signal in signals:
            order = self.create_order(signal)
            if order:
                orders.append(order)
        
        return orders
    
    def start(self) -> None:
        """Start the strategy."""
        if not self.is_running:
            self.initialize()
            self.is_running = True
            self.logger.info(f"Started strategy: {self.name}")
    
    def stop(self) -> None:
        """Stop the strategy."""
        if self.is_running:
            self.is_running = False
            self.logger.info(f"Stopped strategy: {self.name}")
    
    def get_state(self) -> Dict[str, Any]:
        """
        Get the current state of the strategy.
        
        Returns:
            Dictionary with strategy state
        """
        return {
            "name": self.name,
            "symbols": self.symbols,
            "timeframe": self.timeframe,
            "parameters": self.parameters,
            "is_running": self.is_running,
            "last_update_time": self.last_update_time,
            "state": self.state,
        }
    
    def set_state(self, state: Dict[str, Any]) -> None:
        """
        Set the state of the strategy.
        
        Args:
            state: Dictionary with strategy state
        """
        if "state" in state:
            self.state = state["state"]
        if "parameters" in state:
            self.parameters = state["parameters"]
        if "is_running" in state:
            self.is_running = state["is_running"]
        if "last_update_time" in state:
            self.last_update_time = state["last_update_time"]
        
        self.logger.debug(f"Updated strategy state: {self.name}")
    
    def __str__(self) -> str:
        """String representation of the strategy."""
        return f"{self.name} ({', '.join(self.symbols)} @ {self.timeframe})" 