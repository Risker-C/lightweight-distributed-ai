# Lightweight Worker Dockerfile for Koyeb/Railway
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies first (better caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY *.py .
COPY backends/ ./backends/

# Create data directory for SQLite
RUN mkdir -p /app/data

# Set default environment variables
ENV PORT=8080
ENV PYTHONUNBUFFERED=1

# Expose API port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health')" || exit 1

# Run the application
CMD ["python", "simple_app.py"]
