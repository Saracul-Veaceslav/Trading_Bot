"""
Unit tests for the OnlineLearner class.

This module contains tests for the online learning system, including
buffer management, update triggering, performance tracking, and model retraining.
"""
import unittest
from unittest.mock import Mock, patch
import numpy as np
import pandas as pd
from collections import deque
from sklearn.base import BaseEstimator
from sklearn.metrics import f1_score

# Import the class to be tested
from abidance.ml.online.learner import OnlineLearner
from abidance.ml.pipeline.trainer import ModelTrainer


class TestOnlineLearner(unittest.TestCase):
    """Test cases for the OnlineLearner class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create mock objects
        self.mock_model = Mock(spec=BaseEstimator)
        self.mock_trainer = Mock(spec=ModelTrainer)
        
        # Create sample data
        self.sample_data = pd.DataFrame({
            'open': [100, 101, 102, 103, 104],
            'high': [105, 106, 107, 108, 109],
            'low': [95, 96, 97, 98, 99],
            'close': [102, 103, 104, 105, 106],
            'volume': [1000, 1100, 1200, 1300, 1400]
        })
        
        # Create the OnlineLearner instance
        self.learner = OnlineLearner(
            model=self.mock_model,
            trainer=self.mock_trainer,
            buffer_size=10,
            update_threshold=0.1
        )

    def test_init(self):
        """Test initialization of OnlineLearner."""
        self.assertEqual(self.learner.model, self.mock_model)
        self.assertEqual(self.learner.trainer, self.mock_trainer)
        self.assertEqual(self.learner.buffer.maxlen, 10)
        self.assertEqual(self.learner.update_threshold, 0.1)
        self.assertEqual(self.learner.performance_history, [])
        self.assertIsInstance(self.learner.buffer, deque)

    def test_buffer_management(self):
        """Test that data is correctly added to the buffer."""
        # Convert DataFrame to dict records for comparison
        data_records = self.sample_data.to_dict('records')
        
        # Mock the _evaluate_performance method to avoid actual computation
        with patch.object(self.learner, '_evaluate_performance', return_value=0.75):
            # Update with sample data
            self.learner.update(self.sample_data)
            
            # Check that data was added to buffer
            self.assertEqual(len(self.learner.buffer), len(data_records))
            buffer_list = list(self.learner.buffer)
            for i, record in enumerate(buffer_list):
                self.assertEqual(record, data_records[i])
            
            # Test buffer size limit
            # Create data that exceeds buffer size
            large_data = pd.DataFrame({
                'open': np.random.rand(15),
                'high': np.random.rand(15),
                'low': np.random.rand(15),
                'close': np.random.rand(15),
                'volume': np.random.rand(15)
            })
            
            self.learner.update(large_data)
            
            # Buffer should be limited to its maxlen
            self.assertEqual(len(self.learner.buffer), 10)

    def test_performance_tracking(self):
        """Test that performance metrics are correctly tracked."""
        # Mock the _evaluate_performance method
        with patch.object(self.learner, '_evaluate_performance', return_value=0.75):
            self.learner.update(self.sample_data)
            
            # Check that performance was added to history
            self.assertEqual(len(self.learner.performance_history), 1)
            self.assertEqual(self.learner.performance_history[0], 0.75)
            
            # Update again
            self.learner.update(self.sample_data)
            
            # Check that performance history was updated
            self.assertEqual(len(self.learner.performance_history), 2)
            self.assertEqual(self.learner.performance_history[1], 0.75)

    def test_should_update_insufficient_history(self):
        """Test that update is not triggered with insufficient history."""
        # With empty performance history
        self.assertFalse(self.learner._should_update())
        
        # With only one performance entry
        self.learner.performance_history = [0.8]
        self.assertFalse(self.learner._should_update())

    def test_should_update_no_degradation(self):
        """Test that update is not triggered when performance is stable."""
        # Set performance history with no degradation
        self.learner.performance_history = [0.8] * 20
        self.assertFalse(self.learner._should_update())
        
        # Set performance history with slight improvement
        self.learner.performance_history = [0.7] * 10 + [0.8] * 10
        self.assertFalse(self.learner._should_update())

    def test_should_update_with_degradation(self):
        """Test that update is triggered when performance degrades."""
        # Set performance history with significant degradation
        self.learner.performance_history = [0.8] * 10 + [0.6] * 10
        self.assertTrue(self.learner._should_update())

    def test_update_triggers_retraining(self):
        """Test that model retraining is triggered when needed."""
        # Mock methods to force update
        with patch.object(self.learner, '_evaluate_performance', return_value=0.6):
            with patch.object(self.learner, '_should_update', return_value=True):
                # Call update
                result = self.learner.update(self.sample_data)
                
                # Check that trainer.train was called
                self.mock_trainer.train.assert_called_once()
                self.assertTrue(result)

    def test_update_no_retraining(self):
        """Test that model retraining is not triggered when not needed."""
        # Mock methods to prevent update
        with patch.object(self.learner, '_evaluate_performance', return_value=0.8):
            with patch.object(self.learner, '_should_update', return_value=False):
                # Call update
                result = self.learner.update(self.sample_data)
                
                # Check that trainer.train was not called
                self.mock_trainer.train.assert_not_called()
                self.assertFalse(result)

    def test_evaluate_performance(self):
        """Test the performance evaluation method."""
        # Mock trainer.predict to return predictions
        self.mock_trainer.predict.return_value = np.array([1, 0, 1, 0, 1])
        
        # Call _evaluate_performance
        with patch('abidance.ml.online.learner.f1_score', return_value=0.75):
            performance = self.learner._evaluate_performance(self.sample_data)
            
            # Check that trainer.predict was called
            self.mock_trainer.predict.assert_called_once()
            
            # Check that performance value is correct
            self.assertEqual(performance, 0.75)


if __name__ == '__main__':
    unittest.main()

# Feature: Online Learning System
# 
#   Scenario: Model performance degradation triggers retraining
#     Given an online learner with a trained model
#     And a performance history showing good baseline performance
#     When recent performance metrics show significant degradation
#     Then the system should trigger model retraining
#     And the model should be updated with the latest data 