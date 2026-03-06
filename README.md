# Qatar Investor Portal Scrapers

Comprehensive web scraping solution for the Qatar Investor Portal.

🌐 **Live Demo**: [https://noaman.cloud](https://noaman.cloud)

## Projects

### 📦 api-scraper (Python + Scrapling + Playwright)
Python-based scraper using Scrapling (StealthyFetcher) + Playwright for browser automation.
- **Endpoint**: `/scrape?code={code}`
- **Health Check**: `/health`
- **Example**: `http://localhost:8080/scrape?code=013001`
- **Documentation**: [CLAUDE.md](CLAUDE.md)

### 📦 API-CR (Company Search & Certificates)
Python-based scraper for company search and certificate downloads.
- **Search**: `/search?cr={cr}` or `/search?q={query}`
- **Download**: `/download?cr={cr}&type={CR|BOTH}`
- **Health Check**: `/health`
- **Example**: `http://localhost:8086/search?cr=12345`
- **Documentation**: [CLAUDE.md](CLAUDE.md)

### 🌐 Portal (Web Interface)
Interactive web portal for testing and using the scrapers.
- **Access**: `http://localhost:8082/`
- **Features**:
  - Real-time testing with engine selection
  - JSON response viewer
  - Google Sheets Scraper buttons with live progress monitoring
  - Terminal-style interface with real-time updates

### 📊 scrape-sw-codes (Business Codes Fetcher)
Fetches 2800+ business activity codes from Qatar portal to PostgreSQL.
- **Trigger**: `http://localhost:8084/trigger-fetch-codes.php`
- **Progress**: `http://localhost:8084/progress.php`
- **Check Update**: `http://localhost:8084/check-update.php`
- **Features**: Smart sync, hourly cron, real-time progress

### 📊 scrape-sw-gsheet (Google Sheets Scraper)
Backend API for triggering and monitoring Google Sheets scraping operations.
- **Trigger EN**: `http://localhost:8085/trigger-scrape-en.php`
- **Trigger AR**: `http://localhost:8085/trigger-scrape-ar.php`
- **Progress EN/AR**: `/progress-en.php`, `/progress-ar.php`
- **Features**: Scrapes data to Google Sheets "Filter" workbook

### 🏢 officernd (OfficeRnD API Clone)
Offline clone of OfficeRnD API with 580 companies and 80 endpoints.
- **API**: `http://localhost:8087/`
- **BFF/UI**: `http://localhost:8088/`
- **Features**: Full sync, smart sync, export to SQL

## 🚀 Quick Start

### **Docker Deployment (GitHub Actions)**
Push to `main` triggers automatic deployment via `.github/workflows/deploy.yml`.

### **Local Development**
```bash
# Clone repository
git clone https://github.com/dev-noaman/single-window.git
cd single-window

# api-scraper (Python + Scrapling)
cd api-scraper && docker compose up -d --build

# API-CR (Company Search)
cd API-CR && docker compose up -d --build

# Portal (Web Interface)
cd Portal && docker compose up -d --build
```

## Features

✅ **Python Scrapling** - StealthyFetcher + Playwright for reliable scraping
✅ **Web Interface** - Interactive portal for testing and usage
✅ **Google Sheets Integration** - Automated scraping to Google Sheets with EN/AR support
✅ **Real-time Progress Monitoring** - Live updates for scraper operations
✅ **JSON API** - Clean REST API responses
✅ **Arabic Support** - Extracts both English and Arabic content
✅ **PostgreSQL Database** - Business activity codes with smart sync
✅ **Docker Ready** - Complete containerization
✅ **Production Ready** - Health checks, auto-restart, proper timeouts

## Requirements

### Docker Deployment
- Docker and Docker Compose
- 2GB+ RAM for VPS deployment
- Network access to ports 8080, 8082, 8084, 8085, 8086, 8087, 8088

### Local Development
- Python 3.12+ (for api-scraper, API-CR)
- PHP 8.2+ (for web interfaces)
- Node.js 18+ (for officernd-bff)
- Docker Desktop (recommended)

## Project Structure

```
single-window/
├── .github/workflows/      # GitHub Actions deployment
├── api-scraper/            # Python + Scrapling scraper (activity codes)
│   ├── scraper.py
│   ├── server.py
│   └── docker-compose.yml
├── API-CR/                 # Python + Scrapling (company search/certs)
│   ├── auto_search_company.py
│   ├── api_server.py
│   └── docker-compose.yml
├── Portal/                 # Web interface (PHP + Nginx)
│   ├── index.php
│   ├── nginx.conf
│   └── docker-compose.yml
├── scrape-sw-codes/        # Business codes fetcher (host PM2)
│   ├── discover_codes.py
│   ├── trigger-fetch-codes.php
│   └── progress.php
├── scrape-sw-gsheet/       # Google Sheets scraper
│   ├── scrape-EN.py
│   ├── scrape-AR.py
│   └── docker-compose.yml
├── officernd/              # OfficeRnD API clone
│   ├── api/                # FastAPI backend
│   └── bff/                # NestJS + React frontend
└── tests/                  # Playwright e2e tests
```

## 📋 API Reference

### Service Endpoints
| Service | Port | Endpoint | Description |
|---------|------|----------|-------------|
| api-scraper | 8080 | `/scrape?code={code}` | Activity code scraper |
| api-scraper | 8080 | `/health` | Health check |
| API-CR | 8086 | `/search?cr={cr}` | Company search by CR |
| API-CR | 8086 | `/search?q={query}` | Search by CR/EN/AR name |
| API-CR | 8086 | `/download?cr={cr}&type={CR\|BOTH}` | Download certificates |
| Portal | 8082 | `/` | Web interface |
| scrape-sw-codes | 8084 | `/trigger-fetch-codes.php` | Trigger code fetch |
| scrape-sw-codes | 8084 | `/progress.php` | Fetch progress |
| scrape-sw-codes | 8084 | `/check-update.php` | Smart update check |
| scrape-sw-gsheet | 8085 | `/trigger-scrape-en.php` | Trigger EN scraper |
| scrape-sw-gsheet | 8085 | `/trigger-scrape-ar.php` | Trigger AR scraper |
| officernd API | 8087 | `/health` | OfficeRnD API |
| officernd BFF | 8088 | `/` | OfficeRnD sync UI |

### Scraper API Response Format
All scrapers return JSON responses in the following format:

```json
{
  "status": "success",
  "data": {
    "activity_code": "013001",
    "status": "Active",
    "name_en": "Activity Name in English",
    "name_ar": "اسم النشاط بالعربية",
    "locations": "Main Location 1: ...",
    "eligible": "Allowed for GCC nationals...",
    "approvals": "Approval 1: ..."
  },
  "error": null
}
```

## License

MIT

## Author

Noaman - [GitHub](https://github.com/dev-noaman)

## Support

For issues and questions, please open an issue on [GitHub](https://github.com/dev-noaman/single-window/issues).
