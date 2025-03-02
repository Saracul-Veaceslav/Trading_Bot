"""
Environment module for managing environment variables.

This module provides a centralized way to manage environment variables in the application.
It supports loading from .env files, type conversion, and validation.
"""

import os
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Type, TypeVar, Union, cast

from dotenv import load_dotenv

from abidance.exceptions import ConfigurationError

T = TypeVar('T')


class Environment:
    """
    Environment class for managing environment variables.

    This class provides methods for loading environment variables from .env files,
    accessing them with type conversion, and validating required variables.
    """

    def __init__(self) -> None:
        """Initialize the Environment instance."""
        self._loaded = False

    def load(self, env_file: Optional[str] = None) -> bool:
        """
        Load environment variables from a .env file.

        Args:
            env_file: Path to the .env file. If None, it will try to find a .env file
                     in the current directory.

        Returns:
            bool: True if the environment variables were loaded successfully, False otherwise.

        Raises:
            ConfigurationError: If the specified env_file does not exist or cannot be loaded.
        """
        # We need to use Path.exists() for proper mocking in tests
        if env_file and not Path(env_file).exists():
            raise ConfigurationError(f"Environment file not found: {env_file}")

        try:
            result = load_dotenv(dotenv_path=env_file, override=True)
            if not result and env_file:
                raise ConfigurationError(f"Failed to load environment from {env_file}")
            self._loaded = result
            return result
        except Exception as e:
            raise ConfigurationError(f"Failed to load environment variables: {str(e)}") from e

    def get(self, key: str, default: Optional[Any] = None, required: bool = False) -> Optional[str]:
        """
        Get an environment variable.

        Args:
            key: The name of the environment variable.
            default: The default value to return if the variable is not set.
            required: If True and the environment variable is not set, raises an error.

        Returns:
            The value of the environment variable, or the default value if not set.

        Raises:
            ConfigurationError: If required is True and the environment variable is not set.
        """
        value = os.environ.get(key)
        if value is None:
            if required:
                raise ConfigurationError(f"Required environment variable not set: {key}")
            return default
        return value

    def get_required(self, key: str) -> str:
        """
        Get a required environment variable.

        Args:
            key: The name of the environment variable.

        Returns:
            The value of the environment variable.

        Raises:
            ConfigurationError: If the environment variable is not set.
        """
        return self.get(key, required=True)  # type: ignore

    def get_bool(self, key: str, default: Optional[bool] = None, required: bool = False) -> Optional[bool]:
        """
        Get an environment variable as a boolean.

        Args:
            key: The name of the environment variable.
            default: The default value to return if the variable is not set.
            required: If True and the environment variable is not set, raises an error.

        Returns:
            The boolean value of the environment variable, or the default value if not set.

        Raises:
            ConfigurationError: If required is True and the environment variable is not set,
                               or if the value cannot be converted to a boolean.
        """
        value = self.get(key, None, required)
        if value is None:
            return default

        value = str(value).lower()
        if value in ('true', 'yes', '1', 'y', 'on'):
            return True
        if value in ('false', 'no', '0', 'n', 'off'):
            return False

        raise ConfigurationError(f"Cannot convert environment variable {key}={value} to boolean")

    def get_int(self, key: str, default: Optional[int] = None, required: bool = False) -> Optional[int]:
        """
        Get an environment variable as an integer.

        Args:
            key: The name of the environment variable.
            default: The default value to return if the variable is not set.
            required: If True and the environment variable is not set, raises an error.

        Returns:
            The integer value of the environment variable, or the default value if not set.

        Raises:
            ConfigurationError: If required is True and the environment variable is not set,
                               or if the value cannot be converted to an integer.
        """
        value = self.get(key, None, required)
        if value is None:
            return default

        try:
            return int(value)
        except ValueError:
            raise ConfigurationError(f"Cannot convert environment variable {key}={value} to integer")

    def get_float(self, key: str, default: Optional[float] = None, required: bool = False) -> Optional[float]:
        """
        Get an environment variable as a float.

        Args:
            key: The name of the environment variable.
            default: The default value to return if the variable is not set.
            required: If True and the environment variable is not set, raises an error.

        Returns:
            The float value of the environment variable, or the default value if not set.

        Raises:
            ConfigurationError: If required is True and the environment variable is not set,
                               or if the value cannot be converted to a float.
        """
        value = self.get(key, None, required)
        if value is None:
            return default

        try:
            return float(value)
        except ValueError:
            raise ConfigurationError(f"Cannot convert environment variable {key}={value} to float")

    def get_list(self, key: str, default: Optional[list] = None, required: bool = False) -> Optional[list]:
        """
        Get an environment variable as a list.

        The environment variable should be a JSON-encoded list or a comma-separated string.

        Args:
            key: The name of the environment variable.
            default: The default value to return if the variable is not set.
            required: If True and the environment variable is not set, raises an error.

        Returns:
            The list value of the environment variable, or the default value if not set.

        Raises:
            ConfigurationError: If required is True and the environment variable is not set,
                               or if the value cannot be converted to a list.
        """
        value = self.get(key, None, required)
        if value is None:
            return default

        # Try to parse as JSON
        if value.startswith('['):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                pass

        # Fall back to comma-separated string
        return [item.strip() for item in value.split(',')]
    
    def get_dict(self, key: str, default: Optional[Dict[str, Any]] = None, required: bool = False) -> Optional[Dict[str, Any]]:
        """
        Get an environment variable as a dictionary.

        The environment variable should be a JSON-encoded dictionary.

        Args:
            key: The name of the environment variable.
            default: The default value to return if the variable is not set.
            required: If True and the environment variable is not set, raises an error.

        Returns:
            The dictionary value of the environment variable, or the default value if not set.

        Raises:
            ConfigurationError: If required is True and the environment variable is not set,
                               or if the value cannot be converted to a dictionary.
        """
        value = self.get(key, None, required)
        if value is None:
            return default

        try:
            return cast(Dict[str, Any], json.loads(value))
        except json.JSONDecodeError:
            raise ConfigurationError(f"Cannot convert environment variable {key}={value} to dictionary")

    def get_path(self, key: str, default: Optional[Path] = None, required: bool = False) -> Optional[Path]:
        """
        Get an environment variable as a Path.

        Args:
            key: The name of the environment variable.
            default: The default value to return if the variable is not set.
            required: If True and the environment variable is not set, raises an error.

        Returns:
            The Path value of the environment variable, or the default value if not set.
            
        Raises:
            ConfigurationError: If required is True and the environment variable is not set.
        """
        value = self.get(key, None, required)
        if value is None:
            return default

        return Path(value)

    def get_typed(self, key: str, type_: Type[T], default: Optional[T] = None, required: bool = False) -> Optional[T]:
        """
        Get a typed environment variable.

        Args:
            key: The name of the environment variable.
            type_: The type to convert the value to.
            default: The default value to return if the variable is not set.
            required: If True and the environment variable is not set, raises an error.

        Returns:
            The typed value of the environment variable, or the default value if not set.

        Raises:
            ConfigurationError: If required is True and the environment variable is not set,
                               or if the value cannot be converted to the specified type.
        """
        value = self.get(key, None, required)
        if value is None:
            return default

        try:
            return type_(value)  # type: ignore
        except (ValueError, TypeError):
            raise ConfigurationError(f"Cannot convert environment variable {key}={value} to {type_.__name__}")

    def get_all(self, prefix: str = '') -> Dict[str, str]:
        """
        Get all environment variables with an optional prefix.

        Args:
            prefix: Only include environment variables that start with this prefix.

        Returns:
            A dictionary of environment variables.
        """
        result = {}
        for key, value in os.environ.items():
            if not prefix or key.startswith(prefix):
                result[key] = value
        return result


# Global environment instance
env = Environment() 