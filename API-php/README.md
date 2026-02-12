# API-php Scraper (Python + Playwright)

Qatar Investor Portal scraper using Python and Playwright.

For Docker deployment instructions, see [Docker.md](../Docker.md).

## API Usage

**Endpoint**: `GET /scraper.php`

**Parameters**:
- `code` (required): Business activity code (e.g., 013001)

**Response**: JSON format
```json
{
  "status": "success",
  "data": {
    "activity_code": "013001",
    "status": "Active",
    "name_en": "Activity Name in English",
    "name_ar": "اسم النشاط بالعربية",
    "locations": "Main Location 1: ...\nSub Location 1: ...\nFee 1: ...",
    "eligible": "Allowed for GCC nationals\nAllowed for Non-GCC nationals",
    "approvals": "Approval 1: ...\nAgency 1: ..."
  },
  "error": null
}
```

## Local Development (Without Docker)

### Prerequisites
- Python 3.11+
- PHP 8.2+

### Setup
```bash
pip install -r requirements.txt
playwright install chromium
```

### Run Scraper Directly
```bash
python scraper.py --code 013001 --json
```

### Run via PHP Wrapper
```bash
php scraper.php 013001
```

## Files

- `scraper.py` - Main Python scraper using Playwright
- `scraper.php` - PHP wrapper for the Python scraper
- `Dockerfile` - Docker image configuration
- `docker-compose.yml` - Docker Compose setup
- `nginx.conf` - Nginx web server configuration
- `docker-entrypoint.sh` - Container startup script
