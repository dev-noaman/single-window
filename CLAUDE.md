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
│                scrape-sw-codes (8084, HOST)                     │
│  PM2: php -S (port 8084) → python3 discover_codes.py           │
│  Host crontab: hourly smart sync (GMT+3)                       │
│  → Host PostgreSQL (codesdb)                                   │
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
4. Deploys scrape-sw-codes on host (PM2 + php-cli + pip + crontab)
5. Redeploys officernd host services via PM2
6. Reloads host nginx config

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

### scrape-sw-codes (runs on host, not Docker)
```bash
# VPS: PM2 serves PHP on port 8084, crontab runs hourly sync
# Local dev: docker-compose up -d --build
# Trigger: curl http://localhost:8084/trigger-fetch-codes.php
# Check: curl http://localhost:8084/check-update.php
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
- **scrape-sw-codes**: Python (aiohttp, asyncpg), PHP-CLI, PostgreSQL 16, PM2 (host service)
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
- `SW_GSHEET`
- `sw-codes-web` (PHP host service via PM2, php-cli on port 8084)
- `officernd-api` (Python host service via PM2, uvicorn on port 8087)
- `officernd-bff` (Node.js host service via PM2, NestJS on port 8088)

## Key Files

- **API-node/src/scrapers/FastQatarScraper.ts**: Main TypeScript scraper implementation
- **API-node/server.js**: HTTP server wrapper
- **API-php/scraper.py**: Main Python async scraper
- **API-CR/auto_search_company.py**: Company search and certificate download (`run_company_search` for single CR, `search_companies_by_query` for name/CR multi-result search)
- **API-CR/api_server.py**: HTTP API wrapper for certificate downloads and company search
- **Portal/index.php**: Web portal with engine selection and CR search/download modal (supports search by CR number, English name, or Arabic name with multi-result selection)
- **scrape-sw-codes/discover_codes.py**: Business codes fetcher (2800+ codes, three-strategy: last-page-first / full no-skip / full with smart-skip)
- **scrape-sw-codes/trigger-fetch-codes.php**: Trigger endpoint — resets progress file, restarts container, checks for crash and returns logs
- **scrape-sw-codes/progress.php**: Real-time progress endpoint — reads `/tmp/fetch_progress.json`
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
- **Portal monitoring guards**: `monitorFetchProgress()` requires seeing at least one `"running"` or `"starting"` status before accepting `"completed"` (`seenRunning` flag). Also has a 30s stuck-timeout: if still `"pending"` after 10 polls, shows an error. Crash/error logs from `trigger-fetch-codes.php` are displayed directly in the terminal.
- **Portal error surfacing**: `Portal/index.php` fetch-codes flow reads the JSON body from `trigger-fetch-codes.php` even on non-2xx responses, so the real error is shown in the terminal instead of a generic "HTTP Error: 500".

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
