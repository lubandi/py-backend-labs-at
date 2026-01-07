"""Tests for Weather Service"""
import pytest
from weather_api_service_2.exceptions import CityNotFoundError, InvalidAPIKeyError
from weather_api_service_2.providers import MockWeatherProvider
from weather_api_service_2.service import WeatherService


class TestWeatherService:
    """Test suite for WeatherService"""

    def test_get_forecast_valid_city(self):
        """Test getting forecast for a valid city"""
        # Arrange
        service = WeatherService()
        city = "London"

        # Act
        result = service.get_forecast(city)

        # Assert
        assert "city" in result
        assert result["city"] == city
        assert "temperature" in result
        assert "condition" in result

    def test_get_forecast_unknown_city(self):
        """Test that unknown city raises CityNotFoundError"""
        # Arrange
        service = WeatherService()
        city = "UnknownCity"

        # Act & Assert
        with pytest.raises(CityNotFoundError):
            service.get_forecast(city)

    def test_get_forecast_with_api_key_invalid(self):
        """Test that invalid API key raises InvalidAPIKeyError"""
        # Arrange
        service = WeatherService(api_key="invalid-key")
        city = "London"

        # Act & Assert
        with pytest.raises(InvalidAPIKeyError):
            service.get_forecast(city)

    def test_logging_on_success(self, mocker):
        """Test that logging occurs on successful forecast retrieval"""
        # Arrange
        mock_logger = mocker.Mock()
        service = WeatherService()
        service.logger = mock_logger

        # Act
        service.get_forecast("London")

        # Assert
        assert mock_logger.info.call_count >= 2

    def test_logging_on_error(self, mocker):
        """Test that logging occurs on error"""
        # Arrange
        mock_logger = mocker.Mock()
        service = WeatherService(api_key="invalid")
        service.logger = mock_logger

        # Act & Assert
        with pytest.raises(InvalidAPIKeyError):
            service.get_forecast("London")

        # Verify error was logged
        mock_logger.error.assert_called_once()

    def test_service_uses_provider_dependency(self):
        """Test that WeatherService uses dependency injection"""
        # Arrange
        mock_provider = MockWeatherProvider()
        service = WeatherService(weather_provider=mock_provider)

        # Act
        result = service.get_forecast("London")

        # Assert
        assert result["city"] == "London"

    def test_service_without_provider_creates_default(self):
        """Test that service creates default provider if none provided"""
        # Arrange & Act
        service = WeatherService()
        result = service.get_forecast("London")

        # Assert
        assert result["city"] == "London"
