"""Tests for Weather Service"""
import pytest
from weather_api_service_2.exceptions import CityNotFoundError, InvalidAPIKeyError
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
