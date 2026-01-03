"""
Integration tests for the Resilient Data Importer using pytest only.
These test the entire system working together.
"""

import csv
from pathlib import Path

import pytest

from importer_cli.cli import ResilientImporter
from importer_cli.models.models import ImportResult


class TestIntegration:
    """Integration test cases."""

    def test_end_to_end_import_success(self, tmp_path: Path) -> None:
        """
        Complete end-to-end test: CSV → Parser → Validator → Repository

        This is the main happy path integration test.
        """
        # 1. Create test CSV file
        csv_file = tmp_path / "users.csv"
        with open(csv_file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["user_id", "name", "email"])  # Header
            writer.writerow(["1", "John Doe", "john@example.com"])
            writer.writerow(["2", "Jane Smith", "jane@example.com"])
            writer.writerow(["3", "Bob Johnson", "bob@example.com"])

        # 2. Create test database file path
        db_file = tmp_path / "database.json"

        # 3. Run the full import process
        importer = ResilientImporter(csv_file, db_file)
        result = importer.import_users()

        # 4. Verify everything worked
        assert isinstance(result, ImportResult)
        assert result.total_processed == 3
        assert result.successful == 3  # All 3 should succeed
        assert result.failed == 0
        assert result.duplicates_skipped == 0
        assert len(result.errors) == 0

        # 5. Verify database was created
        assert db_file.exists()

    def test_end_to_end_import_with_errors(self, tmp_path: Path) -> None:
        """
        Integration test with various errors in CSV.

        Tests error handling across the entire pipeline.
        """
        # Create CSV with mixed valid and invalid data
        csv_file = tmp_path / "users.csv"
        with open(csv_file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["user_id", "name", "email"])
            writer.writerow(["1", "John Doe", "john@example.com"])  # Valid
            writer.writerow(["", "Jane Smith", "jane@example.com"])  # Missing user_id
            writer.writerow(["3", "", "bob@example.com"])  # Missing name
            writer.writerow(["4", "Alice Brown", "invalid-email"])  # Invalid email
            writer.writerow(["1", "John Duplicate", "john2@example.com"])  # Duplicate

        db_file = tmp_path / "database.json"

        # Run import
        importer = ResilientImporter(csv_file, db_file)
        result = importer.import_users()

        # Verify error handling
        assert result.total_processed == 5
        assert result.successful == 1  # Only first valid row
        assert result.failed == 3  # 3 validation errors
        assert result.duplicates_skipped == 1  # 1 duplicate
        assert (
            len(result.errors) == 4
        )  # Changed from 3 to 4 (3 validation + 1 duplicate)

    def test_import_with_missing_csv_file(self, tmp_path: Path) -> None:
        """Test import when CSV file doesn't exist."""
        non_existent_csv = tmp_path / "nonexistent.csv"
        db_file = tmp_path / "database.json"

        importer = ResilientImporter(non_existent_csv, db_file)
        result = importer.import_users()

        # Should report failure
        assert result.failed > 0
        assert len(result.errors) > 0

    def test_consecutive_imports(self, tmp_path: Path) -> None:
        """
        Test multiple imports to same database.

        Verifies that duplicates are handled and new users are added.
        """
        # First import
        csv_file1 = tmp_path / "users1.csv"
        with open(csv_file1, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["user_id", "name", "email"])
            writer.writerow(["1", "John Doe", "john@example.com"])
            writer.writerow(["2", "Jane Smith", "jane@example.com"])

        db_file = tmp_path / "database.json"

        importer1 = ResilientImporter(csv_file1, db_file)
        result1 = importer1.import_users()

        assert result1.successful == 2  # Both users added

        # Second import with duplicates and new users
        csv_file2 = tmp_path / "users2.csv"
        with open(csv_file2, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["user_id", "name", "email"])
            writer.writerow(["1", "John Doe", "john@example.com"])  # Duplicate
            writer.writerow(["3", "Bob Johnson", "bob@example.com"])  # New
            writer.writerow(["4", "Alice Brown", "alice@example.com"])  # New

        importer2 = ResilientImporter(csv_file2, db_file)
        result2 = importer2.import_users()

        assert result2.successful == 2  # 2 new users
        assert result2.duplicates_skipped == 1  # 1 duplicate

        # Verify total users in database
        import json

        with open(db_file, "r") as f:
            data = json.load(f)
        assert len(data) == 4  # All unique users

    @pytest.mark.parametrize(
        "csv_content,expected_successful,expected_errors",
        [
            # Test various scenarios using parametrize
            (
                "user_id,name,email\n1,John Doe,john@example.com",
                1,  # 1 successful
                0,  # 0 errors
            ),
            (
                "user_id,name,email\n,John Doe,john@example.com",
                0,  # 0 successful (missing user_id)
                1,  # 1 error
            ),
            (
                "user_id,name,email\n1,,john@example.com",
                0,  # 0 successful (missing name)
                1,  # 1 error
            ),
            (
                "user_id,name,email\n1,John Doe,invalid-email",
                0,  # 0 successful (bad email)
                1,  # 1 error
            ),
            (
                "user_id,name,email\n1,John Doe,john@example.com\n2,Jane Smith,jane@example.com",
                2,  # 2 successful
                0,  # 0 errors
            ),
        ],
    )
    def test_parametrized_imports(
        self,
        tmp_path: Path,
        csv_content: str,
        expected_successful: int,
        expected_errors: int,
    ) -> None:
        """
        Parametrized integration tests for various CSV scenarios.

        This is efficient testing - one test function handles many cases!
        """
        csv_file = tmp_path / "test.csv"
        csv_file.write_text(csv_content)

        db_file = tmp_path / "database.json"

        importer = ResilientImporter(csv_file, db_file)
        result = importer.import_users()

        assert result.successful == expected_successful
        assert len(result.errors) == expected_errors
