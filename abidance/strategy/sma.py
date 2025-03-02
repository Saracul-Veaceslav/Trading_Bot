"""
Simple Moving Average (SMA) strategy implementation.
"""
from typing import Any, Dict, List, Optional

import pandas as pd
import numpy as np

from ..trading.order import Order, OrderSide, OrderType
from .base import Strategy


class SMAStrategy(Strategy):
    """
    Simple Moving Average (SMA) crossover strategy.
    
    This strategy generates buy signals when the fast SMA crosses above the slow SMA,
    and sell signals when the fast SMA crosses below the slow SMA.
    """
    
    def __init__(self, name: str, symbols: List[str], timeframe: str = '1h', 
                 parameters: Optional[Dict[str, Any]] = None):
        """
        Initialize the SMA strategy.
        
        Args:
            name: Strategy name
            symbols: List of symbols to trade
            timeframe: Timeframe for analysis
            parameters: Strategy-specific parameters
        """
        # Default parameters
        default_params = {
            "fast_period": 20,
            "slow_period": 50,
            "volume_factor": 1.5,
            "risk_per_trade": 0.02,  # 2% risk per trade
        }
        
        # Merge with provided parameters
        if parameters:
            default_params.update(parameters)
            
        super().__init__(name, symbols, timeframe, default_params)
    
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
        if len(data) < self.parameters["slow_period"]:
            self.logger.warning(f"Not enough data for {symbol} analysis")
            return {"error": "Not enough data"}
        
        # Calculate SMAs
        fast_period = self.parameters["fast_period"]
        slow_period = self.parameters["slow_period"]
        
        # Calculate SMAs on the close price
        data['fast_sma'] = data['close'].rolling(window=fast_period).mean()
        data['slow_sma'] = data['close'].rolling(window=slow_period).mean()
        
        # Calculate crossover signals
        data['signal'] = 0
        data.loc[data['fast_sma'] > data['slow_sma'], 'signal'] = 1  # Buy signal
        data.loc[data['fast_sma'] < data['slow_sma'], 'signal'] = -1  # Sell signal
        
        # Calculate signal changes (crossovers)
        data['signal_change'] = data['signal'].diff()
        
        # Volume analysis
        data['volume_sma'] = data['volume'].rolling(window=fast_period).mean()
        data['volume_ratio'] = data['volume'] / data['volume_sma']
        
        # Get the latest data point
        latest = data.iloc[-1]
        
        # Check if we have a crossover
        crossover = False
        crossover_type = None
        
        if not pd.isna(latest['signal_change']):
            if latest['signal_change'] > 0:  # Bullish crossover
                crossover = True
                crossover_type = "bullish"
            elif latest['signal_change'] < 0:  # Bearish crossover
                crossover = True
                crossover_type = "bearish"
        
        # Prepare analysis results
        analysis = {
            "symbol": symbol,
            "timestamp": latest.name,
            "close": latest['close'],
            "fast_sma": latest['fast_sma'],
            "slow_sma": latest['slow_sma'],
            "signal": latest['signal'],
            "volume_ratio": latest['volume_ratio'],
            "crossover": crossover,
            "crossover_type": crossover_type,
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
            volume_confirmed = analysis["volume_ratio"] >= self.parameters["volume_factor"]
            
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
        symbol = signal["symbol"]
        price = signal["price"]
        
        if signal["type"] == "buy":
            # Calculate position size based on risk
            risk_amount = self.parameters["risk_per_trade"]
            # In a real implementation, this would calculate based on account balance
            quantity = risk_amount * 100 / price  # Simplified calculation
            
            order = Order(
                symbol=symbol,
                side=OrderSide.BUY,
                order_type=OrderType.MARKET,
                quantity=quantity,
                price=price
            )
            
            # Update state
            self.state[symbol]["position_size"] = quantity
            self.state[symbol]["entry_price"] = price
            
            return order
            
        elif signal["type"] == "sell":
            # Check if we have a position to sell
            position_size = self.state[symbol]["position_size"]
            
            if position_size > 0:
                order = Order(
                    symbol=symbol,
                    side=OrderSide.SELL,
                    order_type=OrderType.MARKET,
                    quantity=position_size,
                    price=price
                )
                
                # Update state
                self.state[symbol]["position_size"] = 0
                self.state[symbol]["entry_price"] = 0
                
                return order
        
        return None 