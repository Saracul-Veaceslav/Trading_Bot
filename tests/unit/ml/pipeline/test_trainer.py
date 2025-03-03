"""
Unit tests for the ModelTrainer class.

This module contains tests for the model training pipeline, including parameter
combination generation, strategy evaluation, parallel optimization, and result sorting.
"""
import numpy as np
import pandas as pd
import pytest
from sklearn.base import BaseEstimator
from sklearn.linear_model import LogisticRegression
from unittest.mock import MagicMock, patch

from abidance.ml.pipeline.trainer import ModelTrainer
from abidance.ml.features.base import FeatureGenerator


class MockFeatureGenerator(FeatureGenerator):
    """Mock feature generator for testing."""
    
    def generate(self, data: pd.DataFrame) -> pd.DataFrame:
        """Generate mock features."""
        return pd.DataFrame({
            'feature1': np.random.randn(len(data)),
            'feature2': np.random.randn(len(data))
        })
    
    @property
    def feature_names(self):
        """Return feature names."""
        return ['feature1', 'feature2']


@pytest.fixture
def sample_data():
    """Create sample data for testing."""
    return pd.DataFrame({
        'open': np.random.randn(100) + 100,
        'high': np.random.randn(100) + 101,
        'low': np.random.randn(100) + 99,
        'close': np.random.randn(100) + 100,
        'volume': np.random.randint(1000, 10000, 100)
    }, index=pd.date_range(start='2023-01-01', periods=100))


@pytest.fixture
def model_trainer():
    """Create a model trainer instance for testing."""
    model = LogisticRegression(random_state=42)
    feature_generator = MockFeatureGenerator()
    return ModelTrainer(model=model, feature_generator=feature_generator)


