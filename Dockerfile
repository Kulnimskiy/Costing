FROM python:3.11-slim

# Environment
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y build-essential curl && rm -rf /var/lib/apt/lists/*

# Copy pyproject.toml first for caching
COPY pyproject.toml uv.lock* /app/

# Upgrade pip and install dependencies
RUN pip install --upgrade pip
RUN pip install uv
RUN uv use python3
RUN uv sync

# Copy the rest of the project
COPY . /app

# Expose port 5000
EXPOSE 8000