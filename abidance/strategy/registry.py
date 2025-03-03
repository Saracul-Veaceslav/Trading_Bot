"""
Strategy registry module for managing strategy implementations.
"""
from typing import Any, Dict, List, Optional, Type
import logging


from ..exceptions import StrategyError
from .base import Strategy


class StrategyRegistry:
    """
    Registry for managing strategy implementations.

    This class provides a central registry for strategy classes and instances,
    allowing for dynamic strategy creation and management.
    """

    def __init__(self):
        """Initialize the strategy registry."""
        self.strategy_classes: Dict[str, Type[Strategy]] = {}
        self.strategy_instances: Dict[str, Strategy] = {}
        self.logger = logging.getLogger(__name__)

    def register_strategy_class(self, strategy_id: str, strategy_class: Type[Strategy]) -> None:
        """
        Register a strategy class.

        Args:
            strategy_id: Identifier for the strategy
            strategy_class: Strategy class to register
        """
        if strategy_id in self.strategy_classes:
            self.logger.warning("Overwriting existing strategy class: %s", strategy_id)

        self.strategy_classes[strategy_id] = strategy_class
        self.logger.debug("Registered strategy class: %s", strategy_id)

    def create_strategy(self, strategy_id: str, name: str, symbols: List[str],
                        timeframe: str = '1h', parameters: Optional[Dict[str, Any]] = None) -> Strategy:
        """
        Create a strategy instance.

        Args:
            strategy_id: Identifier for the strategy class
            name: Name for the strategy instance
            symbols: List of symbols to trade
            timeframe: Timeframe for analysis
            parameters: Strategy-specific parameters

        Returns:
            The created Strategy instance

        Raises:
            StrategyError: If the strategy class is not registered
        """
        if strategy_id not in self.strategy_classes:
            raise StrategyError(f"Unknown strategy: {strategy_id}")

        strategy_class = self.strategy_classes[strategy_id]
        strategy = strategy_class(
            name=name,
            symbols=symbols,
            timeframe=timeframe,
            parameters=parameters
        )

        # Add to instances
        instance_id = f"{strategy_id}_{name}"
        self.strategy_instances[instance_id] = strategy

        self.logger.info("Created strategy instance: %s", instance_id)
        return strategy

    def get_strategy(self, instance_id: str) -> Strategy:
        """
        Get a strategy instance.

        Args:
            instance_id: Identifier for the strategy instance

        Returns:
            The Strategy instance

        Raises:
            StrategyError: If the strategy instance is not found
        """
        if instance_id not in self.strategy_instances:
            raise StrategyError(f"Strategy instance not found: {instance_id}")

        return self.strategy_instances[instance_id]

    def remove_strategy(self, instance_id: str) -> None:
        """
        Remove a strategy instance.

        Args:
            instance_id: Identifier for the strategy instance

        Raises:
            StrategyError: If the strategy instance is not found
        """
        if instance_id not in self.strategy_instances:
            raise StrategyError(f"Strategy instance not found: {instance_id}")

        # Stop the strategy if it's running
        strategy = self.strategy_instances[instance_id]
        if strategy.is_running:
            strategy.stop()

        del self.strategy_instances[instance_id]
        self.logger.info("Removed strategy instance: %s", instance_id)

    def get_all_strategies(self) -> List[Strategy]:
        """
        Get all registered strategy instances.

        Returns:
            List of Strategy instances
        """
        return list(self.strategy_instances.values())

    def get_available_strategy_classes(self) -> List[str]:
        """
        Get all registered strategy class IDs.

        Returns:
            List of strategy class IDs
        """
        return list(self.strategy_classes.keys())
