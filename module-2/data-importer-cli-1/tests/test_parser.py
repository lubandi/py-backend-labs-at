from pathlib import Path

import pytest

from importer_cli.exceptions.exceptions import CSVFormatError, MissingFileError
from importer_cli.parser.parser import CSVParser, RawUserData


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
        assert isinstance(users[0], RawUserData)
        assert users[0].user_id == "1"
        assert users[0].name == "John Doe"
        assert users[0].email == "john@example.com"
        assert users[0].line_number == 2

        assert users[1].user_id == "2"
        assert users[1].name == "Jane Smith"
        assert users[1].email == "jane@example.com"
        assert users[1].line_number == 3

    def test_parse_empty_csv(self, tmp_path: Path) -> None:
        csv_file = tmp_path / "empty.csv"
        csv_file.write_text("")

        parser = CSVParser(csv_file)
        with pytest.raises(CSVFormatError, match="CSV file is empty"):
            list(parser.parse())

    @pytest.mark.parametrize(
        "csv_content,expected_data",
        [
            # Missing column - should parse with empty email
            ("user_id,name,email\n1,John Doe", RawUserData("1", "John Doe", "", 2)),
            # Extra column - should parse ignoring extra column
            (
                "user_id,name,email\n1,John Doe,john@example.com,extra",
                RawUserData("1", "John Doe", "john@example.com", 2),
            ),
        ],
    )
    def test_parse_invalid_row_format(
        self, tmp_path: Path, csv_content: str, expected_data: RawUserData
    ) -> None:
        """Test that parser handles invalid row formats gracefully."""
        csv_file = tmp_path / "invalid.csv"
        csv_file.write_text(csv_content)

        parser = CSVParser(csv_file)
        users = list(parser.parse())

        # Should parse one user despite format issues
        assert len(users) == 1
        assert users[0].user_id == expected_data.user_id
        assert users[0].name == expected_data.name
        assert users[0].email == expected_data.email
        assert users[0].line_number == expected_data.line_number

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
        """Test that parser returns raw data even with empty required fields."""
        csv_file = tmp_path / "empty_required.csv"
        csv_file.write_text(
            "user_id,name,email\n"
            ",John Doe,john@example.com\n"  # empty user_id
        )

        parser = CSVParser(csv_file)
        users = list(parser.parse())

        # Parser should return the data (validation happens later)
        assert len(users) == 1
        assert users[0].user_id == ""  # Empty user_id
        assert users[0].name == "John Doe"
        assert users[0].email == "john@example.com"
        assert users[0].line_number == 2

    def test_parse_nonexistent_file(self, tmp_path: Path) -> None:
        csv_file = tmp_path / "nonexistent.csv"
        parser = CSVParser(csv_file)
        with pytest.raises(MissingFileError):
            list(parser.parse())

    def test_parse_with_whitespace(self, tmp_path: Path) -> None:
        """Test parsing with extra whitespace in cells."""
        csv_file = tmp_path / "whitespace.csv"
        csv_file.write_text(
            "user_id,name,email\n" "  1  ,  John Doe  ,  john@example.com  \n"
        )

        parser = CSVParser(csv_file)
        users = list(parser.parse())

        assert len(users) == 1
        assert users[0].user_id == "1"  # Should be stripped
        assert users[0].name == "John Doe"  # Should be stripped
        assert users[0].email == "john@example.com"  # Should be stripped

    def test_parse_multiple_issues(self, tmp_path: Path) -> None:
        """Test parsing CSV with multiple issues, all should be handled gracefully."""
        csv_file = tmp_path / "multiple_issues.csv"
        csv_file.write_text(
            "user_id,name,email\n"
            "1,John Doe\n"  # Missing email column
            "2,Jane Smith,jane@example.com,extra1,extra2\n"  # Extra columns
            "3,,bob@example.com\n"  # Empty name
            "\n"  # Empty row
            "4,Alice Brown,alice@example.com\n"  # Valid
        )

        parser = CSVParser(csv_file)
        users = list(parser.parse())

        # Should parse all 4 rows (empty row skipped)
        assert len(users) == 4

        # Row 1: missing email
        assert users[0].user_id == "1"
        assert users[0].name == "John Doe"
        assert users[0].email == ""

        # Row 2: extra columns
        assert users[1].user_id == "2"
        assert users[1].name == "Jane Smith"
        assert users[1].email == "jane@example.com"

        # Row 3: empty name
        assert users[2].user_id == "3"
        assert users[2].name == ""
        assert users[2].email == "bob@example.com"

        # Row 5: valid (row 4 was empty)
        assert users[3].user_id == "4"
        assert users[3].name == "Alice Brown"
        assert users[3].email == "alice@example.com"
