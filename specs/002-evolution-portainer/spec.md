# Feature Specification: Evolution API + BillionMail + Portainer Container Management

**Feature Branch**: `002-evolution-portainer`
**Created**: 2026-03-06
**Status**: Draft
**Input**: User description: "https://github.com/EvolutionAPI/evolution-api need to implement this also to docker then restructure to have Portainer ui" + "https://github.com/Billionmail/BillionMail Also"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Deploy Evolution API as a Docker Service (Priority: P1)

As a platform operator, I want Evolution API (WhatsApp Business API) running as a Docker container alongside my existing services, so that I can offer WhatsApp messaging capabilities through the same infrastructure.

**Why this priority**: Evolution API is the core new capability being added. Without it running, Portainer management is secondary.

**Independent Test**: Can be fully tested by starting the Evolution API container and successfully accessing its API endpoints. Delivers WhatsApp integration capability.

**Acceptance Scenarios**:

1. **Given** the project repository is cloned and Docker is available, **When** I run the Docker Compose command, **Then** the Evolution API container starts successfully and responds on its configured port.
2. **Given** Evolution API is running, **When** I access the API health endpoint, **Then** it returns a healthy status.
3. **Given** Evolution API is running, **When** I configure a WhatsApp instance through the API, **Then** the instance is created and ready for connection.
4. **Given** Evolution API is running behind nginx, **When** I access it via the public URL path, **Then** the API is reachable through the reverse proxy.

---

### User Story 2 - Deploy BillionMail as a Docker Service (Priority: P1)

As a platform operator, I want BillionMail (self-hosted mail server + email marketing platform) running as Docker containers alongside my existing services, so that I can send emails, manage campaigns, and provide webmail access from the same infrastructure.

**Why this priority**: BillionMail is another core new capability being added. It provides email infrastructure (SMTP, campaign management, webmail via RoundCube) that complements the WhatsApp capability from Evolution API.

**Independent Test**: Can be fully tested by accessing the BillionMail admin panel, creating a test email campaign, and accessing RoundCube webmail. Delivers self-hosted email infrastructure.

**Acceptance Scenarios**:

1. **Given** the project repository is cloned and Docker is available, **When** I run the Docker Compose command, **Then** the BillionMail containers start successfully.
2. **Given** BillionMail is running, **When** I access the admin panel, **Then** I can log in and see the dashboard with campaign management features.
3. **Given** BillionMail is running, **When** I access the RoundCube webmail path, **Then** I can log in and send/receive emails.
4. **Given** BillionMail is running behind nginx, **When** I access it via the public URL path, **Then** the admin panel and webmail are reachable through the reverse proxy.

---

### User Story 3 - Portainer UI for Container Management (Priority: P2)

As a platform operator, I want a Portainer web UI to visually manage all Docker containers (existing services + Evolution API + BillionMail), so that I can monitor, start, stop, and inspect containers without SSH and CLI commands.

**Why this priority**: Portainer provides operational visibility and management but is not required for the core services to function. It adds management convenience on top of working services.

**Independent Test**: Can be fully tested by accessing the Portainer UI, seeing all running containers listed, and performing a container restart through the UI.

**Acceptance Scenarios**:

1. **Given** Portainer is deployed, **When** I access the Portainer URL, **Then** I see a login page and can authenticate.
2. **Given** I am logged into Portainer, **When** I view the container list, **Then** I see all project containers (API-SCRAPER, API-CR, PORTAL, Evolution API, etc.) with their status.
3. **Given** I am logged into Portainer, **When** I restart a container through the UI, **Then** the container restarts and the corresponding service recovers.
4. **Given** Portainer is running, **When** I access container logs through the UI, **Then** I can view real-time logs for any container.

---

### User Story 4 - Unified Docker Compose Orchestration (Priority: P2)

As a platform operator, I want all Docker-based services (existing + Evolution API + BillionMail + Portainer) orchestrated under a coherent Docker Compose structure, so that the entire platform can be managed consistently.

**Why this priority**: Restructuring the Docker setup is necessary for Portainer to have visibility into all containers and for consistent deployment. Tied to P2 since it enables Portainer's value.

