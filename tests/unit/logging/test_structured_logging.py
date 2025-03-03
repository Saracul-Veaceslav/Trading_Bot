import json
import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
import logging

from abidance.logging.structured import StructuredLogger, request_id


class TestStructuredLogger(unittest.TestCase):
    """Test cases for the StructuredLogger class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a mock logger
        self.mock_logger = MagicMock(spec=logging.Logger)
        
        # Create a structured logger with the mock
        with patch('logging.getLogger', return_value=self.mock_logger):
            self.structured_logger = StructuredLogger('test_logger')
    
    def test_json_log_formatting(self):
        """Test that logs are properly formatted as JSON."""
        # Log a message
        self.structured_logger.info("Test message")
        
        # Get the argument passed to the mock logger's info method
        log_arg = self.mock_logger.info.call_args[0][0]
        
        # Parse the JSON string
        log_entry = json.loads(log_arg)
        
        # Verify the structure
        self.assertEqual(log_entry['logger'], 'test_logger')
        self.assertEqual(log_entry['level'], 'INFO')
        self.assertEqual(log_entry['message'], 'Test message')
        self.assertIn('timestamp', log_entry)
        self.assertIn('request_id', log_entry)
    
    def test_context_variable_handling(self):
        """Test that context variables are included in logs."""
        # Set a request ID
        token = request_id.set('test-request-id')
        try:
            # Log a message
            self.structured_logger.info("Test with request ID")
            
            # Get the argument passed to the mock logger's info method
            log_arg = self.mock_logger.info.call_args[0][0]
            
            # Parse the JSON string
            log_entry = json.loads(log_arg)
            
            # Verify the request ID is included
            self.assertEqual(log_entry['request_id'], 'test-request-id')
        finally:
            # Reset the request ID
            request_id.reset(token)
    
    def test_different_log_levels(self):
        """Test that different log levels work correctly."""
        # Test info level
        self.structured_logger.info("Info message")
        log_arg = self.mock_logger.info.call_args[0][0]
        log_entry = json.loads(log_arg)
        self.assertEqual(log_entry['level'], 'INFO')
        
        # Test error level
        self.structured_logger.error("Error message")
        log_arg = self.mock_logger.error.call_args[0][0]
        log_entry = json.loads(log_arg)
        self.assertEqual(log_entry['level'], 'ERROR')
    
    def test_extra_fields_in_logs(self):
        """Test that extra fields are included in logs."""
        # Log with extra fields
        self.structured_logger.info(
            "Message with extras",
            correlation_id="abc123",
            user_id=42,
            tags=["important", "test"]
        )
        
        # Get the argument passed to the mock logger's info method
        log_arg = self.mock_logger.info.call_args[0][0]
        
        # Parse the JSON string
        log_entry = json.loads(log_arg)
        
        # Verify extra fields are included
        self.assertEqual(log_entry['correlation_id'], "abc123")
        self.assertEqual(log_entry['user_id'], 42)
        self.assertEqual(log_entry['tags'], ["important", "test"])


if __name__ == '__main__':
    unittest.main()

# Gherkin format test description:
"""
Feature: Structured Logging
  As a developer
  I want to have structured JSON logs
  So that I can easily analyze and search logs

  Scenario: Log formatting as JSON
    Given a structured logger is configured
    When I log a message
    Then the log should be formatted as valid JSON
    And the JSON should contain standard fields like timestamp and level

  Scenario: Context variable handling
    Given a structured logger is configured
    And a request ID is set in the context
    When I log a message
    Then the log should include the request ID

  Scenario: Different log levels
    Given a structured logger is configured
    When I log messages at different levels
    Then each log should have the correct level field

  Scenario: Extra fields in logs
    Given a structured logger is configured
    When I log a message with extra fields
    Then the log should include all the extra fields
""" 