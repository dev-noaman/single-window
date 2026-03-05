# CLAUDE.md

Review this plan thoroughly before making any code changes. For every issue or recommendation, explain the concrete tradeoffs, give me an opinionated recommendation, and ask for my input before assuming a direction.
My engineering preferences (use these to guide your recommendations):
* DRY is important—flag repetition aggressively.
* Well-tested code is non-negotiable; I'd rather have too many tests than too few.
* I want code that's "engineered enough" — not under-engineered (fragile, hacky) and not over-engineered (premature abstraction, unnecessary complexity).
* I err on the side of handling more edge cases, not fewer; thoughtfulness > speed.
* Bias toward explicit over clever.

1) Architecture review
Evaluate:
* Overall system design and component boundaries.
* Dependency graph and coupling concerns.
* Data flow patterns and potential bottlenecks.
* Scaling characteristics and single points of failure.
* Security architecture (auth, data access, API boundaries).

2) Code quality review
Evaluate:
* Code organization and module structure.
* DRY violations—be aggressive here.
* Error handling patterns and missing edge cases (call these out explicitly).
* Technical debt hotspots.
* Areas that are over-engineered or under-engineered relative to my preferences.

3) Test review
Evaluate:
* Test coverage gaps (unit, integration, e2e).
* Test quality and assertion strength.
* Missing edge case coverage—be thorough.
* Untested failure modes and error paths.

4) Performance review
Evaluate:
* N+1 queries and database access patterns.
* Memory-usage concerns.
* Caching opportunities.
* Slow or high-complexity code paths.

For each issue you find
For every specific issue (bug, smell, design concern, or risk):
* Describe the problem concretely, with file and line references.
* Present 2–3 options, including "do nothing" where that's reasonable.
* For each option, specify: implementation effort, risk, impact on other code, and maintenance burden.
* Give me your recommended option and why, mapped to my preferences above.
* Then explicitly ask whether I agree or want to choose a different direction before proceeding.

Workflow and interaction
* Do not assume my priorities on timeline or scale.
* After each section, pause and ask for my feedback before moving on.

BEFORE YOU START
Ask if I want one of two options:
1/ BIG CHANGE: Work through this interactively, one section at a time (Architecture → Code Quality → Tests → Performance) with at most 4 top issues in each section.
2/ SMALL CHANGE: Work through interactively ONE question per review section.

FOR EACH STAGE OF REVIEW: output the explanation and pros and cons of each stage's questions AND your opinionated recommendation and why, and then use AskUserQuestion. Also NUMBER issues and then give LETTERS for options, and when using AskUserQuestion make sure each option clearly labels the issue NUMBER and option LETTER so the user doesn't get confused. Make the recommended option always the 1st option.

