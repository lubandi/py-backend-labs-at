"""
Data validation module for user data.

This module provides validation functions for user data.
"""

import logging
import re

from exceptions.exceptions import ValidationError
from models.models import User

logger = logging.getLogger(__name__)


class UserValidator:
    """Validator for user data."""

    # Email validation regex (simplified)
    EMAIL_REGEX = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

    def __init__(self) -> None:
        """Initialize user validator."""
        self.email_pattern = re.compile(self.EMAIL_REGEX)
        logger.debug("Initialized UserValidator")

    def validate(self, user: User) -> bool:
        """
        Validate a user object.

        Args:
            user: User object to validate.

        Returns:
            bool: True if user is valid.

        Raises:
            ValidationError: If validation fails.
        """
        logger.debug(f"Validating user: {user.user_id}")

        # Check user_id
        if not user.user_id or not user.user_id.strip():
            raise ValidationError(
                field="user_id",
                value=user.user_id,
                message="User ID cannot be empty",
            )

        # Check name
        if not user.name or not user.name.strip():
            raise ValidationError(
                field="name",
                value=user.name,
                message="Name cannot be empty",
            )

        # Check email format
        if not self._validate_email(user.email):
            raise ValidationError(
                field="email",
                value=user.email,
                message="Invalid email format",
            )

        logger.debug(f"User validation passed: {user.user_id}")
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
