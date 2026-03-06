# Feature Specification: Evolution API + Portainer Container Management

**Feature Branch**: `002-evolution-portainer`
**Created**: 2026-03-06
**Status**: Draft
**Input**: User description: "https://github.com/EvolutionAPI/evolution-api need to implement this also to docker then restructure to have Portainer ui"

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

### User Story 2 - Portainer UI for Container Management (Priority: P2)

As a platform operator, I want a Portainer web UI to visually manage all Docker containers (existing services + Evolution API), so that I can monitor, start, stop, and inspect containers without SSH and CLI commands.

**Why this priority**: Portainer provides operational visibility and management but is not required for the core services to function. It adds management convenience on top of working services.

**Independent Test**: Can be fully tested by accessing the Portainer UI, seeing all running containers listed, and performing a container restart through the UI.

**Acceptance Scenarios**:

1. **Given** Portainer is deployed, **When** I access the Portainer URL, **Then** I see a login page and can authenticate.
2. **Given** I am logged into Portainer, **When** I view the container list, **Then** I see all project containers (API-SCRAPER, API-CR, PORTAL, Evolution API, etc.) with their status.
3. **Given** I am logged into Portainer, **When** I restart a container through the UI, **Then** the container restarts and the corresponding service recovers.
4. **Given** Portainer is running, **When** I access container logs through the UI, **Then** I can view real-time logs for any container.

---

### User Story 3 - Unified Docker Compose Orchestration (Priority: P2)

As a platform operator, I want all Docker-based services (existing + Evolution API + Portainer) orchestrated under a coherent Docker Compose structure, so that the entire platform can be managed consistently.

**Why this priority**: Restructuring the Docker setup is necessary for Portainer to have visibility into all containers and for consistent deployment. Tied to P2 since it enables Portainer's value.

**Independent Test**: Can be fully tested by running `docker compose up` from the project root and verifying all services start correctly with proper networking.

**Acceptance Scenarios**:

1. **Given** the restructured Docker setup, **When** I run the compose command, **Then** all services (api-scraper, API-CR, Portal, Evolution API, Portainer) start with correct networking.
2. **Given** services are running, **When** one service needs to communicate with another, **Then** inter-service networking works via Docker network.
3. **Given** a new deployment is triggered, **When** GitHub Actions runs the deploy workflow, **Then** the deployment handles the new unified structure correctly.

---

### User Story 4 - Nginx Routing for New Services (Priority: P3)

As an end user, I want Evolution API and Portainer accessible through the existing noaman.cloud domain via dedicated URL paths, so that all services are reachable through one domain.

**Why this priority**: Routing is the final integration step. Services must work first before exposing them publicly.

**Independent Test**: Can be fully tested by accessing the Evolution API and Portainer paths on noaman.cloud and verifying correct proxy behavior.

**Acceptance Scenarios**:

1. **Given** nginx is configured, **When** I access the Evolution API path on noaman.cloud, **Then** requests are proxied to the Evolution API container.
2. **Given** nginx is configured, **When** I access the Portainer path on noaman.cloud, **Then** requests are proxied to the Portainer container (including WebSocket for real-time UI).

---

### Edge Cases

- What happens when Evolution API's database conflicts with the existing host PostgreSQL on port 5432?
- How does Portainer handle containers managed by PM2 on the host (scrape-sw-codes, officernd-api, officernd-bff) that are not Docker containers?
- What happens if Portainer is restarted -- does it lose configuration or persist state?
- What happens if Evolution API's storage volume runs out of space (media files from WhatsApp)?
- How does the GitHub Actions deployment workflow interact with Portainer-managed containers (potential conflict between CI/CD and manual UI actions)?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST run Evolution API as a Docker container with persistent data storage (volumes for database and media files).
- **FR-002**: System MUST run Portainer as a Docker container with access to the Docker socket for container management.
- **FR-003**: System MUST provide a unified Docker Compose configuration that includes all Docker-based services (api-scraper, API-CR, Portal, Evolution API, Portainer).
- **FR-004**: System MUST expose Evolution API through nginx reverse proxy at a dedicated URL path on noaman.cloud.
- **FR-005**: System MUST expose Portainer through nginx reverse proxy at a dedicated URL path on noaman.cloud, including WebSocket support for the real-time UI.
- **FR-006**: System MUST persist Portainer data (users, settings) across container restarts via a named volume.
- **FR-007**: System MUST persist Evolution API data (instances, messages, media) across container restarts via named volumes.
- **FR-008**: System MUST integrate new services into the GitHub Actions deployment workflow.
- **FR-009**: Portainer MUST display all Docker containers on the host, including those from other compose files or standalone containers.
- **FR-010**: Evolution API MUST be configurable via environment variables (API key, database connection, webhook URLs) without rebuilding the container.
- **FR-011**: System MUST ensure Evolution API's database does not conflict with the existing host PostgreSQL instance. [NEEDS CLARIFICATION: Should Evolution API use the existing host PostgreSQL (adding a new database like `evolutiondb`) or run its own database container?]

### Key Entities

- **Evolution API Instance**: A WhatsApp connection instance managed by Evolution API. Has connection state (connected/disconnected), QR code for pairing, and message history.
- **Portainer Environment**: The Docker host environment that Portainer manages. Contains stacks, containers, images, volumes, and networks.
- **Docker Network**: Shared network allowing inter-service communication between all containers.
- **Service Configuration**: Environment variables and volumes defining each service's runtime behavior.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All Docker-based services start successfully with a single compose command within 3 minutes.
- **SC-002**: Evolution API health endpoint responds successfully after deployment.
- **SC-003**: Portainer UI loads and displays all running containers within 5 seconds of login.
- **SC-004**: Container restart via Portainer UI completes and service recovers within 30 seconds.
- **SC-005**: A full deployment via GitHub Actions completes successfully with the new services included.
- **SC-006**: All existing services remain accessible via their noaman.cloud URL paths after the restructuring.
- **SC-007**: Data persists across container restarts for both Evolution API and Portainer (no data loss on restart cycles).

## Assumptions

- Evolution API will use the official Docker image from EvolutionAPI (latest stable).
- Portainer Community Edition (free, open-source) is sufficient; Portainer Business Edition is not required.
- The VPS has sufficient resources (RAM, disk) to run the additional containers.
- Host-based PM2 services (scrape-sw-codes, officernd-api, officernd-bff) will remain on the host and will NOT be visible in Portainer (Portainer only manages Docker containers).
- Evolution API will run on a port that does not conflict with existing services (e.g., 8089).
- Portainer will run on port 9000 (HTTP) internally, proxied through nginx.
- The existing per-service docker-compose.yml files may be consolidated or kept separate depending on the restructuring approach chosen during planning.
