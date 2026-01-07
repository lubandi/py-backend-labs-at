"""Weather provider abstractions"""
from abc import ABC, abstractmethod
from typing import Any, Dict


class WeatherProvider(ABC):
    """Abstract base class for weather providers"""

    @abstractmethod
    def get_forecast(self, city: str) -> Dict[str, Any]:
        """Get weather forecast for a city"""
        pass


class MockWeatherProvider(WeatherProvider):
    """Mock weather provider for testing"""

    def __init__(self):
        self.forecast_data = {
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
        """Get mock weather forecast"""
        return self.forecast_data.get(city, {})
