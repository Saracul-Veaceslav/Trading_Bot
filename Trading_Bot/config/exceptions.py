"""
Configuration-specific exceptions for the Trading Bot framework.

This module contains exceptions specific to configuration operations,
including loading, validating, and accessing configuration settings.
"""

from trading_bot.exceptions import ConfigurationError


class ConfigFileNotFoundError(ConfigurationError):
    """Raised when a configuration file cannot be found."""
    pass


class ConfigValidationError(ConfigurationError):
    """Raised when configuration fails validation."""
    pass


class ConfigKeyError(ConfigurationError):
    """Raised when a required configuration key is missing."""
    pass


class ConfigTypeError(ConfigurationError):
    """Raised when a configuration value has an incorrect type."""
    pass


class CredentialsError(ConfigurationError):
    """Raised when there is an error with credentials configuration."""
    pass


class EnvironmentVariableError(ConfigurationError):
    """Raised when a required environment variable is missing or invalid."""
    pass 