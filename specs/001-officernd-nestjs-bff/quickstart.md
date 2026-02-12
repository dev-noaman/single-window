# Quickstart: OfficeRnD NestJS BFF

## Prerequisites

- Node.js 20+
- npm 9+
- FastAPI sync API running on localhost:8000 (or other configured URL)
- PostgreSQL running on the host machine (used by FastAPI, not by BFF directly)

## Setup

```bash
cd officernd/bff

# Install backend dependencies
npm install

# Install frontend dependencies and build React SPA
cd frontend && npm install && npm run build && cd ..

# Configure environment
cp .env.example .env
# Edit .env if needed (defaults work for local development)
```

## Environment Variables

| Variable           | Default                 | Description                     |
| ------------------ | ----------------------- | ------------------------------- |
| OFFICERND_API_URL  | http://localhost:8000   | FastAPI sync API base URL       |
| OFFICERND_ORG_SLUG | arafat-business-centers | Organization slug for API calls |
| PORT               | 8088                    | BFF server port                 |

## Run

```bash
# Development (watch mode - backend only, frontend must be pre-built)
npm run start:dev

# Production
npm run build
npm run start:prod

# Rebuild frontend after UI changes
cd frontend && npm run build
```

## Verify

1. Open http://localhost:8088 in a browser - you should see the React terminal-style sync UI.
2. Click STATUS - should show company count and last sync time.
3. Click FETCH - should start a full sync and show progress in the terminal log.

## Endpoints

| Method | Path                    | Description             |
| ------ | ----------------------- | ----------------------- |
| GET    | /                       | React SPA (static)      |
| GET    | /api/officernd/status   | Combined sync status    |
| GET    | /api/officernd/progress | Real-time sync progress |
| POST   | /api/officernd/sync/run | Trigger sync operation  |

## Cleanup Note

The following files were removed (replaced by this BFF):
- `officernd/web/` (all PHP files)
- `officernd/Dockerfile.web`
