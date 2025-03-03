"""
Unit tests for the validation module.

This module contains tests for model validation functionality, including
cross-validation strategies and performance metrics.
"""
import numpy as np
import pandas as pd
import pytest
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

from abidance.ml.pipeline.validation import (
    TimeSeriesValidator,
    calculate_metrics,
    calculate_profit_metrics
)


@pytest.fixture
def sample_data():
    """Create sample data for testing."""
    # Create a DataFrame with 100 rows of data
    np.random.seed(42)
    data = pd.DataFrame({
        'feature1': np.random.randn(100),
        'feature2': np.random.randn(100),
        'target': np.random.randint(0, 2, 100)  # Binary target
    }, index=pd.date_range(start='2023-01-01', periods=100))
    
    return data


@pytest.fixture
def sample_model():
    """Create a sample model for testing."""
    return LogisticRegression(random_state=42)


class TestTimeSeriesValidator:
    """Tests for the TimeSeriesValidator class."""
    
    def test_initialization(self):
        """Test that the validator initializes correctly."""
        validator = TimeSeriesValidator(n_splits=5)
        assert validator.n_splits == 5
    
    def test_split_indices(self, sample_data):
        """Test that split indices are generated correctly."""
        validator = TimeSeriesValidator(n_splits=3)
        splits = list(validator.split(sample_data))
        
        # Check that we have the correct number of splits
        assert len(splits) == 3
        
        # Check that each split has train and test indices
        for train_idx, test_idx in splits:
            assert len(train_idx) > 0
            assert len(test_idx) > 0
            
            # Check that train indices come before test indices
            assert max(train_idx) < min(test_idx)
    
    def test_expanding_window(self, sample_data):
        """Test expanding window validation strategy."""
        validator = TimeSeriesValidator(n_splits=3, method='expanding')
        splits = list(validator.split(sample_data))
        
        # Check that train sets are expanding
        train_sizes = [len(train_idx) for train_idx, _ in splits]
        assert train_sizes[0] < train_sizes[1] < train_sizes[2]
        
        # Check that test sets are of similar size
        test_sizes = [len(test_idx) for _, test_idx in splits]
        assert len(set(test_sizes)) <= 2  # Allow for off-by-one differences
    
    def test_sliding_window(self, sample_data):
        """Test sliding window validation strategy."""
        validator = TimeSeriesValidator(n_splits=3, method='sliding', window_size=30)
        splits = list(validator.split(sample_data))
        
        # Check that train sets are of similar size
        train_sizes = [len(train_idx) for train_idx, _ in splits]
        assert len(set(train_sizes)) <= 2  # Allow for off-by-one differences
        
        # Check that each train set is approximately the window size
        assert abs(train_sizes[0] - 30) <= 5
    
    def test_cross_validate(self, sample_data, sample_model):
        """Test cross-validation with a model."""
        X = sample_data[['feature1', 'feature2']]
        y = sample_data['target']
        
        validator = TimeSeriesValidator(n_splits=3)
        scores = validator.cross_validate(sample_model, X, y, scoring='accuracy')
        
        # Check that we have scores for each fold
        assert len(scores) == 3
        
        # Check that scores are between 0 and 1
        assert all(0 <= score <= 1 for score in scores)


class TestMetrics:
    """Tests for the metrics calculation functions."""
    
    def test_calculate_metrics(self):
        """Test calculation of classification metrics."""
        y_true = np.array([0, 1, 1, 0, 1, 0, 1, 1, 0, 0])
        y_pred = np.array([0, 1, 0, 0, 1, 0, 1, 0, 1, 0])
        
        metrics = calculate_metrics(y_true, y_pred)
        
        # Check that we have the expected metrics
        assert 'accuracy' in metrics
        assert 'precision' in metrics
        assert 'recall' in metrics
        assert 'f1' in metrics
        
        # Check that metrics match sklearn's calculations
        assert metrics['accuracy'] == accuracy_score(y_true, y_pred)
        assert metrics['precision'] == precision_score(y_true, y_pred)
        assert metrics['recall'] == recall_score(y_true, y_pred)
        assert metrics['f1'] == f1_score(y_true, y_pred)
    
    def test_calculate_profit_metrics(self):
        """Test calculation of profit-based metrics."""
        y_true = np.array([1, 1, 0, 0, 1, 0, 1, 0, 0, 1])
        y_pred = np.array([1, 1, 1, 0, 1, 0, 0, 0, 1, 1])
        returns = np.array([0.02, 0.03, -0.01, -0.02, 0.01, -0.03, 0.02, -0.01, -0.02, 0.03])
        
        metrics = calculate_profit_metrics(y_true, y_pred, returns)
        
        # Check that we have the expected metrics
        assert 'total_return' in metrics
        assert 'win_rate' in metrics
        assert 'profit_factor' in metrics
        
        # Check that win rate is reasonable
        assert 0 <= metrics['win_rate'] <= 1
        
        # Check that total return is calculated correctly
        # For correct predictions where y_true is 1, we add the return
        # For correct predictions where y_true is 0, we add 0
        # For incorrect predictions, we subtract the absolute return
        correct_predictions = y_true == y_pred
        
        # Calculate returns for correct predictions where y_true is 1
        correct_returns = sum(returns[i] for i in range(len(y_true)) 
                             if correct_predictions[i] and y_true[i] == 1)
        
        # Calculate penalty for incorrect predictions
        incorrect_penalty = sum(abs(returns[i]) for i in range(len(y_true))
                              if not correct_predictions[i])
        
        expected_return = correct_returns - incorrect_penalty
        
        # Check that the calculated total return matches the expected value
        assert abs(metrics['total_return'] - expected_return) < 1e-10


# Feature: Model Validation Framework
# 
#   Scenario: Validating a model with time series cross-validation
#     Given a time series dataset with features and target
#     And a machine learning model to evaluate
#     When I perform time series cross-validation
#     Then I should get performance metrics for each fold
#     And the validation should respect the temporal order of data
#
#   Scenario: Calculating profit-based performance metrics
#     Given a set of true labels and predicted labels
#     And the corresponding asset returns
#     When I calculate profit-based metrics
#     Then I should get metrics like total return and win rate
#     And these metrics should reflect trading performance 