"""
Tests for the validation framework.
"""

import pytest
from decimal import Decimal
from typing import List, Dict, Any

from abidance.core.validation import ValidationError, Validator, ValidationContext
from abidance.core.validators import (
    RequiredValidator,
    TypeValidator,
    RangeValidator,
    LengthValidator,
    PatternValidator,
    EmailValidator,
    CustomValidator
)


class TestValidationError:
    """Tests for the ValidationError class."""
    
    def test_validation_error_creation(self):
        """Test creating a ValidationError instance."""
        error = ValidationError(field="name", message="Name is required", code="required")
        
        assert error.field == "name"
        assert error.message == "Name is required"
        assert error.code == "required"
    
    def test_validation_error_str(self):
        """Test the string representation of ValidationError."""
        error = ValidationError(field="name", message="Name is required", code="required")
        
        assert str(error) == "ValidationError(field='name', message='Name is required', code='required')"


class TestValidator:
    """Tests for the Validator abstract base class."""
    
    def test_validator_is_abstract(self):
        """Test that Validator cannot be instantiated directly."""
        with pytest.raises(TypeError):
            Validator()


class TestValidationContext:
    """Tests for the ValidationContext class."""
    
    def test_add_validator(self):
        """Test adding a validator to the context."""
        context = ValidationContext()
        validator = RequiredValidator()
        
        context.add_validator("name", validator)
        
        assert "name" in context.validators
        assert validator in context.validators["name"]
    
    def test_add_multiple_validators_for_field(self):
        """Test adding multiple validators for a single field."""
        context = ValidationContext()
        required_validator = RequiredValidator()
        type_validator = TypeValidator(str)
        
        context.add_validator("name", required_validator)
        context.add_validator("name", type_validator)
        
        assert len(context.validators["name"]) == 2
        assert required_validator in context.validators["name"]
        assert type_validator in context.validators["name"]
    
    def test_validate_valid_data(self):
        """Test validating data that passes all validators."""
        context = ValidationContext()
        context.add_validator("name", RequiredValidator())
        context.add_validator("name", TypeValidator(str))
        context.add_validator("age", TypeValidator(int))
        context.add_validator("age", RangeValidator(min_value=18, max_value=120))
        
        data = {"name": "John Doe", "age": 30}
        errors = context.validate(data)
        
        assert not errors
        assert context.is_valid(data)
    
    def test_validate_invalid_data(self):
        """Test validating data that fails validation."""
        context = ValidationContext()
        context.add_validator("name", RequiredValidator())
        context.add_validator("age", TypeValidator(int))
        context.add_validator("age", RangeValidator(min_value=18, max_value=120))
        
        data = {"name": "", "age": 15}
        errors = context.validate(data)
        
        assert len(errors) == 2
        assert any(e.field == "name" and e.code == "required" for e in errors)
        assert any(e.field == "age" and e.code == "min_value" for e in errors)
        assert not context.is_valid(data)
    
    def test_validate_missing_field(self):
        """Test validating data with a missing field."""
        context = ValidationContext()
        context.add_validator("name", RequiredValidator())
        context.add_validator("age", RequiredValidator())
        
        data = {"name": "John Doe"}
        errors = context.validate(data)
        
        # No error for age since it's not in the data
        assert not errors
        assert context.is_valid(data)
    
    def test_validate_with_none_value(self):
        """Test validating data with a None value."""
        context = ValidationContext()
        context.add_validator("name", RequiredValidator())
        
        data = {"name": None}
        errors = context.validate(data)
        
        assert len(errors) == 1
        assert errors[0].field == "name"
        assert errors[0].code == "required"
        assert not context.is_valid(data)


class TestRequiredValidator:
    """Tests for the RequiredValidator class."""
    
    def test_required_validator_with_none(self):
        """Test RequiredValidator with None value."""
        validator = RequiredValidator()
        errors = validator.validate(None)
        
        assert len(errors) == 1
        assert errors[0].code == "required"
    
    def test_required_validator_with_empty_string(self):
        """Test RequiredValidator with empty string."""
        validator = RequiredValidator()
        errors = validator.validate("")
        
        assert len(errors) == 1
        assert errors[0].code == "required"
    
    def test_required_validator_with_whitespace_string(self):
        """Test RequiredValidator with whitespace string."""
        validator = RequiredValidator()
        errors = validator.validate("   ")
        
        assert len(errors) == 1
        assert errors[0].code == "required"
    
    def test_required_validator_with_empty_list(self):
        """Test RequiredValidator with empty list."""
        validator = RequiredValidator()
        errors = validator.validate([])
        
        assert len(errors) == 1
        assert errors[0].code == "required"
    
    def test_required_validator_with_empty_dict(self):
        """Test RequiredValidator with empty dict."""
        validator = RequiredValidator()
        errors = validator.validate({})
        
        assert len(errors) == 1
        assert errors[0].code == "required"
    
    def test_required_validator_with_valid_value(self):
        """Test RequiredValidator with valid value."""
        validator = RequiredValidator()
        errors = validator.validate("John Doe")
        
        assert not errors


