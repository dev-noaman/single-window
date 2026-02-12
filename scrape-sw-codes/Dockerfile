FROM python:3.12-slim

WORKDIR /app

# Install system dependencies for PostgreSQL
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir \
    aiohttp \
    asyncpg

COPY discover_codes.py /app/discover_codes.py

CMD ["python", "discover_codes.py"]
