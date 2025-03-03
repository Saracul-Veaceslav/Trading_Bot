"""
Model training pipeline module.

This module provides functionality for training machine learning models,
including time series cross-validation and hyperparameter optimization.
"""
from typing import Dict, Any, Optional, Tuple, List, Callable
from concurrent.futures import ProcessPoolExecutor
import copy
import itertools

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator
from sklearn.model_selection import TimeSeriesSplit
from sklearn.preprocessing import StandardScaler

from .preprocessing import DataPreprocessor
from ..features.base import FeatureGenerator


class ModelTrainer:
    """
    Pipeline for training machine learning models.
    
    This class provides functionality for training and evaluating machine learning
    models with time series cross-validation and hyperparameter optimization.
    """
    
    def __init__(self, 
                 model: BaseEstimator,
                 feature_generator: FeatureGenerator,
                 n_splits: int = 5):
        """
        Initialize the model trainer.
        
        Args:
            model: Scikit-learn model to train
            feature_generator: Feature generator to create features from raw data
            n_splits: Number of splits for time series cross-validation
        """
        self.model = model
        self.feature_generator = feature_generator
        self.preprocessor = DataPreprocessor()
        self.n_splits = n_splits
        self.scaler = StandardScaler()
    
    def prepare_data(self, data: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepare data for training.
        
        Args:
            data: Input DataFrame with OHLCV data
            
        Returns:
            Tuple of (features, labels)
        """
        # Generate features
        features = self.feature_generator.generate(data)
        
        # Prepare labels (next day returns)
        labels = data['close'].pct_change().shift(-1).fillna(0)
        labels = np.where(labels > 0, 1, 0)  # Binary classification
        
        # Scale features
        scaled_features = self.scaler.fit_transform(features)
        
        return scaled_features, labels
    
    def train(self, data: pd.DataFrame) -> Dict[str, float]:
        """
        Train model with time series cross-validation.
        
        Args:
            data: Input DataFrame with OHLCV data
            
        Returns:
            Dictionary of performance metrics
        """
        X, y = self.prepare_data(data)
        
        # Time series cross-validation
        tscv = TimeSeriesSplit(n_splits=self.n_splits)
        metrics = []
        
        for train_idx, val_idx in tscv.split(X):
            X_train, X_val = X[train_idx], X[val_idx]
            y_train, y_val = y[train_idx], y[val_idx]
            
            # Train model
            self.model.fit(X_train, y_train)
            
            # Evaluate
            score = self.model.score(X_val, y_val)
            metrics.append(score)
        
        # Train final model on all data
        self.model.fit(X, y)
        
        return {
            'mean_cv_score': np.mean(metrics),
            'std_cv_score': np.std(metrics)
        }
    
    def predict(self, data: pd.DataFrame) -> np.ndarray:
        """
        Generate predictions for new data.
        
        Args:
            data: Input DataFrame with OHLCV data
            
        Returns:
            Array of predictions
        """
        features = self.feature_generator.generate(data)
        scaled_features = self.scaler.transform(features)
        return self.model.predict(scaled_features)
    
    def generate_parameter_combinations(self, param_grid: Dict[str, List[Any]]) -> List[Dict[str, Any]]:
        """
        Generate all combinations of parameters from a parameter grid.
        
        Args:
            param_grid: Dictionary mapping parameter names to lists of values
            
        Returns:
            List of parameter dictionaries, each representing one combination
        """
        param_names = list(param_grid.keys())
        param_values = list(param_grid.values())
        
        combinations = []
        for values in itertools.product(*param_values):
            combination = dict(zip(param_names, values))
            combinations.append(combination)
        
        return combinations
    
    def evaluate_parameters(self, params: Dict[str, Any], data: pd.DataFrame) -> Dict[str, Any]:
        """
        Evaluate a set of parameters on the data.
        
        Args:
            params: Parameter dictionary to evaluate
            data: Input DataFrame with OHLCV data
            
        Returns:
            Dictionary with evaluation metrics and parameters
        """
        # Create a copy of the model with the specified parameters
        model_copy = copy.deepcopy(self.model)
        model_copy.set_params(**params)
        
        # Create a new trainer with the model copy
        trainer = ModelTrainer(
            model=model_copy,
            feature_generator=self.feature_generator,
            n_splits=self.n_splits
        )
        
        # Train and evaluate
        metrics = trainer.train(data)
        
        # Add parameters to results
        metrics['parameters'] = params
        
        return metrics
    
    def optimize(self, data: pd.DataFrame, param_grid: Dict[str, List[Any]], 
                n_jobs: int = 1) -> List[Dict[str, Any]]:
        """
        Optimize model hyperparameters using grid search.
        
        Args:
            data: Input DataFrame with OHLCV data
            param_grid: Dictionary mapping parameter names to lists of values
            n_jobs: Number of parallel jobs to run
            
        Returns:
            List of dictionaries with evaluation metrics and parameters, sorted by performance
        """
        # Generate parameter combinations
        combinations = self.generate_parameter_combinations(param_grid)
        
        # Evaluate each combination
        results = []
        
        if n_jobs > 1:
            # Parallel execution
            with ProcessPoolExecutor(max_workers=n_jobs) as executor:
                eval_func = lambda params: self.evaluate_parameters(params, data)
                results = list(executor.map(eval_func, combinations))
        else:
            # Sequential execution
            for params in combinations:
                result = self.evaluate_parameters(params, data)
                results.append(result)
        
        # Sort results by performance (descending)
        results.sort(key=lambda x: x['mean_cv_score'], reverse=True)
        
        return results 