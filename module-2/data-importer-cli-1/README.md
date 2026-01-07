# 📊 Resilient Data Importer CLI

A robust command-line tool for importing user data from CSV files into a JSON database with comprehensive error handling, validation, and logging.

## 🎯 Overview

This project implements a resilient data importer that gracefully handles various error scenarios including missing files, malformed CSV data, duplicate entries, and validation errors. Built with clean code practices, SOLID principles, and comprehensive testing.

## 📋 Features

- **Robust Error Handling**: Custom exception hierarchy for specific error cases
- **Safe File Operations**: Context managers for automatic resource cleanup
- **Comprehensive Validation**: Email format, required fields, duplicate detection
- **Structured Logging**: Detailed logs for debugging and monitoring
- **Type Safety**: Full type hints with mypy validation
- **High Test Coverage**: 93% overall test coverage with pytest
- **Clean CLI**: Simple, focused command-line interface
- **Git Flow Workflow**: Professional branching strategy with pre-commit hooks

## 🏗️ Architecture

### Project Structure

```
src/importer_cli/
├── context_manager/     # Safe file handling with context managers
├── exceptions/          # Custom exception hierarchy
├── models/             # Data models and dataclasses
├── parser/             # CSV parsing with error resilience
├── repository/         # JSON database operations
├── validator/          # Data validation logic
└── cli.py             # Main CLI entry point

tests/                  # Comprehensive test suite
├── unit tests for each module
├── integration tests
└── pytest fixtures
```

### Component Design

- **CSVParser**: Resilient CSV parsing with graceful error handling
- **UserValidator**: Validates user data against business rules
- **UserRepository**: Manages JSON database operations
- **CSVFileReader**: Context manager for safe file reading
- **Custom Exceptions**: Hierarchical error types for precise error handling
- **ResilientImporter**: Main orchestrator class coordinating all components

## 🚀 Quick Start

### Prerequisites

- Python 3.11 or higher
- Poetry for dependency management


### Basic Usage

1. **Prepare a CSV file:**

```csv
user_id,name,email
1,John Doe,john@example.com
2,Jane Smith,jane@example.com
3,Bob Johnson,bob@example.com
```

2. **Run the importer:**

```bash
# Simple import
python src/importer_cli/cli.py users.csv

# With custom database location
python src/importer_cli/cli.py users.csv --db-file custom_db.json

# With verbose logging
python src/importer_cli/cli.py users.csv -v
```

## 📖 Detailed Usage

### Import Command

```bash
# Basic import with default database
python src/importer_cli/cli.py users.csv

# Import with custom database file
python src/importer_cli/cli.py users.csv --db-file /path/to/database.json

# Enable verbose logging
python src/importer_cli/cli.py users.csv --verbose
# or
python src/importer_cli/cli.py users.csv -v

# Show help
python src/importer_cli/cli.py --help
```

### Output Example

```
✅ Successfully imported 45 users.
❌ Failed to import 3 users.
⚠️  Skipped 2 duplicate users.

Errors encountered:
Line 12: Invalid email format: user@invalid
Line 24: Missing required field: name
Line 47: Duplicate user_id: 101
```

### File Structure

```
data/
├── users.json           # Default database (auto-created)
logs/
├── importer.log        # Application logs (auto-created)
src/importer_cli/
├── cli.py              # Main CLI entry point
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=src/importer_cli --cov-report=html

# Run specific test file
pytest tests/test_parser.py

# Run tests with verbose output
pytest -v
```

### Test Coverage

The project maintains **93% test coverage** across all modules:

| Module | Coverage |
|--------|----------|
| CLI | 93% |
| Parser | 88% |
| Validator | 100% |
| Repository | 89% |
| Exceptions | 97% |
| Models | 98% |
| File Handler | 87% |

View detailed coverage: `pytest --cov=src/importer_cli --cov-report=html` then open `htmlcov/index.html`

## 🛠️ Development

### Git Workflow

This project follows **Git Flow**:

- `main`: Production-ready code
- `develop`: Integration branch
- `feature/*`: Feature development
- `hotfix/*`: Emergency fixes

### Code Quality Tools

Pre-commit hooks automatically run:

- **Black**: Code formatting
- **Ruff**: Linting
- **mypy**: Type checking
- **pytest**: Quick test run

To set up pre-commit hooks:

```bash
pre-commit install
```

### Development Commands

```bash
# Format code
black src/ tests/

# Run linter
ruff check src/ tests/

# Type checking
mypy src/

# Run all checks
pre-commit run --all-files
```

## 📊 Error Handling

The importer gracefully handles various error scenarios:

| Error Type | Example | Tool Response |
|------------|---------|---------------|
| Missing file | `users.csv` not found | Logs error, shows clear message |
| Malformed CSV | Invalid headers/columns | Skips invalid rows, logs warnings |
| Invalid email | `user@invalid` | Fails that row, continues with others |
| Duplicate user | Same `user_id` twice | Skips duplicate, continues import |
| Missing fields | Empty `name` or `email` | Fails that row, continues with others |
| Database issues | Permission denied | Logs error, stops import |

### Exception Hierarchy

```
ImporterError
├── FileError
│   ├── MissingFileError
│   └── FileAccessError
├── CSVFormatError
│   ├── InvalidHeaderError
│   └── InvalidRowError
├── ValidationError
│   ├── InvalidEmailError
│   ├── MissingFieldError
│   └── InvalidFormatError
├── DatabaseError
│   ├── DuplicateUserError
│   └── DatabaseAccessError
└── ConfigurationError
```

## 📝 Logging

The application uses structured logging:

- **Console**: Shows import summary and critical errors
- **File**: Detailed logs in `logs/importer.log`
- **Levels**:
  - `INFO`: Import progress, statistics
  - `WARNING`: Non-critical issues (empty rows, extra columns)
  - `ERROR`: Validation failures, parsing errors
  - `CRITICAL`: System failures

Enable verbose logging with `-v` flag for debug-level output.

## 🔧 Configuration

### Database Location

By default, the database is stored at `data/users.json`. Change this with:

```bash
python src/importer_cli/cli.py users.csv --db-file /custom/path/db.json
```

### Log Location

Logs are stored in `logs/importer.log`. The directory is created automatically.

## 🧩 How It Works

### Import Pipeline

1. **Parsing**: Read CSV file with error resilience
2. **Validation**: Check each row for data integrity
3. **Sanitization**: Clean and normalize data
4. **Storage**: Save to JSON database with duplicate checking

### Resilient Features

- **Line-by-line processing**: Memory efficient for large files
- **Continue on error**: Individual row failures don't stop entire import
- **Atomic operations**: All-or-nothing database updates
- **Detailed reporting**: Clear summary of successes and failures

## 📈 Performance

- **Memory Efficient**: Processes large files line by line
- **Fast Validation**: Early exit on critical errors
- **Atomic Operations**: Database updates are all-or-nothing
- **Parallel Safe**: File locking prevents concurrent modifications

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/improvement`)
3. Commit changes (`git commit -am 'Add new feature'`)
4. Push to branch (`git push origin feature/improvement`)
5. Create Pull Request

### Code Standards

- Follow PEP 8 style guidelines
- Include type hints for all functions
- Write comprehensive docstrings
- Add tests for new functionality
- Update documentation as needed
