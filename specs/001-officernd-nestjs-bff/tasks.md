# Tasks: OfficeRnD NestJS BFF

**Input**: Design documents from `/specs/001-officernd-nestjs-bff/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/openapi.yaml

**Tests**: Not explicitly requested in the feature specification. Test tasks are omitted.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `officernd/bff/src/`
- **Frontend**: `officernd/bff/frontend/src/`
- **Static output**: `officernd/bff/public/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize the NestJS project, React frontend scaffold, and environment configuration

- [x] T001 Create NestJS project scaffold at `officernd/bff/` with package.json, tsconfig.json, tsconfig.build.json, nest-cli.json
- [x] T002 Install NestJS dependencies: @nestjs/core, @nestjs/common, @nestjs/platform-express, @nestjs/axios, @nestjs/cache-manager, @nestjs/serve-static, cache-manager, rxjs, reflect-metadata in `officernd/bff/package.json`
- [x] T003 Create `.env.example` at `officernd/bff/.env.example` with OFFICERND_API_URL=http://localhost:8000, OFFICERND_ORG_SLUG=arafat-business-centers, PORT=8088
- [x] T004 Create Vite+React project scaffold at `officernd/bff/frontend/` with package.json, vite.config.ts (outDir: ../public), tsconfig.json, index.html
- [x] T005 Install React dependencies: react, react-dom, @types/react, @types/react-dom, typescript, vite, @vitejs/plugin-react in `officernd/bff/frontend/package.json`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core NestJS module wiring, DTOs, and service skeleton that ALL user stories depend on

**CRITICAL**: No user story work can begin until this phase is complete

- [x] T006 Create app bootstrap in `officernd/bff/src/main.ts` — read PORT from env (default 8088), start NestJS app
- [x] T007 Create root module in `officernd/bff/src/app.module.ts` — import CacheModule.register({ ttl: 5000, isGlobal: true }), HttpModule, ServeStaticModule.forRoot({ rootPath: join(__dirname, '..', 'public') }), OfficerndModule
- [x] T008 [P] Create SyncStatusDto in `officernd/bff/src/officernd/dto/sync-status.dto.ts` — fields: success, api_status, companies, last_sync, health, message (per data-model.md SyncStatusResponse)
- [x] T009 [P] Create SyncProgressDto in `officernd/bff/src/officernd/dto/sync-progress.dto.ts` — fields: status, phase, current, total, endpoint, company, message, error, timestamp (per data-model.md SyncProgressResponse)
- [x] T010 [P] Create SyncRunDto (request) in `officernd/bff/src/officernd/dto/sync-run.dto.ts` — fields: mode ('full'|'incremental', default 'full'), resume (boolean, default false); also SyncRunResponseDto: success, message, data
- [x] T011 Create OfficerndModule in `officernd/bff/src/officernd/officernd.module.ts` — imports HttpModule.register({ timeout: 10000 }), provides OfficerndService, declares OfficerndController
- [x] T012 Create OfficerndService skeleton in `officernd/bff/src/officernd/officernd.service.ts` — inject CACHE_MANAGER, HttpService, ConfigService; read OFFICERND_API_URL and OFFICERND_ORG_SLUG from env; stub getStatus(), getProgress(), triggerSync() methods
- [x] T013 Create OfficerndController skeleton in `officernd/bff/src/officernd/officernd.controller.ts` — inject OfficerndService; declare GET /api/officernd/status, GET /api/officernd/progress, POST /api/officernd/sync/run with correct decorators
- [x] T014 Create React entry point in `officernd/bff/frontend/src/main.tsx` and root App component in `officernd/bff/frontend/src/App.tsx` with placeholder layout

**Checkpoint**: NestJS starts on port 8088, serves empty React page, controller routes respond with 200 stubs

---

## Phase 3: User Story 1 — View Sync Status Instantly (Priority: P1) MVP

