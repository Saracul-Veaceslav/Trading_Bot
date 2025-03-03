"""
Configuration management system for the Abidance trading bot.

This module provides functionality for loading, accessing, and validating
configuration settings from various sources including YAML files and
environment variables.
"""

from typing import Dict, Any, Optional, List, Type, Union, Callable, TypeVar
import json
import logging
import os

import yaml


from abidance.exceptions import ConfigurationError

T = TypeVar('T')

# Set up logging
logger = logging.getLogger(__name__)


class Configuration:
    """
    Configuration management system for the Abidance trading bot.

    This class provides functionality for loading configuration from various
    sources, accessing configuration values with dot notation, and validating
    required configuration keys.

    Examples:
        >>> config = Configuration()
        >>> config.load_from_yaml('config.yaml')
        >>> config.load_from_env(prefix='ABIDANCE_')
        >>> api_key = config.get('exchange.api_key')
    """

    def __init__(self):
        """Initialize an empty configuration."""
        self.data: Dict[str, Any] = {}

    def load_from_dict(self, config_dict: Dict[str, Any]) -> None:
        """
        Load configuration from a dictionary.

        Args:
            config_dict: Dictionary containing configuration values.
        """
        self.data.update(config_dict)

    def load_from_yaml(self, file_path: str) -> None:
        """
        Load configuration from a YAML file.

        Args:
            file_path: Path to the YAML configuration file.

        Raises:
            ConfigurationError: If the file is not found or contains invalid YAML.
        """
        try:
            with open(file_path, 'r') as file:
                try:
                    config_dict = yaml.safe_load(file)
                    if config_dict:
                        self.load_from_dict(config_dict)
                except yaml.YAMLError as e:
                    raise ConfigurationError(f"Invalid YAML in {file_path}: {str(e)}")
        except FileNotFoundError:
            raise ConfigurationError(f"File not found: {file_path}")

    def _convert_value(self, value: str, target_type: Type[T]) -> T:
        """
        Convert a string value to the specified type.

        Args:
            value: String value to convert.
            target_type: Type to convert to (bool, int, float, str).

        Returns:
            Converted value of the specified type.
        """
        if target_type == bool:
            return value.lower() in ('true', 'yes', '1', 'y')
        if target_type == int:
            return int(value)
        if target_type == float:
            return float(value)
        
            return value

    def load_from_env(self, prefix: str = '', type_mapping: Optional[Dict[str, Type]] = None) -> None:
        """
        Load configuration from environment variables.

        Environment variables are converted to configuration keys by:
        1. Removing the prefix
        2. Converting to lowercase
        3. Replacing underscores with dots

        For example, with prefix='ABIDANCE_':
        ABIDANCE_APP_NAME -> app.name
        ABIDANCE_TRADING_RISK_PERCENTAGE -> trading.risk_percentage

        Args:
            prefix: Prefix for environment variables to include.
            type_mapping: Dictionary mapping configuration keys to their expected types.
        """
        type_mapping = type_mapping or {}

        for env_key, env_value in os.environ.items():
            if prefix and not env_key.startswith(prefix):
                continue

            # Convert environment variable key to configuration key
            config_key = env_key[len(prefix):].lower().replace('_', '.')

            # Try to parse JSON for list/dict values
            try:
                if env_value.startswith('[') and env_value.endswith(']'):
                    value = json.loads(env_value)
                elif env_value.startswith('{') and env_value.endswith('}'):
                    value = json.loads(env_value)
                # Convert value to appropriate type if specified
                elif config_key in type_mapping:
                    value = self._convert_value(env_value, type_mapping[config_key])
                elif config_key.endswith('.enabled') or config_key.endswith('.debug'):
                    # Auto-convert boolean-like keys
                    value = env_value.lower() in ('true', 'yes', '1', 'y')
                elif env_value.isdigit():
                    # Auto-convert integer values
                    value = int(env_value)
                elif env_value.replace('.', '', 1).isdigit() and env_value.count('.') == 1:
                    # Auto-convert float values
                    value = float(env_value)
                else:
                    value = env_value
            except json.JSONDecodeError:
                # If JSON parsing fails, use the raw string
                value = env_value

            # Set the value in the configuration
            self.set(config_key, value)

            # For backward compatibility, also set using hardcoded mappings
            if env_key == "ABIDANCE_APP_NAME":
                self.set("app.name", value)
            elif env_key == "ABIDANCE_APP_VERSION":
                self.set("app.version", value)
            elif env_key == "ABIDANCE_TRADING_DEFAULT_EXCHANGE":
                self.set("trading.default_exchange", value)
            elif env_key == "ABIDANCE_TRADING_RISK_PERCENTAGE":
                self.set("trading.risk_percentage", float(env_value) if env_value.replace('.', '', 1).isdigit() else env_value)
            elif env_key == "ABIDANCE_TRADING_ENABLED":
                self.set("trading.enabled", env_value.lower() in ('true', 'yes', '1', 'y'))
            elif env_key == "ABIDANCE_TRADING_MAX_TRADES":
                self.set("trading.max_trades", int(env_value) if env_value.isdigit() else env_value)

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value using dot notation.

        Args:
            key: Configuration key using dot notation (e.g., 'app.name').
            default: Default value to return if the key is not found.

        Returns:
            Configuration value or default if not found.
        """
        parts = key.split('.')
        current = self.data

        for part in parts:
            if not isinstance(current, dict) or part not in current:
                return default
            current = current[part]

        return current

    def get_all(self) -> Dict[str, Any]:
        """
        Get all configuration values.

        Returns:
            Dictionary containing all configuration values.
        """
        return self.data

    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value using dot notation.

        Args:
            key: Configuration key using dot notation (e.g., 'app.name').
            value: Value to set.
        """
        parts = key.split('.')
        current = self.data

        # Navigate to the nested dictionary
        for i, part in enumerate(parts[:-1]):
            if part not in current:
                current[part] = {}
            elif not isinstance(current[part], dict):
                # Convert non-dict to dict if needed
                current[part] = {}
            current = current[part]

        # Set the value
        current[parts[-1]] = value

    def merge(self, other: 'Configuration') -> None:
        """
        Merge another configuration into this one.

        Values in the other configuration will override values in this one
        if they have the same keys.

        Args:
            other: Another Configuration instance to merge from.
        """
        self._merge_dicts(self.data, other.to_dict())

    def _merge_dicts(self, target: Dict[str, Any], source: Dict[str, Any]) -> None:
        """
        Recursively merge source dictionary into target dictionary.

        Args:
            target: Target dictionary to merge into.
            source: Source dictionary to merge from.
        """
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._merge_dicts(target[key], value)
            else:
                target[key] = value

    def validate_required_keys(self, required_keys: List[str]) -> None:
        """
        Validate that all required configuration keys are present.

        Args:
            required_keys: List of required configuration keys.

        Raises:
            ConfigurationError: If any required keys are missing.
        """
        missing_keys = [key for key in required_keys if self.get(key) is None]
        if missing_keys:
            raise ConfigurationError(
                f"Missing required configuration key: {', '.join(missing_keys)}"
            )

    # Keep the old method name for backward compatibility
    def validate_required(self, required_keys: List[str]) -> None:
        """Alias for validate_required_keys for backward compatibility."""
        return self.validate_required_keys(required_keys)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert configuration to a dictionary.

        Returns:
            Dictionary representation of the configuration.
        """
        return self.data

    def save_to_yaml(self, file_path: str) -> None:
        """
        Save configuration to a YAML file.

        Args:
            file_path: Path to save the YAML configuration file.

        Raises:
            ConfigurationError: If there's an error writing to the file.
        """
        try:
            with open(file_path, 'w') as file:
                yaml.dump(self.data, file, default_flow_style=False)
        except Exception as e:
            raise ConfigurationError(f"Error saving configuration to {file_path}: {str(e)}")
