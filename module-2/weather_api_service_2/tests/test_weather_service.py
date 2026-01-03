"""Tests for Weather Service"""
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
