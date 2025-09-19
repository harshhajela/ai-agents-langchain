# Use slim Python base for smaller image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# No additional OS packages required

# Copy requirements first (for caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Create non-root user and prepare log directory
RUN adduser --disabled-password --gecos "" appuser \
    && mkdir -p /var/log/ai-agents \
    && chown -R appuser:appuser /app /var/log/ai-agents

# Switch to non-root user
USER appuser

# Expose FastAPI port
EXPOSE 8000

# Run FastAPI with Uvicorn (suppress access logs; our middleware logs requests)
CMD ["uvicorn", "research_agent.app.main:app", "--host", "0.0.0.0", "--port", "8000", "--no-access-log"]
