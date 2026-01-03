"""Structured logging configuration"""
import json
import logging


class StructuredLogger:
    """Logger that outputs structured JSON logs"""

    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)

        # Create console handler with JSON formatter
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            json.dumps(
                {
                    "timestamp": "%(asctime)s",
                    "level": "%(levelname)s",
                    "module": "%(name)s",
                    "message": "%(message)s",
                }
            )
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def info(self, message: str, **kwargs):
        """Log info message with structured data"""
        log_data = {"message": message, **kwargs}
        self.logger.info(json.dumps(log_data))

    def error(self, message: str, **kwargs):
        """Log error message with structured data"""
        log_data = {"message": message, **kwargs}
        self.logger.error(json.dumps(log_data))
