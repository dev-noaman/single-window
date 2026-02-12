FROM python:3.11-slim

WORKDIR /app

# Install system dependencies including Chromium
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Set Playwright browser path
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright
RUN mkdir -p /ms-playwright

# Install Playwright browsers
RUN playwright install chromium

# Copy application files
COPY auto_search_company.py /app/auto_search_company.py
COPY api_server.py /app/api_server.py

# Create data directory for caches
RUN mkdir -p /app/data

# Expose API port
EXPOSE 8086

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8086/health || exit 1

# Run the API server
CMD ["python", "api_server.py"]
