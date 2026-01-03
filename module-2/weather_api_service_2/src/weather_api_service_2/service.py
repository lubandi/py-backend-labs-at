"""Weather Service module"""
from typing import Any, Dict


class WeatherService:
    """Mock Weather API Service"""

    def get_forecast(self, city: str) -> Dict[str, Any]:
        """Get weather forecast for a city"""
        # For now, return a simple response for London and nothing else
        if city == "London":
            return {
                "city": "London",
                "temperature": 15.5,
                "condition": "Partly Cloudy",
                "humidity": 65,
                "wind_speed": 12.0,
            }
        return {}
