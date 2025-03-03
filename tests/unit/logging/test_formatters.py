"""
Tests for the custom log formatters.
"""

import json
import unittest
from unittest.mock import MagicMock, patch
import logging
import time

from abidance.logging.formatters import JsonFormatter, ColoredConsoleFormatter


class TestJsonFormatter(unittest.TestCase):
    """Test cases for the JsonFormatter class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.formatter = JsonFormatter()
        
        # Create a mock log record
        self.record = MagicMock(spec=logging.LogRecord)
        self.record.levelname = 'INFO'
        self.record.name = 'test_logger'
        self.record.getMessage.return_value = 'Test message'
        self.record.created = 1609459200.0  # 2021-01-01 00:00:00
        self.record.pathname = '/path/to/file.py'
        self.record.lineno = 42
        self.record.funcName = 'test_function'
        self.record.exc_info = None
        
    def test_basic_json_formatting(self):
        """Test basic JSON formatting of log records."""
        # Format the record
        formatted = self.formatter.format(self.record)
        
        # Parse the JSON
        log_data = json.loads(formatted)
        
        # Verify the structure
        self.assertEqual(log_data['level'], 'INFO')
        self.assertEqual(log_data['name'], 'test_logger')
        self.assertEqual(log_data['message'], 'Test message')
        self.assertIn('timestamp', log_data)
        self.assertIn('location', log_data)
        self.assertEqual(log_data['location']['file'], '/path/to/file.py')
        self.assertEqual(log_data['location']['line'], 42)
        self.assertEqual(log_data['location']['function'], 'test_function')
        
    def test_json_formatting_with_exception(self):
        """Test JSON formatting of log records with exception info."""
        # Add exception info to the record
        try:
            raise ValueError("Test exception")
        except ValueError as e:
            self.record.exc_info = (ValueError, e, e.__traceback__)
            
        # Format the record
        formatted = self.formatter.format(self.record)
        
        # Parse the JSON
        log_data = json.loads(formatted)
        
        # Verify exception info is included
        self.assertIn('exception', log_data)
        self.assertEqual(log_data['exception']['type'], 'ValueError')
        self.assertEqual(log_data['exception']['message'], 'Test exception')
        
    def test_json_formatting_with_additional_fields(self):
        """Test JSON formatting with additional fields."""
        # Create a formatter with additional fields
        formatter = JsonFormatter(additional_fields={
            'app_name': 'test_app',
            'environment': 'testing'
        })
        
        # Format the record
        formatted = formatter.format(self.record)
        
        # Parse the JSON
        log_data = json.loads(formatted)
        
        # Verify additional fields are included
        self.assertEqual(log_data['app_name'], 'test_app')
        self.assertEqual(log_data['environment'], 'testing')
        
    def test_json_formatting_with_extra_fields(self):
        """Test JSON formatting with extra fields from the record."""
        # Add extra fields to the record
        self.record.extra_fields = {
            'user_id': 123,
            'request_id': 'abc-123',
            'tags': ['important', 'test']
        }
        
        # Format the record
        formatted = self.formatter.format(self.record)
        
        # Parse the JSON
        log_data = json.loads(formatted)
        
        # Verify extra fields are included
        self.assertEqual(log_data['user_id'], 123)
        self.assertEqual(log_data['request_id'], 'abc-123')
        self.assertEqual(log_data['tags'], ['important', 'test'])


class TestColoredConsoleFormatter(unittest.TestCase):
    """Test cases for the ColoredConsoleFormatter class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.formatter = ColoredConsoleFormatter()
        
        # Create a real LogRecord instead of a mock to avoid attribute errors
        self.record = logging.LogRecord(
            name='test_logger',
            level=logging.INFO,
            pathname='/path/to/file.py',
            lineno=42,
            msg='Test message',
            args=(),
            exc_info=None
        )
        
    def test_color_codes_added(self):
        """Test that color codes are added to the formatted message."""
        # Test with different levels
        for level_name, level_num in [
            ('DEBUG', logging.DEBUG),
            ('INFO', logging.INFO),
            ('WARNING', logging.WARNING),
            ('ERROR', logging.ERROR),
            ('CRITICAL', logging.CRITICAL)
        ]:
            # Create a new record with the current level
            record = logging.LogRecord(
                name='test_logger',
                level=level_num,
                pathname='/path/to/file.py',
                lineno=42,
                msg='Test message',
                args=(),
                exc_info=None
            )
            
            # Format the record
            formatted = self.formatter.format(record)
            
            # Verify color codes are added
            self.assertIn(self.formatter.COLORS[level_name], formatted)
            self.assertIn(self.formatter.COLORS['RESET'], formatted)
            
    def test_unknown_level_no_color(self):
        """Test that unknown levels don't get color codes."""
        # Create a record with a custom level
        custom_level = 123
        logging.addLevelName(custom_level, 'CUSTOM')
        
        record = logging.LogRecord(
            name='test_logger',
            level=custom_level,
            pathname='/path/to/file.py',
            lineno=42,
            msg='Test message',
            args=(),
            exc_info=None
        )
        
        # Format the record
        formatted = self.formatter.format(record)
        
        # Verify no color codes are added
        for color in self.formatter.COLORS.values():
            self.assertNotIn(color, formatted)


if __name__ == '__main__':
    unittest.main()

# Gherkin format test description:
"""
Feature: Log Formatters
  As a developer
  I want to have customizable log formatters
  So that I can format logs in different ways for different outputs

  Scenario: JSON formatting of log records
    Given a JSON formatter is configured
    When I format a log record
    Then the result should be valid JSON
    And the JSON should contain standard log fields

  Scenario: JSON formatting with exception info
    Given a JSON formatter is configured
    When I format a log record with exception info
    Then the result should include exception details in the JSON

  Scenario: JSON formatting with additional fields
    Given a JSON formatter is configured with additional fields
    When I format a log record
    Then the result should include the additional fields

  Scenario: Colored console output
    Given a colored console formatter is configured
    When I format log records with different levels
    Then each record should have the appropriate color codes
""" 