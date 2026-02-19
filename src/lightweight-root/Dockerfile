FROM python:3.11-slim

WORKDIR /app

# Install Flask only
RUN pip install --no-cache-dir flask==3.0.0

# Copy only the app file
COPY app.py .

# Environment
ENV PORT=8080
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 8080

# Run
CMD ["python", "app.py"]
