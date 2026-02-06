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

        Example:
            >>> rows = list(IOManager.read_csv("students.csv"))

            >>> rows[0]
            {
                'student_id': 'S001',
                'first_name': 'John',
                'last_name': 'Doe',
                'major': 'CS',
                'year': '2023',
                'course_id': 'CS101',
                'course_name': 'Intro into CS',
                'credits': '3',
                'semester': 'Fall 2023',
                'score': '95.5'
            }

            >>> len(rows)
            10

        Notes:
            - All values are returned as strings (CSV behavior).
            - The function yields one row at a time.
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

        Example:
            >>> report = {
            ...     "students": [
            ...         {
            ...             "student_id": "S001",
            ...             "name": "John Doe",
            ...             "gpa": 3.75
            ...         }
            ...     ],
            ...     "course_count": 5
            ... }

            >>> IOManager.write_json(report, "output/report.json")

            Resulting JSON file (output/report.json):
            {
                "students": [
                    {
                        "student_id": "S001",
                        "name": "John Doe",
                        "gpa": 3.75
                    }
                ],
                "course_count": 5
            }

        Notes:
            - Parent directories are created automatically.
            - Output is pretty-printed using indent=4.
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
