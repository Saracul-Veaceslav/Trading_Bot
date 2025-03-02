"""
Simple Moving Average (SMA) strategy implementation.
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import pandas as pd
import numpy as np

from ..trading.order import Order, OrderSide, OrderType
from .base import Strategy, StrategyConfig
from .indicators import calculate_sma, detect_crossover


@dataclass
class SMAConfig(StrategyConfig):
    """Configuration for SMA strategy."""
    fast_period: int = 20
    slow_period: int = 50
    volume_factor: float = 1.5
    

class SMAStrategy(Strategy):
    """
    Simple Moving Average (SMA) crossover strategy.
    
    This strategy generates buy signals when the fast SMA crosses above the slow SMA,
    and sell signals when the fast SMA crosses below the slow SMA.
    """
    
    def __init__(self, config: SMAConfig):
        """
        Initialize the SMA strategy.
        
        Args:
            config: Strategy configuration
        """
        super().__init__(config)
        self.config: SMAConfig = config  # Type hint for IDE support
        
    def initialize(self) -> None:
        """Initialize the strategy before running."""
        self.logger.info(f"Initializing SMA strategy: {self.name}")
        
        # Initialize state for each symbol
        for symbol in self.symbols:
            self.state[symbol] = {
                "last_signal": None,
                "position_size": 0.0,
                "entry_price": 0.0,
            }
    
    def analyze(self, symbol: str, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze market data using SMA crossover.
        
        Args:
            symbol: The market symbol
            data: OHLCV data as a pandas DataFrame
            
        Returns:
            Dictionary with analysis results
        """
        # Ensure we have enough data
        if len(data) < self.config.slow_period:
            self.logger.warning(f"Not enough data for {symbol} analysis")
            return {"error": "Not enough data"}
        
        # Calculate SMAs
        data['fast_sma'] = calculate_sma(data, self.config.fast_period)
        data['slow_sma'] = calculate_sma(data, self.config.slow_period)
        
        # Detect crossovers
        data['crossover'] = detect_crossover(data['fast_sma'], data['slow_sma'])
        
        # Volume analysis
        data['volume_sma'] = calculate_sma(data, self.config.fast_period, 'volume')
        data['volume_ratio'] = data['volume'] / data['volume_sma']
        
        # Get the latest data point
        latest = data.iloc[-1]
        
        # Check if we have a crossover
        crossover_value = latest['crossover']
        crossover = crossover_value != 0
        crossover_type = None
        
        if crossover:
            if crossover_value > 0:
                crossover_type = "bullish"
            else:
                crossover_type = "bearish"
        
        # Prepare analysis results
        analysis = {
            "symbol": symbol,
            "timestamp": latest.name,
            "close": latest['close'],
            "fast_sma": latest['fast_sma'],
            "slow_sma": latest['slow_sma'],
            "crossover": crossover,
            "crossover_type": crossover_type,
            "volume_ratio": latest['volume_ratio'],
            "data": data,  # Include the full data for signal generation
        }
        
        return analysis
    
    def generate_signals(self, symbol: str, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate trading signals based on SMA analysis.
        
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
        
        # Get current state for this symbol
        symbol_state = self.state.get(symbol, {
            "last_signal": None,
            "position_size": 0.0,
            "entry_price": 0.0,
        })
        
        # Check for crossover
        if analysis["crossover"]:
            # Volume confirmation
            volume_confirmed = analysis["volume_ratio"] >= self.config.volume_factor
            
            if analysis["crossover_type"] == "bullish" and volume_confirmed:
                # Generate buy signal
                signal = {
                    "symbol": symbol,
                    "timestamp": analysis["timestamp"],
                    "type": "buy",
                    "price": analysis["close"],
                    "reason": "SMA bullish crossover with volume confirmation",
                    "fast_sma": analysis["fast_sma"],
                    "slow_sma": analysis["slow_sma"],
                    "volume_ratio": analysis["volume_ratio"],
                }
                signals.append(signal)
                
                # Update state
                symbol_state["last_signal"] = "buy"
                
            elif analysis["crossover_type"] == "bearish" and volume_confirmed:
                # Generate sell signal
                signal = {
                    "symbol": symbol,
                    "timestamp": analysis["timestamp"],
                    "type": "sell",
                    "price": analysis["close"],
                    "reason": "SMA bearish crossover with volume confirmation",
                    "fast_sma": analysis["fast_sma"],
                    "slow_sma": analysis["slow_sma"],
                    "volume_ratio": analysis["volume_ratio"],
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