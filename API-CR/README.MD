# Qatar Single Window - Company Search & Certificate Download

Automated tool for searching company details and downloading official CR/CP certificates from the Qatar Single Window investor portal.

## Features

- **Automated Login**: Headless browser automation for secure portal authentication
- **Company Search**: Query company details by CR (Commercial Registration) number
- **Certificate Download**: Download official PDF certificates:
  - **CR Certificate** - Commercial Registration Extract
  - **CP Certificate** - Commercial Permit Extract
- **Smart Request Caching**: Automatically reuses certificate requests for up to 6 days
  - **Independent Caching**: Separate request IDs for CR and CP to ensure correct downloads
  - Avoids creating suspicious multiple requests
  - Tracks request lifecycle (start/close times)
  - Auto-detects closed requests and creates new ones
- **Session Caching**: Stores login session for 1 hour to avoid repeated logins
- **Session Management**: Automatic token retrieval (`dpToken`, `accessId`, `LtpaToken2`)
- **Extended Timeouts**: 90-second timeout for slow CP certificate downloads
- **Unicode Support**: Proper Arabic text display in console output

## Prerequisites

- **Python 3.7+**
- **Valid Qatar Single Window investor account**

### Quick Setup (Windows)

```bash
setup.bat
```

### Manual Setup

```bash
pip install -r requirements.txt
playwright install chromium
```

## Configuration

Create a `.env` file in the `data/` directory:

```env
USER_QID=your_qid_here
USER_PASSWORD=your_password_here
```

> **Security Note:** Never commit `.env` to version control. It's already in `.gitignore`.

### Data Folder Structure

All configuration and cache files are stored in the `data/` directory:
- `data/.env` - Your credentials (required)
- `data/request_cache.json` - Certificate request cache (auto-created)
- `data/session_cache.json` - Login session cache (auto-created)

## Usage

### Basic Syntax

```bash
python auto_search_company.py <CR_NUMBER> [OPTIONS]
```

### Options

| Option | Description |
|--------|-------------|
| `--cr` | Download CR (Commercial Registration) certificate PDF |
| `--cp` | Download CP (Commercial Permit) certificate PDF |
| `-o, --output` | Output directory for PDF files (default: current directory) |

### Examples

```bash
# Search company info only
python auto_search_company.py 76053

# Search + download CR certificate
python auto_search_company.py 76053 --cr

# Search + download CP certificate
python auto_search_company.py 76053 --cp

# Search + download both certificates
python auto_search_company.py 76053 --cr --cp

# Download to specific folder
python auto_search_company.py 76053 --cr --cp -o ./certificates
```

### Sample Output

```
Launching browser to search for CR 76053...
Navigating to login page...
Waiting for login form to load...
Entering credentials...
Submitting login form...
Login successful! (URL: False, Cookie: True)
Token retrieved. Proceeding to API call for CR 76053...

========================================
CR Number    : 76053
English Name : Arafat Business Center
Arabic Name  : عرفات بيزنس سنتر
CP Number    : 116867
Status       : Active
Internal ID  : 1@76053
========================================

[*] Downloading Commercial Registration certificate for CR: 76053...
[*] Step 1: Saving certificate request...
[+] Received requestId: 2363585
[*] Waiting for certificate generation...
[*] Step 2: Downloading PDF...
PDF saved to: .\CR_76053.pdf
[+] Commercial Registration certificate downloaded successfully!
```

## How It Works

### Architecture Overview

```
┌─────────────────┐     ┌──────────────────────┐     ┌─────────────────┐
│  User Input     │────▶│  Playwright Browser  │────▶│  Portal Login   │
│  (CR Number)    │     │  (Headless Chrome)   │     │  (sw.gov.qa)    │
└─────────────────┘     └──────────────────────┘     └─────────────────┘
                                   │
                                   ▼
                        ┌──────────────────────┐
                        │  Extract Auth Tokens │
                        │  - dpToken           │
                        │  - accessId          │
                        │  - LtpaToken2        │
                        └──────────────────────┘
                                   │
                                   ▼
                        ┌──────────────────────┐
                        │  API Gateway         │
                        │  api.sw.gov.qa       │
                        └──────────────────────┘
                                   │
              ┌────────────────────┼────────────────────┐
              ▼                    ▼                    ▼
     ┌─────────────┐      ┌─────────────┐      ┌─────────────┐
     │ Search API  │      │ Save Cert   │      │ Download    │
     │ (Company)   │      │ Request     │      │ PDF         │
     └─────────────┘      └─────────────┘      └─────────────┘
```

