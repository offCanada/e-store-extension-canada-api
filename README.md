# e-store-extension-canada-api

Backend API for Canadian e-store extension built with FastAPI.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Project](#running-the-project)
- [API Documentation](#api-documentation)
- [Project Structure](#project-structure)

## Prerequisites

- **Python 3.14+** - The project requires Python version 3.14 or higher
- **uv** - Package manager for Python. Install from [https://astral.sh/uv](https://astral.sh/uv)

## Installation

1. **Clone the repository** (if not already done):
   ```bash
   git clone <repository-url>
   cd e-store-extension-canada-api
   ```

2. **Install dependencies** using uv:
   ```bash
   uv sync
   ```

   This will install all required dependencies:
   - FastAPI (web framework)
   - Uvicorn (ASGI server)
   - DuckDB (database)
   - Pydantic Settings (configuration management)
   - SlowAPI (rate limiting)

## Configuration

Create a `.env` file in the project root to configure environment variables:

```env
# Database configuration
DB_PATH=data/nutrilens.duckdb
READ_ONLY=true
```

**Environment Variables:**
- `DB_PATH` - Path to the DuckDB database file (default: `data/nutrilens.duckdb`)
- `READ_ONLY` - Set to `true` for read-only mode (default: `true`)

## Running the Project

### Using the Project Script

```bash
uv run serve
```

This command will:
- Start the FastAPI development server
- Listen on `http://127.0.0.1:8000` by default
- Enable auto-reload during development

### Using Direct Python

```bash
uv run python -m uvicorn app.main:app --reload
```

## API Documentation

Once the server is running, you can access:

- **Interactive API Documentation (Swagger UI)**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Alternative API Documentation (ReDoc)**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

### Health Check

The API provides a health check endpoint:

```bash
curl http://localhost:8000/
```

Response:
```json
{
  "status": "ok"
}
```

## Project Structure

```
e-store-extension-canada-api/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── configs/
│   │   ├── settings.py         # Configuration management
│   │   └── db.py               # Database setup
│   ├── models/
│   │   └── product.py          # Data models
│   ├── router/
│   │   └── products.py         # API route handlers
│   ├── services/
│   │   └── product_service.py  # Business logic
│   └── data/
│       └── nutrilens.duckdb    # DuckDB database file
├── pyproject.toml              # Project configuration and dependencies
└── README.md                   # This file
```

## Troubleshooting

### Port Already in Use
If port 8000 is already in use, specify a different port:
```bash
uv run python -m uvicorn app.main:app --port 8001
```

### Python Version Mismatch
Verify your Python version:
```bash
python --version
```
Must be Python 3.14 or higher.

### Dependencies Installation Issues
Clear the cache and reinstall:
```bash
uv sync --force
``` 