---

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Qatar Investor Portal Scrapers - a multi-service web scraping platform that extracts business activity data from the Qatar Investor Portal (https://investor.sw.gov.qa/). Services: **api-scraper** (activity codes, Python + Scrapling + Playwright), **API-CR** (company search & certificate download), **Portal** (terminal-style UI), **scrape-sw-codes** (2800+ codes → PostgreSQL, hourly sync), **scrape-sw-gsheet** (Scrapling → Google Sheets), **officernd** (OfficeRnD API offline clone).

**Live Demo**: https://noaman.cloud

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Portal (8082)                           │
│                    PHP 8.4 + Tailwind CSS                       │
│                      Terminal-style UI                          │
└────────────────────────────┬────────────────────────────────────┘
                             │
                 ┌───────────▼───────────┐
                 │  api-scraper (8080)   │
                 │   Python + Scrapling  │
                 │   /scrape?code        │
                 └───────────────────────┘
                             │
                 ┌───────────▼───────────┐
                 │    API-CR (8086)      │
                 │   Python + Scrapling  │
                 │  /search, /download   │
                 └───────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                scrape-sw-codes (8084, HOST)                     │
│  PM2: php -S (port 8084) → discover_codes.py | fetch_codes_php  │
│  Two fetch methods: FETCH_CODES (Python httpx) + FETCH_CODES_3 (PHP curl) │
│  Host crontab: hourly smart sync (GMT+3) → Host PostgreSQL     │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                   scrape-sw-gsheet (8085)                       │
│  PHP web (trigger + progress) → Docker: GSHEET_SCRAPER_EN/AR     │
│  Scrapling + gspread → Google Sheets | trigger-scrape-en/ar.php  │
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
1. SSHs into VPS, pulls latest code from `dev-noaman/single-window` repo
2. Force-removes orphaned containers by name (prevents "container name already in use" conflicts)
3. Rebuilds all Docker services with `--no-cache`
4. Docker: api-scraper, API-CR, Portal, scrape-sw-gsheet (all with --no-cache rebuild)
5. Host: scrape-sw-codes (PM2 php -S 8084, pip httpx asyncpg, crontab hourly)
6. Host: officernd-api, officernd-bff via PM2
7. Nginx: copies noaman.cloud.nginx.conf, reloads

Manual trigger: Go to GitHub Actions > "Deploy to VPS" > Run workflow

**GitHub Secrets required**: `VPS_HOST`, `VPS_USER`, `VPS_PASS`, `GH_TOKEN`

### api-scraper (Python 3.12 + Scrapling + Playwright)
```bash
cd api-scraper
pip install -r requirements.txt
python -m playwright install chromium
# CLI: python scraper.py --code 013001 --json
# HTTP: python server.py  # serves on 8080
# Docker: docker-compose up -d --build
```

### API-CR (Company Search & Certificate Download)
```bash
cd API-CR
pip install -r requirements.txt
python -m playwright install chromium
# Credentials: data/.env (USER_QID, USER_PASSWORD)
# HTTP: python api_server.py  # serves on 8086
# Docker: docker-compose up -d --build
```

### Portal
```bash
cd Portal
docker-compose up -d --build
# Access at http://localhost:8082
```

### scrape-sw-codes (runs on host, not Docker)
```bash
# VPS: PM2 php -S on 8084, crontab hourly (cron-scheduler.sh)
# Local: docker-compose up -d (optional)
# Trigger: curl http://localhost:8084/trigger-fetch-codes.php
# PHP fallback: curl http://localhost:8084/trigger-fetch-codes-php.php
# Check: curl http://localhost:8084/check-update.php
```

### scrape-sw-gsheet (Docker: EN/AR scrapers + PHP web)
```bash
cd scrape-sw-gsheet
# Requires: drive/google-credentials.json
# Docker: docker-compose up -d --build
# Triggers: /trigger-scrape-en.php, /trigger-scrape-ar.php
# Progress: /progress-en.php, /progress-ar.php
# Containers: SW_GSHEET, GSHEET_SCRAPER_EN, GSHEET_SCRAPER_AR, GSHEET_SCRAPER_WEB
```

## Key Service Endpoints

| Service | Port | Endpoint | Description |
|---------|------|----------|-------------|
| api-scraper | 8080 | `/scrape?code={code}` | Python Scrapling scraper (replaces API-php + API-node) |
| api-scraper | 8080 | `/health` | Health check |
| API-CR | 8086 | `/search?cr={cr_number}` | Company search by CR (single result) |
| API-CR | 8086 | `/search?q={query}` | Search by CR, EN name, or AR name (multiple results) |
| API-CR | 8086 | `/download?cr={cr}&type={CR\|BOTH}` | Download certificate PDFs |
| API-CR | 8086 | `/health` | Health check |
| Portal | 8082 | `/` | Web interface |
| scrape-sw-codes | 8084 | `/trigger-fetch-codes.php` | Trigger Python fetch (FETCH_CODES) |
| scrape-sw-codes | 8084 | `/trigger-fetch-codes-php.php` | Trigger PHP fetch (FETCH_CODES_3, fallback) |
| scrape-sw-codes | 8084 | `/progress.php` | Real-time fetch progress |
| scrape-sw-codes | 8084 | `/check-update.php` | Smart update checker |
| scrape-sw-gsheet | 8085 | `/trigger-scrape-en.php` | Trigger EN scraper (restarts GSHEET_SCRAPER_EN) |
| scrape-sw-gsheet | 8085 | `/trigger-scrape-ar.php` | Trigger AR scraper (restarts GSHEET_SCRAPER_AR) |
| scrape-sw-gsheet | 8085 | `/progress-en.php` | EN scraper progress |
| scrape-sw-gsheet | 8085 | `/progress-ar.php` | AR scraper progress |
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

## Nginx Routing (noaman.cloud)

| Path | Proxies to | Service |
|------|-------------|---------|
| `/` | 8082 | Portal |
| `/api-scraper/` | 8080 | api-scraper |
| `/api-cr/` | 8086 | API-CR (fallback; Portal uses cr.noaman.cloud in prod) |
| `/sw-codes/` | 8084 | scrape-sw-codes (PM2 PHP) |
| `/gsheet-scraper/` | 8085 | scrape-sw-gsheet (PHP web container) |
| `/officernd/` | 8088 | officernd-bff |
| `/officernd-api/` | 8087 | officernd-api |
| `/health` | 8082/health | Portal health |

**cr.noaman.cloud** (separate server block): Direct proxy to 8086. Bypasses Cloudflare for SCRAPE_CR (avoids 524 timeout). DNS: A → VPS IP, grey cloud. SSL: deploy runs certbot; if failed: `certbot certonly --webroot -w /var/www/html -d cr.noaman.cloud`

## Technology Stack

- **api-scraper**: Python 3.12, Scrapling (StealthyFetcher), Playwright Chromium, built-in HTTP server
- **API-CR**: Python 3.12, Scrapling (StealthyFetcher), Playwright Chromium, HTTP server (data/.env for credentials)
- **Portal**: PHP 8.4, Tailwind CSS, Nginx
- **scrape-sw-codes**: Python (httpx, asyncpg) + PHP curl (fetch_codes_php.php), PostgreSQL 16, PM2 (host service)
- **scrape-sw-gsheet**: Python 3.12, Scrapling (StealthyFetcher), Playwright, gspread, oauth2client, PHP 8.2-CLI (trigger/progress web)
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

VPS path `/root/scrapers/`. Docker: `API-SCRAPER`, `API-CR`, `PORTAL`, `SW_GSHEET`, `GSHEET_SCRAPER_EN`, `GSHEET_SCRAPER_AR`, `GSHEET_SCRAPER_WEB`. Host (PM2): `sw-codes-web` (port 8084), `officernd-api` (8087), `officernd-bff` (8088).

## Key Files

- **api-scraper/scraper.py**: Main Python Scrapling scraper (replaces API-php/scraper.py + API-node/FastQatarScraper.ts)
- **api-scraper/server.py**: Python HTTP server (replaces API-php/scraper.php + API-node/server.js)
- **API-CR/auto_search_company.py**: Company search and certificate download (`run_company_search` for single CR, `search_companies_by_query` for name/CR multi-result search)
- **API-CR/api_server.py**: HTTP API wrapper for certificate downloads and company search
- **Portal/index.php**: Terminal-style UI — CODE (api-scraper), FETCH_CODES, FETCH_CODES_3, SCRAPE_ENG (gsheet), SCRAPE_CR (api-cr modal: CR/EN/AR search, certificate download), OfficeRnD link
- **scrape-sw-codes/discover_codes.py**: Business codes fetcher (httpx, 2800+ codes, three-strategy: last-page-first / full no-skip / full with smart-skip)
- **scrape-sw-codes/fetch_codes_php.php**: Pure PHP fetch (curl, no Python) — fallback when Python has SSL issues
- **scrape-sw-codes/trigger-fetch-codes.php**: Trigger Python fetch — resets progress, runs discover_codes.py, returns logs
- **scrape-sw-codes/trigger-fetch-codes-php.php**: Trigger PHP fetch — runs fetch_codes_php.php
- **scrape-sw-codes/progress.php**: Real-time progress — reads `/tmp/fetch_progress.json`
- **scrape-sw-gsheet/trigger-scrape-en.php**: Restarts GSHEET_SCRAPER_EN container
- **scrape-sw-gsheet/trigger-scrape-ar.php**: Restarts GSHEET_SCRAPER_AR container
- **scrape-sw-gsheet/progress-en.php**, **progress-ar.php**: Scraper progress from /tmp
- **scrape-sw-gsheet/scrape-EN.py**, **scrape-AR.py**: Scrapling + gspread, write to Google Sheets "Filter"
- **scrape-sw-gsheet/progress_writer.py**: Real-time progress for EN/AR scrapers
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
- **tests/fetch-codes.spec.js**: Playwright e2e tests for FETCH_CODES and FETCH_CODES_3 (against live noaman.cloud)

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
- **Deploy stale-process kill**: Uses `pgrep` + `kill` with PID exclusion (`$$`) — **never** `pkill -f`, which matches the deploy script itself and causes SIGTERM 143. Pattern: `for pid in $(pgrep -f '...'); do [ "$pid" != "$MY_PID" ] && kill -TERM "$pid"; done`
- **VPS repo**: `dev-noaman/single-window` (GitHub). VPS path: `/root/scrapers/`. Workflow auto-sets remote URL to prevent stale repo issues.
- **Portal Dockerfile** is written directly via heredoc in the workflow (VPS previously had a stale nginx:alpine Dockerfile from old `dev-noaman/scrapers` repo)
- **`scripts/Deploy-to-Docker.ps1`** exists for manual PowerShell deployment but paths assume running from project root (currently broken — use GitHub Actions instead)
- **officernd-api** runs as PM2 host service (`uvicorn api.main:app --host 0.0.0.0 --port 8087`), config/.env is preserved across deploys
- **officernd-bff** connects to officernd API at `http://localhost:8087` (set in `.env` as `OFFICERND_API_URL`)
- **officernd-bff** Vite `base: '/officernd/'` — all frontend assets and API calls are prefixed with `/officernd` to work behind nginx reverse proxy at `noaman.cloud/officernd/`
- **scrape-sw-codes** runs entirely on the host (no Docker). PM2 `sw-codes-web` serves PHP on port 8084. `discover_codes.py` runs directly via `python3`. Host crontab for hourly sync. Uses host PostgreSQL (`codesdb` on `localhost:5432`). Docker compose file kept for local dev only.
- **API-CR** requirements.txt uses minimum version pins (`>=`), not exact pins — exact pins break `--no-cache` builds when PyPI versions change
- **Portal landing page**: Only `index.php` (terminal-style) should be served. `index.html` is gitignored and excluded via `.dockerignore`.

## scrape-sw-codes Features

- **Smart sync**: Hourly cron checks MOCI API `totalElements` vs DB `COUNT(*)` (fetches only 1 record from API). Only triggers full fetch if counts differ (either direction: new codes added or codes removed). Skips with "Already up to date" if counts match.
- **Hourly schedule**: Host crontab runs `cron-scheduler.sh` every hour (`0 * * * *`, Qatar timezone GMT+3).
- **Three-strategy fetch** (`discover_codes.py`): Peeks at API page 1 to get `totalElements`, then picks the optimal strategy:
  - `api > db` (codes added): **Last-page-first** — checks the last page for new codes (typically appended to the end). If found, inserts only that page (fast path, ~2 pages instead of ~29). If not on last page, falls back to full fetch with smart skip disabled.
  - `api < db` (codes removed): Full fetch with smart skip **disabled** — must scan every page to build complete API code set, then deletes codes from DB that no longer exist in the API.
  - `api == db` (data changes only): Full fetch with smart skip enabled — bails after 3 consecutive no-change pages.
- **Helper functions**: `fetch_single_page()` (single HTTP page fetch + parse), `save_page_to_db()` (DB insert/update/skip with change detection). Both used by `fetch_all_activities()` and the fast-path in `main()`.
- **Change detection**: `discover_codes.py` fetches existing records with all fields (industry_id, name_en, name_ar, description_en) and compares tuple values before writing. Unchanged records are skipped (no DB write, no `updated_at` bump). Progress tracks new/updated/skipped counts.
- **Stale code deletion**: After a complete fetch (all pages successfully processed), compares all DB codes against all API codes and deletes any that no longer exist in the API. Safety guard: deletion only runs when `fetch_complete=True` — skipped on errors, exceptions, smart-skip (incomplete data), or fast-path last-page-only syncs. Prints which codes were deleted.
- **Real-time progress**: `discover_codes.py` writes `/tmp/fetch_progress.json` in real-time. Portal polls `progress.php` for live page count, new codes, updated codes, and skipped (unchanged) codes.
- **Host architecture**: Runs directly on the VPS (no Docker). PM2 serves PHP files via `php -S` on port 8084. `trigger-fetch-codes.php` runs `python3 discover_codes.py` as a background process. Includes: duplicate-run prevention (`pgrep`), progress file reset to `"pending"` before launch, process health check with log tail on failure. Non-JSON API responses are logged with Content-Type and first 300 chars for debugging.
- **Portal fetch methods**: Two buttons — **FETCH_CODES** (primary: Python httpx, smart check-first) and **FETCH_CODES_3** (fallback: pure PHP curl). Recommended: use FETCH_CODES first; use FETCH_CODES_3 if Python/SSL fails.
- **Portal monitoring guards**: `monitorFetchProgress()` requires seeing at least one `"running"` or `"starting"` status before accepting `"completed"` (`seenRunning` flag). Stuck-timeout: if still `"pending"` after 40 polls (~2 min), shows an error. Crash/error logs from trigger endpoints are displayed in the terminal.
- **Portal error surfacing**: `Portal/index.php` fetch-codes flow reads the JSON body from `trigger-fetch-codes.php` even on non-2xx responses, so the real error is shown in the terminal instead of a generic "HTTP Error: 500".

## scrape-sw-gsheet Features

- **Containers**: SW_GSHEET (scrape_codes.py), GSHEET_SCRAPER_EN (scrape-EN.py), GSHEET_SCRAPER_AR (scrape-AR.py), GSHEET_SCRAPER_WEB (PHP trigger + progress on 8085)
- **Credentials**: `drive/google-credentials.json` (Google Service Account) required
- **Target**: Google Sheets "Filter" worksheet, EN and AR tabs
- **Trigger**: PHP restarts container; scraper writes progress to /tmp; Portal polls progress-en.php / progress-ar.php
- **Scrapling**: StealthyFetcher + Playwright for Qatar investor portal, gspread for Sheets API

## API-CR Features

- **Credentials**: `data/.env` with USER_QID, USER_PASSWORD (Qatar ID portal login)
- **Search**: Single CR (`/search?cr=`), or multi-result by query (`/search?q=`) — CR number, EN name, or AR name
- **Download**: PDF certificates (CR only or CR+CP) via `/download?cr=&type=&format=base64`
- **Cache**: request_cache.json, session_cache.json in data/ (6-day validity)

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

## Legacy / Deprecated

- **API-php**, **API-node**: Replaced by api-scraper. Deploy removes API-PHP, API-NODE containers.