**Independent Test**: Can be fully tested by running `docker compose up` from the project root and verifying all services start correctly with proper networking.

**Acceptance Scenarios**:

1. **Given** the restructured Docker setup, **When** I run the compose command, **Then** all services (api-scraper, API-CR, Portal, Evolution API, BillionMail, Portainer) start with correct networking.
2. **Given** services are running, **When** one service needs to communicate with another, **Then** inter-service networking works via Docker network.
3. **Given** a new deployment is triggered, **When** GitHub Actions runs the deploy workflow, **Then** the deployment handles the new unified structure correctly.

---

### User Story 5 - Nginx Routing for New Services (Priority: P3)

As an end user, I want Evolution API, BillionMail, and Portainer accessible through the existing noaman.cloud domain via dedicated URL paths, so that all services are reachable through one domain.

**Why this priority**: Routing is the final integration step. Services must work first before exposing them publicly.

**Independent Test**: Can be fully tested by accessing the Evolution API, BillionMail, and Portainer paths on noaman.cloud and verifying correct proxy behavior.

**Acceptance Scenarios**:

1. **Given** nginx is configured, **When** I access the Evolution API path on noaman.cloud, **Then** requests are proxied to the Evolution API container.
2. **Given** nginx is configured, **When** I access `mail.noaman.cloud`, **Then** requests are proxied to the BillionMail container serving admin panel and RoundCube webmail.
3. **Given** nginx is configured, **When** I access the Portainer path on noaman.cloud, **Then** requests are proxied to the Portainer container (including WebSocket for real-time UI).

---

### Edge Cases

