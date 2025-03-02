"""
Relative Strength Index (RSI) strategy implementation.
"""
from typing import Any, Dict, List, Optional

import pandas as pd
import numpy as np

from ..trading.order import Order, OrderSide, OrderType
from .base import Strategy


class RSIStrategy(Strategy):
    """
    Relative Strength Index (RSI) strategy.
    
    This strategy generates buy signals when the RSI crosses below the oversold level
    and sell signals when the RSI crosses above the overbought level.
    """
    
    def __init__(self, name: str, symbols: List[str], timeframe: str = '1h', 
                 parameters: Optional[Dict[str, Any]] = None):
        """
        Initialize the RSI strategy.
        
        Args:
            name: Strategy name
            symbols: List of symbols to trade
            timeframe: Timeframe for analysis
            parameters: Strategy-specific parameters
        """
        # Default parameters
        default_params = {
            "rsi_period": 14,
            "oversold_threshold": 30,
            "overbought_threshold": 70,
            "risk_per_trade": 0.02,  # 2% risk per trade
        }
        
        # Merge with provided parameters
        if parameters:
            default_params.update(parameters)
            
        super().__init__(name, symbols, timeframe, default_params)
    
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
    
    def calculate_rsi(self, data: pd.DataFrame, period: int = 14) -> pd.Series:
        """
        Calculate the Relative Strength Index (RSI).
        
        Args:
            data: OHLCV data as a pandas DataFrame
            period: RSI period
            
        Returns:
            Series with RSI values
        """
        # Calculate price changes
        delta = data['close'].diff()
        
        # Separate gains and losses
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        
        # Calculate average gain and loss
        avg_gain = gain.rolling(window=period).mean()
        avg_loss = loss.rolling(window=period).mean()
        
        # Calculate RS
        rs = avg_gain / avg_loss
        
        # Calculate RSI
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
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
        if len(data) < self.parameters["rsi_period"] + 1:
            self.logger.warning(f"Not enough data for {symbol} analysis")
            return {"error": "Not enough data"}
        
        # Calculate RSI
        rsi_period = self.parameters["rsi_period"]
        data['rsi'] = self.calculate_rsi(data, rsi_period)
        
        # Get the latest data points
        latest = data.iloc[-1]
        previous = data.iloc[-2] if len(data) > 1 else None
        
        # Get current state for this symbol
        symbol_state = self.state.get(symbol, {
            "last_signal": None,
            "position_size": 0.0,
            "entry_price": 0.0,
            "last_rsi": None,
        })
        
        # Check for RSI crossovers
        oversold_crossover = False
        overbought_crossover = False
        
        if previous is not None and not pd.isna(latest['rsi']) and not pd.isna(previous['rsi']):
            # Check for oversold crossover (RSI crosses below oversold threshold)
            if (previous['rsi'] >= self.parameters["oversold_threshold"] and 
                latest['rsi'] < self.parameters["oversold_threshold"]):
                oversold_crossover = True
                
            # Check for overbought crossover (RSI crosses above overbought threshold)
            if (previous['rsi'] <= self.parameters["overbought_threshold"] and 
                latest['rsi'] > self.parameters["overbought_threshold"]):
                overbought_crossover = True
        
        # Update state with latest RSI
        symbol_state["last_rsi"] = latest['rsi'] if not pd.isna(latest['rsi']) else None
        self.state[symbol] = symbol_state
        
        # Prepare analysis results
        analysis = {
            "symbol": symbol,
            "timestamp": latest.name,
            "close": latest['close'],
            "rsi": latest['rsi'],
            "oversold_threshold": self.parameters["oversold_threshold"],
            "overbought_threshold": self.parameters["overbought_threshold"],
            "oversold_crossover": oversold_crossover,
            "overbought_crossover": overbought_crossover,
            "data": data,  # Include the full data for signal generation
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
        
        # Get current state for this symbol
        symbol_state = self.state.get(symbol, {
            "last_signal": None,
            "position_size": 0.0,
            "entry_price": 0.0,
            "last_rsi": None,
        })
        
        # Check for oversold crossover (buy signal)
        if analysis["oversold_crossover"]:
            # Generate buy signal
            signal = {
                "symbol": symbol,
                "timestamp": analysis["timestamp"],
                "type": "buy",
                "price": analysis["close"],
                "reason": f"RSI oversold crossover ({analysis['rsi']:.2f} < {analysis['oversold_threshold']})",
                "rsi": analysis["rsi"],
            }
            signals.append(signal)
            
            # Update state
            symbol_state["last_signal"] = "buy"
            
        # Check for overbought crossover (sell signal)
        elif analysis["overbought_crossover"]:
            # Generate sell signal
            signal = {
                "symbol": symbol,
                "timestamp": analysis["timestamp"],
                "type": "sell",
                "price": analysis["close"],
                "reason": f"RSI overbought crossover ({analysis['rsi']:.2f} > {analysis['overbought_threshold']})",
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