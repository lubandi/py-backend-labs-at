"""
Pytest configuration and fixtures for the Resilient Data Importer tests.
Fixtures are reusable setup/teardown functions that pytest makes available to tests.
"""

import csv
import json
import tempfile
from pathlib import Path
from typing import Generator

import pytest

from src.importer_cli.models.models import User
from src.importer_cli.repository.repository import UserRepository


@pytest.fixture
def temp_csv_file() -> Generator[Path, None, None]:
    """
    Creates a temporary CSV file with valid data for testing.

    What it does:
    1. Creates a temporary file that will be automatically deleted
    2. Writes 3 valid user records
    3. Yields the file path for tests to use
    4. Deletes the file after the test finishes
    """
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".csv", delete=False, newline=""
    ) as f:
        writer = csv.writer(f)
        # Write header
        writer.writerow(["user_id", "name", "email"])
        # Write data rows WITHOUT blank lines
        writer.writerow(["1", "John Doe", "john@example.com"])
        writer.writerow(["2", "Jane Smith", "jane@example.com"])
        writer.writerow(["3", "Bob Johnson", "bob@example.com"])
        temp_path = Path(f.name)

    # Yield control to the test that uses this fixture
    yield temp_path

    # Cleanup - runs AFTER the test completes
    if temp_path.exists():
        temp_path.unlink()


@pytest.fixture
def temp_csv_file_with_errors() -> Generator[Path, None, None]:
    """
    Creates a CSV file with various errors to test error handling.

    Contains:
    - Row 2: Missing user_id (empty string)
    - Row 3: Missing name
    - Row 4: Invalid email format
    - Row 5: Duplicate user_id
    """
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        writer = csv.writer(f)
        writer.writerow(["user_id", "name", "email"])
        writer.writerow(["1", "John Doe", "john@example.com"])  # Valid
        writer.writerow(["", "Jane Smith", "jane@example.com"])  # Missing user_id
        writer.writerow(["3", "", "bob@example.com"])  # Missing name
        writer.writerow(["4", "Alice Brown", "invalid-email"])  # Invalid email
        writer.writerow(["1", "John Duplicate", "john2@example.com"])  # Duplicate ID
        temp_path = Path(f.name)

    yield temp_path

    # Cleanup
    if temp_path.exists():
        temp_path.unlink()


@pytest.fixture
def sample_user() -> User:
    """Creates a sample User object for testing."""
    return User(user_id="test123", name="Test User", email="test@example.com")


@pytest.fixture
def empty_user_repository(tmp_path) -> UserRepository:
    path = tmp_path / "users.json"
    path.write_text("{}")
    return UserRepository(path)


@pytest.fixture
def populated_user_repository(tmp_path) -> UserRepository:
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
def temp_json_db() -> Generator[Path, None, None]:
    """Create a temporary JSON database file for testing."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        data = {
            "1": {
                "user_id": "1",
                "name": "Existing User",
                "email": "existing@example.com",
            }
        }
        json.dump(data, f)
        temp_path = Path(f.name)

    yield temp_path

    # Cleanup
    if temp_path.exists():
        temp_path.unlink()
