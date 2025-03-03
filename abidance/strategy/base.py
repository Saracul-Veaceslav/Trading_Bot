"""
Base strategy module defining the abstract Strategy interface.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union, ClassVar
import logging

from dataclasses import dataclass, field


import pandas as pd

from ..trading.order import Order


@dataclass
class StrategyConfig:
    """Base configuration for trading strategies."""
    name: str
    symbols: List[str]
    timeframe: str = '1h'
    risk_per_trade: float = 0.02  # Default 2% risk per trade
    parameters: Dict[str, Any] = field(default_factory=dict)


class Strategy(ABC):
    """
    Abstract base class for trading strategies.

    All strategy implementations must inherit from this class and implement
    its abstract methods to provide a consistent interface.
    """

    def __init__(self, config: StrategyConfig):
        """
        Initialize the strategy.

        Args:
            config: Strategy configuration
        """
        self.config = config
        self.name = config.name
        self.symbols = config.symbols
        self.timeframe = config.timeframe
        self.parameters = config.parameters
        self.logger = logging.getLogger(f"{__name__}.{self.name}")

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
        Analyze market data and compute indicators.

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
        Generate trading signals based on analysis results.

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
        # Default implementation returns None
        # Subclasses can override this method to create orders
        return None

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
        # Analyze market data
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
        self.is_running = True
        self.initialize()

    def stop(self) -> None:
        """Stop the strategy."""
        self.is_running = False

    def get_state(self) -> Dict[str, Any]:
        """
        Get the current state of the strategy.

        Returns:
            Dictionary with the current state
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
            state: Dictionary with the state to set
        """
        if "state" in state:
            self.state = state["state"]
        if "last_update_time" in state:
            self.last_update_time = state["last_update_time"]

    def __str__(self) -> str:
        """String representation of the strategy."""
        return f"{self.name} ({self.__class__.__name__})"

    def backtest(self, data: pd.DataFrame, initial_capital: float = 10000.0) -> pd.DataFrame:
        """
        Run a backtest of the strategy on historical data.

        Args:
            data: Historical price data as a pandas DataFrame
            initial_capital: Initial capital for the backtest

        Returns:
            DataFrame with trade results
        """
        self.logger.info("Starting backtest for %s strategy", self.name)

        # Initialize backtest variables
        equity = initial_capital
        position = 0
        trades = []

        # Make a copy of the data to avoid modifying the original
        df = data.copy()

        # Analyze the entire dataset
        symbol = self.symbols[0] if self.symbols else "UNKNOWN"
        analysis = self.analyze(symbol, df)

        # Generate signals for the entire dataset
        signals = self.generate_signals(symbol, analysis)

        # Process signals and simulate trades
        for i, signal in enumerate(signals):
            timestamp = signal.get('timestamp', df.index[i] if i < len(df) else None)
            signal_type = signal.get('type')
            price = signal.get('price', df['close'].iloc[i] if i < len(df) else None)

            if not timestamp or not price:
                continue

            if signal_type == 'buy' and position <= 0:
                # Calculate position size based on risk
                size = (equity * self.config.risk_per_trade) / price
                cost = size * price

                # Enter long position
                position = size
                entry_price = price
                entry_time = timestamp

            elif signal_type == 'sell' and position >= 0:
                # Calculate position size based on risk
                size = (equity * self.config.risk_per_trade) / price
                cost = size * price

                # Enter short position
                position = -size
                entry_price = price
                entry_time = timestamp

            elif signal_type == 'exit' and position != 0:
                # Exit position
                exit_price = price
                exit_time = timestamp

                # Calculate profit/loss
                if position > 0:  # Long position
                    profit = position * (exit_price - entry_price)
                else:  # Short position
                    profit = -position * (entry_price - exit_price)

                # Update equity
                equity += profit

                # Record trade
                trades.append({
                    'entry_time': entry_time,
                    'exit_time': exit_time,
                    'entry_price': entry_price,
                    'exit_price': exit_price,
                    'position': position,
                    'profit': profit,
                    'equity': equity,
                    'returns': profit / (abs(position) * entry_price)
                })

                # Reset position
                position = 0

        # Close any open position at the end of the backtest
        if position != 0:
            exit_price = df['close'].iloc[-1]
            exit_time = df.index[-1]

            # Calculate profit/loss
            if position > 0:  # Long position
                profit = position * (exit_price - entry_price)
            else:  # Short position
                profit = -position * (entry_price - exit_price)

            # Update equity
            equity += profit

            # Record trade
            trades.append({
                'entry_time': entry_time,
                'exit_time': exit_time,
                'entry_price': entry_price,
                'exit_price': exit_price,
                'position': position,
                'profit': profit,
                'equity': equity,
                'returns': profit / (abs(position) * entry_price)
            })

        # Create DataFrame from trades
        if trades:
            trades_df = pd.DataFrame(trades)
            trades_df.set_index('exit_time', inplace=True)

            # Calculate cumulative returns
            trades_df['cumulative_returns'] = (1 + trades_df['returns']).cumprod()

            self.logger.info("Backtest completed with %s trades", len(trades_df))
            return trades_df
        
            self.logger.warning("No trades were generated during backtest")
            return pd.DataFrame()
