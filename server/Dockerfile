# Use Python 3.12 slim image
FROM python:3.12-slim

# Set working directory in container
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose the WebSocket port
EXPOSE 8000

# Run the main server
CMD ["python", "main.py"]
