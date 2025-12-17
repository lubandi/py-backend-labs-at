"""
Context managers for safe file operations.

This module provides context managers for reading and writing files
with proper error handling and resource management.
"""

import csv
import json
import logging
from pathlib import Path
from typing import Any, Iterator

from exceptions.exceptions import CSVFormatError, MissingFileError

logger = logging.getLogger(__name__)


class CSVFileReader:
    """Context manager for safely reading CSV files."""

    def __init__(self, filepath: str | Path) -> None:
        """
        Initialize CSV file reader.

        Args:
            filepath: Path to the CSV file.

        Raises:
            MissingFileError: If the file does not exist.
        """
        self.filepath = Path(filepath)
        self._file = None

    def __enter__(self) -> Iterator[list[str]]:
        """
        Enter the context manager and open the CSV file.

        Returns:
            Iterator yielding rows from the CSV file.

        Raises:
            MissingFileError: If the file does not exist.
            CSVFormatError: If there's an error reading the CSV.
        """
        try:
            if not self.filepath.exists():
                raise MissingFileError(str(self.filepath))

            logger.info(f"Opening CSV file: {self.filepath}")
            self._file = open(self.filepath, "r", newline="", encoding="utf-8")
            reader = csv.reader(self._file)

            # Read and yield each row
            for line_num, row in enumerate(reader, start=1):
                try:
                    yield row
                except Exception as e:
                    logger.error(f"Error processing line {line_num}: {e}")
                    raise CSVFormatError(
                        f"Error processing line {line_num}",
                        line_number=line_num,
                        line_content=str(row),
                    ) from e

        except MissingFileError:
            logger.error(f"File not found: {self.filepath}")
            raise
        except Exception as e:
            logger.error(f"Error opening CSV file: {e}")
            raise CSVFormatError(f"Error reading CSV file: {e}") from e

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit the context manager and close the file."""
        if self._file and not self._file.closed:
            logger.info(f"Closing CSV file: {self.filepath}")
            self._file.close()


class JSONFileHandler:
    """Context manager for reading and writing JSON files."""

    def __init__(self, filepath: str | Path, mode: str = "r") -> None:
        """
        Initialize JSON file handler.

        Args:
            filepath: Path to the JSON file.
            mode: File mode ('r' for read, 'w' for write).

        Raises:
            ValueError: If mode is not 'r' or 'w'.
        """
        self.filepath = Path(filepath)
        self.mode = mode
        self._file = None

        if mode not in ("r", "w"):
            raise ValueError("Mode must be 'r' (read) or 'w' (write)")

    def __enter__(self) -> dict | None:
        """
        Enter the context manager and open the JSON file.

        Returns:
            dict: The loaded JSON data if mode is 'r', None if mode is 'w'.

        Raises:
            MissingFileError: If file doesn't exist in read mode.
            JSONDecodeError: If JSON is malformed.
        """
        if self.mode == "r":
            if not self.filepath.exists():
                logger.error(f"JSON file not found: {self.filepath}")
                raise MissingFileError(str(self.filepath))

            logger.info(f"Opening JSON file for reading: {self.filepath}")
            self._file = open(self.filepath, "r", encoding="utf-8")
            try:
                data = json.load(self._file)
                logger.debug(f"Successfully loaded JSON from {self.filepath}")
                return data
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON in {self.filepath}: {e}")
                raise
        else:  # mode == 'w'
            logger.info(f"Opening JSON file for writing: {self.filepath}")
            self._file = open(self.filepath, "w", encoding="utf-8")
            return None

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit the context manager and close the file."""
        if self._file and not self._file.closed:
            logger.info(f"Closing JSON file: {self.filepath}")
            self._file.close()

    def write_data(self, data: Any) -> None:
        """
        Write data to the JSON file.

        Args:
            data: Data to write (must be JSON serializable).

        Raises:
            ValueError: If handler is not in write mode.
        """
        if self.mode != "w":
            raise ValueError("Handler must be in write mode to write data")
        if self._file:
            json.dump(data, self._file, indent=2)
            logger.debug(f"Data written to {self.filepath}")
