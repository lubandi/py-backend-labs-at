"""
CSV parser module for reading and parsing user data.

This module handles CSV parsing with robust error handling and validation.
"""

import logging
from pathlib import Path
from typing import Iterator

from importer_cli.context_manager.file_handler import CSVFileReader
from importer_cli.exceptions.exceptions import CSVFormatError, ValidationError
from importer_cli.models.models import User

logger = logging.getLogger(__name__)


class CSVParser:
    """Parser for CSV files containing user data."""

    REQUIRED_FIELDS = ["user_id", "name", "email"]
    OPTIONAL_FIELDS = []  # Can be extended if needed

    def __init__(self, csv_path: str | Path) -> None:
        """
        Initialize CSV parser.

        Args:
            csv_path: Path to the CSV file.

        Raises:
            MissingFileError: If the file does not exist.
        """
        self.csv_path = Path(csv_path)
        logger.info(f"Initialized CSV parser for: {self.csv_path}")

    def parse(self) -> Iterator[User]:
        """
        Parse the CSV file and yield User objects.

        Yields:
            User: Parsed user objects.

        Raises:
            CSVFormatError: If CSV format is invalid.
            ValidationError: If data validation fails.
        """
        logger.info(f"Starting parsing of {self.csv_path}")

        with CSVFileReader(self.csv_path) as reader:
            header = None
            for line_number, row in enumerate(reader, start=1):
                try:
                    # First row should be header
                    if line_number == 1:
                        header = self._validate_header(row)
                        continue

                    # Skip empty rows
                    if not row or all(cell.strip() == "" for cell in row):
                        logger.warning(f"Skipping empty row at line {line_number}")
                        continue

                    # Parse user data
                    user = self._parse_row(row, header, line_number)
                    yield user

                    logger.debug(
                        f"""Successfully parsed user at line
                        {line_number}: {user.user_id}"""
                    )

                except (CSVFormatError, ValidationError) as e:
                    logger.error(f"Error at line {line_number}: {e}")
                    raise
                except Exception as e:
                    logger.error(f"Unexpected error at line {line_number}: {e}")
                    raise CSVFormatError(
                        f"Unexpected error at line {line_number}",
                        line_number=line_number,
                        line_content=str(row),
                    ) from e

        logger.info(f"Completed parsing of {self.csv_path}")

    def _validate_header(self, header_row: list[str]) -> list[str]:
        """
        Validate CSV header row.

        Args:
            header_row: List of header fields.

        Returns:
            list[str]: Normalized header fields.

        Raises:
            CSVFormatError: If header is invalid.
        """
        if not header_row:
            raise CSVFormatError("Empty header row", line_number=1)

        # Normalize header fields (strip whitespace, lowercase)
        normalized_header = [field.strip().lower() for field in header_row]

        # Check for required fields
        missing_fields = []
        for required_field in self.REQUIRED_FIELDS:
            if required_field not in normalized_header:
                missing_fields.append(required_field)

        if missing_fields:
            raise CSVFormatError(
                f"Missing required fields in header: {missing_fields}",
                line_number=1,
                line_content=str(header_row),
            )

        logger.debug(f"Validated header: {normalized_header}")
        return normalized_header

    def _parse_row(self, row: list[str], header: list[str], line_number: int) -> User:
        """
        Parse a single CSV row into a User object.

        Args:
            row: List of cell values.
            header: List of header fields.
            line_number: Current line number for error reporting.

        Returns:
            User: Parsed user object.

        Raises:
            CSVFormatError: If row format is invalid.
            ValidationError: If data validation fails.
        """
        if len(row) != len(header):
            raise CSVFormatError(
                f"Row has {len(row)} columns, expected {len(header)}",
                line_number=line_number,
                line_content=str(row),
            )

        # Create dictionary from row data
        row_dict = {}
        for i, field in enumerate(header):
            if i < len(row):
                row_dict[field] = row[i].strip()
            else:
                row_dict[field] = ""

        # Validate required fields are not empty
        for field in self.REQUIRED_FIELDS:
            if not row_dict.get(field):
                raise ValidationError(
                    field=field,
                    value=row_dict.get(field, ""),
                    message=f"Required field '{field}' is empty",
                )

        try:
            user = User(
                user_id=row_dict["user_id"],
                name=row_dict["name"],
                email=row_dict["email"],
            )
            return user
        except ValueError as e:
            raise ValidationError(
                field="user_data",
                value=str(row_dict),
                message=f"Invalid user data: {e}",
            )
