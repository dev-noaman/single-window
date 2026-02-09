# OfficeRnD API Offline Clone

## Project Purpose
Sync ALL data from OfficeRnD API (580 active companies x 37 endpoints) to local PostgreSQL database + organized JSON files for offline access. Full pagination fetches every record. NO company is skipped. NO endpoint is skipped. NO data is lost.

## Architecture

```
Phase 1: Global endpoints (22) -> fetches ALL pages -> /data/global/
    |       Populates companies table (2,180 total, 580 active)
    v
Phase 2: Per-company endpoints (580 active companies x 13 endpoints)
    |       Company IDs loaded from DB after Phase 1, filtered by status='active'
    |       Max 500 pages per endpoint per company (safety cap)
    v
Backfill: Syncs new endpoints for companies synced with older code
    |       Detects companies with < 13 endpoints, syncs only missing ones
    v
Phase 3: Dependent endpoints (require parent IDs from Phase 1/2)
    |   +-- payments/{id}/documents (for every payment in DB, ~14,828)
    |   +-- assignments?membership={id} (for every membership in DB, ~1,586)
    |   +-- SyncJob tracking for real-time UI progress (updates every 10 items)
    |   +-- Skip logic: skips if SyncJob records already completed
    |   +-- 0.1s delay between requests to avoid 429 rate limits
    v
sync/pipeline.py (ETL per endpoint)
    |
    +-- Fetch (api/client.py -> asyncio.to_thread)
    |       Cursor-based pagination via $cursorNext (API v2)
    |       Rate limited via asyncio.Semaphore
    |       Retry with exponential backoff (5 attempts)
    |       Deduplicates overlapping pagination results
    |       Heartbeat callback keeps progress fresh during long fetches
    |
    +-- Save (parallel via asyncio.gather)
        +-- JSON -> /data/company_{id}/endpoint.json
        +-- DB  -> PostgreSQL (batch upsert, 100 rows/batch)
```

## Key Files

| File | Purpose |
|------|---------|
| `config/ID.csv` | 669 MEMBER IDs (legacy, NOT used for company sync) |
| `config/.env` | OAuth credentials + DB URL |
| `sync/run_by_company.py` | Main entry point, 3-phase async orchestrator |
| `sync/pipeline.py` | ETL: fetch -> save JSON + DB in parallel |
| `sync/json_writer.py` | Organized JSON file storage |
| `sync/writer.py` | DB upsert with batch support + endpoint->model mapping |
| `sync/fetcher.py` | Paginated API fetcher with cursor support |
| `api/client.py` | HTTP client with OAuth + auto token refresh |
| `api/config.py` | Config from config/.env |
| `api/models.py` | Endpoint definitions (43 endpoints in 6 groups) |
| `api/routes/__init__.py` | Shared helpers: paginated_query, get_single, apply_filters |
| `db/models.py` | SQLAlchemy ORM models (45 tables, ALL columns nullable) |
| `db/engine.py` | PostgreSQL connection pool |

## Important: Company IDs & Pagination

**ID.csv contains 669 MEMBER IDs, NOT company IDs.** Company IDs come from the API.

- Total companies in API: **2,180** (active: 580, former: 932, drop-in: 336, inactive: 282, lead: 49, pending: 1)
- Phase 2 defaults to **active companies only** (580)
- Company IDs are loaded from the database after Phase 1 syncs the global `/companies` endpoint

**Pagination**: OfficeRnD API v2 uses cursor-based pagination with `$cursorNext` query parameter (note the `$` prefix). Response body returns `cursorNext` (no `$`). Default/max page size is 50. Without proper pagination, endpoints were capped at 50 records.

## Commands

```bash
# Full sync - active companies only (default, 580 companies)
python -m sync.run_by_company

# Incremental sync - only NEW companies added since last sync
# (fetches /companies, compares with sync_jobs_company, syncs only new ones)
python -m sync.run_by_company --incremental

# Sync ALL companies regardless of status (2,180)
python -m sync.run_by_company --status all

# Sync specific status
python -m sync.run_by_company --status former

# Resume interrupted sync (skip completed companies)
python -m sync.run_by_company --resume

# Single company test
python -m sync.run_by_company --company 5b30ea1c14fb5716001c579d

# Adjust concurrency (default: 5)
python -m sync.run_by_company --concurrency 10
```

