FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH=/app/src

# Set working directory
WORKDIR /app

# Install dependencies
COPY infra/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code and docs
COPY src/ /app/src/
COPY docs/ /app/docs/

# Create a non-root user
RUN adduser --disabled-password --gecos '' appuser
RUN chown -R appuser:appuser /app
USER appuser

# Default command to run the orchestrator loop
CMD ["python", "src/orchestrator.py"]
