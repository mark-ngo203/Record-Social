FROM python:3.10-slim

WORKDIR /backend

# Install system dependencies
RUN apt-get update && apt-get install -y \
  gcc \
  postgresql-client \
  curl \
  && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY pyproject.toml uv.lock* ./

# Sync the project dependencies
RUN uv sync --frozen

COPY . .

# Run the application
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--reload"]