**Goal**: Admin opens the web UI and immediately sees company count, last sync time, and API health — cached for 5 seconds

**Independent Test**: Open http://localhost:8088, verify status panel loads within 1 second with correct data. Click STATUS again within 5 seconds and confirm sub-100ms response.

### Implementation for User Story 1

- [x] T015 [US1] Implement `getStatus()` in `officernd/bff/src/officernd/officernd.service.ts` — check cache key `officernd:status`; if miss, call GET {API_URL}/health and GET {API_URL}/api/v2/organizations/{org_slug}/sync/status in parallel; extract companies count from 'companies' endpoint record where status==='completed' (records_upserted or records_fetched); extract last_sync from first record with last_run; combine into SyncStatusDto { success: true, api_status: 'online', companies, last_sync, health }; cache result with TTL 5000ms; on error return { success: false, api_status: 'offline', companies: 0, last_sync: 'Never', message: error.message }
- [x] T016 [US1] Wire `GET /api/officernd/status` in `officernd/bff/src/officernd/officernd.controller.ts` — call service.getStatus(), return result
- [x] T017 [P] [US1] Create API client in `officernd/bff/frontend/src/api/officernd.ts` — export fetchStatus(): Promise<SyncStatusResponse> calling GET /api/officernd/status; export fetchProgress(): Promise<SyncProgressResponse>; export triggerSync(mode, resume?): Promise<SyncRunResponse> calling POST /api/officernd/sync/run
- [x] T018 [P] [US1] Create useStatus hook in `officernd/bff/frontend/src/hooks/useStatus.ts` — call fetchStatus on mount; expose { status, loading, refresh } state; refresh function for STATUS button
- [x] T019 [US1] Create StatusBar component in `officernd/bff/frontend/src/components/StatusBar.tsx` — display company count, last sync timestamp, API status indicator (online/offline with color); use useStatus hook
- [x] T020 [US1] Integrate StatusBar into App.tsx in `officernd/bff/frontend/src/App.tsx` — add header with "> OFFICERND_SYNC" title and StatusBar; add STATUS button that calls refresh; apply terminal-style dark theme
- [x] T021 [US1] Build frontend and verify: run `npm run build` in `officernd/bff/frontend/`, confirm `officernd/bff/public/index.html` is generated, start NestJS, open http://localhost:8088, verify status loads

**Checkpoint**: User Story 1 fully functional — status display with caching, React UI served by NestJS

---

## Phase 4: User Story 2 — Trigger and Monitor Full Sync (Priority: P1)

**Goal**: Admin clicks FETCH, full sync starts, terminal log shows real-time progress every 3 seconds until completion or error

**Independent Test**: Click FETCH button, verify sync starts (terminal shows "Sync started"), watch progress lines appear every 3s with phase/company/endpoint/counts, confirm terminal shows completion message when done.

### Implementation for User Story 2

