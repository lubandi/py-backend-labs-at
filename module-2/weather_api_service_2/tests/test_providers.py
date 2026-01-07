"""Tests for weather providers"""
from weather_api_service_2.providers import MockWeatherProvider, WeatherProvider


class TestMockWeatherProvider:
    """Test suite for MockWeatherProvider"""

    def test_implements_abstract_class(self):
        """Test that MockWeatherProvider implements WeatherProvider"""
        provider = MockWeatherProvider()
        assert isinstance(provider, WeatherProvider)

    def test_get_forecast_valid_city(self):
        """Test getting forecast for valid city"""
        # Arrange
        provider = MockWeatherProvider()

        # Act
        result = provider.get_forecast("London")

        # Assert
        assert result["city"] == "London"
        assert "temperature" in result

    def test_get_forecast_invalid_city(self):
        """Test getting forecast for invalid city returns empty dict"""
        # Arrange
        provider = MockWeatherProvider()

        # Act
        result = provider.get_forecast("UnknownCity")

        # Assert
        assert result == {}
