from typing import List, Dict, Any
import pandas as pd
import numpy as np
from abc import ABC, abstractmethod
from .base import Strategy, StrategyConfig
from ..core.domain import SignalType


class CompositeStrategy(Strategy):
    """Base class for composite trading strategies."""
    
    def __init__(self, config: StrategyConfig, strategies: List[Strategy],
                 weights: List[float] = None):
        """
        Initialize a composite strategy.
        
        Args:
            config: Strategy configuration
            strategies: List of strategy instances to combine
            weights: Optional list of weights for each strategy (must sum to 1.0)
        
        Raises:
            ValueError: If weights don't match strategies or don't sum to 1.0
        """
        super().__init__(config)
        self.strategies = strategies
        
        # Handle empty strategies list
        if not strategies:
            self.weights = []
            return
            
        self.weights = weights or [1.0 / len(strategies)] * len(strategies)
        
        if len(self.weights) != len(strategies):
            raise ValueError("Number of weights must match number of strategies")
            
        if not np.isclose(sum(self.weights), 1.0):
            raise ValueError("Weights must sum to 1.0")
    
    def initialize(self) -> None:
        """Initialize all component strategies."""
        for strategy in self.strategies:
            strategy.initialize()
    
    def analyze(self, symbol: str, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze market data using all component strategies.
        
        Args:
            symbol: The trading symbol to analyze
            data: DataFrame containing market data
            
        Returns:
            Dictionary containing analysis results from all strategies
        """
        results = {}
        for i, strategy in enumerate(self.strategies):
            strategy_name = f"{strategy.name}_{i}"
            results[strategy_name] = strategy.analyze(symbol, data)
        
        return {
            "component_analyses": results,
            "strategies": self.strategies,
            "weights": self.weights
        }
    
    def generate_signals(self, symbol: str, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate trading signals based on composite analysis.
        
        Args:
            symbol: The trading symbol
            analysis: Analysis results from analyze() method
            
        Returns:
            List of signal dictionaries
        """
        # Get individual signals from each strategy
        signals = []
        for i, strategy in enumerate(self.strategies):
            strategy_name = f"{strategy.name}_{i}"
            if strategy_name in analysis["component_analyses"]:
                strategy_signals = strategy.generate_signals(
                    symbol, analysis["component_analyses"][strategy_name]
                )
                if strategy_signals:
                    signals.extend(strategy_signals)
        
        # If no signals were generated, return empty list
        if not signals:
            return []
        
        # Combine signals using the calculate_signal method
        combined_signal_type = self.calculate_signal(data=None, signals=signals)
        
        # Create a combined signal
        return [{
            "symbol": symbol,
            "signal_type": combined_signal_type,
            "price": signals[0].get("price", 0.0),  # Use price from first signal
            "timestamp": signals[0].get("timestamp"),  # Use timestamp from first signal
            "confidence": self._calculate_confidence(signals),
            "metadata": {
                "composite_type": self.__class__.__name__,
                "component_signals": signals,
                "weights": self.weights
            }
        }]
    
    def _calculate_confidence(self, signals: List[Dict[str, Any]]) -> float:
        """
        Calculate confidence level for the composite signal.
        
        Args:
            signals: List of component signals
            
        Returns:
            Confidence value between 0.0 and 1.0
        """
        # Default implementation: average of component confidences
        confidences = [s.get("confidence", 0.5) for s in signals]
        return sum(confidences) / len(confidences) if confidences else 0.5
    
    def calculate_signal(self, data: pd.DataFrame, signals: List[Dict[str, Any]] = None) -> SignalType:
        """
        Calculate combined signal from multiple strategies.
        
        Args:
            data: DataFrame containing market data (may be None if signals provided)
            signals: Optional list of signals from component strategies
            
        Returns:
            Combined SignalType
        """
        # Handle empty strategies case
        if not self.strategies and not signals:
            return SignalType.HOLD
            
        if signals is None:
            # If no signals provided, get them from each strategy
            if data is None:
                raise ValueError("Either data or signals must be provided")
                
            signals = []
            for strategy in self.strategies:
                analysis = strategy.analyze(self.symbols[0], data)
                strategy_signals = strategy.generate_signals(self.symbols[0], analysis)
                if strategy_signals:
                    signals.extend(strategy_signals)
        
        # Extract signal types
        signal_types = [s.get("signal_type", SignalType.HOLD) for s in signals]
        
        # Convert signals to numeric values
        numeric_signals = [
            1 if s == SignalType.BUY else
            -1 if s == SignalType.SELL else
            0 for s in signal_types
        ]
        
        # If no signals or weights, return HOLD
        if not numeric_signals or not self.weights:
            return SignalType.HOLD
            
        # Use provided weights or create equal weights for the signals
        weights_to_use = self.weights
        if len(weights_to_use) != len(numeric_signals):
            weights_to_use = [1.0 / len(numeric_signals)] * len(numeric_signals)
            
        # Calculate weighted average
        weighted_signal = sum(
            signal * weight
            for signal, weight in zip(numeric_signals, weights_to_use[:len(numeric_signals)])
        )
        
        # Convert back to SignalType based on threshold
        if weighted_signal >= 0.5:  # Changed from > to >= for consistency with test
            return SignalType.BUY
        elif weighted_signal <= -0.5:  # Changed from < to <= for consistency
            return SignalType.SELL
        return SignalType.HOLD


class VotingStrategy(CompositeStrategy):
    """Strategy that uses majority voting to combine signals."""
    
    def calculate_signal(self, data: pd.DataFrame, signals: List[Dict[str, Any]] = None) -> SignalType:
        """
        Calculate signal using majority voting.
        
        Args:
            data: DataFrame containing market data (may be None if signals provided)
            signals: Optional list of signals from component strategies
            
        Returns:
            Combined SignalType based on voting
        """
        # Handle empty strategies case
        if not self.strategies and not signals:
            return SignalType.HOLD
            
        if signals is None:
            # If no signals provided, get them from each strategy
            if data is None:
                raise ValueError("Either data or signals must be provided")
                
            signals = []
            for strategy in self.strategies:
                analysis = strategy.analyze(self.symbols[0], data)
                strategy_signals = strategy.generate_signals(self.symbols[0], analysis)
                if strategy_signals:
                    signals.extend(strategy_signals)
        
        # Extract signal types
        signal_types = [s.get("signal_type", SignalType.HOLD) for s in signals]
        
        # If no signals or weights, return HOLD
        if not signal_types or not self.weights:
            return SignalType.HOLD
            
        # Use provided weights or create equal weights for the signals
        weights_to_use = self.weights
        if len(weights_to_use) != len(signal_types):
            weights_to_use = [1.0 / len(signal_types)] * len(signal_types)
        
        # Apply weighted voting
        buy_score = sum(
            weight for s, weight in zip(signal_types, weights_to_use)
            if s == SignalType.BUY
        )
        
        sell_score = sum(
            weight for s, weight in zip(signal_types, weights_to_use)
            if s == SignalType.SELL
        )
        
        # Make decision
        if buy_score > sell_score and buy_score >= 0.5:  # Changed from > to >= for consistency with test
            return SignalType.BUY
        elif sell_score > buy_score and sell_score >= 0.5:  # Changed from > to >= for consistency
            return SignalType.SELL
        return SignalType.HOLD 