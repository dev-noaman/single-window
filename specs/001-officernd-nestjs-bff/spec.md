# Feature Specification: OfficeRnD NestJS BFF (Backend-for-Frontend)

**Feature Branch**: `001-officernd-nestjs-bff`
**Created**: 2026-02-08
**Status**: Draft
**Input**: User description: "Implement a NestJS BFF for the officernd project so the officernd web UI is served by Node.js and gets fast responses via caching. Replace the PHP layer with a NestJS app that serves the same web UI and exposes a small API with in-memory caching."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - View Sync Status Instantly (Priority: P1)

As a platform administrator, I want to open the OfficeRnD web UI and immediately see the current sync status (number of companies in database, last sync timestamp, API health) without noticeable delay, so I can quickly assess the system state.

**Why this priority**: The status check is the most frequently used action. Every session starts with this. Fast, cached responses make the UI feel responsive and reliable.

**Independent Test**: Can be fully tested by opening the web UI at port 8088, verifying the status display loads within 1 second, and confirming the data matches what the underlying sync API reports.

**Acceptance Scenarios**:

1. **Given** the BFF is running and the sync API is healthy, **When** the user opens the web UI, **Then** the status panel shows company count, last sync time, and API status within 1 second.
2. **Given** the user has already loaded status within the last 10 seconds, **When** they click STATUS again, **Then** the response is served from cache (sub-100ms) without hitting the sync API.
3. **Given** the sync API is unreachable, **When** the user opens the web UI, **Then** the status panel shows "offline" for the API status with an appropriate error message, without crashing.

---

### User Story 2 - Trigger and Monitor Full Sync (Priority: P1)

As a platform administrator, I want to start a full data sync and watch its progress in real-time through a terminal-style log, so I can see which phase, company, and endpoint is being processed and know when it completes.

**Why this priority**: Full sync is the primary operational task. The 3-phase progress display (global endpoints, per-company, dependent) is critical for understanding what the system is doing across 579 companies and 30+ endpoints.

**Independent Test**: Can be fully tested by clicking the FETCH button, verifying a full sync starts, and watching the terminal log update every 3 seconds with phase, company, endpoint, and progress counts until completion.

**Acceptance Scenarios**:

1. **Given** no sync is running, **When** the user clicks the FETCH button, **Then** the BFF forwards the request to the sync API with mode "full" and the terminal log begins showing progress updates.
2. **Given** a sync is in progress, **When** the UI polls for progress every 3 seconds, **Then** it receives updated phase, company name, endpoint, current/total counts, and a descriptive message.
3. **Given** the sync completes, **When** the progress response returns status "completed", **Then** the UI stops polling and shows a completion message with final statistics.
4. **Given** the sync encounters an error, **When** the progress response returns status "error", **Then** the UI stops polling and shows the error message clearly.

---

### User Story 3 - Trigger Incremental Sync (Priority: P2)

As a platform administrator, I want to start an incremental sync that only processes new companies, so I can update the database quickly without re-syncing all existing data.

**Why this priority**: Incremental sync is a time-saving alternative to full sync, used daily for catching new companies. It shares the same progress monitoring flow as full sync.

**Independent Test**: Can be fully tested by clicking the INCREMENT button, verifying the sync starts with mode "incremental", and watching the terminal log show progress for only new companies.

**Acceptance Scenarios**:

1. **Given** no sync is running, **When** the user clicks the INCREMENT button, **Then** the BFF forwards the request to the sync API with mode "incremental" and the terminal log begins showing progress.
2. **Given** there are no new companies, **When** an incremental sync runs, **Then** it completes quickly with a message indicating zero new companies were found.

---

### User Story 4 - Cached Progress Polling (Priority: P2)

As the web UI, I want progress polling to feel snappy even under rapid repeated requests, so that the terminal log updates smoothly without overloading the sync API.

**Why this priority**: Progress is polled every 3 seconds. Short-lived caching (1-2 seconds) prevents duplicate requests from hammering the backend while still showing near-real-time data.

**Independent Test**: Can be tested by triggering a sync, then verifying that two rapid progress requests within 1 second return the same cached response without hitting the sync API twice.

**Acceptance Scenarios**:

