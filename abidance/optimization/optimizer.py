"""
Strategy parameter optimization module.

This module provides tools for optimizing trading strategy parameters
through backtesting and performance evaluation.
"""

from typing import Dict, Any, List, Tuple, Callable, Iterator, Type
import numpy as np
from dataclasses import dataclass
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
import logging

from abidance.strategy.base import Strategy

logger = logging.getLogger(__name__)

@dataclass
class OptimizationResult:
    """Results from strategy parameter optimization."""
    parameters: Dict[str, Any]
    performance_metrics: Dict[str, float]
    trades: pd.DataFrame

class StrategyOptimizer:
    """Optimizer for strategy parameters."""
    
    def __init__(self, strategy_class: Type[Strategy],
                 parameter_ranges: Dict[str, List[Any]],
                 metric_function: Callable[[pd.DataFrame], float]):
        """
        Initialize the strategy optimizer.
        
        Args:
            strategy_class: The strategy class to optimize
            parameter_ranges: Dictionary mapping parameter names to lists of possible values
            metric_function: Function that calculates a performance metric from trades DataFrame
        """
        self.strategy_class = strategy_class
        self.parameter_ranges = parameter_ranges
        self.metric_function = metric_function
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
    def _evaluate_parameters(self, params: Dict[str, Any],
                           data: pd.DataFrame) -> OptimizationResult:
        """
        Evaluate a set of parameters.
        
        Args:
            params: Dictionary of parameter values to evaluate
            data: Historical price data
            
        Returns:
            OptimizationResult with performance metrics
        """
        self.logger.debug(f"Evaluating parameters: {params}")
        try:
            strategy = self.strategy_class(**params)
            trades = strategy.backtest(data)
            performance = self.metric_function(trades)
            
            return OptimizationResult(
                parameters=params,
                performance_metrics={'metric': performance},
                trades=trades
            )
        except Exception as e:
            self.logger.error(f"Error evaluating parameters {params}: {str(e)}")
            # Return a result with very poor performance to indicate failure
            return OptimizationResult(
                parameters=params,
                performance_metrics={'metric': float('-inf')},
                trades=pd.DataFrame()
            )
    
    def optimize(self, data: pd.DataFrame, 
                max_iterations: int = 100,
                n_jobs: int = -1) -> List[OptimizationResult]:
        """
        Optimize strategy parameters using grid search.
        
        Args:
            data: Historical price data
            max_iterations: Maximum number of parameter combinations to try
            n_jobs: Number of parallel jobs to run (-1 for all available cores)
            
        Returns:
            List of optimization results sorted by performance
        """
        # Generate parameter combinations
        self.logger.info(f"Starting optimization with max {max_iterations} iterations")
        param_combinations = []
        for params in self._generate_parameter_combinations():
            param_combinations.append(params)
            if len(param_combinations) >= max_iterations:
                break
                
        self.logger.info(f"Generated {len(param_combinations)} parameter combinations")
        
        # Determine number of workers
        if n_jobs <= 0:
            import multiprocessing
            n_jobs = multiprocessing.cpu_count()
        
        # Evaluate parameters in parallel
        results = []
        with ThreadPoolExecutor(max_workers=n_jobs) as executor:
            self.logger.info(f"Evaluating parameters using {n_jobs} workers")
            futures = [
                executor.submit(self._evaluate_parameters, params, data)
                for params in param_combinations
            ]
            
            for future in futures:
                try:
                    results.append(future.result())
                except Exception as e:
                    self.logger.error(f"Error in parameter evaluation: {str(e)}")
                
        # Sort by performance
        results.sort(key=lambda x: x.performance_metrics['metric'], 
                    reverse=True)
        
        self.logger.info(f"Optimization complete. Best metric: {results[0].performance_metrics['metric']}")
        return results
    
    def _generate_parameter_combinations(self) -> Iterator[Dict[str, Any]]:
        """
        Generate combinations of parameters to try.
        
        Yields:
            Dictionary mapping parameter names to values
        """
        keys = list(self.parameter_ranges.keys())
        values = list(self.parameter_ranges.values())
        
        for combination in np.ndindex(*[len(v) for v in values]):
            yield {
                key: values[i][combination[i]]
                for i, key in enumerate(keys)
            } 