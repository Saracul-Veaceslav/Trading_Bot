"""
Validation framework for the Abidance trading bot.

This module provides a validation framework for ensuring data integrity
and consistent validation across the application.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type, Union, Callable

from dataclasses import dataclass


@dataclass
class ValidationError:
    """
    Represents a validation error.

    Attributes:
        field: The name of the field that failed validation
        message: The error message
        code: A code identifying the type of error
    """
    field: str
    message: str
    code: str

    def __str__(self) -> str:
        """Return a string representation of the validation error."""
        return f"ValidationError(field='{self.field}', message='{self.message}', code='{self.code}')"


class Validator(ABC):
    """
    Abstract base class for validators.

    All validators should inherit from this class and implement the validate method.
    """

    @abstractmethod
    def validate(self, value: Any) -> List[ValidationError]:
        """
        Validate a value and return a list of validation errors.

        Args:
            value: The value to validate

        Returns:
            A list of validation errors, or an empty list if validation passes
        """
        pass


class ValidationContext:
    """
    Manages multiple validators for different fields.

    This class allows adding validators for specific fields and validating
    a data dictionary against all registered validators.
    """

    def __init__(self):
        """Initialize the validation context with an empty validators dictionary."""
        self.validators: Dict[str, List[Validator]] = {}

    def add_validator(self, field: str, validator: Validator) -> None:
        """
        Add a validator for a specific field.

        Args:
            field: The name of the field to validate
            validator: The validator to use
        """
        if field not in self.validators:
            self.validators[field] = []
        self.validators[field].append(validator)

    def validate(self, data: Dict[str, Any]) -> List[ValidationError]:
        """
        Validate a data dictionary against all registered validators.

        Args:
            data: The data dictionary to validate

        Returns:
            A list of validation errors, or an empty list if validation passes
        """
        errors = []

        for field, validators in self.validators.items():
            if field in data:
                value = data[field]
                for validator in validators:
                    field_errors = validator.validate(value)
                    for error in field_errors:
                        # Set the field name if not already set
                        if not error.field:
                            error.field = field
                        errors.append(error)

        return errors

    def is_valid(self, data: Dict[str, Any]) -> bool:
        """
        Check if a data dictionary is valid.

        Args:
            data: The data dictionary to validate

        Returns:
            True if the data is valid, False otherwise
        """
        return len(self.validate(data)) == 0
