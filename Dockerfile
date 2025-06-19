# Use Python 3.13 slim image
FROM python:3.13-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        curl \
        && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

# Set work directory to the Django project root
WORKDIR /app/app

# Copy uv configuration files to parent directory
COPY pyproject.toml uv.lock /app/

# Install Python dependencies using uv
RUN cd /app && uv sync --frozen --no-dev

# Copy project
COPY . /app/

# Create non-root user with fixed UID/GID
RUN groupadd -g 1000 app \
    && useradd -u 1000 -g app -s /bin/bash -m app \
    && chown -R app:app /app

# Create necessary directories with proper permissions
RUN mkdir -p /app/app/media /app/app/staticfiles /app/app/logs \
    && chown -R app:app /app/app/media \
    && chown -R app:app /app/app/staticfiles \
    && chown -R app:app /app/app/logs \
    && chmod -R 755 /app/app/media \
    && chmod -R 755 /app/app/staticfiles \
    && chmod -R 755 /app/app/logs

USER app

# Collect static files
RUN uv run python manage.py collectstatic --noinput

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

# Create startup script
RUN echo '#!/bin/bash\n\
echo "Checking database connection..."\n\
uv run python check_db.py\n\
echo "Starting Django application..."\n\
uv run gunicorn app.wsgi:application --bind 0.0.0.0:8000 --workers 4\n\
' > /app/app/start.sh && chmod +x /app/app/start.sh

# Run with startup script
CMD ["/app/app/start.sh"]