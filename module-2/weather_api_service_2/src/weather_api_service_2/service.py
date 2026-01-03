"""Weather Service module"""
from typing import Any, Dict, Optional

from weather_api_service_2.exceptions import CityNotFoundError, InvalidAPIKeyError
from weather_api_service_2.logger import StructuredLogger


class WeatherService:
    """Mock Weather API Service"""

    def __init__(self, api_key: Optional[str] = "valid-key"):
        """Initialize WeatherService with optional API key"""
        self.api_key = api_key
        self.logger = StructuredLogger(__name__)
        self.valid_cities = {
            "London": {
                "city": "London",
                "temperature": 15.5,
                "condition": "Partly Cloudy",
                "humidity": 65,
                "wind_speed": 12.0,
            },
            "Paris": {
                "city": "Paris",
                "temperature": 18.0,
                "condition": "Sunny",
                "humidity": 60,
                "wind_speed": 8.0,
            },
            "Tokyo": {
                "city": "Tokyo",
                "temperature": 22.0,
                "condition": "Clear",
                "humidity": 70,
                "wind_speed": 5.0,
            },
        }

    def get_forecast(self, city: str) -> Dict[str, Any]:
        """Get weather forecast for a city"""
        self.logger.info("Weather forecast request received", city=city)

        # Check API key
        if self.api_key != "valid-key":
            self.logger.error("Invalid API key provided", api_key=self.api_key)
            raise InvalidAPIKeyError("Invalid API key provided")

        # Check if city exists
        if city not in self.valid_cities:
            self.logger.error("City not found", city=city)
            raise CityNotFoundError(f"City '{city}' not found")

        forecast = self.valid_cities[city]
        self.logger.info("Weather forecast retrieved", city=city, forecast=forecast)
        return forecast
