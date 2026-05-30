# Use a lightweight Python image
FROM python:slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080

# Set the working directory
WORKDIR /app

# Install system dependencies required by LightGBM
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy the application code
COPY . .

# Install the package in editable mode
RUN pip install --no-cache-dir -e .

# Install Gunicorn explicitly
RUN pip install --no-cache-dir gunicorn

# Pre-train the model during build (CRITICAL - model ready before app starts)
RUN python pipeline/training_pipeline.py

# Expose the port that Flask will run on
EXPOSE 8080

# Health check - ensures container is ready before Cloud Run routes traffic
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Run the app with Gunicorn (production WSGI server)
# Cloud Run requires app to listen on PORT env var
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT} --workers 2 --worker-class sync --timeout 120 --access-logfile - --error-logfile - --log-level info application:app"]
