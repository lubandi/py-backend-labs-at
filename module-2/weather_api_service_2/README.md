# Weather API Service - TDD Implementation

## Overview
A mock Weather API service built using Test-Driven Development (TDD) principles with Python. This project demonstrates clean code practices, SOLID architecture, and comprehensive testing.

## Features
- TDD workflow with Red-Green-Refactor cycle
- SOLID principles implementation
- Dependency injection with abstract providers
- Custom exception handling
- Structured logging
- 100% test coverage
- Pre-commit hooks for code quality

## Architecture
src/weather_service/
├── init.py
├── service.py # Main WeatherService class
├── providers.py # Abstract WeatherProvider and implementations
├── exceptions.py # Custom exceptions
└── logger.py # Structured logging


## TDD Process
1. **Day 1**: Setup and first feature (get_forecast for valid city)
2. **Day 2**: Error handling and edge cases
3. **Day 3**: SOLID architecture with dependency injection
4. **Day 4**: Finalization, documentation, and coverage
