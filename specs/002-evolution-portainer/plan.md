# Implementation Plan: Evolution API + BillionMail + Portainer

**Branch**: `002-evolution-portainer` | **Date**: 2026-03-06 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/002-evolution-portainer/spec.md`

## Summary

Add three new Docker services to the platform: Evolution API (WhatsApp Business API), BillionMail (self-hosted email server + marketing platform), and Portainer (container management UI). Restructure all Docker services into a single root `docker-compose.yml`. Update nginx routing and GitHub Actions deployment. Evolution API uses existing host PostgreSQL (new `evolutiondb` database). BillionMail runs self-contained with its own PostgreSQL. Portainer provides web UI for monitoring all containers.

## Technical Context

**Language/Version**: Docker Compose 3.x (orchestration), no application code written — all services use official Docker images
**Primary Dependencies**: `evoapicloud/evolution-api:latest`, `billionmail/*` (7 images), `portainer/portainer-ce:latest`, `redis:latest`
**Storage**: Host PostgreSQL 16 (port 5432) for Evolution API (`evolutiondb`); BillionMail's own PostgreSQL 17.4 (port 25432, internal); Portainer BoltDB (volume); named Docker volumes for persistence
**Testing**: Playwright e2e tests (extend existing `tests/` with health checks for new services), manual verification of email delivery and WhatsApp connectivity
**Target Platform**: Linux VPS (Ubuntu), Docker host
**Project Type**: Infrastructure/DevOps — Docker Compose orchestration + nginx configuration
**Performance Goals**: All services start within 3 minutes; health endpoints respond in <5s
**Constraints**: Single VPS, shared host PostgreSQL, no port conflicts with existing 8 services
**Scale/Scope**: Single-operator platform, ~15 Docker containers total after deployment

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Constitution is an unfilled template — no gates defined. No violations to check.

**Post-design re-check**: Still no gates. Proceeding.

## Project Structure

### Documentation (this feature)

```text
specs/002-evolution-portainer/
├── plan.md              # This file
├── research.md          # Phase 0: Docker setup research for all 3 services
├── data-model.md        # Phase 1: Database, volume, and network topology
├── quickstart.md        # Phase 1: How to start all services
├── contracts/
│   ├── nginx-routing.md # Nginx location blocks and DNS records
│   └── port-allocation.md # Complete port map (no conflicts)
└── tasks.md             # Phase 2 output (created by /speckit.tasks)
```

### Source Code (repository root)

```text
single-window/                          # Project root
├── docker-compose.yml                  # NEW: Root compose — all Docker services
├── .env.example                        # NEW: Template for all service env vars
├── .env                                # NEW: Actual env vars (gitignored)
│
├── api-scraper/                        # Existing (unchanged)
│   ├── docker-compose.yml              # Kept for local dev
│   └── ...
├── API-CR/                             # Existing (unchanged)
│   ├── docker-compose.yml              # Kept for local dev
│   └── ...
├── Portal/                             # Existing (unchanged)
│   ├── docker-compose.yml              # Kept for local dev
│   ├── noaman.cloud.nginx.conf         # MODIFIED: add /evolution/, /portainer/
│   └── ...
├── scrape-sw-gsheet/                   # Existing (unchanged)
│   ├── docker-compose.yml              # Kept for local dev
│   └── ...
├── scrape-sw-codes/                    # Existing host service (unchanged)
├── officernd/                          # Existing host service (unchanged)
│
├── billionmail/                        # NEW: BillionMail configuration
│   ├── .env                            # BillionMail-specific env vars
│   ├── conf/                           # Service configs (postfix, dovecot, etc.)
│   ├── ssl/                            # SSL certificates
│   └── init.sql                        # Database initialization
│
├── mail.noaman.cloud.nginx.conf        # NEW: Nginx server block for mail subdomain
│
├── .github/workflows/
│   └── deploy.yml                      # MODIFIED: unified compose deployment
│
├── scripts/
│   └── setup-databases.py              # MODIFIED: add evolutiondb creation
│
└── tests/
    ├── fetch-codes.spec.js             # Existing
    └── services-health.spec.js         # NEW: Health check tests for all services
```

**Structure Decision**: This is an infrastructure/DevOps feature — no application source code is written. Changes are Docker Compose files, nginx configs, env files, and deployment scripts. Existing service directories remain unchanged; their per-service compose files are kept for local development.

## Complexity Tracking

No constitution violations to justify.

## Key Implementation Decisions

### 1. Root docker-compose.yml structure

The root compose file defines all Docker services in a single file:

**Existing services** (migrated from per-service compose files):
- `api-scraper` (port 8080, builds from `./api-scraper`)
- `api-cr` (port 8086, builds from `./API-CR`)
- `portal` (port 8082, builds from `./Portal`)
- `scraper`, `gsheet-scraper-en`, `gsheet-scraper-ar`, `gsheet-web` (from `./scrape-sw-gsheet`)

**New services**:
- `evolution-api` (port 8089->8080, image `evoapicloud/evolution-api:latest`)
- `evolution-redis` (internal only, image `redis:latest`)
- `portainer` (port 9000, image `portainer/portainer-ce:latest`)
- `billionmail-core` / container_name `BILLIONMAIL-CORE` (port 8090->80, 8443->443)
- `billionmail-postfix` (ports 25, 465, 587)
- `billionmail-dovecot` (ports 143, 993, 110, 995)
- `billionmail-rspamd`
- `billionmail-roundcube`
- `billionmail-pgsql` (port 25432, localhost only)
- `billionmail-redis` (port 26379, localhost only)

**Networks**: `scrapers-network` (shared), `billionmail-network` (internal)

### 2. GitHub Actions deployment refactor

Replace per-service loop with:
1. Generate `.env` file from GitHub Secrets
2. `docker compose down --remove-orphans`
3. Force-remove containers by name (same pattern as current)
4. `docker compose up -d --build --no-cache`
5. Run BillionMail DB init on first deploy
6. Copy both nginx configs, reload
7. PM2 services unchanged

### 3. BillionMail integration approach

BillionMail's `install.sh` does too much (installs Docker, modifies firewall, disables SELinux). Instead:
1. Extract the `docker-compose.yml` and `env_init` from BillionMail repo
2. Adapt into our root compose file with remapped ports (80->8090, 443->8443)
3. Generate credentials in GitHub Actions (like `install.sh` does)
4. Run DB initialization manually via `docker exec` on first deploy
5. Handle SSL cert generation separately (certbot for `mail.noaman.cloud`)

### 4. Evolution API connection to host PostgreSQL

Connection URI: `postgresql://evolution_user:<pass>@host.docker.internal:5432/evolutiondb?schema=evolution_api`

The `extra_hosts: host.docker.internal:host-gateway` directive is already used by Portal and will be added to the Evolution API service. Prisma runs auto-migrations on container startup.
