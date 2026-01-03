"""Tests for custom exceptions"""
from weather_api_service_2.exceptions import (
    CityNotFoundError,
    InvalidAPIKeyError,
    ServiceUnavailableError,
    WeatherServiceError,
)


class TestExceptions:
    """Test suite for custom exceptions"""

    def test_exception_hierarchy(self):
        """Test that all exceptions inherit from WeatherServiceError"""
        assert issubclass(InvalidAPIKeyError, WeatherServiceError)
        assert issubclass(CityNotFoundError, WeatherServiceError)
        assert issubclass(ServiceUnavailableError, WeatherServiceError)

    def test_exception_messages(self):
        """Test exception messages are properly set"""
        # Test InvalidAPIKeyError
        error = InvalidAPIKeyError("Invalid key")
        assert str(error) == "Invalid key"

        # Test CityNotFoundError
        error = CityNotFoundError("City not found")
        assert str(error) == "City not found"
