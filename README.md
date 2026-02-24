# Labs & Projects Monorepo - by Lubandi Joseph

📚 Overview
This monorepo contains my completed labs and projects from various modules, demonstrating skills in Python development, testing, database fundamentals, and web development.

🗂️ Repository Structure

### Module 2: Clean Code, Testing, Git
#### Lab 1: Resilient Data Importer CLI
* CLI tool for importing user data from CSV to JSON database
* Implements robust exception handling with custom exceptions
* Adheres to PEP 8, SOLID principles, and Git Flow workflow
* Comprehensive test suite with >90% coverage

#### Lab 2: TDD-based API Service Stub
* Mock Weather API service built using Test-Driven Development
* Strict TDD workflow (Red-Green-Refactor)
* SOLID principles with dependency injection
* Near 100% test coverage

### Module 3: Python Advanced
#### Student Grade Analytics Tool
* Processes student records from CSV/JSON files
* Uses advanced collections (Counter, defaultdict, OrderedDict, deque)
* Implements dataclasses with comprehensive type hints
* Generates statistical reports and visualizations

### Module 4: Database Fundamentals
#### E-Commerce Analytics Data Pipeline
* Normalized PostgreSQL schema for e-commerce platform
* Transactional CRUD operations using psycopg2
* NoSQL integration (Redis for caching, MongoDB for sessions)
* Complex SQL queries with window functions and CTEs
* Query optimization with EXPLAIN ANALYZE and indexing

### Module 5: Flask/Django Web Development
#### URL Shortener Microservice
* Flask application using application factory pattern and blueprints
* Dependency injection with Flask-Injector
* Docker containerization with Redis
* REST API with Flask-RESTX and OpenAPI/Swagger documentation
* Production-ready deployment configuration

### Modules 6, 7, 8 & 9: Advanced Web Backend & Microservices
#### Enterprise-Grade URL Shortener Microservice (`module-6-7-8-9/`)
* **Microservice Architecture**: Decoupled Django main backend handling core business logic natively paired with an independent Preview Service for external metadata extraction.
* **Asynchronous Processing**: Celery & Redis integrations for background parsing and nightly dead-link archiving.
* **Advanced Analytics**: Granular click tracking recording time-series arrays, IP mapping, and geographic location breakdowns for Premium-tier users.
* **High-Performance Infrastructure**: Optimized redirect performance with synchronous Redis cache-lookups to slash database I/O, coupled with strictly configured DRF rate limiters.
* **Production Observability & Security**: Comprehensive testing routines, explicit Base/Dev/Prod split configurations, structured JSON logging, and fully polished Swagger REST documentation.

### Additional Projects
* **Homework/Todo Project**: Django-based todo application
* **Module 1**: Initial lab work and setup

🛠️ Common Features Across Projects
* **Code Quality**: PEP 8 compliance, type hints, comprehensive docstrings
* **Testing**: High test coverage with pytest, mocking, and fixtures
* **Git Workflow**: Proper branching strategies with pull requests
* **Pre-commit Hooks**: Automated code quality checks
* **Documentation**: Detailed README files and usage instructions

🚀 Getting Started

#### Prerequisites
* Python 3.11+
* Git
* Docker & Docker Compose (for Modules 4-9)
* PostgreSQL, Redis, MongoDB (for backend projects)

#### Installation
Each module contains its own `requirements.txt` file. Navigate to the specific project directory and install dependencies:

```bash
cd module-2/lab-name
pip install -r requirements.txt
```

#### Running Projects
Detailed setup and execution instructions are available in each module's respective `README.md` file.

📊 Skills Demonstrated
* **Python Development**: Clean code, SOLID principles, advanced data structures
* **Testing**: TDD, BDD, unit testing, integration testing
* **Databases**: SQL (PostgreSQL), NoSQL (Redis, MongoDB), query optimization
* **Web Development**: Django REST Framework, Flask, REST APIs, microservices, containerization
* **DevOps**: Docker, Git workflows, CI/CD practices
* **Documentation**: Detailed Swagger API documentation, code comments, architecture designs, comprehensive repository READMEs

👨‍💻 Author
**Lubandi Joseph**  
Software Developer
