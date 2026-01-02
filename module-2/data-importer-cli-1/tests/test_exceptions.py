"""
Tests for custom exceptions.
We test that our custom exceptions work properly and include the right information.
"""


from src.importer_cli.exceptions.exceptions import CSVFormatError, ImporterError


class TestExceptions:
    """Test cases for custom exceptions."""

    def test_importer_error_base(self) -> None:
        """Test the base exception class."""
        error = ImporterError("Test error")
        assert str(error) == "Test error"
        assert error.message == "Test error"

    def test_csv_format_error_with_details(self) -> None:
        """
        Test CSVFormatError includes line information.
        This helps with debugging when CSV files have issues.
        """
        error = CSVFormatError("CSV error", line_number=5, line_content="bad,row,data")

        # Check error message includes all relevant info
        error_message = str(error)
        assert "CSV error" in error_message
        assert "line 5" in error_message  # Line number should be mentioned
        assert "bad,row,data" in error_message  # Problematic content

        # Check attributes are stored
        assert error.line_number == 5
        assert error.line_content == "bad,row,data"