- [x] T022 [US2] Implement `triggerSync(body)` in `officernd/bff/src/officernd/officernd.service.ts` — POST to {API_URL}/api/v2/organizations/{org_slug}/sync/run with body { mode, resume }; return { success: true, message: `${mode} sync started`, data: response }; on error return { success: false, message: `Connection failed: ${error.message}` }
- [x] T023 [US2] Implement `getProgress()` in `officernd/bff/src/officernd/officernd.service.ts` — check cache key `officernd:progress`; if miss, GET {API_URL}/api/v2/organizations/{org_slug}/sync/progress; cache with TTL 2000ms; on error return idle state { status: 'idle', phase: '', current: 0, total: 0, message: 'No sync running' }
- [x] T024 [US2] Wire `POST /api/officernd/sync/run` and `GET /api/officernd/progress` in `officernd/bff/src/officernd/officernd.controller.ts` — POST calls service.triggerSync(body), GET calls service.getProgress()
- [x] T025 [P] [US2] Create ProgressLine component in `officernd/bff/frontend/src/components/ProgressLine.tsx` — render a single terminal log line with timestamp, colored type prefix ([ERROR] red, [SUCCESS] green, [PHASE] orange, [time] gray), message text, slide-in animation
- [x] T026 [P] [US2] Create Terminal component in `officernd/bff/frontend/src/components/Terminal.tsx` — scrollable container with dark background; renders list of ProgressLine entries; auto-scrolls to bottom on new entries; initial system message "OfficeRnD Sync Terminal ready..."
- [x] T027 [US2] Create useSync hook in `officernd/bff/frontend/src/hooks/useSync.ts` — expose { logs, isPolling, startSync(mode), stopSync }; startSync(mode) calls triggerSync API then starts 3s polling via setInterval calling fetchProgress; append progress to logs (deduplicate by message); stop polling on status 'completed' or 'error'; add completion/error log entry; call useStatus.refresh on completion
- [x] T028 [US2] Create ActionButtons component in `officernd/bff/frontend/src/components/ActionButtons.tsx` — FETCH button calls startSync('full'), text changes to "SYNCING..." when polling; disabled state during active sync; styled with orange border/hover per terminal theme
- [x] T029 [US2] Integrate Terminal and ActionButtons into App.tsx in `officernd/bff/frontend/src/App.tsx` — add Terminal below header, FETCH button in header next to STATUS; wire useSync hook; pass logs to Terminal
- [x] T030 [US2] Build frontend and verify full sync flow end-to-end

**Checkpoint**: User Stories 1 AND 2 both work — status + full sync with live terminal progress

---

## Phase 5: User Story 3 — Trigger Incremental Sync (Priority: P2)

**Goal**: Admin clicks INCREMENT, incremental sync starts with mode "incremental", same terminal progress monitoring

**Independent Test**: Click INCREMENT button, verify sync starts with "incremental" mode, terminal shows progress for new companies only.

### Implementation for User Story 3

- [x] T031 [US3] Add INCREMENT button to ActionButtons component in `officernd/bff/frontend/src/components/ActionButtons.tsx` — calls startSync('incremental'), text changes to "SYNCING..." when polling; yellow border/hover; disabled during active sync
- [x] T032 [US3] Verify incremental sync flow: click INCREMENT, confirm POST body has mode:'incremental', watch terminal progress

**Checkpoint**: All three sync operations (status, full sync, incremental sync) work

---

## Phase 6: User Story 4 — Cached Progress Polling (Priority: P2)

**Goal**: Progress polling feels snappy; duplicate requests within 2 seconds are served from cache without hitting FastAPI

**Independent Test**: Trigger a sync, verify that two rapid progress requests within 1 second return the same cached data.

### Implementation for User Story 4

- [x] T033 [US4] Verify progress caching in `officernd/bff/src/officernd/officernd.service.ts` — confirm getProgress() checks cache before HTTP call; TTL is 2000ms; two calls within 2s return same object without second HTTP call to FastAPI

**Checkpoint**: Caching verified for both status (5s) and progress (2s) endpoints

---

## Phase 7: React UI Polish via /frontend-design

**Purpose**: Use `/frontend-design` skill to create a polished, production-grade terminal-style UI

- [x] T034 Use `/frontend-design` skill to design the complete React UI in `officernd/bff/frontend/src/` — terminal-style dark theme, polished components (Terminal, StatusBar, ActionButtons, ProgressLine), responsive layout, smooth animations, professional color scheme (dark bg, orange accents, green success, red errors)
- [x] T035 Final frontend build and verify all UI interactions in `officernd/bff/frontend/`

---

## Phase 8: Cleanup & Cross-Cutting Concerns

**Purpose**: Remove old PHP files and finalize

