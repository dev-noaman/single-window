# Qatar Investor Portal Scrapers

Comprehensive web scraping solution for the Qatar Investor Portal, featuring multiple implementations and deployment options.

🌐 **Live Demo**: [https://noaman.cloud](https://noaman.cloud)  
📦 **GitHub**: [https://github.com/dev-noaman/scrapers](https://github.com/dev-noaman/scrapers)  
🐳 **Docker Guide**: [Docker.md](Docker.md)

## Projects

### 📦 API-php (Python + Playwright)
Python-based scraper using Playwright for browser automation.
- **Endpoint**: `/scraper.php?code={bacode}`
- **Example**: `http://localhost:8080/scraper.php?code=013001`
- **Documentation**: [API-php/README.md](API-php/README.md)

### 📦 API-node (Node.js + Playwright)
Node.js-based scraper using Playwright for browser automation with TypeScript implementation.
- **Endpoint**: `/scrape?code={bacode}`
- **Health Check**: `/health`
- **Example**: `http://localhost:8081/scrape?code=013001`
- **Documentation**: [API-node/README.md](API-node/README.md)

### 🌐 Portal (Web Interface)
Interactive web portal for testing and using the scrapers.
- **Access**: `http://localhost:8082/`
- **Features**: 
  - Real-time testing with engine selection
  - JSON response viewer
  - **📊 Google Sheets Scraper Buttons** - Trigger EN/AR scrapers with live progress monitoring
  - Terminal-style interface with real-time updates

### 📊 Fetch-codes (Business Codes API)
RESTful API for business activity codes with MySQL database.
- **Health Check**: `http://localhost:8000/health`
- **Status**: `http://localhost:8000/status`
- **Features**: Auto-fetches codes from Qatar portal, stores in database

### 📊 Google Sheets Scraper (gsheet-scraper)
Backend API for triggering and monitoring Google Sheets scraping operations.
- **Trigger EN Scraper**: `http://localhost:8085/trigger-scrape-en.php`
- **Trigger AR Scraper**: `http://localhost:8085/trigger-scrape-ar.php`
- **Progress EN**: `http://localhost:8085/progress-en.php`
- **Progress AR**: `http://localhost:8085/progress-ar.php`
- **Features**: 
  - Scrapes Qatar investor website data to Google Sheets
  - Real-time progress monitoring via JSON files
  - Docker container-based execution
  - Integrated with Portal UI buttons

### 🔄 Scraper (Background Service)
Background service for continuous data collection and processing.

## 🚀 Quick Start

### **Docker Deployment (Recommended)**
For complete Docker deployment instructions, see [Docker.md](Docker.md).

```powershell
# One-command deployment to VPS
.\Deploy-to-Docker.ps1
```

### **Local Development**
```bash
# Clone repository
git clone https://github.com/dev-noaman/scrapers.git
cd scrapers

# Choose your implementation:
# Python + Playwright
cd API-php && docker compose up -d --build

# Node.js + Playwright
cd API-node && docker compose up -d --build

# Web Interface
cd Portal && docker compose up -d --build
```

## Features

✅ **Dual Implementation** - Choose between Python (Playwright) or Node.js (Playwright)  
✅ **Web Interface** - Interactive portal for testing and usage  
✅ **Google Sheets Integration** - Automated scraping to Google Sheets with EN/AR support  
✅ **Real-time Progress Monitoring** - Live updates for scraper operations  
✅ **JSON API** - Clean REST API responses  
✅ **Arabic Support** - Extracts both English and Arabic content  
✅ **Status Extraction** - Extracts activity status from details page  
✅ **Database Integration** - MySQL with business activity codes  
✅ **Docker Ready** - Complete containerization with one-command deployment  
✅ **Production Ready** - Health checks, auto-restart, proper timeouts  
✅ **Headless Browsers** - Chromium/Playwright included in containers  

## Requirements

### Docker Deployment (Recommended)
- Docker and Docker Compose
- 2GB+ RAM for VPS deployment
- Network access to ports 8000, 8080, 8081, 8082

### Local Development
- Python 3.11+ (for API-php)
- Node.js 18+ (for API-node)  
- PHP 8.2+ (for web interfaces)
- Docker Desktop (optional but recommended)

## Project Structure

```
scrapers/
├── Docker.md                # 🐳 Complete Docker deployment guide
├── Deploy-to-Docker.ps1     # 🚀 Automated deployment script
├── README.md               # 📋 Project overview (this file)
├── API-php/                 # Python + Playwright implementation
│   ├── scraper.py          # Main Python scraper
│   ├── scraper.php         # PHP API wrapper
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── README.md
├── API-node/                # Node.js + Puppeteer implementation  
│   ├── scraper.js          # Main Node.js scraper
│   ├── api.php             # PHP API wrapper
│   ├── package.json
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── README.md
├── Portal/                  # Web interface
│   ├── index.php           # Interactive web portal
│   ├── nginx.conf
│   ├── Dockerfile
│   └── docker-compose.yml
├── Fetch-codes/             # Business codes API + Database
│   ├── app.py              # FastAPI application
│   ├── init.sql            # Database schema
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── For Docker.md       # Detailed setup guide
├── docker-scraper/          # Background scraper service
│   ├── scrape-AR.py        # Arabic scraper
│   ├── scrape-EN.py        # English scraper
│   ├── scrape_codes.py     # Code fetcher
│   └── docker-compose.yml
└── scraper/                 # Legacy components
    └── Fetch-codes/
```

## 📋 API Reference

### Google Sheets Scraper Buttons

The Portal interface includes two buttons for triggering Google Sheets scraping operations:

#### **📊 SCRAPE_ENG Button**
Triggers the English scraper to extract data from the Qatar investor website and write to Google Sheets.

**How it works:**
1. Click the **SCRAPE_ENG** button in the Portal interface
2. Backend restarts the `GSHEET_SCRAPER_EN` Docker container
3. Python scraper reads activity codes from Google Sheets "Filter" workbook (EN worksheet)
4. For each code, scrapes English data from Qatar investor portal
5. Writes results back to Google Sheets
6. Real-time progress updates displayed in Portal terminal

**Progress Monitoring:**
- Updates every 3 seconds
- Shows current row / total rows
- Displays completion summary with total rows processed
- Error messages shown in red if issues occur

**Example Progress Output:**
```
[INFO] Starting EN scraper...
[INFO] Processing row 5/10
[INFO] Processing row 10/10
[SUCCESS] Scraping completed successfully - 10 rows processed
```

#### **📊 SCRAPE_AR Button**
Triggers the Arabic scraper with identical functionality for Arabic data.

**Backend API Endpoints:**

**Trigger EN Scraper:**
```bash
curl http://localhost:8085/trigger-scrape-en.php
```

**Response:**
```json
{
  "success": true,
  "message": "GSHEET_SCRAPER_EN container restarted successfully",
  "output": "GSHEET_SCRAPER_EN\n",
  "docker_path": "/usr/bin/docker"
}
```

**Check Progress:**
```bash
curl http://localhost:8085/progress-en.php
```

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

**Error Handling:**
- Missing Google credentials: Returns error message
- Docker container failure: Returns error with details
- Scraper runtime errors: Displayed in Portal with error status
- Button re-enables after completion or error for retry

**Requirements:**
- Google credentials file at `scrape-sw-gsheet/drive/google-credentials.json`
- Docker containers `GSHEET_SCRAPER_EN` and `GSHEET_SCRAPER_AR` configured
- Google Sheets "Filter" workbook with EN and AR worksheets
- Write access to `/tmp` for progress files

### Scraper API Response Format
All APIs return JSON responses in the following format:

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

### Field Descriptions
- **activity_code**: The business activity code
- **status**: Activity status (e.g., "Active", "Transferred", "Inactive", "Unknown")
- **name_en**: English name of the activity
- **name_ar**: Arabic name of the activity
- **locations**: Location details with fees
- **eligible**: Ownership eligibility information
- **approvals**: Required approvals and agencies

### Service Endpoints
| Service | Port | Endpoint | Description |
|---------|------|----------|-------------|
| API-php | 8080 | `/scraper.php?code={code}` | Python Playwright API |
| API-node | 8081 | `/scrape?code={code}` | Node.js Playwright API |
| Portal | 8082 | `/` | Web Interface |
| Fetch-codes | 8000 | `/health`, `/status` | Business Codes API |
| gsheet-scraper | 8085 | `/trigger-scrape-en.php`, `/trigger-scrape-ar.php` | Google Sheets Scraper API |

## License

MIT

## Author

Noaman - [GitHub](https://github.com/dev-noaman)

## Support

For issues and questions, please open an issue on [GitHub](https://github.com/dev-noaman/scrapers/issues).

---

## Legacy Scraper Documentation

The original scraper system (Selenium/Playwright with Google Sheets integration) documentation is preserved below for reference.

<details>
<summary>Click to expand legacy documentation</summary>

# Qatar Investor Portal Data Scraper (EN Version)

## System Overview

This automated scraper extracts business activity data from the Qatar Investor Portal (https://investor.sw.gov.qa/) and saves it to a Google Spreadsheet. The system extracts the following information for each business activity:

1. **Activity_Code**: The official activity code from the details page
2. **AR-Activity**: Arabic activity name/description (extracted by switching site language to Arabic)
3. **EN-Activity**: English activity name/description (extracted after switching back to English)
4. **Location Data**: Extracts location information including classifications, types, and fees
5. **Eligible Status**: Eligibility information for the activity
6. **Approvals Data**: All required approvals and associated agencies

### Technical Architecture

The system uses:
- **Selenium WebDriver** OR **Playwright**: For browser automation and interaction
  - `code.py`: Uses Selenium with Microsoft Edge WebDriver
  - `code_playwright.py`: Uses Playwright with Chromium (faster, more reliable)
- **Google Sheets API**: For saving extracted data to spreadsheets
- **Python**: As the programming language

[... rest of the original README content ...]

</details>
