# Use Python 3.12 slim image
FROM python:3.12-slim

# Install system dependencies for Bluetooth support
RUN apt-get update && apt-get install -y \
    bluetooth \
    bluez \
    libbluetooth-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash app

# Set working directory in container
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Change ownership to app user
RUN chown -R app:app /app

# Switch to non-root user
USER app

# Expose the WebSocket port
EXPOSE 8000

# Run the main server
CMD ["python", "main.py"]
