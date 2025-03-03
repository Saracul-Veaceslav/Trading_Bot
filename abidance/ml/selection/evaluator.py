"""
Model evaluator module.

This module provides functionality for evaluating and selecting machine learning models
based on various performance metrics.
"""
from typing import Dict, List
import pandas as pd
import numpy as np
from sklearn.base import BaseEstimator
from sklearn.metrics import precision_score, recall_score, f1_score

from ..pipeline.trainer import ModelTrainer
from ..features.base import FeatureGenerator


class ModelEvaluator:
    """Framework for evaluating and selecting models."""

    def __init__(self,
                 models: List[BaseEstimator],
                 feature_generator: FeatureGenerator):
        """
        Initialize the model evaluator.

        Args:
            models: List of scikit-learn models to evaluate
            feature_generator: Feature generator to create features from raw data
        """
        self.models = models
        self.feature_generator = feature_generator
        self.results: Dict[str, Dict[str, float]] = {}

    def evaluate_models(self, data: pd.DataFrame) -> Dict[str, Dict[str, float]]:
        """
        Evaluate all models on the dataset.

        Args:
            data: Input DataFrame containing raw data (e.g., OHLCV data)

        Returns:
            Dictionary mapping model names to dictionaries of performance metrics
        """
        for model in self.models:
            trainer = ModelTrainer(
                model=model,
                feature_generator=self.feature_generator
            )

            # Train and evaluate
            cv_metrics = trainer.train(data)

            # Get predictions for final evaluation
            predictions = trainer.predict(data)
            y_true = data['close'].pct_change().shift(-1).fillna(0)
            y_true = np.where(y_true > 0, 1, 0)

            # Calculate metrics
            self.results[model.__class__.__name__] = {
                **cv_metrics,
                'precision': precision_score(y_true, predictions, zero_division=0),
                'recall': recall_score(y_true, predictions, zero_division=0),
                'f1': f1_score(y_true, predictions, zero_division=0)
            }

        return self.results

    def select_best_model(self, metric: str = 'f1') -> BaseEstimator:
        """
        Select the best performing model based on a specific metric.

        Args:
            metric: Metric to use for model selection (default: 'f1')

        Returns:
            Best performing model

        Raises:
            ValueError: If evaluate_models has not been called yet
        """
        if not self.results:
            raise ValueError("Must run evaluate_models first")

        best_score = -float('inf')
        best_model = None

        for model in self.models:
            score = self.results[model.__class__.__name__][metric]
            if score > best_score:
                best_score = score
                best_model = model

        return best_model