class TestTypeValidator:
    """Tests for the TypeValidator class."""
    
    def test_type_validator_with_correct_type(self):
        """Test TypeValidator with correct type."""
        validator = TypeValidator(str)
        errors = validator.validate("John Doe")
        
        assert not errors
    
    def test_type_validator_with_incorrect_type(self):
        """Test TypeValidator with incorrect type."""
        validator = TypeValidator(str)
        errors = validator.validate(123)
        
        assert len(errors) == 1
        assert errors[0].code == "type"
    
    def test_type_validator_with_none(self):
        """Test TypeValidator with None value."""
        validator = TypeValidator(str)
        errors = validator.validate(None)
        
        assert not errors
    
    def test_type_validator_with_multiple_types(self):
        """Test TypeValidator with multiple allowed types."""
        validator = TypeValidator((str, int))
        
        assert not validator.validate("John Doe")
        assert not validator.validate(123)
        assert len(validator.validate(1.23)) == 1


class TestRangeValidator:
    """Tests for the RangeValidator class."""
    
    def test_range_validator_with_valid_value(self):
        """Test RangeValidator with valid value."""
        validator = RangeValidator(min_value=0, max_value=100)
        errors = validator.validate(50)
        
        assert not errors
    
    def test_range_validator_with_min_value_only(self):
        """Test RangeValidator with only min_value specified."""
        validator = RangeValidator(min_value=0)
        
        assert not validator.validate(0)
        assert not validator.validate(100)
        assert len(validator.validate(-1)) == 1
    
    def test_range_validator_with_max_value_only(self):
        """Test RangeValidator with only max_value specified."""
        validator = RangeValidator(max_value=100)
        
        assert not validator.validate(0)
        assert not validator.validate(100)
        assert len(validator.validate(101)) == 1
    
    def test_range_validator_with_decimal(self):
        """Test RangeValidator with Decimal values."""
        validator = RangeValidator(min_value=Decimal('0.1'), max_value=Decimal('1.0'))
        
        assert not validator.validate(Decimal('0.5'))
        assert len(validator.validate(Decimal('0.05'))) == 1
        assert len(validator.validate(Decimal('1.1'))) == 1
    
    def test_range_validator_with_non_numeric(self):
        """Test RangeValidator with non-numeric value."""
        validator = RangeValidator(min_value=0, max_value=100)
        errors = validator.validate("50")
        
        assert len(errors) == 1
        assert errors[0].code == "type"
    
    def test_range_validator_with_none(self):
        """Test RangeValidator with None value."""
        validator = RangeValidator(min_value=0, max_value=100)
        errors = validator.validate(None)
        
        assert not errors


class TestLengthValidator:
    """Tests for the LengthValidator class."""
    
    def test_length_validator_with_valid_string(self):
        """Test LengthValidator with valid string."""
        validator = LengthValidator(min_length=3, max_length=10)
        errors = validator.validate("John")
        
        assert not errors
    
    def test_length_validator_with_valid_list(self):
        """Test LengthValidator with valid list."""
        validator = LengthValidator(min_length=1, max_length=5)
        errors = validator.validate([1, 2, 3])
        
        assert not errors
    
    def test_length_validator_with_min_length_only(self):
        """Test LengthValidator with only min_length specified."""
        validator = LengthValidator(min_length=3)
        
        assert not validator.validate("John")
        assert len(validator.validate("Jo")) == 1
    
    def test_length_validator_with_max_length_only(self):
        """Test LengthValidator with only max_length specified."""
        validator = LengthValidator(max_length=5)
        
        assert not validator.validate("John")
        assert len(validator.validate("John Doe")) == 1
    
    def test_length_validator_with_no_length(self):
        """Test LengthValidator with value that has no length."""
        validator = LengthValidator(min_length=1)
        errors = validator.validate(123)
        
        assert len(errors) == 1
        assert errors[0].code == "length"
    
    def test_length_validator_with_none(self):
        """Test LengthValidator with None value."""
        validator = LengthValidator(min_length=1)
        errors = validator.validate(None)
        
        assert not errors


