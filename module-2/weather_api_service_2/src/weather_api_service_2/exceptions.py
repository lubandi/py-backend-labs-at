"""Custom exceptions for Weather Service"""


class WeatherServiceError(Exception):
    """Base exception for Weather Service"""

    pass


class InvalidAPIKeyError(WeatherServiceError):
    """Raised when API key is invalid"""

    pass


class CityNotFoundError(WeatherServiceError):
    """Raised when city is not found"""

    pass


class ServiceUnavailableError(WeatherServiceError):
    """Raised when service is unavailable"""

    pass
