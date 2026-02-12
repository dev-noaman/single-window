# Implementation Plan: OfficeRnD NestJS BFF

**Branch**: `001-officernd-nestjs-bff` | **Date**: 2026-02-08 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-officernd-nestjs-bff/spec.md`

## Summary

Replace the PHP web UI layer (`officernd/web/`) with a NestJS Backend-for-Frontend that serves a new React-based terminal-style sync management interface and exposes 3 API endpoints (`/api/officernd/status`, `/api/officernd/progress`, `/api/officernd/sync/run`). The BFF proxies all requests to the existing FastAPI sync API with in-memory caching (5s for status, 2s for progress) to provide instant UI responses. The React frontend (built via `/frontend-design` skill) replaces the old PHP+Tailwind page with a polished, production-grade UI. Old PHP files in `officernd/web/` are removed. Runs directly on the host (no Docker).

## Technical Context

**Language/Version**: TypeScript 5.x, Node.js 20+
**Primary Dependencies**: NestJS 10, @nestjs/axios, @nestjs/cache-manager, @nestjs/serve-static, React 18, Vite
**Storage**: None (in-memory cache only; no database access)
**Testing**: Jest (included with NestJS CLI scaffold)
**Target Platform**: Linux/Windows host, port 8088
**Project Type**: Web (BFF - backend serving static frontend + API proxy)
**Performance Goals**: Status response <1s cold, <100ms cached; progress polling every 3s
**Constraints**: No Docker for BFF; host-only with npm scripts; must match existing PHP response shapes exactly
**Scale/Scope**: Single admin user; 3 API endpoints; React SPA (built to static files)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Constitution is a blank template (not customized for this project). No gates to enforce. Proceeding with standard NestJS best practices.

**Post-Phase 1 Re-check**: N/A (no constitution rules defined).

## Project Structure

### Documentation (this feature)

```text
specs/001-officernd-nestjs-bff/
├── plan.md              # This file
├── spec.md              # Feature specification
├── research.md          # Phase 0: Technology decisions
├── data-model.md        # Phase 1: DTO shapes and state transitions
├── quickstart.md        # Phase 1: Setup and run instructions
├── contracts/
│   └── openapi.yaml     # Phase 1: API contract (OpenAPI 3.0)
└── checklists/
    └── requirements.md  # Spec quality validation
```

### Source Code (repository root)

```text
officernd/bff/
├── package.json
├── tsconfig.json
├── tsconfig.build.json
├── nest-cli.json
├── .env.example
├── public/                          # React build output (served by NestJS)
│   ├── index.html                   # Vite build output
│   └── assets/                      # JS/CSS bundles
├── frontend/                        # React SPA source (built via /frontend-design)
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── index.html                   # Vite entry HTML
│   └── src/
│       ├── main.tsx                 # React entry point
│       ├── App.tsx                  # Root component
│       ├── components/
│       │   ├── Terminal.tsx         # Terminal log display
│       │   ├── StatusBar.tsx        # Company count, last sync, API health
│       │   ├── ActionButtons.tsx    # FETCH, INCREMENT, STATUS buttons
│       │   └── ProgressLine.tsx     # Single terminal log line
│       ├── hooks/
│       │   ├── useStatus.ts        # Fetch + cache status from BFF
│       │   └── useSync.ts          # Trigger sync + poll progress
│       └── api/
│           └── officernd.ts         # API client (fetch wrappers)
├── src/                             # NestJS backend
│   ├── main.ts                      # Bootstrap, port config
│   ├── app.module.ts                # Root module: CacheModule, HttpModule, ServeStaticModule
│   └── officernd/
│       ├── officernd.module.ts      # Feature module
│       ├── officernd.controller.ts  # 3 endpoints: status, progress, sync/run
│       ├── officernd.service.ts     # Business logic: upstream calls, caching
│       └── dto/
│           ├── sync-status.dto.ts
│           ├── sync-progress.dto.ts
│           └── sync-run.dto.ts
└── test/
    └── officernd.controller.spec.ts # Unit tests for controller
