"""
Command Line Interface for the Resilient Data Importer.
Simple argparse-based CLI.
"""

import argparse
import logging
import sys
from pathlib import Path

from importer_cli.exceptions.exceptions import (
    DuplicateUserError,
    ImporterError,
    MissingFileError,
)
from importer_cli.models.models import ImportResult, User
from importer_cli.parser.parser import CSVParser
from importer_cli.repository.repository import UserRepository
from importer_cli.validator.validator import UserValidator

# Create logs directory if it doesn't exist
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True, parents=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_dir / "importer.log"),
        logging.StreamHandler(sys.stdout),
    ],
)

logger = logging.getLogger(__name__)


class ResilientImporter:
    """Main importer class coordinating parsing, validation, and storage."""

    def __init__(
        self,
        csv_path: str | Path,
        db_path: str | Path = "data/users.json",
    ) -> None:
        """
        Initialize the importer.

        Args:
            csv_path: Path to the CSV file.
            db_path: Path to the JSON database file.
        """
        self.csv_path = Path(csv_path)
        self.parser = CSVParser(csv_path)
        self.validator = UserValidator()
        self.repository = UserRepository(db_path)
        self.result = ImportResult()

        logger.info(f"Initialized importer for {csv_path}")

    def import_users(self) -> ImportResult:
        """
        Import users from CSV file.

        Returns:
            ImportResult: Results of the import operation.
        """
        logger.info(f"Starting import from {self.csv_path}")

        try:
            for user in self.parser.parse():
                self.result.total_processed += 1

                try:
                    # Validate user
                    self.validator.validate(user)

                    # Sanitize user data
                    user = User(
                        user_id=self.validator.sanitize_user_id(user.user_id),
                        name=self.validator.sanitize_name(user.name),
                        email=self.validator.sanitize_email(user.email),
                    )

                    # Save to repository
                    try:
                        self.repository.save(user)
                        self.result.add_success()
                        logger.info(f"Successfully imported user: {user.user_id}")
                    except DuplicateUserError as de:
                        # Count duplicates without raising
                        self.result.duplicates_skipped += 1
                        self.result.add_error(self.result.total_processed, str(de))
                        logger.warning(f"Duplicate user skipped: {de}")

                except ImporterError as e:
                    # Handle validation or parser row-level errors
                    self.result.failed += 1
                    self.result.add_error(self.result.total_processed, str(e))
                    logger.error(f"Failed to import user: {e}")

                except Exception as e:
                    # Catch unexpected errors per row
                    self.result.failed += 1
                    error_msg = f"Unexpected import error: {e}"
                    self.result.add_error(self.result.total_processed, error_msg)
                    logger.error(error_msg)

        except MissingFileError as mfe:
            # CSV file missing
            logger.error(f"File not found: {self.csv_path}")
            self.result.failed += 1
            self.result.add_error(0, str(mfe))

        except Exception as e:
            # Any other top-level errors
            error_msg = f"Unexpected error during import: {e}"
            logger.error(error_msg)
            self.result.failed += 1
            self.result.add_error(0, error_msg)

        logger.info(f"Import completed: {self.result}")
        return self.result


def import_csv_command(args):
    """Handle the CSV import."""
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    importer = ResilientImporter(args.csv_file, args.db_file)
    result = importer.import_users()

    # Print summary
    print(f"✅ Successfully imported {result.successful} users.")
    if result.failed > 0:
        print(f"❌ Failed to import {result.failed} users.")
    if result.duplicates_skipped > 0:
        print(f"⚠️  Skipped {result.duplicates_skipped} duplicate users.")

    # Optional: detailed errors
    if result.errors:
        print("Errors encountered:")
        for line_num, error in result.errors:
            print(f"Line {line_num}: {error}")


def main():
    parser = argparse.ArgumentParser(description="Resilient Data Importer CLI")
    parser.add_argument("csv_file", help="Path to the CSV file")
    parser.add_argument(
        "--db-file", default="data/users.json", help="JSON database file"
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose logging"
    )
    args = parser.parse_args()

    # Print help if no arguments
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    import_csv_command(args)


if __name__ == "__main__":
    main()
