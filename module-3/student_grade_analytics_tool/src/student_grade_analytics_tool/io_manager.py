import csv
import json
import logging
from pathlib import Path
from typing import Any, Dict, Iterator, Union


class IOManager:
    """
    Handles file input and output operations.
    """

    @staticmethod
    def read_csv(file_path: Union[str, Path]) -> Iterator[Dict[str, str]]:
        """
        Reads a CSV file and yields records as dictionaries.
        Uses a generator for memory efficiency with large files.
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        try:
            with path.open(mode="r", encoding="utf-8", newline="") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    yield row
        except PermissionError:
            logging.error(f"Permission denied: {path}")
            raise
        except Exception as e:
            logging.error(f"Error reading file {path}: {e}")
            raise

    @staticmethod
    def write_json(data: Any, output_path: Union[str, Path]) -> None:
        """
        Writes data to a JSON file.
        """
        path = Path(output_path)
        try:
            path.parent.mkdir(parents=True, exist_ok=True)

            with path.open(mode="w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
            logging.info(f"Report written to {path}")
        except PermissionError:
            logging.error(f"Permission denied: {path}")
            raise
        except Exception as e:
            logging.error(f"Error writing to {path}: {e}")
            raise
