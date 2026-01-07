"""
Tests for data models.
These tests verify that our User and ImportResult classes work correctly.
"""

import pytest

from importer_cli.models.models import ImportResult, User


class TestUser:
    """Test cases for User model."""

    def test_user_creation(self) -> None:
        """Basic test: can we create a user with valid data?"""
        user = User(user_id="123", name="John Doe", email="john@example.com")

        # Assertions verify expected behavior
        assert user.user_id == "123"
        assert user.name == "John Doe"
        assert user.email == "john@example.com"

    def test_user_validation_valid(self) -> None:
        """
        Test that valid data passes validation.
        The _validate() method is called during __init__.
        If no exception is raised, the test passes
        """
        user = User(user_id="123", name="John Doe", email="john@example.com")
        user._validate()

    @pytest.mark.parametrize(
        "user_id,name,email,expected_error",
        [
            # Empty user_id
            ("", "John Doe", "john@example.com", "user_id must be a non-empty string"),
            # Empty name
            ("123", "", "john@example.com", "name must be a non-empty string"),
            # Empty email
            ("123", "John Doe", "", "email must be a non-empty string"),
            # Invalid email format
            ("123", "John Doe", "invalid", "email must contain '@'"),
            # None values
            (
                None,
                "John Doe",
                "john@example.com",
                "user_id must be a non-empty string",
            ),
        ],
    )
    def test_user_validation_invalid(
        self, user_id: str, name: str, email: str, expected_error: str
    ) -> None:
        """
        Test validation with various invalid inputs.

        @pytest.mark.parametrize runs this test multiple times with different data.
        This is more efficient than writing separate test functions!
        """
        with pytest.raises(ValueError, match=expected_error):
            # Creating a User with invalid data should raise ValueError
            User(user_id=user_id, name=name, email=email)


class TestImportResult:
    """Test cases for ImportResult model."""

    def test_import_result_creation(self) -> None:
        """Test that ImportResult starts with default values."""
        result = ImportResult()
        assert result.total_processed == 0
        assert result.successful == 0
        assert result.failed == 0
        assert result.duplicates_skipped == 0
        assert result.errors == []

    def test_add_error(self) -> None:
        """Test adding an error to the result."""
        result = ImportResult()
        result.add_error(1, "Test error")

        # Check error was recorded
        assert result.errors == [(1, "Test error")]
        # Check failed count was incremented
        assert result.failed == 1

    def test_str_representation(self) -> None:
        """Test the string output format."""
        result = ImportResult(
            total_processed=10,
            successful=7,
            failed=2,
            duplicates_skipped=1,
            errors=[(3, "Error 1"), (5, "Error 2")],
        )
        str_result = str(result)

        # Check all important info is in the string
        assert "Total Processed: 10" in str_result
        assert "Successful: 7" in str_result
        assert "Failed: 2" in str_result
        assert "Duplicates Skipped: 1" in str_result