class TestPatternValidator:
    """Tests for the PatternValidator class."""
    
    def test_pattern_validator_with_matching_value(self):
        """Test PatternValidator with matching value."""
        validator = PatternValidator(r'^\d{3}-\d{2}-\d{4}$')
        errors = validator.validate("123-45-6789")
        
        assert not errors
    
    def test_pattern_validator_with_non_matching_value(self):
        """Test PatternValidator with non-matching value."""
        validator = PatternValidator(r'^\d{3}-\d{2}-\d{4}$')
        errors = validator.validate("123-456-789")
        
        assert len(errors) == 1
        assert errors[0].code == "pattern"
    
    def test_pattern_validator_with_custom_error_message(self):
        """Test PatternValidator with custom error message."""
        validator = PatternValidator(r'^\d{3}-\d{2}-\d{4}$', "Invalid SSN format")
        errors = validator.validate("123-456-789")
        
        assert len(errors) == 1
        assert errors[0].message == "Invalid SSN format"
    
    def test_pattern_validator_with_non_string(self):
        """Test PatternValidator with non-string value."""
        validator = PatternValidator(r'^\d+$')
        errors = validator.validate(123)
        
        assert len(errors) == 1
        assert errors[0].code == "type"
    
    def test_pattern_validator_with_none(self):
        """Test PatternValidator with None value."""
        validator = PatternValidator(r'^\d+$')
        errors = validator.validate(None)
        
        assert not errors


class TestEmailValidator:
    """Tests for the EmailValidator class."""
    
    def test_email_validator_with_valid_email(self):
        """Test EmailValidator with valid email."""
        validator = EmailValidator()
        errors = validator.validate("user@example.com")
        
        assert not errors
    
    def test_email_validator_with_invalid_email(self):
        """Test EmailValidator with invalid email."""
        validator = EmailValidator()
        
        assert len(validator.validate("user@")) == 1
        assert len(validator.validate("user@example")) == 1
        assert len(validator.validate("user.example.com")) == 1
    
    def test_email_validator_with_none(self):
        """Test EmailValidator with None value."""
        validator = EmailValidator()
        errors = validator.validate(None)
        
        assert not errors


class TestCustomValidator:
    """Tests for the CustomValidator class."""
    
    def test_custom_validator_with_valid_value(self):
        """Test CustomValidator with valid value."""
        validator = CustomValidator(
            lambda x: x % 2 == 0,
            "Value must be even",
            "even"
        )
        errors = validator.validate(2)
        
        assert not errors
    
    def test_custom_validator_with_invalid_value(self):
        """Test CustomValidator with invalid value."""
        validator = CustomValidator(
            lambda x: x % 2 == 0,
            "Value must be even",
            "even"
        )
        errors = validator.validate(3)
        
        assert len(errors) == 1
        assert errors[0].message == "Value must be even"
        assert errors[0].code == "even"
    
    def test_custom_validator_with_complex_validation(self):
        """Test CustomValidator with more complex validation logic."""
        def is_valid_password(password):
            if not isinstance(password, str):
                return False
            if len(password) < 8:
                return False
            if not any(c.isupper() for c in password):
                return False
            if not any(c.islower() for c in password):
                return False
            if not any(c.isdigit() for c in password):
                return False
            return True
        
        validator = CustomValidator(
            is_valid_password,
            "Password must be at least 8 characters and contain uppercase, lowercase, and digits",
            "password"
        )
        
        assert not validator.validate("Password123")
        assert len(validator.validate("password")) == 1
        assert len(validator.validate("PASSWORD123")) == 1
        assert len(validator.validate("Password")) == 1


class TestIntegration:
    """Integration tests for the validation framework."""
    
    def test_complex_validation_scenario(self):
        """Test a complex validation scenario with multiple validators."""
        # Create a validation context for a user registration form
        context = ValidationContext()
        
        # Add validators for username
        context.add_validator("username", RequiredValidator())
        context.add_validator("username", LengthValidator(min_length=3, max_length=20))
        context.add_validator("username", PatternValidator(r'^[a-zA-Z0-9_]+$', "Username can only contain letters, numbers, and underscores"))
        
        # Add validators for email
        context.add_validator("email", RequiredValidator())
        context.add_validator("email", EmailValidator())
        
        # Add validators for age
        context.add_validator("age", TypeValidator(int))
        context.add_validator("age", RangeValidator(min_value=18, max_value=120))
        
        # Add validators for password
        context.add_validator("password", RequiredValidator())
        context.add_validator("password", LengthValidator(min_length=8))
        context.add_validator("password", CustomValidator(
            lambda p: isinstance(p, str) and any(c.isupper() for c in p) and any(c.islower() for c in p) and any(c.isdigit() for c in p),
            "Password must contain uppercase, lowercase, and digits",
            "password_complexity"
        ))
        
        # Valid data
        valid_data = {
            "username": "john_doe",
            "email": "john@example.com",
            "age": 30,
            "password": "Password123"
        }
        
        assert context.is_valid(valid_data)
        
        # Invalid data
        invalid_data = {
            "username": "j",
            "email": "john@example",
            "age": 15,
            "password": "password"
        }
        
        errors = context.validate(invalid_data)
        assert len(errors) == 4
        
        # Check specific errors
        error_codes = [e.code for e in errors]
        assert "min_length" in error_codes  # Username too short
        assert "pattern" in error_codes     # Email invalid
        assert "min_value" in error_codes   # Age too low
        assert "password_complexity" in error_codes  # Password not complex enough 