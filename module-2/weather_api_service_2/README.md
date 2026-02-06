# Weather API Service - TDD & SOLID Implementation

## 📋 Project Overview
A robust **Weather API Service Stub** built to demonstrate strict **Test-Driven Development (TDD)**, **SOLID architecture**, and production-grade **Python best practices**. This project simulates an external weather provider with predictable responses, achieving high reliability and maintainability.

> **Note:** This project strictly adheres to the "Red-Green-Refactor" cycle and trunk-based development workflow.

## 🎯 Key Objectives Achieved
| Category | Achievement |
| :--- | :--- |
| **Testing** | **98% Test Coverage** (Near 100% target met) using `pytest` & `pytest-mock`. |
| **Architecture** | **SOLID Principles** applied (Dependency Injection, Open/Closed). |
| **Code Quality** | Strict **Type Hints**, **Google-style Docstrings**, and **Structured Logging**. |
| **Workflow** | **Trunk-based development** with simulated code reviews. |

## 🛠️ Tech Stack & Tools
- **Core**: Python 3.8+, `dataclasses`
- **Testing**: `pytest`, `pytest-cov`, `pytest-mock`
- **Quality**: `black` (formatting), `ruff` (linting), `mypy` (static analysis)
- **CI/CD**: `pre-commit` hooks for quality checks

## 📁 Project Structure
```text
weather_api_service_2/
├── src/
│   └── weather_api_service_2/
│       ├── __init__.py
│       ├── service.py          # core logic (Dependency Injection)
│       ├── providers.py        # abstract interface & mock implementation
│       ├── exceptions.py       # custom domain exceptions
│       └── logger.py           # structured json logger
├── tests/
│   ├── test_service.py         # main tdd test suite
│   ├── test_providers.py       # contract tests
│   └── test_exceptions.py      # error handling tests
├── htmlcov/                    # coverage reports
├── pyproject.toml              # configuration
├── requirements.txt            # prod dependencies
└── README.md                   # documentation
```

## 🔄 TDD & Implementation Journey

This project was built in 4 distinct phases, reflecting a professional software engineering lifecycle:

### **Phase 1: Foundation (The "Red-Green-Refactor" Cycle)**
- Established the Git environments and `pytest` configuration.
- Implemented `get_forecast(city)` using strict TDD:
    - **RED**: Wrote failing test for valid city retrieval.
    - **GREEN**: Implemented minimal pass code.
    - **REFACTOR**: Optimized structure.

### **Phase 2: Robustness (Edge Cases)**
- Handled failure scenarios with custom exceptions:
    - `InvalidAPIKeyError`: Authentication validation.
    - `CityNotFoundError`: Graceful handling of unknown inputs.
- Integrated **Structured Logging** for traceability of requests/errors.

### **Phase 3: Architecture (SOLID Refactoring)**
- **Dependency Inversion**: Decoupled `WeatherService` from concrete data sources.
- Introduced `WeatherProvider` abstract base class.
- Verified system extensibility (Open/Closed Principle) without modifying core logic.

### **Phase 4: Polish & Validation**
- Achieved **98% Code Coverage**, rigorously validating all logical branches.
- Finalized strict type hinting and comprehensive docstrings.
- Verified adherence to Google Style Guide.

## 🧪 Testing & Validation

### Running the Test Suite
The project uses `pytest` for all testing needs.

```bash
# 1. Install Dependencies
pip install -r requirements.txt

# 2. Run Tests (Verbose)
pytest -v

# 3. Generate Coverage Report
pytest --cov=weather_api_service_2 --cov-report=html --cov-report=term-missing
```

### Coverage Report Summary
The project maintains near-perfect coverage to ensure reliability.

```text
Name                                      Stmts   Miss  Cover
-------------------------------------------------------------
src\weather_api_service_2\__init__.py         0      0   100%
src\weather_api_service_2\exceptions.py       8      0   100%
src\weather_api_service_2\logger.py          16      0   100%
src\weather_api_service_2\providers.py       11      1    91%
src\weather_api_service_2\service.py         20      0   100%
-------------------------------------------------------------
TOTAL                                        55      1    98%
```
*(Note: The remaining missing line in `providers.py` is typically the abstract method definition, which is excluded from execution flow.)*

## 🏗️ Design Principles (SOLID)

1.  **Single Responsibility Principle (SRP)**:
    - `service.py` handles business logic.
    - `providers.py` handles data fetching.
    - `logger.py` handles observability.

2.  **Open/Closed Principle (OCP)**:
    - New data sources (e.g., a real `OpenWeatherMapProvider`) can be added by extending `WeatherProvider` without changing `WeatherService`.

3.  **Dependency Inversion Principle (DIP)**:
    - `WeatherService` depends on the `WeatherProvider` abstraction, not concrete implementations.

## 🚀 Quick Usage

# Start Python interpreter
python

# Import and test the service
>>> from weather_api_service_2.service import WeatherService
>>> service = WeatherService()
>>> forecast = service.get_forecast("London")
>>> print(forecast)
{'city': 'London', 'temperature': 15.5, ...}

# Test error handling
>>> service = WeatherService(api_key="invalid")
>>> try:
...     service.get_forecast("London")
... except Exception as e:
...     print(f"Error correctly raised: {type(e).__name__}")
InvalidAPIKeyError
