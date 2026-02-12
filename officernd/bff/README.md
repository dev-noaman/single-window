# OfficeRnD NestJS BFF

Backend-for-Frontend (BFF) for OfficeRnD sync management UI.

## Overview

This is a NestJS-based BFF that serves a React frontend and provides a cached proxy to the OfficeRnD FastAPI backend. The BFF provides:

- **Status Display**: View company count, last sync time, and API health with 5-second caching
- **Full Sync**: Trigger complete sync operations with real-time terminal progress
- **Incremental Sync**: Trigger incremental sync for new companies only
- **Cached Progress**: Progress polling with 2-second caching for snappy UI

## Tech Stack

- **Backend**: NestJS with TypeScript
- **Frontend**: React with Vite
- **Caching**: NestJS CacheManager (in-memory)
- **HTTP Client**: NestJS HttpService (Axios)
- **Styling**: Inline CSS with terminal-style dark theme

## Project Structure

```
officernd/bff/
├── src/
│   ├── main.ts                 # NestJS bootstrap
│   ├── app.module.ts            # Root module with global config
│   └── officernd/
│       ├── officernd.module.ts   # Feature module
│       ├── officernd.controller.ts  # API routes
│       ├── officernd.service.ts     # Business logic & caching
│       └── dto/
│           ├── sync-status.dto.ts
│           ├── sync-progress.dto.ts
│           └── sync-run.dto.ts
├── frontend/
│   ├── src/
│   │   ├── main.tsx            # React entry point
│   │   ├── App.tsx             # Root component
│   │   ├── index.css            # Global styles & animations
│   │   ├── api/
│   │   │   └── officernd.ts    # API client
│   │   ├── hooks/
│   │   │   ├── useStatus.ts    # Status hook
│   │   │   └── useSync.ts      # Sync hook
│   │   └── components/
│   │       ├── StatusBar.tsx    # Status display
│   │       ├── Terminal.tsx     # Log viewer
│   │       ├── ProgressLine.tsx # Single log line
│   │       └── ActionButtons.tsx # Sync buttons
│   ├── package.json
│   ├── vite.config.ts
│   └── tsconfig.json
├── public/                      # Built React output (served by NestJS)
├── package.json
├── tsconfig.json
├── nest-cli.json
├── .env.example
└── .env
```

## API Endpoints

### GET /api/officernd/status
Returns combined sync status with company count, last sync time, and API health.
- **Cache**: 5 seconds
- **Response**: `SyncStatusResponse`

### GET /api/officernd/progress
Returns real-time sync progress with phase, counts, and messages.
- **Cache**: 2 seconds
- **Response**: `SyncProgressResponse`

### POST /api/officernd/sync/run
Triggers a sync operation (full or incremental).
- **Cache**: Never (always pass-through)
- **Request**: `{ mode: 'full' | 'incremental', resume?: boolean }`
- **Response**: `SyncRunResponse`

## Installation

### Prerequisites

- Node.js 18+
- npm or yarn
- OfficeRnD FastAPI backend running on port 8000

### Setup

1. Copy environment variables:
   ```bash
   cp .env.example .env
   ```

2. Install backend dependencies:
   ```bash
   npm install
   ```

3. Install frontend dependencies:
   ```bash
   cd frontend
   npm install
   ```

## Development

### Start Backend (NestJS)

```bash
npm run start:dev
```

The BFF will start on port 8088.

### Start Frontend (Vite Dev Server)

```bash
cd frontend
npm run dev
```

The frontend dev server will start on port 5173.

## Production Build

### Build Frontend

```bash
cd frontend
npm run build
```

This builds the React app to `../public/` which is served by NestJS.

### Build Backend

```bash
npm run build
```

This compiles TypeScript to `dist/`.

### Start Production Server

```bash
npm run start:prod
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OFFICERND_API_URL` | FastAPI backend URL | `http://localhost:8000` |
| `OFFICERND_ORG_SLUG` | Organization slug | `arafat-business-centers` |
| `PORT` | BFF server port | `8088` |

## Usage

1. Open http://localhost:8088 in your browser
2. View status panel showing API health, company count, and last sync time
3. Click **FETCH** to start a full sync with terminal progress
4. Click **INCREMENT** to start an incremental sync for new companies
5. Click **STATUS** to refresh the status display (cached for 5 seconds)
6. Watch the terminal for real-time sync progress with colored log types

## UI Features

- **Terminal-style dark theme** with gradient background
- **Real-time progress** with 3-second polling
- **Color-coded log types**:
  - 🔴 `[ERROR]` - Red for errors
  - 🟢 `[SUCCESS]` - Green for success
  - 🟠 `[PHASE]` - Orange for phase changes
  - ⚪ `[INFO]` - Gray for general info
- **Smooth animations** for log entries and button hover states
- **Responsive layout** that wraps on smaller screens
- **Auto-scrolling** terminal to latest log entries

## Caching Strategy

- **Status endpoint**: 5-second TTL to avoid hammering FastAPI
- **Progress endpoint**: 2-second TTL for snappy polling
- **Sync/run endpoint**: No caching (always fresh request)

## VPS Deployment

The BFF runs as a host service (not Docker) managed by PM2:

```bash
# Deployed automatically via Deploy-to-Docker.ps1
# On VPS, the service runs at /root/scrapers/officernd/bff

# Manual PM2 management:
pm2 start dist/main.js --name officernd-bff
pm2 stop officernd-bff
pm2 restart officernd-bff
pm2 logs officernd-bff
```

The `Deploy-to-Docker.ps1` script handles the full deployment:
1. Archives `officernd/bff/` (excludes `node_modules`)
2. Uploads and extracts on VPS
3. Copies `.env` from `officernd/config/.env` (BFF vars)
4. Runs `npm install` + frontend build + backend build
5. Starts/restarts via PM2

## Quick Start

```bash
# 1. Setup
cp .env.example .env
npm install
cd frontend && npm install && npm run build && cd ..

# 2. Build & run
npm run build
npm run start:prod

# 3. Open http://localhost:8088
```
