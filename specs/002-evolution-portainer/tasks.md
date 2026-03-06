# Tasks: Evolution API + BillionMail + Portainer

**Input**: Design documents from `/specs/002-evolution-portainer/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/

**Tests**: Not explicitly requested. Health check tests included in Polish phase as operational validation.

**Organization**: Tasks grouped by user story. US1 and US2 are both P1 (parallelizable). US3 and US4 are P2. US5 is P3.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create shared files and directory structure needed by all user stories

- [ ] T001 Create root environment template with all service variables in .env.example
- [ ] T002 Add .env to .gitignore (prevent credential leaks)
- [ ] T003 [P] Create billionmail/ directory structure: billionmail/.env, billionmail/conf/, billionmail/ssl/
- [ ] T004 [P] Update scripts/setup-databases.py to create `evolutiondb` database and `evolution_user` role on host PostgreSQL (following existing `officernd`/`codesdb` pattern)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Create root docker-compose.yml with existing services migrated from per-service files. This is the foundation all new services are added to.

**CRITICAL**: No user story work can begin until this phase is complete

- [ ] T005 Create root docker-compose.yml with `scrapers-network` (bridge) and migrate existing api-scraper service (build: ./api-scraper, port 8080, container_name API-SCRAPER, healthcheck, shm_size 2gb) in docker-compose.yml
- [ ] T006 [P] Migrate API-CR service to root docker-compose.yml (build: ./API-CR, port 8086, container_name API-CR, volumes ./API-CR/data:/app/data, healthcheck, shm_size 2gb)
- [ ] T007 [P] Migrate Portal service to root docker-compose.yml (build: ./Portal, port 8082->80, container_name PORTAL, extra_hosts host.docker.internal, healthcheck)
- [ ] T008 [P] Migrate scrape-sw-gsheet services (scraper, gsheet-scraper-en, gsheet-scraper-ar, web) to root docker-compose.yml with all volumes and port mappings from scrape-sw-gsheet/docker-compose.yml
- [ ] T009 Verify root docker-compose.yml starts all existing services correctly: `docker compose up -d` and confirm API-SCRAPER, API-CR, PORTAL, SW_GSHEET, GSHEET_SCRAPER_EN, GSHEET_SCRAPER_AR, GSHEET_SCRAPER_WEB containers are running with correct ports

**Checkpoint**: Foundation ready — existing services work from root compose. User story implementation can begin.

---

## Phase 3: User Story 1 - Deploy Evolution API (Priority: P1) MVP

**Goal**: Evolution API running as a Docker container with Redis, connected to host PostgreSQL `evolutiondb`, accessible on port 8089

**Independent Test**: `curl http://localhost:8089/` returns Evolution API response after `docker compose up -d`

### Implementation for User Story 1

- [ ] T010 [US1] Add `evolution-redis` service to docker-compose.yml (image redis:latest, volume evolution_redis_data, network scrapers-network, no host port exposure, command: redis-server --appendonly yes)
- [ ] T011 [US1] Add `evolution-api` service to docker-compose.yml (image evoapicloud/evolution-api:latest, port 8089->8080, container_name EVOLUTION-API, depends_on evolution-redis, extra_hosts host.docker.internal:host-gateway, volume evolution_instances, network scrapers-network, env_file .env)
- [ ] T012 [US1] Configure Evolution API environment variables in .env.example: SERVER_PORT=8080, SERVER_URL, AUTHENTICATION_API_KEY, DATABASE_PROVIDER=postgresql, DATABASE_CONNECTION_URI=postgresql://evolution_user:pass@host.docker.internal:5432/evolutiondb?schema=evolution_api, CACHE_REDIS_ENABLED=true, CACHE_REDIS_URI=redis://evolution-redis:6379/6, DATABASE_SAVE_DATA_* toggles
- [ ] T013 [US1] Create .env file from .env.example with actual credentials (Evolution API key, database password) — document in quickstart.md that this step is manual
- [ ] T014 [US1] Verify Evolution API starts and connects to host PostgreSQL: `docker compose up -d evolution-api evolution-redis`, confirm Prisma migrations run (check logs), confirm `curl http://localhost:8089/` responds

**Checkpoint**: Evolution API functional on port 8089 with Redis and host PostgreSQL. WhatsApp instances can be created via the API.

---

## Phase 4: User Story 2 - Deploy BillionMail (Priority: P1)

**Goal**: BillionMail 7-container mail server running with admin panel on port 8090, mail ports (25, 587, 993) exposed, using `noaman.cloud` as email domain

**Independent Test**: Access `http://localhost:8090/` to see BillionMail admin panel; `http://localhost:8090/roundcube/` for webmail

### Implementation for User Story 2

