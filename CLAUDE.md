# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Qatar Investor Portal Scrapers - a multi-service web scraping platform that extracts business activity data from the Qatar Investor Portal (https://investor.sw.gov.qa/). The system has dual scraper implementations (Python and Node.js), a web portal interface, and background services for Google Sheets integration and business activity codes management.

**Live Demo**: https://noaman.cloud

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Portal (8082)                           │
│                    PHP 8.4 + Tailwind CSS                       │
│              Terminal-style UI with engine selection            │
└─────────────────┬───────────────────────┬───────────────────────┘
                  │                       │
        ┌─────────▼─────────┐   ┌─────────▼─────────┐
        │   API-php (8080)  │   │  API-node (8081)  │
        │ Python+Playwright │   │   TS + Playwright │
        │ /scraper.php?code │   │   /scrape?code    │
        └───────────────────┘   └───────────────────┘
                                          │
                              ┌───────────▼───────────┐
                              │    API-CR (8086)      │
                              │  Python + Playwright  │
                              │  /search, /download   │
                              └───────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    scrape-sw-codes (8084)                       │
│  SW_CODES_WEB (PHP) → SW_CODES_PYTHON → Host PostgreSQL (codesdb) │
│  SW_CODES_CRON smart sync every hour (GMT+3)                   │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                   scrape-sw-gsheet (8085)                       │
│  EN scrapers → Google Sheets via API                            │
│  /trigger-scrape-en.php                                         │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│               officernd (8087 API + 8088 BFF)                   │
│  OFFICERND_API (FastAPI+Uvicorn) → Host PostgreSQL              │
│  officernd-bff (NestJS+React) → Terminal-style sync UI          │
│  580 companies x 37 endpoints → offline clone                   │
└─────────────────────────────────────────────────────────────────┘
```

## Build and Run Commands

### Automated Deployment (GitHub Actions)
Push to `main` triggers `.github/workflows/deploy.yml` which:
1. SSHs into VPS, pulls latest code from `dev-noaman/single` repo
2. Force-removes orphaned containers by name (prevents "container name already in use" conflicts)
3. Rebuilds all Docker services with `--no-cache`
4. Redeploys officernd host services via PM2
5. Reloads host nginx config

Manual trigger: Go to GitHub Actions > "Deploy to VPS" > Run workflow

**GitHub Secrets required**: `VPS_HOST`, `VPS_USER`, `VPS_PASS`, `GH_TOKEN`

### API-node (TypeScript + Playwright)
```bash
cd API-node
npm install
npm run build          # Compile TypeScript to dist/
npm start              # Run server.js
npm run dev            # Build + start combined
npm run test           # Run test-json-only.js
# Docker: docker-compose up -d --build
```

### API-php (Python + Playwright)
```bash
cd API-php
pip install -r requirements.txt
playwright install chromium
python scraper.py --code 013001 --json
# Docker: docker-compose up -d --build
```

### Portal
```bash
cd Portal
docker-compose up -d --build
# Access at http://localhost:8082
```

### scrape-sw-codes
```bash
cd scrape-sw-codes
docker-compose up -d --build
# Web UI: http://localhost:8084
# Trigger: curl http://localhost:8084/trigger-fetch-codes.php
# Check cron status: ./check-cron-today.sh
```

## Key Service Endpoints

| Service | Port | Endpoint | Description |
|---------|------|----------|-------------|
| API-php | 8080 | `/scraper.php?code={code}` | Python Playwright scraper |
| API-node | 8081 | `/scrape?code={code}` | Node.js TypeScript scraper |
| API-node | 8081 | `/health` | Health check |
| API-CR | 8086 | `/search?cr={cr_number}` | Company search by CR (single result) |
| API-CR | 8086 | `/search?q={query}` | Search by CR, EN name, or AR name (multiple results) |
| API-CR | 8086 | `/download?cr={cr}&type={CR\|BOTH}` | Download certificate PDFs |
| API-CR | 8086 | `/health` | Health check |
| Portal | 8082 | `/` | Web interface |
| scrape-sw-codes | 8084 | `/trigger-fetch-codes.php` | Trigger code fetch |
| scrape-sw-codes | 8084 | `/check-update.php` | Smart update checker |
| scrape-sw-gsheet | 8085 | `/trigger-scrape-en.php` | Trigger EN scraper |
| officernd API | 8087 | `/health` | OfficeRnD API clone |
| officernd BFF | 8088 | `/` | OfficeRnD sync web UI (NestJS+React) |
| officernd BFF | 8088 | `/api/officernd/status` | Sync status (cached 5s) |
| officernd BFF | 8088 | `/api/officernd/progress` | Sync progress (cached 1s) |
| officernd BFF | 8088 | `/api/officernd/companies` | Per-company sync results |
| officernd BFF | 8088 | `/api/officernd/phases` | Phase progress tracker (cached 2s) |
| officernd BFF | 8088 | `/api/officernd/sync/run` | Trigger sync (POST, modes: full/incremental/smart) |
| officernd BFF | 8088 | `/api/officernd/export` | Export DB as pg_dump SQL backup |

## API Response Format

All scrapers return:
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

## Technology Stack

- **API-node**: TypeScript, Node.js 20, Playwright, Winston (logging)
- **API-php**: Python 3.11, Playwright, PHP-FPM, Nginx
- **API-CR**: Python 3.12, Playwright, HTTP server
- **Portal**: PHP 8.4, Tailwind CSS, Nginx
- **scrape-sw-codes**: Python, PostgreSQL 16, PHP, Alpine Linux (cron)
- **scrape-sw-gsheet**: Python, Google Sheets API
- **officernd-api**: Python 3.10+, FastAPI, Uvicorn, SQLAlchemy, asyncio
- **officernd-bff**: NestJS 10, React 18, Vite, TypeScript, cache-manager

## Host PostgreSQL (shared, no conflict)

Single PostgreSQL instance on the host (port 5432). Two separate databases:

| Service           | Database   | User          | Purpose                    |
|-------------------|------------|---------------|----------------------------|
| officernd         | `officernd`| `officernd_user` | OfficeRnD sync data     |
| scrape-sw-codes   | `codesdb`  | `codesuser`   | Business activity codes   |

Docker containers connect via `host.docker.internal:5432`. Host services (officernd-api, officernd-bff via PM2) use `localhost:5432`. Deploy-to-Docker.ps1 auto-replaces `host.docker.internal` with `localhost` in .env for host services.

## Container Names

All containers follow naming pattern for VPS path `/root/scrapers/`:
- `API-PHP`, `API-NODE`, `API-CR`, `PORTAL`
- `SW_CODES_PYTHON`, `SW_CODES_WEB`, `SW_CODES_CRON` (PostgreSQL on host, not in Docker)
- `SW_GSHEET`
- `officernd-api` (Python host service via PM2, uvicorn on port 8087)
- `officernd-bff` (Node.js host service via PM2, NestJS on port 8088)

## Key Files

- **API-node/src/scrapers/FastQatarScraper.ts**: Main TypeScript scraper implementation
- **API-node/server.js**: HTTP server wrapper
- **API-php/scraper.py**: Main Python async scraper
- **API-CR/auto_search_company.py**: Company search and certificate download (`run_company_search` for single CR, `search_companies_by_query` for name/CR multi-result search)
- **API-CR/api_server.py**: HTTP API wrapper for certificate downloads and company search
- **Portal/index.php**: Web portal with engine selection and CR search/download modal (supports search by CR number, English name, or Arabic name with multi-result selection)
- **scrape-sw-codes/discover_codes.py**: Business codes fetcher (2800+ codes)
- **scrape-sw-codes/Dockerfile.cron**: Cron scheduler (hourly smart sync)
- **scrape-sw-codes/cron-scheduler.sh**: Smart sync script (checks API vs DB count before fetching)
- **scrape-sw-codes/check-update.php**: Lightweight API vs DB comparison (fetches 1 record)
- **officernd/bff/src/main.ts**: NestJS BFF bootstrap (port 8088)
- **officernd/bff/src/officernd/officernd.service.ts**: Sync status/progress/trigger with caching
- **officernd/bff/src/officernd/officernd.controller.ts**: REST API endpoints
- **officernd/bff/frontend/src/App.tsx**: React terminal-style UI with SHOW/TERMINAL toggle
- **officernd/bff/frontend/src/components/ResultsTable.tsx**: Per-company sync results table (includes PhaseTracker)
- **officernd/bff/frontend/src/components/PhaseTracker.tsx**: Phase progress bars with expandable endpoint details
- **officernd/bff/frontend/src/api/officernd.ts**: API types and fetch functions for all BFF endpoints
- **officernd/api/routes/__init__.py**: Shared helpers (paginated_query, get_single, apply_filters)
- **officernd/api/sync_routes.py**: FastAPI sync endpoints (status, progress, phases, run, companies, export)
- **officernd/sync/run_by_company.py**: 3-phase async sync orchestrator

## Build and Run: officernd-bff

```bash
cd officernd/bff
npm install
cd frontend && npm install && npm run build && cd ..  # Build React → public/
npm run build                                          # Build NestJS → dist/
npm run start:prod                                     # Run on port 8088
# Access at http://localhost:8088
# Requires OFFICERND_API running on port 8087 (BFF proxies to it)
```

## Deployment Notes

- **GitHub Actions** (`.github/workflows/deploy.yml`) is the primary deployment method — triggers on push to `main`
- **VPS repo**: `dev-noaman/single` (GitHub). VPS path: `/root/scrapers/`. Workflow auto-sets remote URL to prevent stale repo issues.
- **Portal Dockerfile** is written directly via heredoc in the workflow (VPS previously had a stale nginx:alpine Dockerfile from old `dev-noaman/scrapers` repo)
- **`scripts/Deploy-to-Docker.ps1`** exists for manual PowerShell deployment but paths assume running from project root (currently broken — use GitHub Actions instead)
- **officernd-api** runs as PM2 host service (`uvicorn api.main:app --host 0.0.0.0 --port 8087`), config/.env is preserved across deploys
- **officernd-bff** connects to officernd API at `http://localhost:8087` (set in `.env` as `OFFICERND_API_URL`)
- **officernd-bff** Vite `base: '/officernd/'` — all frontend assets and API calls are prefixed with `/officernd` to work behind nginx reverse proxy at `noaman.cloud/officernd/`
- **scrape-sw-codes** uses host PostgreSQL (`codesdb` on port 5432), Docker maps web UI to external port `8084`
- **Portal landing page**: Only `index.php` (terminal-style) should be served. `index.html` is gitignored and excluded via `.dockerignore`.

