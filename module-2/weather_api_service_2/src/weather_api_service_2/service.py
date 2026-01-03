"""Weather Service module"""
from typing import Any, Dict, Optional

from weather_api_service_2.exceptions import CityNotFoundError, InvalidAPIKeyError
from weather_api_service_2.logger import StructuredLogger
from weather_api_service_2.providers import MockWeatherProvider, WeatherProvider


class WeatherService:
    """Weather API Service following SOLID principles"""

    def __init__(
        self,
        api_key: Optional[str] = "valid-key",
        weather_provider: Optional[WeatherProvider] = None,
    ):
        """Initialize WeatherService with dependency injection"""
        self.api_key = api_key
        self.logger = StructuredLogger(__name__)

        # Use provided provider or create default mock provider
        self.weather_provider = weather_provider or MockWeatherProvider()

    def get_forecast(self, city: str) -> Dict[str, Any]:
        """Get weather forecast for a city"""
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
