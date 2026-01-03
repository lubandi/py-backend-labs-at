"""
Tests for user repository using pytest only.
"""

from pathlib import Path

import pytest

from importer_cli.exceptions.exceptions import DuplicateUserError
from importer_cli.models.models import User
from importer_cli.repository.repository import UserRepository


class TestUserRepository:
    """Test cases for UserRepository."""

    def test_repository_initialization(self, tmp_path: Path) -> None:
        """Test UserRepository initialization."""
        db_path = tmp_path / "test.db.json"
        repo = UserRepository(db_path)
        assert repo.db_path == db_path
        assert db_path.parent.exists()

    def test_save_and_find_by_id(
        self, empty_user_repository: UserRepository, sample_user
    ):
        saved_user = empty_user_repository.save(sample_user)
        assert saved_user.user_id == sample_user.user_id

        found_user = empty_user_repository.find_by_id(sample_user.user_id)
        assert found_user is not None

    def test_save_duplicate_user(
        self, empty_user_repository: UserRepository, sample_user
    ):
        empty_user_repository.save(sample_user)

        with pytest.raises(DuplicateUserError):
            empty_user_repository.save(sample_user)

    def test_find_by_id_nonexistent(self, empty_user_repository: UserRepository):
        user = empty_user_repository.find_by_id("nonexistent")
        assert user is None

    def test_find_all(self, empty_user_repository: UserRepository) -> None:
        """Test finding all users."""
        # Add multiple users
        users = [
            User("19000", "John Doe", "john@example.com"),
            User("29000", "Jane Smith", "jane@example.com"),
            User("39000", "Bob Johnson", "bob@example.com"),
        ]

        for user in users:
            empty_user_repository.save(user)

        # Get all users
        all_users = empty_user_repository.find_all()
        assert len(all_users) == 3

        user_ids = {user.user_id for user in all_users}
        assert user_ids == {"19000", "29000", "39000"}

    def test_delete_existing_user(
        self, empty_user_repository: UserRepository, sample_user: User
    ) -> None:
        """Test deleting an existing user."""
        empty_user_repository.save(sample_user)
        assert empty_user_repository.find_by_id(sample_user.user_id) is not None

        # Delete user
        result = empty_user_repository.delete(sample_user.user_id)
        assert result is True
        assert empty_user_repository.find_by_id(sample_user.user_id) is None

    def test_delete_nonexistent_user(self, empty_user_repository: UserRepository):
        result = empty_user_repository.delete("nonexistent")
        assert result is False

    def test_clear_database(self, empty_user_repository: UserRepository) -> None:
        """Test clearing the database."""
        # Add some users
        empty_user_repository.save(User("1", "John Doe", "john@example.com"))
        empty_user_repository.save(User("2", "Jane Smith", "jane@example.com"))

        assert empty_user_repository.count() == 2

        # Clear database
        empty_user_repository.clear()
        assert empty_user_repository.count() == 0

    def test_count_users(self, empty_user_repository: UserRepository) -> None:
        """Test counting users."""
        assert empty_user_repository.count() == 0

        empty_user_repository.save(User("1", "John Doe", "john@example.com"))
        assert empty_user_repository.count() == 1

        empty_user_repository.save(User("2", "Jane Smith", "jane@example.com"))
        assert empty_user_repository.count() == 2

    def test_load_data_file_not_found(self, tmp_path: Path) -> None:
        """Test loading data from non-existent file."""
        db_path = tmp_path / "nonexistent.json"
        repo = UserRepository(db_path)

        # Save a user to trigger _load_data internally
        repo.save(User("1", "Test", "test@example.com"))

        # Should work without error
        assert repo.find_by_id("1") is not None

    def test_save_data_persistence(self, tmp_path: Path) -> None:
        """Test that data persists between repository instances."""
        db_path = tmp_path / "test.json"

        # First repository instance
        repo1 = UserRepository(db_path)
        repo1.save(User("1", "John Doe", "john@example.com"))

        # Second repository instance (same file)
        repo2 = UserRepository(db_path)
        user = repo2.find_by_id("1")

        assert user is not None
        assert user.name == "John Doe"