- [ ] T015 [US2] Add `billionmail-network` (bridge, subnet 172.66.1.0/24) to docker-compose.yml networks section
- [ ] T016 [US2] Add `billionmail-pgsql` service to docker-compose.yml (image postgres:17.4-alpine, container_name pgsql-billionmail, volume billionmail_postgres for /var/lib/postgresql/data, volume billionmail_pgsocket for Unix socket, env POSTGRES_DB/USER/PASSWORD from .env, port 127.0.0.1:25432->5432, network billionmail-network)
- [ ] T017 [P] [US2] Add `billionmail-redis` service to docker-compose.yml (image redis:7.4.2-alpine, container_name redis-billionmail, volume billionmail_redis, port 127.0.0.1:26379->6379, requirepass from .env, network billionmail-network)
- [ ] T018 [US2] Add `billionmail-rspamd` service to docker-compose.yml (image billionmail/rspamd:1.2, container_name rspamd-billionmail, volumes for rspamd-data and conf, depends_on pgsql/redis, network billionmail-network)
- [ ] T019 [US2] Add `billionmail-dovecot` service to docker-compose.yml (image billionmail/dovecot:1.6, container_name dovecot-billionmail, ports 143/993/110/995, volumes for vmail-data/conf/pgsocket/rspamd-data, depends_on pgsql/redis/rspamd, network billionmail-network)
- [ ] T020 [US2] Add `billionmail-postfix` service to docker-compose.yml (image billionmail/postfix:1.6, container_name postfix-billionmail, ports 25/465/587, volumes for postfix-data/conf/pgsocket/rspamd-data, depends_on pgsql/redis/rspamd/dovecot, network billionmail-network)
- [ ] T021 [US2] Add `billionmail-roundcube` service to docker-compose.yml (image roundcube/roundcubemail:1.6.11-fpm-alpine, container_name webmail-billionmail, volumes for webmail-data/conf/php-sock, depends_on pgsql/dovecot, network billionmail-network)
- [ ] T022 [US2] Add `billionmail-core` service to docker-compose.yml (image billionmail/core:4.9.0, container_name BILLIONMAIL-CORE, ports 8090->80 and 8443->443, volumes for core-data/ssl/conf/logs/pgsocket/php-sock/.env, docker.sock:ro, depends_on all BillionMail services, networks: billionmail-network + scrapers-network)
- [ ] T023 [US2] Configure BillionMail environment variables in billionmail/.env: BILLIONMAIL_HOSTNAME=noaman.cloud, ADMIN_USERNAME, ADMIN_PASSWORD, SafePath, DBNAME=billionmail, DBUSER=billionmail, DBPASS, REDISPASS, all port mappings (SMTP_PORT=25, etc.), TZ=Asia/Qatar, IPV4_NETWORK=172.66.1, FAIL2BAN_INIT=y
- [ ] T024 [US2] Add all BillionMail named volumes to docker-compose.yml volumes section: billionmail_postgres, billionmail_pgsocket, billionmail_redis, billionmail_rspamd, billionmail_vmail, billionmail_postfix, billionmail_webmail, billionmail_core, billionmail_ssl, billionmail_ssl_selfsigned, billionmail_conf, billionmail_logs, billionmail_phpsock
- [ ] T025 [US2] Create BillionMail database initialization script in billionmail/init-db.sh that runs init.sql and seeds the domain (noaman.cloud) — adapted from BillionMail's install.sh DB init section
- [ ] T026 [US2] Generate self-signed SSL certificates for BillionMail in billionmail/ssl/ (or document certbot setup for production in quickstart.md)
- [ ] T027 [US2] Verify BillionMail starts: `docker compose up -d` all billionmail-* services, run `docker exec BILLIONMAIL-CORE /opt/init-db.sh` for first-time DB seed, confirm admin panel at http://localhost:8090/ and RoundCube at http://localhost:8090/roundcube/
- [ ] T027a [US2] Verify BillionMail can send a test email: log into admin panel, create a test mailbox, send an email via RoundCube webmail or SMTP, confirm delivery (validates SC-009)

**Checkpoint**: BillionMail functional with admin panel, webmail, and mail ports exposed. Can send/receive test emails.

---

## Phase 5: User Story 3 - Portainer UI (Priority: P2)

**Goal**: Portainer CE running on port 9000, Docker socket mounted, showing all containers

**Independent Test**: Access `http://localhost:9000/`, create admin account, see all running containers listed

### Implementation for User Story 3

