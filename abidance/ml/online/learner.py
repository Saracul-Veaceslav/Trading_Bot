"""
Online learner module for continuous model updating.

This module provides functionality for online learning, allowing models
to adapt to changing market conditions over time.
"""
from typing import List
from collections import deque

import pandas as pd
import numpy as np
from sklearn.base import BaseEstimator
from sklearn.metrics import f1_score

from ..pipeline.trainer import ModelTrainer


# pylint: disable=too-few-public-methods
class OnlineLearner:
    """
    System for continuous model updating.

    This class provides functionality for monitoring model performance
    and triggering retraining when performance degrades. It maintains
    a buffer of recent data and tracks performance metrics over time.
    """

    def __init__(self,
                 model: BaseEstimator,
                 trainer: ModelTrainer,
                 buffer_size: int = 1000,
                 update_threshold: float = 0.1):
        """
        Initialize the online learner.

        Args:
            model: Scikit-learn model to monitor and update
            trainer: ModelTrainer instance for retraining the model
            buffer_size: Maximum size of the data buffer
            update_threshold: Performance degradation threshold to trigger update
        """
        self.model = model
        self.trainer = trainer
        self.buffer = deque(maxlen=buffer_size)
        self.update_threshold = update_threshold
        self.performance_history: List[float] = []

    def update(self, new_data: pd.DataFrame) -> bool:
        """
        Update model with new data if necessary.

        This method adds new data to the buffer, evaluates current model
        performance, and triggers retraining if performance has degraded
        beyond the specified threshold.

        Args:
            new_data: DataFrame containing new market data

        Returns:
            True if model was retrained, False otherwise
        """
        # Add new data to buffer
        self.buffer.extend(new_data.to_dict('records'))
        buffer_data = pd.DataFrame(list(self.buffer))

        # Check current performance
        current_performance = self._evaluate_performance(buffer_data)
        self.performance_history.append(current_performance)

        # Check if update is needed
        if self._should_update():
            # Retrain model
            self.trainer.train(buffer_data)
            return True

        return False

    def _evaluate_performance(self, data: pd.DataFrame) -> float:
        """
        Evaluate model performance on recent data.

        Args:
            data: DataFrame containing market data for evaluation

        Returns:
            Performance metric (F1 score)
        """
        if data.empty:
            return 0.0

        predictions = self.trainer.predict(data)
        y_true = data['close'].pct_change().shift(-1).fillna(0)
        y_true = np.where(y_true > 0, 1, 0)

        return f1_score(y_true, predictions, zero_division=0)

    def _should_update(self) -> bool:
        """
        Determine if model should be updated.

        This method compares recent performance to baseline performance
        and triggers an update if performance has degraded beyond the
        specified threshold.

        Returns:
            True if model should be updated, False otherwise
        """
        if len(self.performance_history) < 20:  # Need at least 20 data points
            return False

        # Check for significant performance degradation
        recent_performance = np.mean(self.performance_history[-10:])
        baseline_performance = np.mean(self.performance_history[:-10])

        return (baseline_performance - recent_performance) > self.update_threshold