- [x] T036 Delete `officernd/web/` directory (index.php, status.php, progress.php, trigger-fetch.php, trigger-increment.php)
- [x] T037 Run quickstart.md validation: npm install, build frontend, start BFF, open http://localhost:8088, verify status/fetch/increment all work

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion — BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational — can start after Phase 2
- **User Story 2 (Phase 4)**: Depends on Foundational — can start after Phase 2 (parallel with US1 if desired, but recommended after US1 since US2 uses the API client created in US1)
- **User Story 3 (Phase 5)**: Depends on User Story 2 (reuses ActionButtons and useSync hook)
- **User Story 4 (Phase 6)**: Depends on User Story 2 (verifies caching behavior for progress endpoint)
- **UI Polish (Phase 7)**: Depends on all user stories being functional
- **Cleanup (Phase 8)**: Depends on Phase 7 (new UI confirmed working before deleting old PHP)

### User Story Dependencies

- **US1 (Status)**: Independent — only needs Foundational
- **US2 (Full Sync)**: Independent from US1 but recommended after (reuses API client T017)
- **US3 (Incremental Sync)**: Depends on US2 (extends ActionButtons, reuses useSync hook)
- **US4 (Cached Polling)**: Depends on US2 (verifies caching behavior during active sync)

### Within Each User Story

- DTOs/models before service logic
- Service before controller
- API client before hooks
- Hooks before components
- Components before App integration
- Build + verify as final step

### Parallel Opportunities

**Phase 1**: T001-T005 can all run sequentially (project init order matters)
**Phase 2**: T008, T009, T010 (DTOs) can run in parallel; T014 (React entry) is parallel with T011-T013
**Phase 3 (US1)**: T017 (API client) and T018 (hook) are parallel with T015-T016 (backend)
**Phase 4 (US2)**: T025, T026 (components) are parallel; parallel with T022-T024 (backend)
**Phase 8**: T036 (delete PHP) then T037 (validate) — sequential

---

## Parallel Example: User Story 1

```bash
# Backend and frontend can be built in parallel:
# Backend track:
Task T015: "Implement getStatus() in officernd/bff/src/officernd/officernd.service.ts"
Task T016: "Wire GET /api/officernd/status in officernd/bff/src/officernd/officernd.controller.ts"

# Frontend track (parallel with backend):
Task T017: "Create API client in officernd/bff/frontend/src/api/officernd.ts"
Task T018: "Create useStatus hook in officernd/bff/frontend/src/hooks/useStatus.ts"

# Then integrate (depends on both tracks):
Task T019: "Create StatusBar component"
Task T020: "Integrate into App.tsx"
Task T021: "Build and verify"
```

---

## Parallel Example: User Story 2

```bash
# Backend and frontend components in parallel:
# Backend track:
Task T022: "Implement triggerSync() in service"
Task T023: "Implement getProgress() in service"
Task T024: "Wire POST and GET endpoints in controller"

# Frontend track (parallel with backend):
Task T025: "Create ProgressLine component"
Task T026: "Create Terminal component"

# Then integrate (depends on both tracks):
Task T027: "Create useSync hook"
Task T028: "Create ActionButtons component"
Task T029: "Integrate into App.tsx"
Task T030: "Build and verify"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T005)
2. Complete Phase 2: Foundational (T006-T014)
3. Complete Phase 3: User Story 1 (T015-T021)
4. **STOP and VALIDATE**: Open http://localhost:8088, verify status loads with company count and last sync
5. Deploy/demo if ready — admin can already check system health

### Incremental Delivery

1. Setup + Foundational → NestJS starts, serves placeholder React page
2. Add User Story 1 → Status display works → Demo (MVP!)
3. Add User Story 2 → Full sync + terminal progress works → Demo
4. Add User Story 3 → Incremental sync added → Demo
5. Add User Story 4 → Caching verified → Demo
6. UI Polish via /frontend-design → Professional look → Demo
7. Cleanup → Remove PHP files → Final release

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- The `/frontend-design` skill (Phase 7) should be invoked AFTER all functionality works to avoid reworking logic during design iteration
- PHP cleanup (Phase 8) happens LAST to ensure no rollback is needed