- [ ] T028 [US3] Add `portainer` service to docker-compose.yml (image portainer/portainer-ce:latest, container_name PORTAINER, port 9000->9000, volumes: /var/run/docker.sock:/var/run/docker.sock:ro and portainer_data:/data, restart unless-stopped, network scrapers-network)
- [ ] T029 [US3] Add `portainer_data` named volume to docker-compose.yml volumes section
- [ ] T030 [US3] Verify Portainer starts and shows all containers: `docker compose up -d portainer`, access http://localhost:9000/, create admin account, confirm container list shows API-SCRAPER, API-CR, PORTAL, EVOLUTION-API, BILLIONMAIL-CORE, and all other running containers
- [ ] T030a [US3] Verify container restart via Portainer: pick any running container in Portainer UI, click restart, confirm the container recovers and its service responds within 30 seconds (validates SC-004)

**Checkpoint**: Portainer functional, all Docker containers visible and manageable through the UI.

---

## Phase 6: User Story 4 - Unified Docker Compose Orchestration (Priority: P2)

**Goal**: GitHub Actions deployment workflow updated to use root docker-compose.yml instead of per-service loops. Single `docker compose up` deploys everything.

**Independent Test**: Push to main triggers GitHub Actions; all services deploy successfully including new ones

### Implementation for User Story 4

- [ ] T031 [US4] Refactor .github/workflows/deploy.yml: replace per-service DOCKER_SERVICES loop (lines 128-157) with single `docker compose -f docker-compose.yml down --remove-orphans && docker compose -f docker-compose.yml up -d --build` at repo root
- [ ] T032 [US4] Add .env file generation step to deploy.yml: write Evolution API key, DB credentials, BillionMail credentials from GitHub Secrets into $REPO_DIR/.env and $REPO_DIR/billionmail/.env before docker compose up
- [ ] T033 [US4] Add container force-removal step to deploy.yml: extract all container_name values from root docker-compose.yml and force-remove them before `docker compose up` (same pattern as current per-service removal)
- [ ] T034 [US4] Add BillionMail first-deploy initialization to deploy.yml: check if billionmail DB is empty, if so run `docker exec BILLIONMAIL-CORE /opt/init-db.sh` after containers start
- [ ] T035 [US4] Add new GitHub Secrets documentation: EVOLUTION_API_KEY, BILLIONMAIL_ADMIN_PASS, BILLIONMAIL_DB_PASS — document in quickstart.md
- [ ] T036 [US4] Verify deploy.yml still handles Portal Dockerfile heredoc correctly (lines 56-113 write Dockerfile directly — ensure this still works with root compose referencing build: ./Portal)
- [ ] T037 [US4] Verify `docker compose up -d` from project root starts all ~17 containers and all existing services still work on their original ports (8080, 8082, 8085, 8086)

**Checkpoint**: GitHub Actions deploys all services (existing + new) via single root compose. Full CI/CD pipeline works.

---

## Phase 7: User Story 5 - Nginx Routing (Priority: P3)

**Goal**: Evolution API at noaman.cloud/evolution/, Portainer at noaman.cloud/portainer/, BillionMail at mail.noaman.cloud — all proxied through nginx

**Independent Test**: `curl https://noaman.cloud/evolution/`, `curl https://noaman.cloud/portainer/`, `curl https://mail.noaman.cloud/` all return correct service responses

### Implementation for User Story 5

- [ ] T038 [P] [US5] Add `/evolution/` location block to Portal/noaman.cloud.nginx.conf: proxy_pass http://127.0.0.1:8089/, standard proxy headers, proxy_read_timeout 300
- [ ] T039 [P] [US5] Add `/portainer/` location block to Portal/noaman.cloud.nginx.conf: proxy_pass http://127.0.0.1:9000/, proxy_http_version 1.1, Upgrade/Connection headers for WebSocket support
- [ ] T040 [US5] Create mail.noaman.cloud.nginx.conf at project root: server block for mail.noaman.cloud, listen 80, proxy_pass to 127.0.0.1:8090 for all paths
- [ ] T041 [US5] Update deploy.yml nginx section: copy both Portal/noaman.cloud.nginx.conf AND mail.noaman.cloud.nginx.conf to /etc/nginx/sites-available/, create symlinks in sites-enabled, nginx -t && systemctl reload nginx
- [ ] T042 [US5] Document DNS records required in quickstart.md: A record for mail.noaman.cloud, MX record for noaman.cloud pointing to mail.noaman.cloud, SPF TXT record, DMARC TXT record, DKIM TXT record (retrieved from BillionMail after first start)

**Checkpoint**: All new services accessible via their public URLs. BillionMail has its own subdomain. Existing service routes unchanged.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Validation, documentation, and operational readiness

