# Data Model: OfficeRnD NestJS BFF

**Date**: 2026-02-08 | **Branch**: `001-officernd-nestjs-bff`

> The BFF has no database. All data is transient (cached in-memory or proxied from FastAPI). These entities describe the response shapes (DTOs) that flow through the BFF.

## Entities

### SyncStatusResponse

Aggregated status returned by `GET /api/officernd/status`. Combines FastAPI `/health` and `/sync/status` into one response.

| Field       | Type    | Description                                              |
| ----------- | ------- | -------------------------------------------------------- |
| success     | boolean | Whether the upstream API calls succeeded                 |
| api_status  | string  | `"online"` or `"offline"`                                |
| companies   | number  | Count of companies from the "companies" sync job         |
| last_sync   | string  | ISO timestamp of last completed sync, or `"Never"`       |
| health      | object  | Raw health response from FastAPI (`{status, service}`)   |
| message     | string  | Error message when `success` is false (optional)         |

### SyncProgressResponse

Real-time progress snapshot returned by `GET /api/officernd/progress`.

| Field     | Type         | Description                                          |
| --------- | ------------ | ---------------------------------------------------- |
| status    | string       | `"idle"`, `"running"`, `"completed"`, or `"error"`   |
| phase     | string       | Current phase name (e.g., `"Phase 1: Global"`)       |
| current   | number       | Current item index within the phase                  |
| total     | number       | Total items in the phase                             |
| endpoint  | string\|null | Current endpoint being synced                        |
| company   | string\|null | Current company name (Phase 2 only)                  |
| message   | string\|null | Human-readable progress description                  |
| error     | string\|null | Error message when status is `"error"`               |
| timestamp | number\|null | Unix timestamp of last progress update               |

### SyncRunRequest

Request body for `POST /api/officernd/sync/run`.

| Field  | Type    | Default         | Description                                      |
| ------ | ------- | --------------- | ------------------------------------------------ |
| mode   | string  | `"full"`        | `"full"` or `"incremental"`                      |
| resume | boolean | `false`         | Whether to resume a previously interrupted sync  |

### SyncRunResponse

Response from `POST /api/officernd/sync/run`.

| Field   | Type    | Description                                             |
| ------- | ------- | ------------------------------------------------------- |
| success | boolean | Whether the sync was triggered successfully             |
| message | string  | Human-readable result (e.g., `"Full sync started"`)     |
| data    | object  | Raw response from FastAPI sync/run endpoint (optional)  |

## State Transitions

### Sync Progress Lifecycle

```
idle → running → completed
                ↘ error
```

- **idle**: No sync in progress (default state, progress file absent or stale)
- **running**: Sync is active, progressing through Phase 1 → 2 → 3
- **completed**: All phases finished successfully
- **error**: Sync encountered a fatal error and stopped

### Cache Lifecycle

```
empty → populated (TTL starts) → expired → empty
                                         ↗ (next request triggers refill)
```

- Status cache TTL: 5000ms
- Progress cache TTL: 2000ms
- Sync/run: No caching (always pass-through)
