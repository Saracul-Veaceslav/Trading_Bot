"""
Tests for the model evaluator module.

This module contains tests for the ModelEvaluator class, which is responsible
for evaluating and selecting machine learning models.
"""
import unittest
from unittest.mock import Mock, patch
import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC

from abidance.ml.selection.evaluator import ModelEvaluator
from abidance.ml.features.base import FeatureGenerator


class TestModelEvaluator(unittest.TestCase):
    """Tests for the ModelEvaluator class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create mock feature generator
        self.feature_generator = Mock(spec=FeatureGenerator)
        self.feature_generator.generate.return_value = pd.DataFrame({
            'feature1': np.random.randn(100),
            'feature2': np.random.randn(100)
        })
        self.feature_generator.feature_names = ['feature1', 'feature2']

        # Create test models
        self.models = [
            LogisticRegression(),
            RandomForestClassifier(),
            SVC()
        ]

        # Create test data
        self.data = pd.DataFrame({
            'open': np.random.randn(100) + 100,
            'high': np.random.randn(100) + 101,
            'low': np.random.randn(100) + 99,
            'close': np.random.randn(100) + 100,
            'volume': np.random.randint(1000, 10000, 100)
        })

        # Create evaluator
        self.evaluator = ModelEvaluator(
            models=self.models,
            feature_generator=self.feature_generator
        )

    def test_evaluate_models(self):
        """Test that models are evaluated correctly."""
        # Create mock for ModelTrainer
        with patch('abidance.ml.selection.evaluator.ModelTrainer') as mock_trainer_class:
            # Setup mock trainer
            mock_trainer = Mock()
            mock_trainer_class.return_value = mock_trainer
            mock_trainer.train.return_value = {'accuracy': 0.8, 'precision': 0.75}
            # Match length of data
            mock_trainer.predict.return_value = np.array([1, 0, 1, 0, 1] * 20)

            # Mock numpy.where to return an array of the same length as the data
            with patch('abidance.ml.selection.evaluator.np.where',
                      return_value=np.array([1, 0, 1, 0, 1] * 20)):
                results = self.evaluator.evaluate_models(self.data)

            # Assertions
            self.assertEqual(len(results), 3)
            self.assertIn('LogisticRegression', results)
            self.assertIn('RandomForestClassifier', results)
            self.assertIn('SVC', results)

            # Check metrics
            for _, metrics in results.items():
                self.assertIn('accuracy', metrics)
                self.assertIn('precision', metrics)
                self.assertIn('recall', metrics)
                self.assertIn('f1', metrics)

    def test_select_best_model_without_evaluation(self):
        """Test that an error is raised if select_best_model is called before evaluate_models."""
        with self.assertRaises(ValueError):
            self.evaluator.select_best_model()

    def test_select_best_model(self):
        """Test that the best model is selected correctly."""
        # Mock the results directly
        self.evaluator.results = {
            'LogisticRegression': {'f1': 0.7, 'precision': 0.8},
            'RandomForestClassifier': {'f1': 0.9, 'precision': 0.85},
            'SVC': {'f1': 0.5, 'precision': 0.6}
        }

        # Test with default metric (f1)
        best_model = self.evaluator.select_best_model()
        self.assertIsInstance(best_model, RandomForestClassifier)

        # Test with different metric
        best_model = self.evaluator.select_best_model(metric='precision')
        self.assertIsInstance(best_model, RandomForestClassifier)

    def test_handling_different_model_types(self):
        """Test that the evaluator can handle different types of models."""
        # Create evaluator with different model types
        models = [
            LogisticRegression(),
            RandomForestClassifier(n_estimators=10),
            SVC(kernel='linear')
        ]

        evaluator = ModelEvaluator(
            models=models,
            feature_generator=self.feature_generator
        )

        # Check that models are stored correctly
        self.assertEqual(len(evaluator.models), 3)
        self.assertIsInstance(evaluator.models[0], LogisticRegression)
        self.assertIsInstance(evaluator.models[1], RandomForestClassifier)
        self.assertIsInstance(evaluator.models[2], SVC)


if __name__ == '__main__':
    unittest.main()
