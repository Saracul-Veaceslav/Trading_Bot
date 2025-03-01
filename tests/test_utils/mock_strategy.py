
"""
Mock Strategy Base for Testing
"""
import logging
from datetime import datetime

class Strategy:
    """
    Test version of Strategy base class that accepts trading_logger parameter.
    """
    
    def __init__(self, name="BaseStrategy", trading_logger=None, error_logger=None):
        """
        Initialize the strategy with test-friendly parameters.
        
        Args:
            name: Name of the strategy
            trading_logger: Logger for trading activity
            error_logger: Logger for errors
        """
        self.name = name
        self.logger = trading_logger or logging.getLogger(f'trading_bot.strategies.{name.lower().replace(" ", "_")}')
        self.error_logger = error_logger or self.logger
        self.parameters = {}
        self.metadata = {
            'name': name,
            'description': 'Base strategy class',
            'version': '1.0.0',
            'author': 'Trading Bot',
            'created_at': datetime.now().isoformat(),
        }
    
    def log_info(self, message):
        """Log informational message."""
        self.logger.info(message)
    
    def log_warning(self, message):
        """Log warning message."""
        self.logger.warning(message)
    
    def log_error(self, message):
        """Log error message."""
        self.error_logger.error(message)
