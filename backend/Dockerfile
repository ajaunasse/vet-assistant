FROM python:3.13

# Copy uv from the official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Set working directory
WORKDIR /app

# Copy dependency files first for better caching (still useful for initial build)
COPY pyproject.toml ./

# Copy the rest of the backend code
COPY . .

# Expose the port
EXPOSE 8000

# Note: CMD is overridden by docker-compose command
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]