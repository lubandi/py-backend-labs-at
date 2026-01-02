"""
Tests for file handler context managers.
These test that files are opened, read, and closed properly.
"""

from pathlib import Path

import pytest

from src.importer_cli.context_manager.file_handler import CSVFileReader
from src.importer_cli.exceptions.exceptions import MissingFileError


class TestCSVFileReader:
    """Test cases for CSVFileReader."""

    def test_csv_file_reader_context_manager(self, temp_csv_file: Path) -> None:
        """Test CSVFileReader as context manager."""
        with CSVFileReader(temp_csv_file) as reader:
            rows = list(reader)

            # Filter out empty rows
            non_empty_rows = [row for row in rows if row]  # Remove empty lists

            # Now we should have 4 rows: header + 3 data rows
            assert len(non_empty_rows) == 4

            # Check the content
            assert non_empty_rows[0] == ["user_id", "name", "email"]
            assert non_empty_rows[1] == ["1", "John Doe", "john@example.com"]
            assert non_empty_rows[2] == ["2", "Jane Smith", "jane@example.com"]
            assert non_empty_rows[3] == ["3", "Bob Johnson", "bob@example.com"]

    def test_csv_file_reader_missing_file(self, tmp_path: Path) -> None:
        """
        Test error handling for missing files.

        Note: tmp_path is a built-in pytest fixture that gives us
        a temporary directory for each test.
        """
        non_existent = tmp_path / "nonexistent.csv"

        # Should raise our custom MissingFileError
        with pytest.raises(MissingFileError):
            with CSVFileReader(non_existent) as reader:
                list(reader)  # Try to read the non-existent file

    def test_csv_file_reader_closes_file(self, temp_csv_file: Path) -> None:
        """
        Important test: ensures files are closed properly!
        File handles that aren't closed can cause resource leaks.
        """
        reader = CSVFileReader(temp_csv_file)
        with reader as csv_reader:
            # Read all data
            list(csv_reader)

        # After exiting the context manager, file should be closed
        assert reader._file.closed