### Sync Modes

| Mode | Command | What it does |
|------|---------|-------------|
| **Full** | `python -m sync.run_by_company` | Phase 1 (all global) + Phase 2 (all active companies) + Backfill + Phase 3 |
| **Incremental** | `--incremental` | Re-fetches /companies, syncs only NEW active companies + all 13 endpoints per new company + Backfill + Phase 3 |
| **Resume** | `--resume` | Retries companies that failed or weren't reached in a previous full sync |
| **Single** | `--company ID` | Syncs one company (Phase 2 + Phase 3 only) |

## Endpoints (37 synced + 4 API-only)

### Phase 1 - Global (22 endpoints, synced once, all pages)
companies, visitors, resources, resource-types, locations, floors, posts, events, tickets, ticket-options, charges, tax-rates, revenue-accounts, plans, resource-rates, visits, webhooks, amenities, benefits, custom-properties, opportunity-statuses, secondary-currencies

Known large endpoints (with full pagination, no page cap):
- charges: ~35,610 records (713 pages)
- visitors: ~2,578 records
- companies: ~2,180 records
- visits: ~1,318 records
- resources: ~651 records
- plans: ~127 records

### Phase 2 - Per-Company (13 endpoints x 580 active companies, max 500 pages/endpoint)
members, bookings, bookings/occurrences, memberships, fees, credits, payments, contracts, checkins, opportunities, coins/stats, passes, payment-details

### Backfill (automatic, after Phase 2)
- Detects companies synced with older code (fewer than 13 endpoints)
- Syncs only the missing new endpoints (passes, payment-details) for those companies
- Updates existing sync_jobs_company records with new counts

### Phase 3 - Dependent (fetched using parent IDs from Phase 1/2, with SyncJob tracking)
- payments/{id}/documents: fetched for every payment record in DB (~14,842 payments → ~14,828 docs)
- assignments?membership={id}: fetched for every membership record in DB (~1,586 memberships → ~820 assignments)

### Not synced but served locally (4 endpoints - API returns 404/500 for this org)
- billing-settings, business-hours, reception-flows, organizations
- DB tables + API routes exist but no data synced (OfficeRnD API does not expose these for this org)

### Skipped (1 - POST-only)
- checkout: POST-only endpoint, no GET data available

## Local API Routes (80/80 GET endpoints from reference docs = 100%)

All routes served via FastAPI at `/api/v2/organizations/{orgSlug}/...`

### Community (`/community`)
- GET /members (filter: company, status, _id, name, email, location) + /count ($countBy) + /{id}
- GET /companies (filter: status, _id, name, location) + /{id}
- GET /visitors (filter: member, company, type, location) + /{id}
- GET /opportunities (filter: company, member, status) + /count + /{id}
- GET /passes (filter: company, member) + /{id}

### Space (`/space`)
- GET /resources (filter: type, location, floor, _id, name) + /count + /{id}/status + /{id}
- GET /resource-types
- GET /bookings (filter: resource, company, member, location) + /count + /{id}
- GET /bookings/occurrences (filter: company, member, location, resource)
- GET /assignments (filter: resource, membership)
- GET /locations (filter: name, isOpen, isPublic) + /{id}
- GET /floors (filter: location, name) + /{id}
- GET /amenities + /{id}

### Collaboration (`/collaboration`)
- GET /posts + /{id}
- GET /events + /count + /{id}
- GET /tickets (filter: status, company, member, location, assignedTo) + /count ($countBy) + /{id}
- GET /ticket-options

