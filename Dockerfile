# Use official Python image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y build-essential curl && rm -rf /var/lib/apt/lists/*

# Copy pyproject.toml and lock file first (for caching)
COPY pyproject.toml uv.lock* /app/

# Install uv and dependencies
RUN pip install --upgrade pip
RUN pip install uv

# Install project dependencies
RUN uv sync

# Copy the rest of the project
COPY . /app

# Expose port 5000
EXPOSE 8000