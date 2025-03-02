"""
Relative Strength Index (RSI) strategy implementation.
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import pandas as pd
import numpy as np

from ..trading.order import Order, OrderSide, OrderType
from .base import Strategy, StrategyConfig
from .indicators import calculate_rsi, detect_threshold_crossover


@dataclass
class RSIConfig(StrategyConfig):
    """Configuration for RSI strategy."""
    rsi_period: int = 14
    oversold_threshold: int = 30
    overbought_threshold: int = 70
    

class RSIStrategy(Strategy):
    """
    Relative Strength Index (RSI) strategy.
    
    This strategy generates buy signals when the RSI crosses above the oversold level
    and sell signals when the RSI crosses below the overbought level. It identifies
    potential trend reversals using RSI divergence from price.
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
    
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate RSI and threshold crossovers.
        
        Args:
            data: OHLCV data as a pandas DataFrame
            
        Returns:
            DataFrame with added indicator columns
        """
        # Make a copy to avoid modifying the original data
        df = data.copy()
        
        # Calculate RSI
        df['rsi'] = calculate_rsi(df, self.config.rsi_period)
        
        # Convert to boolean Series first to properly handle the logical operations
        is_above_oversold = df['rsi'] > self.config.oversold_threshold
        was_above_oversold = is_above_oversold.shift(1)
        # Use recommended approach from warning message to avoid downcasting warning
        was_above_oversold = was_above_oversold.fillna(False).infer_objects(copy=False)
        was_above_oversold = was_above_oversold.astype(bool)
        
        is_above_overbought = df['rsi'] > self.config.overbought_threshold
        was_above_overbought = is_above_overbought.shift(1)
        # Use recommended approach from warning message to avoid downcasting warning
        was_above_overbought = was_above_overbought.fillna(False).infer_objects(copy=False)
        was_above_overbought = was_above_overbought.astype(bool)
        
        # Detect oversold crossovers (crossing from below to above)
        df['oversold_crossover'] = 0
        df.loc[(~was_above_oversold) & (is_above_oversold), 'oversold_crossover'] = 1
        
        # Detect overbought crossovers (crossing from above to below)
        df['overbought_crossover'] = 0
        df.loc[(was_above_overbought) & (~is_above_overbought), 'overbought_crossover'] = -1
        
        # Mark oversold and overbought conditions
        df['is_oversold'] = df['rsi'] <= self.config.oversold_threshold
        df['is_overbought'] = df['rsi'] >= self.config.overbought_threshold
        
        return df
    
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
        
        # Calculate indicators
        data_with_indicators = self.calculate_indicators(data)
        
        # Get the latest data points
        latest = data_with_indicators.iloc[-1]
        previous = data_with_indicators.iloc[-2] if len(data_with_indicators) > 1 else None
        
        # Get current state for this symbol
        symbol_state = self.state.get(symbol, {
            "last_signal": None,
            "position_size": 0.0,
            "entry_price": 0.0,
            "last_rsi": None,
        })
        
        # Check for RSI signals
        rsi_value = latest['rsi']
        prev_rsi = previous['rsi'] if previous is not None else symbol_state["last_rsi"]
        
        # Update state with the latest RSI value
        symbol_state["last_rsi"] = rsi_value
        self.state[symbol] = symbol_state
        
        # Define oversold and overbought crossovers
        oversold_crossover = latest['oversold_crossover'] > 0  # Crossing above oversold
        overbought_crossover = latest['overbought_crossover'] < 0  # Crossing below overbought
        
        # Prepare analysis results
        analysis = {
            "symbol": symbol,
            "timestamp": latest.name,
            "close": latest['close'],
            "rsi": rsi_value,
            "prev_rsi": prev_rsi,
            "is_oversold": latest['is_oversold'],
            "is_overbought": latest['is_overbought'],
            "oversold_crossover": oversold_crossover,
            "overbought_crossover": overbought_crossover,
            "data": data_with_indicators,
        }
        
        return analysis
    
    def create_signal(self, symbol: str, analysis: Dict[str, Any], signal_type: str) -> Dict[str, Any]:
        """
        Create a standardized signal dictionary.
        
        Args:
            symbol: The market symbol
            analysis: Analysis results
            signal_type: Type of signal ('buy' or 'sell')
            
        Returns:
            Signal dictionary
        """
        reason = ""
        if signal_type == "buy":
            reason = f"RSI crossed above oversold level ({self.config.oversold_threshold})"
        elif signal_type == "sell":
            reason = f"RSI crossed below overbought level ({self.config.overbought_threshold})"
            
        return {
            "symbol": symbol,
            "timestamp": analysis["timestamp"],
            "type": signal_type,
            "price": analysis["close"],
            "reason": reason,
            "rsi": analysis["rsi"],
        }
    
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
            signal = self.create_signal(symbol, analysis, "buy")
            signals.append(signal)
            
            # Update state
            symbol_state["last_signal"] = "buy"
        
        # Generate sell signal on overbought conditions
        elif analysis["overbought_crossover"]:
            # RSI crossed from above overbought threshold to below
            signal = self.create_signal(symbol, analysis, "sell")
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
        order_side = None
        if signal["type"] == "buy":
            order_side = OrderSide.BUY
        elif signal["type"] == "sell":
            order_side = OrderSide.SELL
        else:
            return None
        
        # Create an order
        order = Order(
            symbol=signal["symbol"],
            side=order_side,
            order_type=OrderType.MARKET,
            quantity=1.0,  # This would be calculated based on position sizing
            price=signal["price"]
        )
        return order 