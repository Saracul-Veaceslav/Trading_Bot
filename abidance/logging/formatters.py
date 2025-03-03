"""
Custom log formatters for Abidance.

This module provides custom formatters for logging, including JSON formatting
and other specialized formats.
"""

from datetime import datetime
from typing import Dict, Any, Optional
import json
import logging



class JsonFormatter(logging.Formatter):
    """
    Formatter that outputs log records as JSON.

    This formatter converts log records to JSON format, making them
    easier to parse and analyze with log management tools.
    """

    def __init__(self, include_timestamp: bool = True,
                 additional_fields: Optional[Dict[str, Any]] = None):
        """
        Initialize the JSON formatter.

        Args:
            include_timestamp: Whether to include a timestamp field
            additional_fields: Additional fields to include in every log record
        """
        super().__init__()
        self.include_timestamp = include_timestamp
        self.additional_fields = additional_fields or {}

    def format(self, record: logging.LogRecord) -> str:
        """
        Format the log record as JSON.

        Args:
            record: The log record to format

        Returns:
            str: JSON-formatted log record
        """
        log_data = {
            'level': record.levelname,
            'name': record.name,
            'message': record.getMessage(),
        }

        # Add timestamp if requested
        if self.include_timestamp:
            log_data['timestamp'] = datetime.fromtimestamp(record.created).isoformat()

        # Add location information
        log_data['location'] = {
            'file': record.pathname,
            'line': record.lineno,
            'function': record.funcName,
        }

        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = {
                'type': record.exc_info[0].__name__,
                'message': str(record.exc_info[1]),
            }

        # Add any additional fields
        log_data.update(self.additional_fields)

        # Add any extra attributes from the record
        if hasattr(record, 'extra_fields'):
            log_data.update(record.extra_fields)

        return json.dumps(log_data)


class ColoredConsoleFormatter(logging.Formatter):
    """
    Formatter that adds color to console output based on log level.

    This formatter adds ANSI color codes to log messages based on their
    level, making it easier to distinguish different log levels in the console.
    """

    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',  # Cyan
        'INFO': '\033[32m',   # Green
        'WARNING': '\033[33m', # Yellow
        'ERROR': '\033[31m',  # Red
        'CRITICAL': '\033[41m\033[37m',  # White on red background
        'RESET': '\033[0m',   # Reset to default
    }

    def __init__(self, fmt: Optional[str] = None):
        """
        Initialize the colored console formatter.

        Args:
            fmt: Format string for log messages
        """
        if fmt is None:
            fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        super().__init__(fmt)

    def format(self, record: logging.LogRecord) -> str:
        """
        Format the log record with color.

        Args:
            record: The log record to format

        Returns:
            str: Colored log message
        """
        # Get the original formatted message
        log_message = super().format(record)

        # Add color based on log level
        if record.levelname in self.COLORS:
            return f"{self.COLORS[record.levelname]}{log_message}{self.COLORS['RESET']}"

        return log_message
