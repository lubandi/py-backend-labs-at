"""
Tests for user validator.
"""

import pytest

from importer_cli.models.models import User
from importer_cli.validator.validator import UserValidator


class TestUserValidator:
    """Test cases for UserValidator."""

    def test_validator_initialization(self) -> None:
        """Test UserValidator initialization."""
        validator = UserValidator()
        assert validator is not None

    @pytest.mark.parametrize(
        "email,expected_valid",
        [
            ("test@example.com", True),
            ("user.name@domain.co.uk", True),
            ("invalid-email", False),
            ("@example.com", False),
            ("test@", False),
            ("", False),
            (None, False),
        ],
    )
    def test_validate_email_pattern(self, email: str, expected_valid: bool) -> None:
        """Test email validation using parametrize."""
        validator = UserValidator()

        # For valid emails, create a User and test validation
        if expected_valid:
            user = User(user_id="123", name="Test User", email=email)
            result = validator.validate_user(user)
            assert result is True
        else:
            # For invalid emails, test _validate_email directly
            result = validator._validate_email(email)
            assert result is False

    @pytest.mark.parametrize(
        "user_id,name,email,should_pass",
        [
            ("123", "John Doe", "john@example.com", True),
            ("", "John Doe", "john@example.com", False),
            ("123", "", "john@example.com", False),
            ("123", "John Doe", "", False),
            ("123", "John Doe", "invalid-email", False),
        ],
    )
    def test_validate_user(
        self, user_id: str, name: str, email: str, should_pass: bool
    ) -> None:
        """Test user validation with parametrize."""
        validator = UserValidator()

        # Only create User objects for cases that would pass User model validation
        if should_pass:
            user = User(user_id=user_id, name=name, email=email)
            assert validator.validate_user(user) is True
        else:
            # For invalid cases, test validate_raw_data instead
            user_data = {"user_id": user_id, "name": name, "email": email}

            with pytest.raises(Exception):
                validator.validate_raw_data(user_data)

    def test_validate_raw_data_valid(self) -> None:
        """Test validate_raw_data with valid data."""
        validator = UserValidator()

        user_data = {"user_id": "123", "name": "John Doe", "email": "john@example.com"}

        result = validator.validate_raw_data(user_data)
        assert result is True

    def test_validate_raw_data_invalid(self) -> None:
        """Test validate_raw_data with invalid data."""
        validator = UserValidator()

        user_data = {"user_id": "", "name": "John Doe", "email": "john@example.com"}

        with pytest.raises(Exception):
            validator.validate_raw_data(user_data)

    @pytest.mark.parametrize(
        "input_name,expected_output",
        [
            ("  john doe  ", "John Doe"),
            ("JOHN DOE", "John Doe"),
            ("john   doe", "John Doe"),
            ("", ""),
            ("  ", ""),
        ],
    )
    def test_sanitize_name(self, input_name: str, expected_output: str) -> None:
        """Test name sanitization with parametrize."""
        validator = UserValidator()
        assert validator.sanitize_name(input_name) == expected_output

    @pytest.mark.parametrize(
        "input_email,expected_output",
        [
            ("  TEST@EXAMPLE.COM  ", "test@example.com"),
            ("Test@Example.com", "test@example.com"),
            ("", ""),
            ("  ", ""),
        ],
    )
    def test_sanitize_email(self, input_email: str, expected_output: str) -> None:
        """Test email sanitization with parametrize."""
        validator = UserValidator()
        assert validator.sanitize_email(input_email) == expected_output

    def test_validate_with_sanitization(self) -> None:
        """Test validation with sanitization workflow."""
        validator = UserValidator()

        # Create a valid user with sanitized data
        user = User(user_id="test123", name="John Doe", email="test@example.com")

        # Should pass validation
        assert validator.validate_user(user) is True
