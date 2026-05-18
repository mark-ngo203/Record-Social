FROM python:3.10-slim

WORKDIR /backend

# Install system dependencies
RUN apt-get update && apt-get install -y \
  gcc \
  postgresql-client \
  curl \
  && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:0.9.21 /uv /uvx /bin/

COPY pyproject.toml README.md uv.lock* ./

# Sync the project dependencies
RUN uv sync --frozen

COPY . .

# Run the application
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--reload"]