class TestModelTrainer:
    """Tests for the ModelTrainer class."""
    
    def test_initialization(self, model_trainer):
        """Test that the model trainer initializes correctly."""
        assert isinstance(model_trainer.model, BaseEstimator)
        assert isinstance(model_trainer.feature_generator, FeatureGenerator)
        assert model_trainer.n_splits == 5  # Default value
    
    def test_prepare_data(self, model_trainer, sample_data):
        """Test data preparation for training."""
        X, y = model_trainer.prepare_data(sample_data)
        
        # Check shapes
        assert X.shape[0] == len(sample_data)
        assert X.shape[1] == 2  # Two features from MockFeatureGenerator
        assert y.shape[0] == len(sample_data)
        
        # Check types
        assert isinstance(X, np.ndarray)
        assert isinstance(y, np.ndarray)
        
        # Check that y contains only binary values (0 or 1)
        assert np.all(np.isin(y, [0, 1]))
    
    def test_train_with_cross_validation(self, model_trainer, sample_data):
        """Test training with time series cross-validation."""
        # Train the model
        results = model_trainer.train(sample_data)
        
        # Check that results contain expected metrics
        assert 'mean_cv_score' in results
        assert 'std_cv_score' in results
        
        # Check that metrics are reasonable values
        assert 0 <= results['mean_cv_score'] <= 1
        assert 0 <= results['std_cv_score'] <= 1
    
    def test_predict(self, model_trainer, sample_data):
        """Test prediction on new data."""
        # First train the model
        model_trainer.train(sample_data)
        
        # Then make predictions
        predictions = model_trainer.predict(sample_data)
        
        # Check predictions shape and values
        assert predictions.shape[0] == len(sample_data)
        assert np.all(np.isin(predictions, [0, 1]))  # Binary classification
    
    def test_parameter_combination_generation(self):
        """Test generation of parameter combinations for grid search."""
        param_grid = {
            'C': [0.1, 1.0, 10.0],
            'penalty': ['l1', 'l2']
        }
        
        model = LogisticRegression(solver='liblinear')
        feature_generator = MockFeatureGenerator()
        trainer = ModelTrainer(model=model, feature_generator=feature_generator)
        
        # Test the parameter combination generation
        combinations = trainer.generate_parameter_combinations(param_grid)
        
        # Check that we have the expected number of combinations
        assert len(combinations) == 6  # 3 C values × 2 penalty values
        
        # Check that all combinations are present
        expected_combinations = [
            {'C': 0.1, 'penalty': 'l1'},
            {'C': 0.1, 'penalty': 'l2'},
            {'C': 1.0, 'penalty': 'l1'},
            {'C': 1.0, 'penalty': 'l2'},
            {'C': 10.0, 'penalty': 'l1'},
            {'C': 10.0, 'penalty': 'l2'}
        ]
        
        for expected in expected_combinations:
            assert any(all(item[k] == expected[k] for k in expected) for item in combinations)
    
    def test_strategy_evaluation_with_different_parameters(self, sample_data):
        """Test evaluation of a strategy with different parameters."""
        param_grid = {'C': [0.1, 1.0]}
        
        model = LogisticRegression(random_state=42, solver='liblinear')
        feature_generator = MockFeatureGenerator()
        trainer = ModelTrainer(model=model, feature_generator=feature_generator)
        
        # Evaluate with different parameters
        results = trainer.optimize(sample_data, param_grid)
        
        # Check that we have results for each parameter combination
        assert len(results) == 2
        
        # Check that results are sorted by performance (best first)
        assert results[0]['mean_cv_score'] >= results[1]['mean_cv_score']
        
        # Check that parameters are included in results
        assert 'parameters' in results[0]
        assert 'C' in results[0]['parameters']
    
    @patch('abidance.ml.pipeline.trainer.ProcessPoolExecutor')
    def test_parallel_optimization_execution(self, mock_executor, sample_data):
        """Test that optimization runs in parallel."""
        param_grid = {'C': [0.1, 1.0, 10.0]}
        
        # Setup mock executor
        mock_instance = mock_executor.return_value.__enter__.return_value
        mock_instance.map.return_value = [
            {'mean_cv_score': 0.8, 'std_cv_score': 0.1, 'parameters': {'C': 0.1}},
            {'mean_cv_score': 0.7, 'std_cv_score': 0.1, 'parameters': {'C': 1.0}},
            {'mean_cv_score': 0.6, 'std_cv_score': 0.1, 'parameters': {'C': 10.0}}
        ]
        
        model = LogisticRegression(random_state=42)
        feature_generator = MockFeatureGenerator()
        trainer = ModelTrainer(model=model, feature_generator=feature_generator)
        
        # Run optimization
        results = trainer.optimize(sample_data, param_grid, n_jobs=2)
        
        # Check that executor was called with correct number of workers
        mock_executor.assert_called_once_with(max_workers=2)
        
        # Check that map was called
        assert mock_instance.map.called
        
        # Check results
        assert len(results) == 3
        assert results[0]['mean_cv_score'] == 0.8
    
    def test_result_sorting_and_ranking(self, sample_data):
        """Test that optimization results are properly sorted and ranked."""
        # Create results with known scores
        mock_results = [
            {'mean_cv_score': 0.6, 'std_cv_score': 0.1, 'parameters': {'C': 10.0}},
            {'mean_cv_score': 0.8, 'std_cv_score': 0.1, 'parameters': {'C': 0.1}},
            {'mean_cv_score': 0.7, 'std_cv_score': 0.1, 'parameters': {'C': 1.0}}
        ]
        
        model = LogisticRegression(random_state=42)
        feature_generator = MockFeatureGenerator()
        trainer = ModelTrainer(model=model, feature_generator=feature_generator)
        
        # Mock the evaluate_parameters method to return our predefined results
        trainer.evaluate_parameters = MagicMock(side_effect=mock_results)
        
        # Run optimization
        param_grid = {'C': [0.1, 1.0, 10.0]}
        results = trainer.optimize(sample_data, param_grid)
        
        # Check that results are sorted by mean_cv_score (descending)
        assert results[0]['mean_cv_score'] == 0.8
        assert results[1]['mean_cv_score'] == 0.7
        assert results[2]['mean_cv_score'] == 0.6
        
        # Check that parameters match the expected order
        assert results[0]['parameters']['C'] == 0.1
        assert results[1]['parameters']['C'] == 1.0
        assert results[2]['parameters']['C'] == 10.0


# Feature: Model Training Pipeline
# 
#   Scenario: Training a model with time series cross-validation
#     Given a dataset with price and volume data
#     And a feature generator that creates technical indicators
#     When I train a model using time series cross-validation
#     Then I should get performance metrics for each fold
#     And the final model should be trained on all data
#
#   Scenario: Optimizing model hyperparameters
#     Given a model with tunable hyperparameters
#     And a grid of parameter combinations to try
#     When I run the optimization process
#     Then I should get results for each parameter combination
#     And the results should be sorted by performance
#     And I should be able to select the best parameter combination 