- [ ] T043 [P] Create tests/services-health.spec.js: Playwright e2e test that checks health/accessibility of all services (api-scraper /health, API-CR /health, Portal /, Evolution API on 8089, BillionMail admin on 8090, Portainer on 9000) against live noaman.cloud
- [ ] T044 [P] Update CLAUDE.md: add Evolution API, BillionMail, Portainer to Architecture diagram, Key Service Endpoints table, Nginx Routing table, Container Names, Technology Stack, and Host PostgreSQL sections
- [ ] T045 [P] Update specs/002-evolution-portainer/quickstart.md with final verified steps, actual port numbers, and any issues discovered during implementation
- [ ] T046 Verify data persistence: `docker compose down && docker compose up -d`, confirm Evolution API instances survive, Portainer users survive, BillionMail mailboxes survive
- [ ] T047 Verify existing services unaffected: run existing tests/fetch-codes.spec.js against noaman.cloud, confirm all existing /api-scraper/, /api-cr/, /sw-codes/, /gsheet-scraper/, /officernd/ routes still work
- [ ] T048 Security review: ensure .env is gitignored, no credentials in docker-compose.yml, Portainer has strong password, BillionMail SafePath is randomized, Evolution API key is not default

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 (.env.example and directory structure)
- **US1 (Phase 3)**: Depends on Phase 2 (root compose with existing services) + T004 (evolutiondb)
- **US2 (Phase 4)**: Depends on Phase 2 (root compose) + T003 (billionmail directory)
- **US3 (Phase 5)**: Depends on Phase 2 (root compose)
- **US4 (Phase 6)**: Depends on US1 + US2 + US3 (all services must be in compose before refactoring deploy)
- **US5 (Phase 7)**: Depends on US1 + US2 + US3 (services must be running before routing to them)
- **Polish (Phase 8)**: Depends on all user stories complete

### User Story Dependencies

- **US1 (Evolution API)**: Independent after Phase 2. No dependency on US2 or US3.
- **US2 (BillionMail)**: Independent after Phase 2. No dependency on US1 or US3.
- **US3 (Portainer)**: Independent after Phase 2. No dependency on US1 or US2. Better to add after US1/US2 so Portainer shows all containers.
- **US4 (Unified Compose)**: Depends on US1 + US2 + US3 (deploy.yml needs all services defined)
- **US5 (Nginx Routing)**: Depends on US1 + US2 + US3 (routes need running services)

### Parallel Opportunities

- **Phase 1**: T003 and T004 can run in parallel (different directories)
- **Phase 2**: T006, T007, T008 can run in parallel (different service blocks in same file — but same file, so sequential recommended)
- **Phase 3 & 4**: US1 and US2 can run in parallel (completely different services, different ports, different volumes)
- **Phase 5**: US3 can start as soon as Phase 2 completes (independent of US1/US2)
- **Phase 7**: T038 and T039 can run in parallel (different location blocks in same file)
- **Phase 8**: T043, T044, T045 can run in parallel (different files)

---

## Parallel Example: US1 + US2 simultaneously

```bash
# After Phase 2 (foundational) completes, launch both P1 stories:

# Stream 1: Evolution API (US1)
Task: T010 "Add evolution-redis to docker-compose.yml"
Task: T011 "Add evolution-api to docker-compose.yml"
Task: T012 "Configure Evolution API env vars in .env.example"
Task: T013 "Create .env with actual credentials"
Task: T014 "Verify Evolution API starts"

# Stream 2: BillionMail (US2) — runs simultaneously
Task: T015 "Add billionmail-network to docker-compose.yml"
Task: T016 "Add billionmail-pgsql to docker-compose.yml"
Task: T017 "Add billionmail-redis to docker-compose.yml"
# ... T018-T027
```

---

## Implementation Strategy

### MVP First (US1 only — Evolution API)

1. Complete Phase 1: Setup (.env.example, directories)
2. Complete Phase 2: Root compose with existing services
3. Complete Phase 3: Evolution API + Redis
4. **STOP and VALIDATE**: `curl http://localhost:8089/` works, WhatsApp instance creation works
5. Deploy via manual docker compose on VPS

### Incremental Delivery

1. Setup + Foundational → existing services work from root compose
2. Add US1 (Evolution API) → test independently → deploy
3. Add US2 (BillionMail) → test independently → deploy
4. Add US3 (Portainer) → test independently → deploy
5. Add US4 (deploy.yml refactor) → test full CI/CD
6. Add US5 (nginx routing) → test public URLs
7. Polish → final validation

---

## Notes

- All new services use official Docker images — no custom Dockerfiles needed
- BillionMail is the most complex addition (7 containers, 13+ volumes, mail ports)
- Evolution API auto-migrates its database on startup — no manual schema management
- Portainer is the simplest addition (1 container, 1 volume, Docker socket mount)
- Existing per-service docker-compose.yml files are NOT deleted — kept for local dev
- Host PM2 services (scrape-sw-codes, officernd) are unchanged throughout