## scrape-sw-codes Features

- **Smart sync**: Hourly cron checks MOCI API `totalElements` vs DB `COUNT(*)` (fetches only 1 record from API). Only triggers full fetch if counts differ. Skips with "Already up to date" if no new codes.
- **Hourly schedule**: `SW_CODES_CRON` runs `cron-scheduler.sh` every hour (`0 * * * *`, Qatar timezone GMT+3). Previously daily at 8 AM.
- **Full fetch**: Paginates MOCI API (100 items/page, ~29 pages, ~2800+ codes). For each code: INSERT if new, UPDATE if exists. Smart skip after 3 consecutive unchanged pages.
- **Real-time progress**: `discover_codes.py` writes `/tmp/fetch_progress.json` in real-time. Portal polls `progress.php` for live page count, new codes, and updated codes.
- **Container architecture**: `SW_CODES_PYTHON` runs once and exits (`restart: "no"`). Triggered by `trigger-fetch-codes.php` which calls `docker restart SW_CODES_PYTHON`.

## OfficeRnD Sync Features

- **Smart sync**: FETCH button uses "smart" mode — gets synced IDs from DB, paginates live OfficeRnD API (`?status=active&$limit=50`, ~12 pages, ~1s), compares IDs to find exact new companies. If none new, reports "Already up to date". If new found, saves them to DB and syncs only their 13 per-company endpoints (no Phase 1 re-fetch).
- **Auto-run**: On page load, automatically triggers smart sync check if idle or interrupted. No manual click needed to verify data is current.
- **Auto-sync scheduler**: Background thread runs smart sync every hour automatically (no browser needed). Skips if a sync is already running. Started at API startup via `start_auto_sync_scheduler()` in `sync_routes.py`.
- **Stale progress reset**: On API startup, `reset_stale_progress()` resets any leftover "running" progress to "idle" (no sync thread exists at startup). Prevents UI from reconnecting to a dead sync.
- **Interrupted sync recovery**: If sync was interrupted (server restart/crash), UI runs smart check (not full re-sync) on next page load. Finds only new companies and syncs those.
- **Export**: EXPORT button downloads a full `pg_dump` SQL backup (~66MB) with schema + data. Real browser download with `Content-Disposition: attachment`.
- **Background sync**: Sync runs in a daemon thread on the server, survives browser close. UI auto-reconnects to running sync on page load.
- **Duplicate prevention**: Server rejects new sync if one is already running (`status: already_running`)
- **SHOW/TERMINAL toggle**: UI switches between terminal log view and per-company results table
- **PhaseTracker**: Shows 2 sync phases as progress bars above the results table. Phase 1 "Sync All Data" covers global endpoints (22) + all active companies (580) — complete only when every company is synced. Phase 2 "Dependent" covers payment docs (~14,828) + assignments (~820) with SyncJob tracking for real-time counts (updates every 10 items). Clicking either phase expands endpoint details. Phase 1 also shows a globals sub-indicator (e.g., "Global endpoints: 22/22 ✓"). Phase 2 correctly shows "completed" even while Phase 1 re-runs. Polls every 3s during sync.
- **ResultsTable**: Shows per-company sync results: company name, status, endpoints completed/failed, records fetched/upserted, match check
- **Auto-updating StatusBar**: Companies count and Last Sync auto-refresh every 5s while sync is running
- **Per-company endpoints**: 13 endpoints per company (max 500 pages each); 22 global (no page cap); 2 dependent (0.1s delay between requests); 37 total synced + 4 API-only. Phase 1 = global + companies. Backfill = new endpoints for old companies. Phase 3 = dependent (skips if already completed).
- **Backfill**: Automatically syncs new endpoints for companies synced with older code (detects companies with < 13 endpoints)
- **Progress polling**: 1.5s interval for near-realtime progress updates
- **API coverage**: 80/80 GET endpoints from OfficeRnD reference docs implemented (100%). 63 write endpoints (POST/PUT/DELETE) intentionally skipped (read-only clone).

## TypeScript Configuration (API-node)

- Target: ES2022, Module: CommonJS
- Strict mode enabled, source maps enabled
- Output: `./dist`, no unused variables allowed
- Compile with `npm run build` before running
