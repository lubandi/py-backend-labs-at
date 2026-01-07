"""
Repository module for data storage operations.

This module implements the repository pattern for storing and retrieving
user data from a JSON file (simulated database).
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional

from importer_cli.context_manager.file_handler import JSONFileHandler
from importer_cli.exceptions.exceptions import DuplicateUserError, MissingFileError
from importer_cli.models.models import User

logger = logging.getLogger(__name__)


class UserRepository:
    """Repository for managing user data storage."""

    def __init__(self, db_path: str | Path = "data/users.json") -> None:
        """
        Initialize user repository.

        Args:
            db_path: Path to the JSON database file.
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        logger.info(f"Initialized UserRepository with database: {self.db_path}")

    def _load_data(self) -> Dict[str, Dict[str, str]]:
        """
        Load user data from JSON file.

        Returns:
            dict: Dictionary of user data.

        Note:
            Creates an empty database file if it doesn't exist.
        """
        try:
            with JSONFileHandler(self.db_path, mode="r") as handler:
                data = handler  # handler returns the data in read mode
                if not isinstance(data, dict):
                    logger.warning(
                        f"Database {self.db_path} is not a dict, creating new"
                    )
                    return {}
                return data
        except (FileNotFoundError, MissingFileError):
            logger.info(f"Database file {self.db_path} not found, creating new")
            return {}
        except Exception as e:
            logger.error(f"Error loading database: {e}")
            raise

    def _save_data(self, data: Dict[str, Dict[str, str]]) -> None:
        """
        Save user data to JSON file.

        Args:
            data: Dictionary of user data to save.
        """
        try:
            # Create the handler object
            handler = JSONFileHandler(self.db_path, mode="w")

            with handler:
                handler.write_data(data)

            logger.debug(f"Database saved to {self.db_path}")
        except Exception as e:
            logger.error(f"Error saving database: {e}")
            raise

    def find_by_id(self, user_id: str) -> Optional[User]:
        """
        Find a user by their ID.

        Args:
            user_id: User ID to search for.

        Returns:
            User: User object if found, None otherwise.
        """
        data = self._load_data()
        user_data = data.get(user_id)
        if user_data:
            return User.from_dict(user_data)
        return None

    def find_all(self) -> List[User]:
        """
        Get all users from the database.

        Returns:
            list[User]: List of all users.
        """
        data = self._load_data()
        users = [User.from_dict(user_data) for user_data in data.values()]
        logger.debug(f"Retrieved {len(users)} users from database")
        return users

    def save(self, user: User) -> User:
        """
        Save a user to the database.

        Args:
            user: User object to save.

        Returns:
            User: The saved user.

        Raises:
            DuplicateUserError: If a user with the same ID already exists.
        """
        # Check for duplicate
        existing = self.find_by_id(user.user_id)
        if existing:
            logger.warning(f"Duplicate user found: {user.user_id}")
            raise DuplicateUserError(user.user_id)

        # Load current data
        data = self._load_data()

        # Add new user
        data[user.user_id] = user.to_dict()

        # Save back to file
        self._save_data(data)

        logger.info(f"User saved successfully: {user.user_id}")
        return user

    def delete(self, user_id: str) -> bool:
        """
        Delete a user by ID.

        Args:
            user_id: ID of the user to delete.

        Returns:
            bool: True if user was deleted, False if not found.
        """
        data = self._load_data()
        if user_id in data:
            del data[user_id]
            self._save_data(data)
            logger.info(f"User deleted: {user_id}")
            return True
        logger.warning(f"User not found for deletion: {user_id}")
        return False

    def clear(self) -> None:
        """Clear all users from the database."""
        self._save_data({})
        logger.info("Database cleared")

    def count(self) -> int:
        """
        Get the number of users in the database.

        Returns:
            int: Number of users.
        """
        data = self._load_data()
        return len(data)
