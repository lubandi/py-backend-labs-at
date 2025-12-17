"""
Custom exception hierarchy for the Resilient Data Importer.

This module defines a hierarchy of exceptions for handling
specific error cases during the CSV import process.
"""


class ImporterError(Exception):
    """Base exception for all importer-related errors."""

    def __init__(self, message: str = "An importer error occurred") -> None:
        super().__init__(message)
        self.message = message


class FileFormatError(ImporterError):
    """Raised when there are issues with the file format."""

    def __init__(self, message: str = "File format error") -> None:
        super().__init__(message)


class CSVFormatError(FileFormatError):
    """Raised when CSV file is malformed."""

    def __init__(
        self,
        message: str = "CSV format error",
        line_number: int | None = None,
        line_content: str | None = None,
    ) -> None:
        super().__init__(message)
        self.line_number = line_number
        self.line_content = line_content

    def __str__(self) -> str:
        base_msg = super().__str__()
        if self.line_number and self.line_content:
            return (
                f"{base_msg} at line {self.line_number}: {self.line_content}"
            )
        elif self.line_number:
            return f"{base_msg} at line {self.line_number}"
        return base_msg


class MissingFileError(FileFormatError):
    """Raised when the specified file does not exist."""

    def __init__(self, filename: str, message: str = "File not found") -> None:
        super().__init__(f"{message}: {filename}")
        self.filename = filename


class DuplicateUserError(ImporterError):
    """Raised when a duplicate user is found in the database."""

    def __init__(
        self,
        user_id: str,
        message: str = "Duplicate user found",
    ) -> None:
        super().__init__(f"{message}: user_id={user_id}")
        self.user_id = user_id


class ValidationError(ImporterError):
    """Raised when data validation fails."""

    def __init__(
        self,
        field: str,
        value: str,
        message: str = "Validation error",
    ) -> None:
        super().__init__(f"{message}: {field}={value}")
        self.field = field
        self.value = value


class DatabaseError(ImporterError):
    """Base exception for database-related errors."""

    pass
