FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN pip install --no-cache-dir --upgrade pip

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Chromium + all OS-level dependencies (libnss3, libatk, etc.)
RUN python -m playwright install --with-deps chromium

COPY . .

CMD ["python", "scrape_codes.py"]
