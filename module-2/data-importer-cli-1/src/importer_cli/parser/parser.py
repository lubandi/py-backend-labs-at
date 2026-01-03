"""
CSV parser module for reading and parsing user data.

This module handles CSV parsing with robust error handling.
"""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator, Optional

from importer_cli.context_manager.file_handler import CSVFileReader
from importer_cli.exceptions.exceptions import CSVFormatError

logger = logging.getLogger(__name__)


@dataclass
class RawUserData:
    """Container for raw, unvalidated user data from CSV."""

    user_id: str
    name: str
    email: str
    line_number: int


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

    def parse(self) -> Iterator[RawUserData]:
        """
        Parse the CSV file and yield raw user data.

        Yields:
            RawUserData: Parsed but unvalidated user data.

        Raises:
            CSVFormatError: If CSV format is invalid.
        """
        logger.info(f"Starting parsing of {self.csv_path}")

        with CSVFileReader(self.csv_path) as reader:
            try:
                first_row = next(reader, None)  # Try to get first row
            except StopIteration:
                first_row = None

            if first_row is None:
                # File is empty
                raise CSVFormatError("CSV file is empty", line_number=1)

            # Validate header immediately
            header = self._validate_header(first_row)

            # Now process the rest of the rows
            for line_number, row in enumerate(reader, start=2):
                if not row or all(cell.strip() == "" for cell in row):
                    logger.warning(f"Skipping empty row at line {line_number}")
                    continue

                try:
                    raw_data = self._parse_row(row, header, line_number)
                    if raw_data:
                        yield raw_data
                        logger.debug(
                            f"Successfully parsed raw data at line {line_number}"
                        )
                except CSVFormatError as e:
                    # Log but continue processing other rows
                    logger.error(f"CSV format error at line {line_number}: {e}")
                    continue
                except Exception as e:
                    # Log unexpected errors but continue
                    logger.error(f"Unexpected error at line {line_number}: {e}")
                    continue

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

    def _parse_row(
        self, row: list[str], header: list[str], line_number: int
    ) -> Optional[RawUserData]:
        """
        Parse a single CSV row into raw data.

        Args:
            row: List of cell values.
            header: List of header fields.
            line_number: Current line number for error reporting.

        Returns:
            RawUserData or None if row is invalid.

        Raises:
            CSVFormatError: If row format is invalid.
        """
        # Check if row has correct number of columns
        if len(row) < len(header):
            # Row has fewer columns than header
            logger.warning(
                f"Line {line_number}: Row has {len(row)} columns, expected at least {len(header)}. "
                f"Filling missing columns with empty strings."
            )
            # Pad row with empty strings
            row = row + [""] * (len(header) - len(row))
        elif len(row) > len(header):
            # Row has extra columns, we can ignore them
            logger.warning(
                f"Line {line_number}: Row has {len(row)} columns, header has {len(header)}. "
                f"Ignoring extra columns."
            )
            row = row[: len(header)]

        # Create dictionary from row data
        row_dict = {}
        for i, field in enumerate(header):
            if i < len(row):
                row_dict[field] = row[i].strip()
            else:
                row_dict[field] = ""

        # Check for completely empty required fields
        for field in self.REQUIRED_FIELDS:
            value = row_dict.get(field, "")
            if not value:
                logger.warning(f"Line {line_number}: Required field '{field}' is empty")
                # We'll still return the data and let validator handle it

        # Return raw data - no validation here!
        return RawUserData(
            user_id=row_dict.get("user_id", ""),
            name=row_dict.get("name", ""),
            email=row_dict.get("email", ""),
            line_number=line_number,
        )
