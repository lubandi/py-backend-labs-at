"""
Pytest configuration and fixtures for the Resilient Data Importer tests.
Fixtures are reusable setup/teardown functions that pytest makes available to tests.
"""

import csv
import json
from pathlib import Path

import pytest

from importer_cli.models.models import User
from importer_cli.repository.repository import UserRepository


@pytest.fixture
def temp_csv_file(tmp_path) -> Path:
    """
    Creates a temporary CSV file with valid data for testing using pytest's tmp_path.

    What it does:
    1. Creates a temporary file in pytest's managed temp directory
    2. Writes 3 valid user records
    3. Returns the file path for tests to use
    4. Pytest automatically cleans up the file after test
    """
    temp_file = tmp_path / "test_users.csv"

    with open(temp_file, "w", newline="") as f:
        writer = csv.writer(f)
        # Write header
        writer.writerow(["user_id", "name", "email"])
        writer.writerow(["1", "John Doe", "john@example.com"])
        writer.writerow(["2", "Jane Smith", "jane@example.com"])
        writer.writerow(["3", "Bob Johnson", "bob@example.com"])

    return temp_file


@pytest.fixture
def temp_csv_file_with_errors(tmp_path) -> Path:
    """
    Creates a CSV file with various errors to test error handling.
    Uses pytest's tmp_path for automatic cleanup.

    Contains:
    - Row 2: Missing user_id (empty string)
    - Row 3: Missing name
    - Row 4: Invalid email format
    - Row 5: Duplicate user_id
    """
    temp_file = tmp_path / "test_users_errors.csv"

    with open(temp_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["user_id", "name", "email"])
        writer.writerow(["1", "John Doe", "john@example.com"])
        writer.writerow(["", "Jane Smith", "jane@example.com"])
        writer.writerow(["3", "", "bob@example.com"])
        writer.writerow(["4", "Alice Brown", "invalid-email"])
        writer.writerow(["1", "John Duplicate", "john2@example.com"])

    return temp_file


@pytest.fixture
def sample_user() -> User:
    """Creates a sample User object for testing."""
    return User(user_id="test123", name="Test User", email="test@example.com")


@pytest.fixture
def empty_user_repository(tmp_path) -> UserRepository:
    """Creates an empty UserRepository with a temporary JSON file."""
    path = tmp_path / "users.json"
    path.write_text("{}")
    return UserRepository(path)


@pytest.fixture
def populated_user_repository(tmp_path) -> UserRepository:
    """Creates a UserRepository with one existing user."""
    path = tmp_path / "users.json"
    json.dump(
        {
            "1": {
                "user_id": "1",
                "name": "Existing User",
                "email": "existing@example.com",
            }
        },
        path.open("w"),
    )
    return UserRepository(path)


@pytest.fixture
def temp_json_db(tmp_path) -> Path:
    """Create a temporary JSON database file for testing using pytest's tmp_path."""
    temp_file = tmp_path / "test_db.json"

    data = {
        "1": {
            "user_id": "1",
            "name": "Existing User",
            "email": "existing@example.com",
        }
    }

    with open(temp_file, "w") as f:
        json.dump(data, f)

    return temp_file