```

### Files to Remove (cleanup)

```text
officernd/web/                       # Entire PHP web UI directory
├── index.php                        # Replaced by React SPA
├── status.php                       # Replaced by GET /api/officernd/status
├── progress.php                     # Replaced by GET /api/officernd/progress
├── trigger-fetch.php                # Replaced by POST /api/officernd/sync/run
└── trigger-increment.php            # Replaced by POST /api/officernd/sync/run

officernd/Dockerfile.web             # No longer needed (officernd runs on host, not Docker)
```

**Structure Decision**: Single NestJS project within `officernd/bff/` with an embedded React frontend. The `frontend/` directory contains the Vite+React SPA source; `npm run build:frontend` compiles it into `public/` which NestJS serves via `ServeStaticModule`. The old `officernd/web/` PHP files and `Dockerfile.web` are deleted since the BFF replaces them entirely.

## Complexity Tracking

No complexity violations. The project is minimal:
- Backend: 1 module, 1 controller, 1 service, 3 DTOs
- Frontend: React SPA with ~5 components, 2 hooks, 1 API client
- No database, no auth, no WebSocket
- Standard NestJS + Vite+React patterns throughout

## Design Decisions

### D1: Module Structure

Single `OfficerndModule` containing one controller and one service. No separate modules for caching or HTTP since the app has only 3 endpoints.

### D2: Caching Approach

Manual cache via `CACHE_MANAGER` injection in the service layer:
- `getStatus()`: Cache key `officernd:status`, TTL 5000ms
- `getProgress()`: Cache key `officernd:progress`, TTL 2000ms
- `triggerSync()`: No caching (pass-through)

This gives precise per-method TTL control without the global `CacheInterceptor`.

### D3: Static File Serving

`ServeStaticModule.forRoot({ rootPath: join(__dirname, '..', 'public') })` serves the React build output (`index.html` + `assets/`). The React SPA lives in `frontend/` and is built with Vite to `public/` via `npm run build:frontend`. NestJS serves these as static files; all non-`/api` routes fall through to `index.html` (SPA routing).

### D4: Error Handling

When FastAPI is unreachable:
- Status endpoint returns `{ success: false, api_status: "offline", companies: 0, last_sync: "Never", message: "<error>" }`
- Progress endpoint returns idle state: `{ status: "idle", phase: "", current: 0, total: 0, message: "No sync running" }`
- Sync trigger returns `{ success: false, message: "Connection failed: <error>" }`

These match the current PHP error responses exactly.

### D5: React Frontend (via `/frontend-design`)

A new React SPA replaces the old PHP `index.php` entirely. Built using the `/frontend-design` skill for a polished, production-grade terminal-style UI. Key components:

- **Terminal.tsx**: Scrollable log display with animated line entries, colored by type (info, error, success, phase)
- **StatusBar.tsx**: Header bar showing company count, last sync timestamp, API health indicator
- **ActionButtons.tsx**: FETCH (full sync), INCREMENT (new only), STATUS buttons with disabled states during sync
- **ProgressLine.tsx**: Single formatted log line component

API integration via custom hooks:
- **useStatus()**: Fetches `GET /api/officernd/status` on mount and on STATUS button click
- **useSync()**: Triggers `POST /api/officernd/sync/run`, then polls `GET /api/officernd/progress` every 3s until completed/error

The React app is built with Vite. `vite.config.ts` sets `build.outDir` to `../public` so the NestJS `ServeStaticModule` can serve it directly.

### D7: PHP Cleanup

Delete the entire `officernd/web/` directory since the BFF+React replaces them:
- `index.php` → React SPA
- `status.php` → `GET /api/officernd/status`
- `progress.php` → `GET /api/officernd/progress`
- `trigger-fetch.php` → `POST /api/officernd/sync/run { mode: "full" }`
- `trigger-increment.php` → `POST /api/officernd/sync/run { mode: "incremental" }`

Also delete `officernd/Dockerfile.web` (leftover from when officernd had a Docker setup; no longer used).

### D6: Port and Deployment

The BFF listens on port 8088 (configurable via `PORT` env var), replacing the PHP dev server on the same port. All officernd services run directly on the host (FastAPI at :8000, BFF at :8088, PostgreSQL at :5432). No Docker involved. Started with `npm run start:prod`.
