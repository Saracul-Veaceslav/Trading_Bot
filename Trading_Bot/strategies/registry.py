"""
Strategy Registry

This module provides functionality for registering, loading, and creating
trading strategies dynamically.
"""
import os
import sys
import importlib
import inspect
import logging
from typing import Dict, Any, List, Type, Optional, Callable

from trading_bot.strategies.base import Strategy

logger = logging.getLogger('trading_bot.strategies.registry')

# Global registry of strategy classes
_strategy_registry: Dict[str, Type[Strategy]] = {}

# Global registry of strategy creators
_strategy_creators: Dict[str, Callable[..., Strategy]] = {}

def register_strategy(strategy_class: Type[Strategy]) -> None:
    """
    Register a strategy class in the registry.
    
    Args:
        strategy_class: Strategy class to register
    """
    if not inspect.isclass(strategy_class) or not issubclass(strategy_class, Strategy):
        raise TypeError("Expected a class derived from Strategy")
    
    # Extract strategy name from class name
    strategy_name = strategy_class.__name__.lower()
    
    # Register the strategy class
    _strategy_registry[strategy_name] = strategy_class
    logger.debug(f"Registered strategy: {strategy_name}")

def register_strategy_creator(name: str, creator_func: Callable[..., Strategy]) -> None:
    """
    Register a strategy creator function.
    
    Args:
        name: Name for the strategy
        creator_func: Function that creates a strategy instance
    """
    if not callable(creator_func):
        raise TypeError("Expected a callable creator function")
    
    _strategy_creators[name.lower()] = creator_func
    logger.debug(f"Registered strategy creator: {name}")

def discover_strategies(strategies_dir: Optional[str] = None) -> None:
    """
    Discover and register strategy classes from Python modules.
    
    Args:
        strategies_dir: Directory to scan for strategy modules, defaults to the 'strategies' directory
    """
    if strategies_dir is None:
        # Default to the directory where this module is located
        strategies_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Get all Python files in the directory
    for root, _, files in os.walk(strategies_dir):
        for file in files:
            if file.endswith('.py') and not file.startswith('__'):
                # Convert file path to module name
                rel_path = os.path.relpath(os.path.join(root, file), os.path.dirname(strategies_dir))
                module_path = os.path.splitext(rel_path)[0].replace(os.path.sep, '.')
                
                try:
                    # Import the module
                    module = importlib.import_module(f"trading_bot.{module_path}")
                    
                    # Find and register all Strategy subclasses in the module
                    for name, obj in inspect.getmembers(module):
                        if (inspect.isclass(obj) and 
                            issubclass(obj, Strategy) and 
                            obj != Strategy):  # Exclude the base class
                            register_strategy(obj)
                            
                except (ImportError, AttributeError) as e:
                    logger.warning(f"Error importing strategy module {module_path}: {e}")

def get_available_strategies() -> List[str]:
    """
    Get the list of available strategy names.
    
    Returns:
        List[str]: List of registered strategy names
    """
    # Combine strategies from both registries
    all_strategies = set(_strategy_registry.keys()) | set(_strategy_creators.keys())
    return sorted(list(all_strategies))

def create_strategy(name: str, config: Optional[Dict[str, Any]] = None) -> Strategy:
    """
    Create a strategy instance by name.
    
    Args:
        name: Name of the strategy to create
        config: Configuration parameters for the strategy
        
    Returns:
        Strategy: Instance of the requested strategy
        
    Raises:
        ValueError: If the strategy is not found
    """
    if config is None:
        config = {}
    
    name = name.lower()
    
    # Try to create using a registered creator function
    if name in _strategy_creators:
        logger.debug(f"Creating strategy '{name}' using creator function")
        return _strategy_creators[name](**config)
    
    # Try to create using a registered strategy class
    if name in _strategy_registry:
        logger.debug(f"Creating strategy '{name}' using registered class")
        return _strategy_registry[name](**config)
    
    # Try to dynamically import and create
    try:
        # Try different module paths
        possible_paths = [
            f"trading_bot.strategies.{name}",
            f"trading_bot.strategies.{name}.{name}",
        ]
        
        for module_path in possible_paths:
            try:
                module = importlib.import_module(module_path)
                
                # Find a class that matches the strategy name
                for class_name, cls in inspect.getmembers(module, inspect.isclass):
                    if class_name.lower() == name or class_name.lower() == f"{name}strategy":
                        if issubclass(cls, Strategy):
                            # Register for future use
                            register_strategy(cls)
                            logger.debug(f"Dynamically loaded strategy '{name}' from {module_path}")
                            return cls(**config)
                
            except ImportError:
                continue
        
        raise ValueError(f"Strategy '{name}' not found in any expected module path")
        
    except Exception as e:
        logger.error(f"Error creating strategy '{name}': {e}")
        raise ValueError(f"Failed to create strategy '{name}': {e}")

def register_builtin_strategies() -> None:
    """Register built-in strategies that are included with the Trading Bot."""
    try:
        # Import and register SMA Crossover strategy
        from trading_bot.strategies.sma_crossover import SMAcrossover
        register_strategy(SMAcrossover)
        
        # Register more built-in strategies here
        
    except ImportError as e:
        logger.warning(f"Error registering built-in strategies: {e}")

# Initialize the registry with built-in strategies
register_builtin_strategies()

# Auto-discover strategies
discover_strategies() 