- What happens when Evolution API's database conflicts with the existing host PostgreSQL on port 5432?
- How does Portainer handle containers managed by PM2 on the host (scrape-sw-codes, officernd-api, officernd-bff) that are not Docker containers?
- What happens if Portainer is restarted -- does it lose configuration or persist state?
- What happens if Evolution API's storage volume runs out of space (media files from WhatsApp)?
- How does the GitHub Actions deployment workflow interact with Portainer-managed containers? → GitHub Actions is source of truth; any manual Portainer changes are overwritten on next deploy.
- What happens if BillionMail's SMTP port (25) is blocked by the VPS provider?
- How does BillionMail's built-in database interact with the existing host PostgreSQL?
- What happens if email sending reputation degrades (IP blacklisting)?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST run Evolution API as a Docker container with persistent data storage (volumes for database and media files).
- **FR-002**: System MUST run Portainer as a Docker container with access to the Docker socket for container management.
- **FR-003**: System MUST provide a unified Docker Compose configuration that includes all Docker-based services (api-scraper, API-CR, Portal, Evolution API, BillionMail, Portainer).
- **FR-004**: System MUST expose Evolution API through nginx reverse proxy at `/evolution/` on noaman.cloud.
- **FR-005**: System MUST expose Portainer through nginx reverse proxy at `/portainer/` on noaman.cloud, including WebSocket support for the real-time UI. Access is protected by Portainer's built-in username/password authentication.
- **FR-006**: System MUST persist Portainer data (users, settings) across container restarts via a named volume.
- **FR-007**: System MUST persist Evolution API data (instances, messages, media) across container restarts via named volumes.
- **FR-008**: System MUST integrate new services into the GitHub Actions deployment workflow.
- **FR-009**: Portainer MUST display all Docker containers on the host, including those from other compose files or standalone containers.
- **FR-010**: Evolution API MUST be configurable via environment variables (API key, database connection, webhook URLs) without rebuilding the container.
- **FR-011**: System MUST use the existing host PostgreSQL instance with a new `evolutiondb` database and dedicated user, following the established pattern used by `officernd` and `scrape-sw-codes`. Evolution API container connects via `host.docker.internal:5432`.
- **FR-012**: System MUST run BillionMail as Docker containers with persistent data storage (volumes for mail data, database, and configuration).
- **FR-013**: System MUST expose BillionMail admin panel and RoundCube webmail via `mail.noaman.cloud` subdomain through nginx reverse proxy (BillionMail's default routing).
- **FR-014**: System MUST persist BillionMail data (emails, campaigns, user accounts, configuration) across container restarts via named volumes.
- **FR-015**: BillionMail MUST be configurable via environment variables (domain, SMTP settings, admin credentials) without rebuilding containers.
- **FR-016**: System MUST expose required mail ports (SMTP 25, submission 587, IMAP 993) on the VPS for BillionMail to send and receive email.

### Key Entities

- **Evolution API Instance**: A WhatsApp connection instance managed by Evolution API. Has connection state (connected/disconnected), QR code for pairing, and message history.
- **Portainer Environment**: The Docker host environment that Portainer manages. Contains stacks, containers, images, volumes, and networks.
- **Docker Network**: Shared network allowing inter-service communication between all containers.
- **BillionMail Instance**: The mail server and marketing platform. Manages email campaigns, subscriber lists, templates, and delivery tracking. Includes RoundCube webmail for end-user email access.
- **Service Configuration**: Environment variables and volumes defining each service's runtime behavior.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All Docker-based services start successfully with a single compose command within 3 minutes.
- **SC-002**: Evolution API health endpoint responds successfully after deployment.
- **SC-003**: Portainer UI loads and displays all running containers within 5 seconds of login.
- **SC-004**: Container restart via Portainer UI completes and service recovers within 30 seconds.
- **SC-005**: A full deployment via GitHub Actions completes successfully with the new services included.
- **SC-006**: All existing services remain accessible via their noaman.cloud URL paths after the restructuring.
- **SC-007**: Data persists across container restarts for Evolution API, BillionMail, and Portainer (no data loss on restart cycles).
- **SC-008**: BillionMail admin panel and RoundCube webmail load successfully via `mail.noaman.cloud`.
- **SC-009**: BillionMail can send a test email successfully after deployment.

## Clarifications

### Session 2026-03-06

- Q: Should Portainer be publicly accessible via noaman.cloud, or restricted? → A: Public via nginx at `/portainer/` with Portainer's built-in username/password authentication.
- Q: Which domain will BillionMail use for sending/receiving email? → A: `noaman.cloud` directly (emails from `user@noaman.cloud`).
- Q: How should Docker Compose be restructured? → A: Single root `docker-compose.yml` combining all Docker services. Per-service files kept for local dev only.
- Q: What is the source of truth for deployments — GitHub Actions or Portainer? → A: GitHub Actions is source of truth. Portainer is for monitoring and debugging only (view logs, restart crashed containers). Manual Portainer changes may be overwritten on next deploy.
- Q: How should BillionMail admin panel and webmail be routed? → A: Subdomain `mail.noaman.cloud` hosts both admin panel and webmail (BillionMail's default behavior).
- Q: What nginx path should Evolution API use on noaman.cloud? → A: `/evolution/` (follows existing naming convention).

## Assumptions

- Evolution API will use the official Docker image from EvolutionAPI (latest stable).
- Portainer Community Edition (free, open-source) is sufficient; Portainer Business Edition is not required.
- The VPS has sufficient resources (RAM, disk) to run the additional containers.
- Host-based PM2 services (scrape-sw-codes, officernd-api, officernd-bff) will remain on the host and will NOT be visible in Portainer (Portainer only manages Docker containers).
- Evolution API will run on a port that does not conflict with existing services (e.g., 8089).
- Portainer will run on port 9000 (HTTP) internally, proxied through nginx.
- A single root `docker-compose.yml` will combine all Docker services (api-scraper, API-CR, Portal, Evolution API, BillionMail, Portainer). Existing per-service compose files are kept for local dev only.
- BillionMail will use its own bundled database (not the host PostgreSQL), as it ships with its own data layer.
- The VPS provider allows outbound SMTP traffic on port 25 (some providers block this by default).
- BillionMail will use `noaman.cloud` as its email domain (emails from `user@noaman.cloud`). DNS MX, SPF, DKIM, and DMARC records must be configured on `noaman.cloud`.
