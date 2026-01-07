"""
Data validation module for user data.

This module provides validation functions for user data.
"""

import logging
import re
from typing import Dict

from importer_cli.exceptions.exceptions import ValidationError
from importer_cli.models.models import User

logger = logging.getLogger(__name__)


class UserValidator:
    """Validator for user data."""

    # Email validation regex
    EMAIL_REGEX = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

    def __init__(self) -> None:
        """Initialize user validator."""
        self.email_pattern = re.compile(self.EMAIL_REGEX)
        logger.debug("Initialized UserValidator")

    def validate_user(self, user: User) -> bool:
        """
        Validate a User object.

        Args:
            user: User object to validate.

        Returns:
            bool: True if user is valid.

        Raises:
            ValidationError: If validation fails.
        """
        logger.debug(f"Validating User object: {user.user_id}")
        return self._validate(user.user_id, user.name, user.email)

    def validate_raw_data(self, user_data: Dict[str, str]) -> bool:
        """
        Validate raw user data (dictionary).

        Args:
            user_data: Dictionary with user_id, name, email.

        Returns:
            bool: True if data is valid.

        Raises:
            ValidationError: If validation fails.
        """
        logger.debug(f"Validating raw user data: {user_data.get('user_id')}")

        user_id = user_data.get("user_id", "")
        name = user_data.get("name", "")
        email = user_data.get("email", "")

        return self._validate(user_id, name, email)

    def _validate(self, user_id: str, name: str, email: str) -> bool:
        """
        Internal validation method.

        Args:
            user_id: User ID to validate.
            name: Name to validate.
            email: Email to validate.

        Returns:
            bool: True if all fields are valid.

        Raises:
            ValidationError: If validation fails.
        """
        # Check user_id
        if not user_id or not user_id.strip():
            raise ValidationError(
                field="user_id",
                value=user_id,
                message="User ID cannot be empty",
            )

        # Check name
        if not name or not name.strip():
            raise ValidationError(
                field="name",
                value=name,
                message="Name cannot be empty",
            )

        # Check email format
        if not self._validate_email(email):
            raise ValidationError(
                field="email",
                value=email,
                message="Invalid email format",
            )

        logger.debug(f"User validation passed: {user_id}")
        return True

    def _validate_email(self, email: str) -> bool:
        """
        Validate email format.

        Args:
            email: Email address to validate.

        Returns:
            bool: True if email format is valid.
        """
        if not email or not isinstance(email, str):
            return False

        return bool(self.email_pattern.match(email))

    def sanitize_user_id(self, user_id: str) -> str:
        """
        Sanitize user ID by removing extra whitespace.

        Args:
            user_id: User ID to sanitize.

        Returns:
            str: Sanitized user ID.
        """
        return user_id.strip()

    def sanitize_name(self, name: str) -> str:
        """
        Sanitize name by removing extra whitespace and title casing.

        Args:
            name: Name to sanitize.

        Returns:
            str: Sanitized name.
        """
        # Remove extra whitespace and title case
        return " ".join(word.strip().title() for word in name.split())

    def sanitize_email(self, email: str) -> str:
        """
        Sanitize email by removing extra whitespace and lowercasing.

        Args:
            email: Email to sanitize.

        Returns:
            str: Sanitized email.
        """
        return email.strip().lower()
