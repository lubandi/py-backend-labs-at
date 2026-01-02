from pathlib import Path

import pytest

from importer_cli.exceptions.exceptions import (
    CSVFormatError,
    MissingFileError,
    ValidationError,
)
from importer_cli.parser.parser import CSVParser


class TestCSVParser:
    """Tests for CSVParser."""

    def test_parse_valid_csv(self, tmp_path: Path) -> None:
        csv_file = tmp_path / "valid.csv"
        csv_file.write_text(
            "user_id,name,email\n"
            "1,John Doe,john@example.com\n"
            "2,Jane Smith,jane@example.com\n"
        )

        parser = CSVParser(csv_file)
        users = list(parser.parse())

        assert len(users) == 2
        assert users[0].user_id == "1"
        assert users[1].user_id == "2"

    def test_parse_empty_csv(self, tmp_path: Path) -> None:
        csv_file = tmp_path / "empty.csv"
        csv_file.write_text("")  # completely empty file

        parser = CSVParser(csv_file)
        with pytest.raises(CSVFormatError, match="CSV file is empty"):
            list(parser.parse())

    @pytest.mark.parametrize(
        "csv_content,match_regex",
        [
            # Missing column
            ("user_id,name,email\n1,John Doe", r"Row has \d+ columns, expected \d+"),
            # Extra column
            (
                "user_id,name,email\n1,John Doe,john@example.com,extra",
                r"Row has \d+ columns, expected \d+",
            ),
        ],
    )
    def test_parse_invalid_row_format(
        self, tmp_path: Path, csv_content: str, match_regex: str
    ) -> None:
        csv_file = tmp_path / "invalid.csv"
        csv_file.write_text(csv_content)

        parser = CSVParser(csv_file)
        with pytest.raises(CSVFormatError, match=match_regex):
            list(parser.parse())

    def test_parse_missing_required_header_field(self, tmp_path: Path) -> None:
        csv_file = tmp_path / "missing_header.csv"
        csv_file.write_text("user_id,name\n1,John Doe")  # missing 'email'

        parser = CSVParser(csv_file)
        with pytest.raises(CSVFormatError, match=r"Missing required fields in header"):
            list(parser.parse())

    def test_parse_empty_row_skipped(self, tmp_path: Path) -> None:
        csv_file = tmp_path / "empty_rows.csv"
        csv_file.write_text(
            "user_id,name,email\n"
            "\n"  # empty row
            "1,John Doe,john@example.com\n"
        )

        parser = CSVParser(csv_file)
        users = list(parser.parse())
        assert len(users) == 1
        assert users[0].user_id == "1"

    def test_parse_required_field_empty(self, tmp_path: Path) -> None:
        csv_file = tmp_path / "empty_required.csv"
        csv_file.write_text(
            "user_id,name,email\n"
            ",John Doe,john@example.com\n"  # empty user_id
        )

        parser = CSVParser(csv_file)
        with pytest.raises(ValidationError, match="Required field 'user_id' is empty"):
            list(parser.parse())

    def test_parse_nonexistent_file(self, tmp_path: Path) -> None:
        csv_file = tmp_path / "nonexistent.csv"
        parser = CSVParser(csv_file)
        with pytest.raises(MissingFileError):
            list(parser.parse())
