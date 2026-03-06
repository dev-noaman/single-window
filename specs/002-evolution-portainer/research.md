# Research: Evolution API + BillionMail + Portainer

**Branch**: `002-evolution-portainer` | **Date**: 2026-03-06

## R1: Evolution API Docker Setup

**Decision**: Use official `evoapicloud/evolution-api:latest` image with host PostgreSQL and containerized Redis.

**Rationale**: Official image is Node.js-based, supports PostgreSQL natively via Prisma ORM. Uses `postgres:15` in their compose but we'll use the existing host PostgreSQL (port 5432) per FR-011. Redis is required for caching (no option to disable).

**Key findings**:
- Image: `evoapicloud/evolution-api:latest`
- Internal port: 8080 (conflicts with api-scraper) — **must remap to 8089 externally**
- Database: PostgreSQL via `DATABASE_PROVIDER=postgresql` and `DATABASE_CONNECTION_URI`
- Redis: Required (`CACHE_REDIS_ENABLED=true`), image `redis:latest`
- Auth: Global API key via `AUTHENTICATION_API_KEY` env var
- Volumes: `evolution_instances` (session state), `evolution_redis` (Redis data)
- Optional frontend manager: `evoapicloud/evolution-manager:latest` (port 3000) — skip for now, API-only
- Runs Prisma migrations on startup via `deploy_database.sh` entrypoint

**Alternatives considered**:
- Running Evolution API's bundled PostgreSQL container → rejected (FR-011 requires host PostgreSQL)
- Using MongoDB → rejected (PostgreSQL is already the project standard)

## R2: BillionMail Docker Setup

**Decision**: Use BillionMail's official multi-container setup (7 services) with its own bundled PostgreSQL and Redis, running on a dedicated Docker network.

**Rationale**: BillionMail ships as a tightly coupled 7-container system (Postfix, Dovecot, Rspamd, RoundCube, Core, PostgreSQL, Redis) with internal Unix socket communication. It's not practical to share the host PostgreSQL since BillionMail's containers communicate via Unix sockets, not TCP. The system is self-contained by design.

**Key findings**:
- 7 containers: core, postfix, dovecot, rspamd, roundcube, pgsql, redis
- Internal PostgreSQL on port 25432 (localhost-bound), Redis on port 26379 (localhost-bound)
- Mail ports: 25 (SMTP), 465 (SMTPS), 587 (submission), 143 (IMAP), 993 (IMAPS), 110 (POP3), 995 (POP3S)
- Web ports: 80/443 (admin panel + webmail) — conflicts with nginx, **must remap**
- Admin panel at `https://<host>/<SafePath>`, RoundCube at `/roundcube/`
- Custom bridge network `billionmail-network` (172.66.1.0/24)
- `install.sh` generates random credentials, SSL certs, initializes DB, seeds domain
- Data: ~14 volume mounts (postgresql-data, vmail-data, postfix-data, core-data, ssl, conf, logs, etc.)
- Domain config: `BILLIONMAIL_HOSTNAME=noaman.cloud` (per clarification)
- Core container mounts Docker socket (read-only) for container management

**Alternatives considered**:
- Sharing host PostgreSQL for BillionMail → rejected (Unix socket communication, tightly coupled)
- Running BillionMail's install.sh on host → rejected (would conflict with existing nginx, ports, packages)

## R3: Port Allocation

**Decision**: Assign non-conflicting ports for all services.

| Service | Internal Port | External Port | Notes |
|---------|--------------|---------------|-------|
| api-scraper | 8080 | 8080 | Existing (unchanged) |
| Portal | 80 | 8082 | Existing (unchanged) |
| scrape-sw-codes | 8084 | 8084 | Host PM2 (unchanged) |
| scrape-sw-gsheet | 8000 | 8085 | Existing (unchanged) |
| API-CR | 8086 | 8086 | Existing (unchanged) |
| officernd-api | 8087 | 8087 | Host PM2 (unchanged) |
| officernd-bff | 8088 | 8088 | Host PM2 (unchanged) |
| Evolution API | 8080 | 8089 | Remapped (8080 taken by api-scraper) |
| Evolution Redis | 6379 | 6379 | Internal only (not exposed to host) |
| BillionMail Core | 80/443 | 8090/8443 | Remapped (80/443 taken by nginx) |
| BillionMail SMTP | 25 | 25 | Direct host binding |
| BillionMail SMTPS | 465 | 465 | Direct host binding |
| BillionMail Submission | 587 | 587 | Direct host binding |
| BillionMail IMAP | 143 | 143 | Direct host binding |
| BillionMail IMAPS | 993 | 993 | Direct host binding |
| BillionMail POP3 | 110 | 110 | Direct host binding |
| BillionMail POP3S | 995 | 995 | Direct host binding |
| BillionMail PostgreSQL | 5432 | 25432 | Localhost only (no conflict with host PG on 5432) |
| BillionMail Redis | 6379 | 26379 | Localhost only |
| Portainer | 9000 | 9000 | HTTP UI |

## R4: Unified Docker Compose Strategy

**Decision**: Create a root `docker-compose.yml` that defines all Docker services. Per-service compose files remain for local dev.

**Rationale**: A single compose file ensures all services share a network, Portainer sees them as one stack, and `docker compose up -d` starts everything. The GitHub Actions workflow will switch from per-service `docker compose` calls to a single root-level call.

**Key design choices**:
- Single shared network (`scrapers-network`) for inter-service communication
- BillionMail keeps its own internal network (`billionmail-network`) plus connects to the shared network
- `extra_hosts: host.docker.internal:host-gateway` on services that need host PostgreSQL
- Portainer mounts `/var/run/docker.sock` for Docker management
- Named volumes for all persistent data

## R5: Nginx Configuration

**Decision**: Extend `noaman.cloud.nginx.conf` with new location blocks. Add separate server block for `mail.noaman.cloud`.

**Rationale**: Evolution API and Portainer use path-based routing on `noaman.cloud` (consistent with existing pattern). BillionMail uses `mail.noaman.cloud` subdomain (per clarification) because mail servers need root-path access for autoconfig/autodiscover.

**New nginx routing**:
- `noaman.cloud/evolution/` → `127.0.0.1:8089` (Evolution API)
- `noaman.cloud/portainer/` → `127.0.0.1:9000` (Portainer, with WebSocket upgrade)
- `mail.noaman.cloud` → `127.0.0.1:8090` (BillionMail Core — admin + RoundCube)

## R6: GitHub Actions Deployment Changes

**Decision**: Refactor deploy.yml to use root `docker-compose.yml` instead of per-service loops.

**Key changes**:
1. Replace per-service loop with single `docker compose -f docker-compose.yml up -d --build`
2. Add `.env` file generation for Evolution API and BillionMail credentials (from GitHub Secrets)
3. Add BillionMail post-deploy initialization (DB seed, domain setup, DKIM key generation)
4. Add `mail.noaman.cloud` nginx server block
5. Keep PM2 host services (scrape-sw-codes, officernd) deployment unchanged

**New GitHub Secrets needed**:
- `EVOLUTION_API_KEY`: Evolution API authentication key
- `BILLIONMAIL_ADMIN_PASS`: BillionMail admin password
- `BILLIONMAIL_DB_PASS`: BillionMail PostgreSQL password
