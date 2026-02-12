# Google Sheets Scraper Backend API

This directory contains both the Python scraper scripts and the PHP backend API endpoints for triggering and monitoring scraper execution.

## Directory Structure

```
scrape-sw-gsheet/
├── scrape-EN.py              # English scraper script
├── scrape-AR.py              # Arabic scraper script
├── progress_writer.py        # Progress tracking module
├── trigger-scrape-en.php     # Backend: Trigger EN scraper
├── trigger-scrape-ar.php     # Backend: Trigger AR scraper
├── progress-en.php           # Backend: Get EN scraper progress
├── progress-ar.php           # Backend: Get AR scraper progress
├── docker-compose.yml        # Docker services configuration
├── Dockerfile                # Container image definition
└── drive/                    # Google credentials directory
    └── google-credentials.json
```

## Backend API Endpoints

### Trigger Endpoints

#### `trigger-scrape-en.php`
Triggers the English scraper by restarting the `GSHEET_SCRAPER_EN` Docker container.

**URL:** `/gsheet-scraper/trigger-scrape-en.php`

**Response:**
```json
{
  "success": true,
  "message": "GSHEET_SCRAPER_EN container restarted successfully. Check progress for updates.",
  "output": "GSHEET_SCRAPER_EN\n",
  "docker_path": "/usr/bin/docker"
}
```

**Error Response:**
```json
{
  "success": false,
  "message": "Google credentials not found"
}
```

#### `trigger-scrape-ar.php`
Triggers the Arabic scraper by restarting the `GSHEET_SCRAPER_AR` Docker container.

**URL:** `/gsheet-scraper/trigger-scrape-ar.php`

**Response:** Same structure as EN endpoint

### Progress Endpoints

#### `progress-en.php`
Returns real-time progress data for the English scraper.

**URL:** `/gsheet-scraper/progress-en.php`

**Response (Running):**
```json
{
  "success": true,
  "status": "running",
  "message": "Processing row 5/10",
  "current_row": 5,
  "total_rows": 10,
  "rows_processed": 0,
  "timestamp": 1234567890
}
```

**Response (Completed):**
```json
{
  "success": true,
  "status": "completed",
  "message": "Scraping completed successfully",
  "current_row": 10,
  "total_rows": 10,
  "rows_processed": 10,
  "timestamp": 1234567890
}
```

**Response (Idle):**
```json
{
  "success": false,
  "status": "idle",
  "message": "No active scrape process"
}
```

#### `progress-ar.php`
Returns real-time progress data for the Arabic scraper.

**URL:** `/gsheet-scraper/progress-ar.php`

**Response:** Same structure as EN endpoint

## Docker Services

### Python Scraper Containers

**GSHEET_SCRAPER_EN:**
- Runs `scrape-EN.py`
- Writes progress to `/tmp/scrape_progress_en.json`
- Mounts `drive/` for Google credentials
- Restart policy: `unless-stopped`

**GSHEET_SCRAPER_AR:**
- Runs `scrape-AR.py`
- Writes progress to `/tmp/scrape_progress_ar.json`
- Mounts `drive/` for Google credentials
- Restart policy: `unless-stopped`

### PHP Web Service

**GSHEET_SCRAPER_WEB:**
- Serves PHP backend endpoints on port 8085
- Has access to Docker socket for container restart
- Mounts `/tmp` for reading progress files
- Mounts `drive/` for credentials validation

## Setup

### 1. Start All Services

```bash
cd scrape-sw-gsheet
docker-compose up -d
```

This starts:
- GSHEET_SCRAPER_EN (Python scraper)
- GSHEET_SCRAPER_AR (Python scraper)
- GSHEET_SCRAPER_WEB (PHP backend on port 8085)

### 2. Verify Services

```bash
# Check all containers are running
docker ps | grep GSHEET_SCRAPER

# Test backend endpoints
curl http://localhost:8085/trigger-scrape-en.php
curl http://localhost:8085/progress-en.php
```

### 3. Nginx Configuration

The nginx reverse proxy routes `/gsheet-scraper/*` to port 8085:

```nginx
location /gsheet-scraper/ {
    proxy_pass http://127.0.0.1:8085/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_read_timeout 300;
}
```

## Usage from Portal

The Portal interface uses these endpoints:

```javascript
// Trigger scraper
fetch('/gsheet-scraper/trigger-scrape-en.php')

// Monitor progress
fetch('/gsheet-scraper/progress-en.php')
```

## Progress File Format

Progress files are written to `/tmp/` by the Python scrapers:

```json
{
  "status": "running|completed|error",
  "current_row": 5,
  "total_rows": 10,
  "message": "Processing row 5/10",
  "rows_processed": 4,
  "timestamp": 1234567890
}
```

## Troubleshooting

### Backend endpoints not accessible

```bash
# Check web service is running
docker ps | grep GSHEET_SCRAPER_WEB

# Check logs
docker logs GSHEET_SCRAPER_WEB

# Restart web service
docker restart GSHEET_SCRAPER_WEB
```

### Scraper won't start

```bash
# Check credentials exist
ls -la drive/google-credentials.json

# Check scraper container
docker logs GSHEET_SCRAPER_EN

# Restart scraper
docker restart GSHEET_SCRAPER_EN
```

### No progress updates

```bash
# Check progress file
cat /tmp/scrape_progress_en.json

# Watch progress file in real-time
watch -n 1 cat /tmp/scrape_progress_en.json
```

## Requirements

- Docker and Docker Compose
- Google credentials file at `drive/google-credentials.json`
- Write access to `/tmp` directory
- Access to Docker socket for container restart

## Related Files

- **Portal/index.php** - Frontend UI with scraper buttons
- **Portal/noaman.cloud.nginx.conf** - Nginx reverse proxy configuration
- **.kiro/specs/gsheet-scraper-buttons/** - Feature specification and documentation