### Process Flow

#### 1. Authentication
- Launch headless Chromium browser via Playwright
- Navigate to `https://investor.sw.gov.qa/wps/portal/investors/login/`
- Fill credentials and submit login form
- Wait for authentication cookies to be set

#### 2. Token Extraction
Extract required cookies from browser session:
- `dpToken` - Main API authentication token
- `accessId` - Access identifier for API requests
- `LtpaToken2` - IBM WebSphere session token (for PDF downloads)

#### 3. Company Search
Call search API to get company details:
- **Endpoint**: `https://api.sw.gov.qa/API/Private`
- **URI Header**: `api/sw-certificates/search-companies`
- **Returns**: Company name, CR/CP numbers, status, internal `sourceKeyId`

#### 4. Certificate Download (Two-Step Process)

**Step 1: Save Certificate Request**
- **URI**: `api/sw-certificates/save-cert-request`
- **Method**: POST
- **Payload**: Contains `sourceKeyId`, `crNo`, `cpNo`, and `requestType.lookupId`
- **Returns**: `requestId` for the certificate

**Step 2: Download PDF**
- **URI**: `api/sw-certificates/get-cert-contents`
- **Method**: GET
- **Header**: `requestId` from Step 1
- **Returns**: PDF binary data

## API Reference

### Certificate Type Lookup IDs

| Certificate Type | Lookup ID | Description |
|-----------------|-----------|-------------|
| CR Certificate | `1360041` | Commercial Registration Extract |
| CP Certificate | `1360040` | Commercial Permit Extract |

These are **static constants** - they define the certificate TYPE, not company-specific values.

### Key API Fields

| Field | Description | Example |
|-------|-------------|---------|
| `sourceKeyId` | Internal database identifier | `1@76053` |
| `crNo` | Commercial Registration number | `76053` |
| `cpNo` | Commercial Permit number | `116867` |
| `requestId` | Certificate request ID (from save-cert-request) | `2363585` |

### Request Headers

All API calls require these headers:
```
Authorization: Bearer {dpToken}
uri: {api-endpoint}
profileId: {QID}
QID: {QID}
accessId: {accessId}
requestSource: Angular
```

## Output Files

Downloaded certificates are saved as:
- `CR_{cr_number}.pdf` - Commercial Registration certificate
- `CP_{cr_number}.pdf` - Commercial Permit certificate

## Troubleshooting

### Login Issues

| Error | Solution |
|-------|----------|
| Login timed out | Check credentials in `data/.env` file |
| dpToken not found | Portal may be down, try again later |
| accessId not found | Session issue, restart script |

### Certificate Download Issues

| Error | Solution |
|-------|----------|
| Timeout 30000ms exceeded | Fixed! Script now uses 90s timeout |
| PDF shows "مرفوض" (Rejected) | Old issue - now uses correct sourceKeyId format |
| Empty/corrupt PDF | Cached request may be closed - script auto-creates new one |

### Cache Issues

| Issue | Solution |
|-------|----------|
| Want to force new request | Delete `data/request_cache.json` |
| Session expired | Delete `data/session_cache.json` to re-login |
| Corrupted cache | Delete JSON files in `data/` folder |

### Common Fixes

1. **Credentials error**: Verify `data/.env` file exists with correct `USER_QID` and `USER_PASSWORD`
2. **SSL errors**: Script uses `ignore_https_errors=True` by default
3. **Encoding issues**: Windows console configured for UTF-8 automatically
4. **CP timeout**: CP certificates take 8s to generate vs 5s for CR - now handled automatically

## Project Structure

```
api-cr-single/
├── auto_search_company.py   # Main script
├── data/                    # Configuration and cache folder
│   ├── .env                 # Credentials (not in git)
│   ├── request_cache.json   # Certificate request cache
│   └── session_cache.json   # Login session cache
├── .env.example             # Credentials template
├── requirements.txt         # Python dependencies
├── setup.bat                # Windows setup script
├── README.MD                # This file
└── *.pdf                    # Downloaded certificates
```

## Dependencies

- `playwright` - Browser automation
- `python-dotenv` - Environment variable management

## License

Internal use only - Qatar Single Window portal access required.
