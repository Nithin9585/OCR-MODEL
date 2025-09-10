# Use Python 3.9 slim image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies for OpenCV and other packages
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libglib2.0-0 \
    libgtk-3-0 \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements-railway.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements-railway.txt

# Copy application code
COPY . .

# Expose port
EXPOSE $PORT

# Command to run the application with optimized settings
CMD gunicorn --bind 0.0.0.0:$PORT app:app \
    --timeout 300 \
    --workers 1 \
    --worker-class sync \
    --worker-connections 1000 \
    --max-requests 100 \
    --max-requests-jitter 10 \
    --preload \
    --log-level info
