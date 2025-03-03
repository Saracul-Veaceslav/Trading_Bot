"""
Structured logging implementation for Abidance.

This module provides a structured logger that outputs logs in JSON format,
making them easier to parse and analyze with log management tools.
"""

from typing import Any, Dict, Optional
import logging
import json
from datetime import datetime
from contextvars import ContextVar

# Context variable for request ID
request_id: ContextVar[str] = ContextVar('request_id', default='')


class StructuredLogger:
    """Logger that outputs structured JSON logs."""
    
    def __init__(self, name: str):
        """
        Initialize a structured logger.
        
        Args:
            name: The name of the logger
        """
        self.name = name
        self._logger = logging.getLogger(name)
        
    def _format_log(self, level: str, message: str, 
                   extra: Optional[Dict[str, Any]] = None) -> str:
        """
        Format log entry as JSON.
        
        Args:
            level: The log level (INFO, ERROR, etc.)
            message: The log message
            extra: Additional fields to include in the log
            
        Returns:
            str: JSON-formatted log entry
        """
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'logger': self.name,
            'level': level,
            'message': message,
            'request_id': request_id.get(),
        }
        if extra:
            log_entry.update(extra)
        return json.dumps(log_entry)
        
    def info(self, message: str, **kwargs: Any) -> None:
        """
        Log info level message.
        
        Args:
            message: The log message
            **kwargs: Additional fields to include in the log
        """
        self._logger.info(self._format_log('INFO', message, kwargs))
        
    def error(self, message: str, **kwargs: Any) -> None:
        """
        Log error level message.
        
        Args:
            message: The log message
            **kwargs: Additional fields to include in the log
        """
        self._logger.error(self._format_log('ERROR', message, kwargs))
        
    def warning(self, message: str, **kwargs: Any) -> None:
        """
        Log warning level message.
        
        Args:
            message: The log message
            **kwargs: Additional fields to include in the log
        """
        self._logger.warning(self._format_log('WARNING', message, kwargs))
        
    def debug(self, message: str, **kwargs: Any) -> None:
        """
        Log debug level message.
        
        Args:
            message: The log message
            **kwargs: Additional fields to include in the log
        """
        self._logger.debug(self._format_log('DEBUG', message, kwargs))
        
    def critical(self, message: str, **kwargs: Any) -> None:
        """
        Log critical level message.
        
        Args:
            message: The log message
            **kwargs: Additional fields to include in the log
        """
        self._logger.critical(self._format_log('CRITICAL', message, kwargs))
        
    def exception(self, message: str, exc_info=True, **kwargs: Any) -> None:
        """
        Log an exception with traceback.
        
        Args:
            message: The log message
            exc_info: Whether to include exception info
            **kwargs: Additional fields to include in the log
        """
        self._logger.exception(
            self._format_log('ERROR', message, kwargs),
            exc_info=exc_info
        )


def get_logger(name: str) -> StructuredLogger:
    """
    Get a structured logger by name.
    
    Args:
        name: The name of the logger
        
    Returns:
        StructuredLogger: A structured logger instance
    """
    return StructuredLogger(name) 