### Billing (`/billing`)
- GET /payments (filter: status, company, member) + /methods + /count + /{id}
- GET /charges (filter: status, payment) + /{id}
- GET /credits (filter: company, member) + /{id}
- GET /coins/stats
- GET /fees (filter: company, status, member, location, plan) + /count + /{id}
- GET /revenue-accounts
- GET /tax-rates
- GET /memberships (filter: company, status, member, plan) + /count + /{id}
- GET /plans + /count + /{id}
- GET /resource-rates + /count + /{id}
- GET /contracts (filter: company, location, status) + /count + /{id}
- GET /benefits (filter: company, member) + /count + /{id}
- GET /payment-details (filter: company, member)

### Visits (`/visits`)
- GET /visits (filter: member, visitor, location) + /{id}
- GET /checkins (filter: member, company, location) + /{id}

### Settings (`/settings`)
- GET /webhooks
- GET /billing-settings
- GET /business-hours
- GET /custom-properties
- GET /opportunity-statuses
- GET /reception-flows
- GET /secondary-currencies + /{id}
- GET /organizations
- GET /integrations/{id}

## Database

- PostgreSQL with SQLAlchemy ORM
- 45 tables mirroring all API resources (including payment_documents, sync tracking)
- ALL columns nullable (except _id, extra, synced_at) - prevents data loss from API nulls
- Batch upsert (100 rows) with ON CONFLICT DO UPDATE
- Row-by-row fallback on batch failure
- JSONB `extra` column stores full raw API response per record
- Connection pool: 5 connections + 10 overflow

## Error Handling (ZERO data loss policy)

- **NEVER skip a company** - all active companies from DB must be synced
- **NEVER skip an endpoint** - all fetchable endpoints must be attempted
- **Full pagination** - every page fetched via `$cursorNext` until exhausted (global endpoints unlimited, per-company capped at 500 pages)
- **Heartbeat callback** - progress file updated every 10 pages to prevent stale detection during long fetches
- **Retry 5 times** with exponential backoff (2s, 4s, 8s, 16s, 32s; 429 rate limits: 30s, 60s, 90s, 120s)
- **Retry covers full pipeline** (fetch + JSON save + DB save)
- **Batch fallback**: if batch insert fails, rollback + row-by-row retry
- **Deduplication**: pagination overlaps handled by _id dedup in fetcher
- **Partial data kept**: if fetch gets some records before error, saves them
- **Resume mode**: `--resume` skips completed companies, retries failed ones
- **Logs**: config/sync.log for full audit trail

## Data Storage Layout

```
data/
+-- global/                     # 22 global endpoint files (42,500+ records)
|   +-- locations.json
|   +-- companies.json
|   +-- resources.json
|   +-- charges.json            # ~35,610 records
|   +-- ...
+-- company_{id}/               # 580 active company folders x 13 endpoint files each
|   +-- members.json
|   +-- bookings.json
|   +-- payments.json
|   +-- ...
+-- payments_documents/{id}/    # Documents per payment ID
+-- assignments/{id}/           # Assignments per membership ID
+-- exports/                    # CSV exports of all DB tables
```

## Environment Variables (config/.env)

```
OFFICERND_ORG_SLUG=arafat-business-centers
OFFICERND_CLIENT_ID=xxx
OFFICERND_CLIENT_SECRET=xxx
OFFICERND_GRANT_TYPE=client_credentials
OFFICERND_SCOPE=flex.*
DATABASE_URL=postgresql://localhost:5432/officernd
```

## Development Rules

- Python 3.10+
- Uses asyncio (NOT threads) for concurrency
- Sync HTTP client wrapped with asyncio.to_thread()
- Rate limiting via asyncio.Semaphore (default: 5 concurrent)
- Do NOT add aiohttp - use existing requests-based client
- Do NOT create nested ThreadPoolExecutors
- Do NOT save files in project root - use /data/ folder
- ALL DB columns nullable to prevent data rejection
- CSV uses utf-8-sig encoding (BOM marker)
- NO endpoint skipped unless technically impossible (POST-only)
- Company IDs come from DB (Phase 1), NOT from ID.csv (which has member IDs)
- Default status filter is 'active' (use --status all to override)
- Pagination uses `$cursorNext` query param (with $ prefix), NOT `cursorNext`
