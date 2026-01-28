# Django URL Shortener Microservice

A production-ready URL Shortener API built with **Django**, **Django REST Framework**, and **Redis**. Designed with a clean **Service Layer architecture** and fully containerized with **Docker**.

## Features

- **Shorten URLs**: Convert long URLs into compact short codes.
- **Redirection**: Instant redirection to the original URL.
- **Analytics**: Track click counts and creation dates.
- **High Performance**: Redis caching for fast lookups.
- **Dockerized**: specific multi-stage build for production.
- **OpenAPI/Swagger**: Auto-generated interactive documentation.
- **Validation**: Robust input validation using Serializers.

## Tech Stack

- **Framework**: Django 5.0 + Django REST Framework
- **Database**: SQLite (Production-ready option: PostgreSQL)
- **Cache**: Redis
- **Documentation**: drf-spectacular (OpenAPI 3.0)
- **Server**: Gunicorn
- **Containerization**: Docker & Docker Compose

## Architecture

This project follows a **Clean Architecture** approach:

1.  **Service Layer (`services.py`)**: Encapsulates all business logic (generating codes, caching, database interactions). Views are thin and only handle HTTP concerns.
2.  **API Layer (`views.py`, `serializers.py`)**: Handles request validation and response formatting.
3.  **Models (`models.py`)**: Defines the data schema.
4.  **Infrastructure**: Docker handles the environment. `config/settings` splits configuration for Dev and Prod.

## Setup Instructions

### Prerequisites

- Docker & Docker Compose

### Running with Docker (Recommended)

1.  **Build and Start**:
    ```bash
    docker-compose up --build
    ```

2.  **Appply Migrations** (First run only):
    In a new terminal:
    ```bash
    docker-compose exec web python manage.py migrate
    ```

3.  **Access the Application**:
    - **API Root**: `http://localhost:8000/api/shorten/`
    - **Swagger UI**: `http://localhost:8000/api/docs/`
    - **Admin**: `http://localhost:8000/admin/`

## API Usage

### 1. Shorten a URL
**POST** `/api/shorten/`
```json
{
  "url": "https://www.example.com/a-long-url"
}
```
**Response:**
```json
{
  "original_url": "https://www.example.com/a-long-url",
  "short_code": "a1b2c3",
  "short_url": "http://localhost:8000/a1b2c3",
  "created_at": "2023-10-27T10:00:00Z",
  "clicks": 0
}
```

### 2. Redirect
**GET** `/{short_code}`
- Redirects to the original URL.

### 3. Get Stats
**GET** `/api/stats/{short_code}/`
**Response:**
```json
{
  "original_url": "...",
  "clicks": 5,
  ...
}
```
