"""
Validation module for machine learning models.

This module provides functionality for validating machine learning models,
including time series cross-validation and performance metrics calculation.
"""
from typing import Dict, List, Optional, Tuple, Union, Callable

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score


class TimeSeriesValidator:
    """
    Time series cross-validation for financial data.
    
    This class implements various time series cross-validation strategies,
    including expanding window and sliding window approaches.
    """
    
    def __init__(self, n_splits: int = 5, method: str = 'expanding',
                window_size: Optional[int] = None, test_size: Optional[int] = None):
        """
        Initialize the time series validator.
        
        Args:
            n_splits: Number of train/test splits
            method: Validation method ('expanding' or 'sliding')
            window_size: Size of the training window for sliding window method
            test_size: Size of the test set (if None, calculated based on data size)
        """
        self.n_splits = n_splits
        self.method = method
        self.window_size = window_size
        self.test_size = test_size
        
        if method not in ['expanding', 'sliding']:
            raise ValueError("Method must be 'expanding' or 'sliding'")
        
        if method == 'sliding' and window_size is None:
            raise ValueError("Window size must be specified for sliding window method")
    
    def split(self, data: Union[pd.DataFrame, np.ndarray]) -> List[Tuple[np.ndarray, np.ndarray]]:
        """
        Generate indices for train/test splits.
        
        Args:
            data: Input data (DataFrame or array)
            
        Returns:
            List of (train_indices, test_indices) tuples
        """
        n_samples = len(data)
        
        # Calculate test size if not specified
        test_size = self.test_size
        if test_size is None:
            test_size = n_samples // (self.n_splits + 1)
        
        # Calculate indices for each split
        splits = []
        
        if self.method == 'expanding':
            # Expanding window: train set grows with each split
            for i in range(self.n_splits):
                # Calculate the end of the training set
                train_end = n_samples - (self.n_splits - i) * test_size
                
                # Ensure we have at least some training data
                train_end = max(train_end, test_size)
                
                # Calculate test indices
                test_start = train_end
                test_end = min(test_start + test_size, n_samples)
                
                # Create train and test indices
                train_indices = np.arange(0, train_end)
                test_indices = np.arange(test_start, test_end)
                
                splits.append((train_indices, test_indices))
        
        elif self.method == 'sliding':
            # Sliding window: fixed-size training window that slides forward
            for i in range(self.n_splits):
                # Calculate the end of the training set
                train_end = n_samples - (self.n_splits - i) * test_size
                
                # Calculate the start of the training set
                train_start = max(0, train_end - self.window_size)
                
                # Calculate test indices
                test_start = train_end
                test_end = min(test_start + test_size, n_samples)
                
                # Create train and test indices
                train_indices = np.arange(train_start, train_end)
                test_indices = np.arange(test_start, test_end)
                
                splits.append((train_indices, test_indices))
        
        return splits
    
    def cross_validate(self, model: BaseEstimator, X: Union[pd.DataFrame, np.ndarray],
                      y: Union[pd.Series, np.ndarray], scoring: Union[str, Callable] = 'accuracy') -> List[float]:
        """
        Perform cross-validation with a model.
        
        Args:
            model: Scikit-learn model to validate
            X: Feature data
            y: Target data
            scoring: Scoring method ('accuracy', 'precision', 'recall', 'f1', or a callable)
            
        Returns:
            List of scores for each fold
        """
        # Convert pandas objects to numpy arrays if needed
        X_array = X.values if isinstance(X, pd.DataFrame) else X
        y_array = y.values if isinstance(y, pd.Series) else y
        
        # Get scoring function
        if scoring == 'accuracy':
            score_func = accuracy_score
        elif scoring == 'precision':
            score_func = precision_score
        elif scoring == 'recall':
            score_func = recall_score
        elif scoring == 'f1':
            score_func = f1_score
        elif callable(scoring):
            score_func = scoring
        else:
            raise ValueError(f"Unknown scoring method: {scoring}")
        
        # Perform cross-validation
        scores = []
        
        for train_idx, test_idx in self.split(X):
            # Split data
            X_train, X_test = X_array[train_idx], X_array[test_idx]
            y_train, y_test = y_array[train_idx], y_array[test_idx]
            
            # Train model
            model.fit(X_train, y_train)
            
            # Make predictions
            y_pred = model.predict(X_test)
            
            # Calculate score
            score = score_func(y_test, y_pred)
            scores.append(score)
        
        return scores


def calculate_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
    """
    Calculate classification performance metrics.
    
    Args:
        y_true: True labels
        y_pred: Predicted labels
        
    Returns:
        Dictionary of metrics
    """
    return {
        'accuracy': accuracy_score(y_true, y_pred),
        'precision': precision_score(y_true, y_pred, zero_division=0),
        'recall': recall_score(y_true, y_pred, zero_division=0),
        'f1': f1_score(y_true, y_pred, zero_division=0)
    }


def calculate_profit_metrics(y_true: np.ndarray, y_pred: np.ndarray,
                           returns: np.ndarray) -> Dict[str, float]:
    """
    Calculate profit-based performance metrics.
    
    Args:
        y_true: True labels (1 for positive return, 0 for negative)
        y_pred: Predicted labels
        returns: Actual returns for each prediction
        
    Returns:
        Dictionary of profit-based metrics
    """
    # Calculate total return based on the test's expected behavior
    correct_predictions = y_true == y_pred
    
    # For correct predictions where y_true is 1, add the return
    # For correct predictions where y_true is 0, add 0
    correct_returns = sum(returns[i] for i in range(len(y_true)) 
                         if correct_predictions[i] and y_true[i] == 1)
    
    # For incorrect predictions, subtract the absolute return
    incorrect_penalty = sum(abs(returns[i]) for i in range(len(y_true))
                           if not correct_predictions[i])
    
    total_return = correct_returns - incorrect_penalty
    
    # Calculate win rate (percentage of correct predictions)
    win_rate = np.mean(correct_predictions)
    
    # Calculate profit factor (ratio of gains to losses)
    gains = sum(max(0, returns[i]) for i in range(len(y_true)) 
               if y_pred[i] == 1)
    losses = sum(abs(min(0, returns[i])) for i in range(len(y_true))
                if y_pred[i] == 1)
    
    profit_factor = gains / losses if losses > 0 else float('inf')
    
    return {
        'total_return': total_return,
        'win_rate': win_rate,
        'profit_factor': profit_factor
    } 