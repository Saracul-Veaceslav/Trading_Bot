"""
Common validators for the Abidance trading bot.

This module provides common validator implementations that can be used
with the validation framework.
"""

import re
from typing import Any, Dict, List, Optional, Type, Union, Callable, Pattern
from decimal import Decimal

from .validation import Validator, ValidationError


class RequiredValidator(Validator):
    """Validator that ensures a value is not None or empty."""
    
    def validate(self, value: Any) -> List[ValidationError]:
        """
        Validate that a value is not None or empty.
        
        Args:
            value: The value to validate
            
        Returns:
            A list of validation errors, or an empty list if validation passes
        """
        errors = []
        
        if value is None:
            errors.append(ValidationError(
                field="",
                message="Value is required",
                code="required"
            ))
        elif isinstance(value, str) and not value.strip():
            errors.append(ValidationError(
                field="",
                message="Value cannot be empty",
                code="required"
            ))
        elif isinstance(value, (list, dict, set, tuple)) and not value:
            errors.append(ValidationError(
                field="",
                message="Value cannot be empty",
                code="required"
            ))
            
        return errors


class TypeValidator(Validator):
    """Validator that ensures a value is of a specific type."""
    
    def __init__(self, expected_type: Union[Type, tuple]):
        """
        Initialize the type validator.
        
        Args:
            expected_type: The expected type or tuple of types
        """
        self.expected_type = expected_type
        
    def validate(self, value: Any) -> List[ValidationError]:
        """
        Validate that a value is of the expected type.
        
        Args:
            value: The value to validate
            
        Returns:
            A list of validation errors, or an empty list if validation passes
        """
        errors = []
        
        if value is None:
            return errors
            
        if not isinstance(value, self.expected_type):
            # Format the type name differently depending on whether it's a single type or a tuple
            if isinstance(self.expected_type, tuple):
                type_names = [t.__name__ for t in self.expected_type]
                expected_type_str = f"one of ({', '.join(type_names)})"
            else:
                expected_type_str = self.expected_type.__name__
                
            errors.append(ValidationError(
                field="",
                message=f"Expected type {expected_type_str}, got {type(value).__name__}",
                code="type"
            ))
            
        return errors


class RangeValidator(Validator):
    """Validator that ensures a numeric value is within a specified range."""
    
    def __init__(self, min_value: Optional[Union[int, float, Decimal]] = None, 
                max_value: Optional[Union[int, float, Decimal]] = None):
        """
        Initialize the range validator.
        
        Args:
            min_value: The minimum allowed value (inclusive)
            max_value: The maximum allowed value (inclusive)
        """
        self.min_value = min_value
        self.max_value = max_value
        
    def validate(self, value: Union[int, float, Decimal]) -> List[ValidationError]:
        """
        Validate that a value is within the specified range.
        
        Args:
            value: The value to validate
            
        Returns:
            A list of validation errors, or an empty list if validation passes
        """
        errors = []
        
        if value is None:
            return errors
            
        if not isinstance(value, (int, float, Decimal)):
            errors.append(ValidationError(
                field="",
                message=f"Expected numeric value, got {type(value).__name__}",
                code="type"
            ))
            return errors
            
        if self.min_value is not None and value < self.min_value:
            errors.append(ValidationError(
                field="",
                message=f"Value must be at least {self.min_value}",
                code="min_value"
            ))
            
        if self.max_value is not None and value > self.max_value:
            errors.append(ValidationError(
                field="",
                message=f"Value must be at most {self.max_value}",
                code="max_value"
            ))
            
        return errors


class LengthValidator(Validator):
    """Validator that ensures a value's length is within a specified range."""
    
    def __init__(self, min_length: Optional[int] = None, max_length: Optional[int] = None):
        """
        Initialize the length validator.
        
        Args:
            min_length: The minimum allowed length (inclusive)
            max_length: The maximum allowed length (inclusive)
        """
        self.min_length = min_length
        self.max_length = max_length
        
    def validate(self, value: Any) -> List[ValidationError]:
        """
        Validate that a value's length is within the specified range.
        
        Args:
            value: The value to validate
            
        Returns:
            A list of validation errors, or an empty list if validation passes
        """
        errors = []
        
        if value is None:
            return errors
            
        try:
            length = len(value)
        except TypeError:
            errors.append(ValidationError(
                field="",
                message=f"Value of type {type(value).__name__} has no length",
                code="length"
            ))
            return errors
            
        if self.min_length is not None and length < self.min_length:
            errors.append(ValidationError(
                field="",
                message=f"Length must be at least {self.min_length}",
                code="min_length"
            ))
            
        if self.max_length is not None and length > self.max_length:
            errors.append(ValidationError(
                field="",
                message=f"Length must be at most {self.max_length}",
                code="max_length"
            ))
            
        return errors


class PatternValidator(Validator):
    """Validator that ensures a string value matches a regular expression pattern."""
    
    def __init__(self, pattern: Union[str, Pattern], error_message: Optional[str] = None):
        """
        Initialize the pattern validator.
        
        Args:
            pattern: The regular expression pattern to match
            error_message: Custom error message to use when validation fails
        """
        self.pattern = re.compile(pattern) if isinstance(pattern, str) else pattern
        self.error_message = error_message or "Value does not match the required pattern"
        
    def validate(self, value: str) -> List[ValidationError]:
        """
        Validate that a string value matches the specified pattern.
        
        Args:
            value: The value to validate
            
        Returns:
            A list of validation errors, or an empty list if validation passes
        """
        errors = []
        
        if value is None:
            return errors
            
        if not isinstance(value, str):
            errors.append(ValidationError(
                field="",
                message=f"Expected string value, got {type(value).__name__}",
                code="type"
            ))
            return errors
            
        if not self.pattern.match(value):
            errors.append(ValidationError(
                field="",
                message=self.error_message,
                code="pattern"
            ))
            
        return errors


class EmailValidator(PatternValidator):
    """Validator that ensures a string value is a valid email address."""
    
    def __init__(self):
        """Initialize the email validator with an email pattern."""
        # Simple email pattern for demonstration purposes
        # In a real application, email validation is more complex
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        super().__init__(pattern, "Invalid email address")


class CustomValidator(Validator):
    """Validator that uses a custom validation function."""
    
    def __init__(self, validation_func: Callable[[Any], bool], 
                error_message: str, error_code: str = "custom"):
        """
        Initialize the custom validator.
        
        Args:
            validation_func: A function that takes a value and returns True if valid
            error_message: The error message to use when validation fails
            error_code: The error code to use when validation fails
        """
        self.validation_func = validation_func
        self.error_message = error_message
        self.error_code = error_code
        
    def validate(self, value: Any) -> List[ValidationError]:
        """
        Validate a value using the custom validation function.
        
        Args:
            value: The value to validate
            
        Returns:
            A list of validation errors, or an empty list if validation passes
        """
        errors = []
        
        if not self.validation_func(value):
            errors.append(ValidationError(
                field="",
                message=self.error_message,
                code=self.error_code
            ))
            
        return errors 