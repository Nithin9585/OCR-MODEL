#!/bin/bash

# Railway startup script for OCR service
echo "🚀 Starting OCR Service on Railway..."

# Print environment info
echo "Python version: $(python --version)"
echo "Port: ${PORT:-5000}"

# Start the application with Gunicorn
exec gunicorn \
    --bind 0.0.0.0:${PORT:-5000} \
    --workers 1 \
    --timeout 120 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --preload \
    --log-level info \
    --access-logfile - \
    --error-logfile - \
    app:app
