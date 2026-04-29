# Record Social Backend API

A backend FastAPI service for Record Social, a platform for managing and organizing social media content.

## Table of Contents

- [Installation](#installation)
- [Technologies & Dependencies](#technologies--dependencies)
- [Running the Server](#running-the-server)
- [JSON Logging Format](#json-logging-format)

## Installation

This project uses `uv` as the package manager for fast, reliable Python dependency management.

### Installing uv

#### macOS

```bash
# Using Homebrew
brew install uv

# Or using curl
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### Windows

```bash
# Using PowerShell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or using pip
pip install uv
```

#### Linux

```bash
# Using curl
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or using your package manager (e.g., for Ubuntu/Debian)
sudo apt-get install uv
```

### Setting Up the Project

After installing `uv`, install the project dependencies:

```bash
uv sync
```

This will install all dependencies specified in `pyproject.toml`.

## Technologies & Dependencies

This project uses the following technologies and dependencies:

- **Python**: >= 3.10
- **FastAPI** (>= 0.136.0): Modern, fast web framework for building APIs with Python
- **Uvicorn** (>= 0.46.0): ASGI web server implementation
- **SQLAlchemy** (>= 2.0.49): Python SQL toolkit and Object-Relational Mapping (ORM)
- **psycopg2** (>= 2.9.12): PostgreSQL adapter for Python
- **python-dotenv** (>= 1.2.2): Loads environment variables from `.env` files
- **python-json-logger** (>= 4.1.0): Structured JSON logging for Python

## Running the Server

To start the development server, use the following command:

```bash
uv run -m app.main
```

The server will start and be available at `http://localhost:8000` by default.

### Additional Server Options

You can also pass additional arguments to the server:

```bash
# Run on a specific port
uv run -m app.main --port 8080

# Run with auto-reload (development mode)
uv run -m app.main --reload
```

## JSON Logging Format

The application uses structured JSON logging for better log aggregation and analysis. Logs are formatted with the following standard structure:

```json
{
  "asctime": "2026-04-29T10:30:45.123456Z",
  "name": "app.main",
  "levelname": "INFO",
  "message": "Server started successfully"
}
```

### Fields Description

- **asctime**: ISO 8601 formatted timestamp when the log message was generated
- **name**: Logger name, typically the module or component name
- **levelname**: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- **message**: The actual log message content

### Configuring Logging

Logging configuration can be customized by modifying the application's logging setup. By default, logs are output to `stdout` in JSON format for easy integration with log aggregation services.
