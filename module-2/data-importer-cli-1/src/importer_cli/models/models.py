"""
Data models for the Resilient Data Importer.

This module contains dataclasses for structured data representation.
"""

from dataclasses import dataclass


@dataclass
class RawUserData:
    """Container for raw, unvalidated user data from CSV."""

    user_id: str
    name: str
    email: str
    line_number: int


@dataclass
class User:
    """Represents a user with unique identifier and contact information."""

    user_id: str
    name: str
    email: str

    def to_dict(self) -> dict[str, str]:
        """Convert User object to dictionary."""
        return {
            "user_id": self.user_id,
            "name": self.name,
            "email": self.email,
        }

    @classmethod
    def from_dict(cls, data: dict[str, str]) -> "User":
        """Create User object from dictionary."""
        return cls(
            user_id=data.get("user_id", ""),
            name=data.get("name", ""),
            email=data.get("email", ""),
        )


@dataclass
class ImportResult:
    """Results of an import operation."""

    total_processed: int = 0
    successful: int = 0
    failed: int = 0
    duplicates_skipped: int = 0
    errors: list[tuple[int, str]] = None  # type: ignore

    def __post_init__(self) -> None:
        """Initialize errors list if None."""
        if self.errors is None:
            self.errors = []

    def add_error(self, line_number: int, error_message: str) -> None:
        """Add an error to the results."""
        self.errors.append((line_number, error_message))
        self.failed += 1

    def add_success(self) -> None:
        """Increment success count."""
        self.successful += 1

    def add_duplicate(self) -> None:
        """Increment duplicate count."""
        self.duplicates_skipped += 1

    def __str__(self) -> str:
        """String representation of import results."""
        return (
            f"Import Results:\n"
            f"  Total Processed: {self.total_processed}\n"
            f"  Successful: {self.successful}\n"
            f"  Failed: {self.failed}\n"
            f"  Duplicates Skipped: {self.duplicates_skipped}"
        )
