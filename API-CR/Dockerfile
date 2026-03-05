FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Chromium + all OS-level dependencies (libnss3, libatk, etc.)
RUN python -m playwright install --with-deps chromium

COPY auto_search_company.py api_server.py ./

RUN mkdir -p /app/data

EXPOSE 8086

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8086/health || exit 1

CMD ["python", "api_server.py"]
