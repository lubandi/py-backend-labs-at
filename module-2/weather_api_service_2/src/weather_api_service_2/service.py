"""
Weather API Service module.

This module provides a WeatherService class that follows TDD and SOLID principles.
"""

from typing import Any, Dict, Optional

from weather_api_service_2.exceptions import CityNotFoundError, InvalidAPIKeyError
from weather_api_service_2.logger import StructuredLogger
from weather_api_service_2.providers import MockWeatherProvider, WeatherProvider


class WeatherService:
    """
    Weather API Service that provides weather forecasts.

    This service uses dependency injection to allow different weather providers
    and follows the SOLID principles for clean architecture.

    Attributes:
        api_key (str): API key for authentication
        logger (StructuredLogger): Logger for structured logging
        weather_provider (WeatherProvider): Provider for weather data
    """

    def __init__(
        self,
        api_key: Optional[str] = "valid-key",
        weather_provider: Optional[WeatherProvider] = None,
    ) -> None:
        """
        Initialize WeatherService.

        Args:
            api_key: Optional API key for authentication. Defaults to "valid-key".
            weather_provider: Optional weather provider. If not provided,
                            a MockWeatherProvider is used.
        """
        self.api_key = api_key
        self.logger = StructuredLogger(__name__)

        # Use provided provider or create default mock provider
        self.weather_provider = weather_provider or MockWeatherProvider()

    def get_forecast(self, city: str) -> Dict[str, Any]:
        """
        Get weather forecast for a specified city.

        Args:
            city: Name of the city to get forecast for.

        Returns:
            Dictionary containing weather forecast data.

        Raises:
            InvalidAPIKeyError: If the provided API key is invalid.
            CityNotFoundError: If the city is not found in the provider's data.

        Examples:
            >>> service = WeatherService()
            >>> forecast = service.get_forecast("London")
            >>> print(forecast["temperature"])
            15.5
        """
        self.logger.info("Weather forecast request received", city=city)

        # Check API key
        if self.api_key != "valid-key":
            self.logger.error("Invalid API key provided", api_key=self.api_key)
            raise InvalidAPIKeyError("Invalid API key provided")

        # Get forecast from provider
        forecast = self.weather_provider.get_forecast(city)

        # Check if city exists
        if not forecast:
            self.logger.error("City not found", city=city)
            raise CityNotFoundError(f"City '{city}' not found")

        self.logger.info("Weather forecast retrieved", city=city, forecast=forecast)
        return forecast
