"""
Relative Strength Index (RSI) strategy implementation.
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import pandas as pd
import numpy as np

from ..trading.order import Order, OrderSide, OrderType
from .base import Strategy, StrategyConfig
from .indicators import calculate_rsi


@dataclass
class RSIConfig(StrategyConfig):
    """Configuration for RSI strategy."""
    rsi_period: int = 14
    oversold_threshold: int = 30
    overbought_threshold: int = 70
    

class RSIStrategy(Strategy):
    """
    Relative Strength Index (RSI) strategy.
    
    This strategy generates buy signals when the RSI crosses below the oversold level
    and sell signals when the RSI crosses above the overbought level.
    """
    
    def __init__(self, config: RSIConfig):
        """
        Initialize the RSI strategy.
        
        Args:
            config: Strategy configuration
        """
        super().__init__(config)
        self.config: RSIConfig = config  # Type hint for IDE support
    
    def initialize(self) -> None:
        """Initialize the strategy before running."""
        self.logger.info(f"Initializing RSI strategy: {self.name}")
        
        # Initialize state for each symbol
        for symbol in self.symbols:
            self.state[symbol] = {
                "last_signal": None,
                "position_size": 0.0,
                "entry_price": 0.0,
                "last_rsi": None,
            }
    
    def analyze(self, symbol: str, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze market data using RSI.
        
        Args:
            symbol: The market symbol
            data: OHLCV data as a pandas DataFrame
            
        Returns:
            Dictionary with analysis results
        """
        # Ensure we have enough data
        if len(data) < self.config.rsi_period + 1:
            self.logger.warning(f"Not enough data for {symbol} RSI analysis")
            return {"error": "Not enough data"}
        
        # Calculate RSI
        data['rsi'] = calculate_rsi(data, self.config.rsi_period)
        
        # Get the latest data point
        latest = data.iloc[-1]
        previous = data.iloc[-2] if len(data) > 1 else None
        
        # Get current state
        symbol_state = self.state.get(symbol, {
            "last_signal": None,
            "position_size": 0.0,
            "entry_price": 0.0,
            "last_rsi": None,
        })
        
        # Check for RSI signals
        rsi_value = latest['rsi']
        prev_rsi = previous['rsi'] if previous is not None else symbol_state["last_rsi"]
        
        # Detect crossovers
        oversold_crossover = (prev_rsi is not None and 
                             prev_rsi <= self.config.oversold_threshold and 
                             rsi_value > self.config.oversold_threshold)
        
        overbought_crossover = (prev_rsi is not None and 
                               prev_rsi >= self.config.overbought_threshold and 
                               rsi_value < self.config.overbought_threshold)
        
        # Extreme values
        is_oversold = rsi_value <= self.config.oversold_threshold
        is_overbought = rsi_value >= self.config.overbought_threshold
        
        # Update state
        symbol_state["last_rsi"] = rsi_value
        self.state[symbol] = symbol_state
        
        # Prepare analysis results
        analysis = {
            "symbol": symbol,
            "timestamp": latest.name,
            "close": latest['close'],
            "rsi": rsi_value,
            "prev_rsi": prev_rsi,
            "is_oversold": is_oversold,
            "is_overbought": is_overbought,
            "oversold_crossover": oversold_crossover,
            "overbought_crossover": overbought_crossover,
            "data": data,  # Include the full data for reference
        }
        
        return analysis
    
    def generate_signals(self, symbol: str, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate trading signals based on RSI analysis.
        
        Args:
            symbol: The market symbol
            analysis: Analysis results from the analyze method
            
        Returns:
            List of signal dictionaries
        """
        signals = []
        
        # Check for errors in analysis
        if "error" in analysis:
            self.logger.warning(f"Analysis error for {symbol}: {analysis['error']}")
            return signals
        
        # Get current state
        symbol_state = self.state.get(symbol, {
            "last_signal": None,
            "position_size": 0.0,
            "entry_price": 0.0,
        })
        
        # Generate buy signal on oversold conditions
        if analysis["oversold_crossover"]:
            # RSI crossed from below oversold threshold to above
            signal = {
                "symbol": symbol,
                "timestamp": analysis["timestamp"],
                "type": "buy",
                "price": analysis["close"],
                "reason": f"RSI crossed above oversold level ({self.config.oversold_threshold})",
                "rsi": analysis["rsi"],
            }
            signals.append(signal)
            
            # Update state
            symbol_state["last_signal"] = "buy"
        
        # Generate sell signal on overbought conditions
        elif analysis["overbought_crossover"]:
            # RSI crossed from above overbought threshold to below
            signal = {
                "symbol": symbol,
                "timestamp": analysis["timestamp"],
                "type": "sell",
                "price": analysis["close"],
                "reason": f"RSI crossed below overbought level ({self.config.overbought_threshold})",
                "rsi": analysis["rsi"],
            }
            signals.append(signal)
            
            # Update state
            symbol_state["last_signal"] = "sell"
        
        # Update state
        self.state[symbol] = symbol_state
        
        return signals
    
    def create_order(self, signal: Dict[str, Any]) -> Optional[Order]:
        """
        Create an order based on a signal.
        
        Args:
            signal: Signal dictionary
            
        Returns:
            Order object or None if no order should be created
        """
        if signal["type"] == "buy":
            # Create a buy order
            order = Order(
                symbol=signal["symbol"],
                side=OrderSide.BUY,
                type=OrderType.MARKET,
                quantity=1.0,  # This would be calculated based on position sizing
                price=signal["price"],
                params={"reason": signal["reason"]}
            )
            return order
        
        elif signal["type"] == "sell":
            # Create a sell order
            order = Order(
                symbol=signal["symbol"],
                side=OrderSide.SELL,
                type=OrderType.MARKET,
                quantity=1.0,  # This would be calculated based on current position
                price=signal["price"],
                params={"reason": signal["reason"]}
            )
            return order
        
        return None 