1. **Given** a sync is running, **When** the UI polls progress twice within 1 second, **Then** only one request reaches the sync API and the second receives a cached response.
2. **Given** a sync is running, **When** more than 2 seconds elapse since the last progress fetch, **Then** the next poll fetches fresh data from the sync API.

---

### Edge Cases

- What happens when the sync API is completely down during a sync trigger? The BFF returns a clear error response indicating the sync API is unreachable.
- What happens when the progress file does not exist (no sync has ever run)? The BFF returns an idle state with all counts at zero.
- What happens when the user triggers a sync while one is already running? The sync API handles this internally (returns an error or queues); the BFF forwards the response as-is.
- What happens when cached status data is stale but the API has recovered? After the cache TTL expires (5-10 seconds), the next request fetches fresh data reflecting the recovered state.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST expose a GET endpoint that returns combined sync status (company count, last sync time, API health) in a single response matching the current status shape.
- **FR-002**: System MUST cache status responses for 5-10 seconds to avoid redundant calls to the sync API on repeated requests.
- **FR-003**: System MUST expose a GET endpoint that returns real-time sync progress (phase, status, current/total counts, endpoint, company name, message, error, timestamp).
- **FR-004**: System MUST cache progress responses for 1-2 seconds to smooth out rapid polling.
- **FR-005**: System MUST expose a POST endpoint that triggers a sync operation, accepting mode ("full" or "incremental") and an optional resume flag, forwarding to the sync API without caching.
- **FR-006**: System MUST serve a new React-based web UI as static files so the complete interface is accessible from a single service.
- **FR-007**: The React UI MUST call the BFF API endpoints for all data (status, progress, sync trigger). No PHP endpoints remain.
- **FR-008**: System MUST provide a polished terminal-style UI with: scrollable log display, three action buttons (FETCH, INCREMENT, STATUS), 3-second progress polling, and visual improvements over the current PHP page.
- **FR-013**: The old PHP web UI files (`officernd/web/`) MUST be removed from the repository since they are fully replaced by the BFF.
- **FR-009**: System MUST use in-memory caching by default, with no external dependencies required for basic operation.
- **FR-010**: System MUST be configurable via environment variables for the sync API base URL and organization slug.
- **FR-011**: System MUST gracefully handle sync API unavailability by returning appropriate error responses without crashing.
- **FR-012**: System MUST run directly on the host machine (no Docker container) and connect to the sync API at a configurable localhost URL.

### Key Entities

- **Sync Status**: Aggregated view of API health and per-endpoint sync results. Key attributes: success flag, API online/offline status, total company count, last sync timestamp, raw health data.
- **Sync Progress**: Real-time snapshot of an active sync operation. Key attributes: phase name, running/completed/error/idle status, current count, total count, current endpoint, current company name, descriptive message, error details, timestamp.
- **Sync Request**: A command to start a sync operation. Key attributes: mode (full or incremental), resume flag.

## Assumptions

- The sync API is running on the same host and accessible at a configurable localhost URL (default: http://localhost:8000).
- PostgreSQL runs on the host machine; the BFF does not interact with the database directly.
- The organization slug is a static configuration value (e.g., "arafat-business-centers") set via environment variable.
- The progress file at /tmp/officernd_sync_progress.json is written by the sync API's background process and may be used as an alternative progress source.
- The web UI will be rebuilt as a React SPA (via `/frontend-design` skill) with a polished design, replacing the old PHP page entirely.
- No authentication is required for the BFF endpoints (matching the current unauthenticated PHP layer).
- No Docker configuration is needed for the BFF; it runs directly on the host with npm scripts.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users see sync status within 1 second of opening the web UI, compared to 2-3 seconds with the PHP layer.
- **SC-002**: Repeated status requests within 10 seconds return in under 100 milliseconds (served from cache).
- **SC-003**: Progress polling updates the terminal log every 3 seconds without missed updates or UI lag.
- **SC-004**: All three sync operations (full sync, incremental sync, status check) work correctly with a visually improved UI compared to the current PHP-based interface.
- **SC-005**: The BFF starts and serves the UI with a single command (npm start) and requires only two environment variables to configure.
- **SC-006**: The web UI is fully functional when served by the BFF, with no broken features compared to the PHP version.
