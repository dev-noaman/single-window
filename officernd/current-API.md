# OfficeRnD API - Current Endpoints Reference

**Base URL**: `/api/v2/organizations/{orgSlug}`
**Live**: `https://noaman.cloud/officernd/api/v2/organizations/arafat-business-centers`
**Total**: 80 GET endpoints + 1 POST endpoint

---

## Standard Response Formats

### Paginated List
```json
{
  "rangeStart": 0,
  "rangeEnd": 49,
  "cursorNext": null,
  "results": [ { "_id": "...", ... } ]
}
```

### Single Record
```json
{
  "rangeStart": 1,
  "rangeEnd": 1,
  "cursorNext": null,
  "results": [ { "_id": "...", ... } ]
}
```

### Count
```json
{
  "total": 580,
  "groups": [ { "key": "active", "count": 580 } ]
}
```

### Common Query Parameters (all list endpoints)

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `limit` | int | 100 | Results per page (1-1000) |
| `offset` | int | 0 | Skip N records |

---

## Community (`/community`)

### GET /members
List members with optional filters.

| Filter | Type | Maps to column |
|--------|------|---------------|
| `company` | string | `company_id` |
| `status` | string | `status` |
| `id` | string | `_id` |
| `name` | string | `name` |
| `email` | string | `email` |
| `location` | string | `location_id` |

### GET /members/count
Count members with optional grouping.

| Param | Type | Description |
|-------|------|-------------|
| `$countBy` | string | Group by field (e.g. `status`, `company`) |

### GET /members/{member_id}
Get single member by ID.

### GET /companies
List companies with optional filters.

| Filter | Type | Maps to column |
|--------|------|---------------|
| `status` | string | `status` |
| `id` | string | `_id` |
| `name` | string | `name` |
| `location` | string | `location_id` |

### GET /companies/{company_id}
Get single company by ID.

### GET /visitors
List visitors with optional filters.

| Filter | Type | Maps to column |
|--------|------|---------------|
| `member` | string | `member_id` |
| `company` | string | `company_id` |
| `type` | string | `type` |
| `location` | string | `location_id` |

### GET /visitors/{visitor_id}
Get single visitor by ID.

### GET /opportunities
List opportunities with optional filters.

| Filter | Type | Maps to column |
|--------|------|---------------|
| `company` | string | `company_id` |
| `member` | string | `member_id` |
| `status` | string | `status` |

### GET /opportunities/count
Count opportunities.

### GET /opportunities/{opportunity_id}
Get single opportunity by ID.

### GET /passes
List passes with optional filters.

| Filter | Type | Maps to column |
|--------|------|---------------|
| `company` | string | `company_id` |
| `member` | string | `member_id` |

### GET /passes/{pass_id}
Get single pass by ID.

---

## Space (`/space`)

### GET /resources
List resources with optional filters.

| Filter | Type | Maps to column |
|--------|------|---------------|
| `type` | string | `type` |
| `location` | string | `location_id` |
| `floor` | string | `floor_id` |
| `id` | string | `_id` |
| `name` | string | `name` |

### GET /resources/count
Count resources.

### GET /resources/{resource_id}/status
Get resource availability status. Returns:
```json
{ "_id": "...", "status": "available", "ownStatus": "free" }
```

### GET /resources/{resource_id}
Get single resource by ID.

### GET /resource-types
List all resource types. No filters.

### GET /bookings
List bookings with optional filters.

| Filter | Type | Maps to column |
|--------|------|---------------|
| `resource` | string | `resource_id` |
| `company` | string | `company_id` |
| `member` | string | `member_id` |
| `location` | string | `location_id` |

### GET /bookings/count
Count bookings.

### GET /bookings/occurrences
List booking occurrences with optional filters.

| Filter | Type | Maps to column |
|--------|------|---------------|
| `company` | string | `company_id` |
| `member` | string | `member_id` |
| `location` | string | `location_id` |
| `resource` | string | `resource_id` |

### GET /bookings/{booking_id}
Get single booking by ID.

### GET /assignments
List resource assignments with optional filters.

| Filter | Type | Maps to column |
|--------|------|---------------|
| `resource` | string | `resource_id` |
| `membership` | string | `membership_id` |

### GET /locations
List locations with optional filters.

| Filter | Type | Maps to column |
|--------|------|---------------|
| `name` | string | `name` |
| `isOpen` | bool | `is_open` |
| `isPublic` | bool | `is_public` |

### GET /locations/{location_id}
Get single location by ID.

### GET /floors
List floors with optional filters.

| Filter | Type | Maps to column |
|--------|------|---------------|
| `location` | string | `location_id` |
| `name` | string | `name` |

### GET /floors/{floor_id}
Get single floor by ID.

### GET /amenities
List amenities. No filters.

### GET /amenities/{amenity_id}
Get single amenity by ID.

---

## Collaboration (`/collaboration`)

### GET /posts
List posts. No filters.

### GET /posts/{post_id}
Get single post by ID.

### GET /events
List events. No filters.

### GET /events/count
Count events.

### GET /events/{event_id}
Get single event by ID.

### GET /tickets
List tickets with optional filters.

| Filter | Type | Maps to column |
|--------|------|---------------|
| `status` | string | `status` |
| `company` | string | `company_id` |
| `member` | string | `member_id` |
| `location` | string | `location_id` |
| `assignedTo` | string | `assigned_to` |

### GET /tickets/count
Count tickets with optional grouping.

| Param | Type | Description |
|-------|------|-------------|
| `$countBy` | string | Group by field (e.g. `status`) |

### GET /tickets/{ticket_id}
Get single ticket by ID.

### GET /ticket-options
List ticket options. No filters.

---

## Billing (`/billing`)

### GET /payments
List payments with optional filters.

| Filter | Type | Maps to column |
|--------|------|---------------|
| `status` | string | `status` |
| `company` | string | `company_id` |
| `member` | string | `member_id` |

### GET /payments/methods
List payment methods. Returns:
```json
{ "paymentMethods": [] }
```

### GET /payments/count
Count payments.

### GET /payments/{payment_id}
Get single payment by ID.

### GET /charges
List charges with optional filters.

| Filter | Type | Maps to column |
|--------|------|---------------|
| `status` | string | `status` |
| `payment` | string | `payment_id` |

### GET /charges/{charge_id}
Get single charge by ID.

### GET /credits
List credits with optional filters.

| Filter | Type | Maps to column |
|--------|------|---------------|
| `company` | string | `company_id` |
| `member` | string | `member_id` |

### GET /credits/{credit_id}
Get single credit by ID.

### GET /coins/stats
List coin statistics. No filters.

### GET /fees
List fees with optional filters.

| Filter | Type | Maps to column |
|--------|------|---------------|
| `company` | string | `company_id` |
| `status` | string | `status` |
| `member` | string | `member_id` |
| `location` | string | `location_id` |
| `plan` | string | `plan_type` |

### GET /fees/count
Count fees.

### GET /fees/{fee_id}
Get single fee by ID.

### GET /revenue-accounts
List revenue accounts. No filters.

### GET /tax-rates
List tax rates. No filters.

### GET /memberships
List memberships with optional filters.

| Filter | Type | Maps to column |
|--------|------|---------------|
| `company` | string | `company_id` |
| `status` | string | `status` |
| `member` | string | `member_id` |
| `plan` | string | `plan_id` |

### GET /memberships/count
Count memberships.

### GET /memberships/{membership_id}
Get single membership by ID.

### GET /plans
List plans. No filters.

### GET /plans/count
Count plans.

### GET /plans/{plan_id}
Get single plan by ID.

### GET /resource-rates
List resource rates. No filters.

### GET /resource-rates/count
Count resource rates.

### GET /resource-rates/{rate_id}
Get single resource rate by ID.

### GET /contracts
List contracts with optional filters.

| Filter | Type | Maps to column |
|--------|------|---------------|
| `company` | string | `company_id` |
| `location` | string | `location_id` |
| `status` | string | `status` |

### GET /contracts/count
Count contracts.

### GET /contracts/{contract_id}
Get single contract by ID.

### GET /benefits
List benefits with optional filters.

| Filter | Type | Maps to column |
|--------|------|---------------|
| `company` | string | `company_id` |
| `member` | string | `member_id` |

### GET /benefits/count
Count benefits.

### GET /benefits/{benefit_id}
Get single benefit by ID.

### GET /payment-details
List payment details with optional filters.

| Filter | Type | Maps to column |
|--------|------|---------------|
| `company` | string | `company_id` |
| `member` | string | `member_id` |

---

## Visits (`/visits`)

### GET /visits
List visits with optional filters.

| Filter | Type | Maps to column |
|--------|------|---------------|
| `member` | string | `member_id` |
| `visitor` | string | `visitor_id` |
| `location` | string | `location_id` |

### GET /visits/{visit_id}
Get single visit by ID.

### GET /checkins
List checkins with optional filters.

| Filter | Type | Maps to column |
|--------|------|---------------|
| `member` | string | `member_id` |
| `company` | string | `company_id` |
| `location` | string | `location_id` |

### GET /checkins/{checkin_id}
Get single checkin by ID.

---

## Settings (`/settings`)

### GET /webhooks
List webhooks. No filters.

### GET /billing-settings
List billing settings. No filters. (Empty - API returns 404 for this org)

### GET /business-hours
List business hours. No filters. (Empty - API returns 404 for this org)

### GET /custom-properties
List custom properties. No filters.

### GET /opportunity-statuses
List opportunity statuses. No filters.

### GET /reception-flows
List reception flows. No filters. (Empty - API returns 500 for this org)

### GET /secondary-currencies
List secondary currencies. No filters.

### GET /secondary-currencies/{currency_id}
Get single secondary currency by ID.

### GET /organizations
List organizations. No filters. (Empty - API returns 404 for this org)

### GET /integrations/{integration_id}
Get single integration by ID.

---

## Sync Management (`/sync`)

These endpoints have **no authentication** requirement.

### GET /sync/status
Get sync status for all endpoints.

| Param | Type | Description |
|-------|------|-------------|
| `endpoint` | string | Filter by endpoint name |

Returns: `[{ endpoint, status, records_fetched, records_upserted, last_run, error }]`

### GET /sync/companies
Get per-company sync results (deduplicated, latest per company).

Returns:
```json
[{
  "company_id": "5b30ea1c14fb5716001c579d",
  "company_name": "Company Name",
  "status": "completed",
  "endpoints_completed": 13,
  "endpoints_failed": 0,
  "records_fetched": 42,
  "records_upserted": 42,
  "started_at": "2026-02-09T18:58:11Z",
  "completed_at": "2026-02-09T18:58:15Z"
}]
```

### GET /sync/stats
Get aggregate company counts.

Returns:
```json
{
  "companies_total": 2180,
  "companies_active": 580,
  "companies_by_status": { "active": 580, "former": 932, ... },
  "companies_synced": 580
}
```

### GET /sync/phases
Get phase-level sync progress for the UI phase tracker.

Returns:
```json
{
  "current_phase": "",
  "phases": [
    {
      "phase": 1,
      "name": "Sync All Data",
      "status": "completed",
      "completed": 580,
      "total": 580,
      "sub_status": null,
      "globals_completed": 22,
      "globals_total": 22,
      "endpoints": [{ "endpoint": "companies", "status": "completed", "records_fetched": 2180, "records_upserted": 2180, "last_run": "...", "error": null }]
    },
    {
      "phase": 2,
      "name": "Dependent",
      "status": "completed",
      "completed": 2,
      "total": 2,
      "endpoints": [{ "endpoint": "payment-documents", "status": "completed", "records_fetched": 14828, "records_upserted": 14828 }]
    }
  ]
}
```

### GET /sync/progress
Get real-time sync progress from shared file.

Returns:
```json
{
  "phase": "Phase 2: Companies",
  "status": "running",
  "current": 150,
  "total": 580,
  "endpoint": "bookings",
  "company": "Company Name",
  "message": "Company 150/580 - bookings page 3 (150 records)...",
  "error": null,
  "timestamp": 1770663491.696
}
```

Status values: `idle`, `running`, `completed`, `error`

### POST /sync/run
Trigger a sync operation in background thread.

**Request Body:**
```json
{
  "endpoint": null,
  "resume": false,
  "mode": "full"
}
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `endpoint` | string\|null | null | Single endpoint to sync (null = all) |
| `resume` | bool | false | Skip completed companies |
| `mode` | string | "full" | `"full"`, `"incremental"`, or `"smart"` |

**Mode Details:**
- `"full"` - Re-sync all global endpoints + all active companies + dependent
- `"incremental"` - Skip already-synced companies, sync only new ones
- `"smart"` - Fetch latest companies from live API, compare count, skip if up to date, else run incremental

**Response:**
```json
{ "status": "started", "mode": "smart", "endpoint": "all", "message": "Sync operation started in background thread" }
```
Or if already running:
```json
{ "status": "already_running", "mode": "smart", "message": "Sync already in progress" }
```

### GET /sync/export
Export full PostgreSQL database backup using `pg_dump` (schema + data, ~66MB).

Returns: `application/sql` with `Content-Disposition: attachment; filename="officernd-backup-{timestamp}.sql"`

---

## Utility Endpoints (no prefix)

### GET /health
```json
{ "status": "healthy", "service": "officernd-api-clone" }
```

### GET /
```json
{ "name": "OfficeRnD API Offline Clone", "version": "1.0.0", "docs": "/docs", "health": "/health" }
```

### GET /docs
Interactive Swagger/OpenAPI documentation (auto-generated by FastAPI).

---

## Endpoint Summary by Category

| Category | List | Count | Single | Special | Total |
|----------|------|-------|--------|---------|-------|
| Community | 5 | 2 | 5 | - | 12 |
| Space | 7 | 2 | 6 | 1 (status) | 16 |
| Collaboration | 4 | 2 | 4 | - | 10 |
| Billing | 13 | 7 | 10 | 1 (methods) | 31 |
| Visits | 2 | - | 2 | - | 4 |
| Settings | 7 | - | 2 | - | 9 |
| Sync | 5 | - | - | 1 (POST) | 6 |
| Utility | - | - | - | 3 | 3 |
| **Total** | **43** | **13** | **29** | **6** | **91** |

**API endpoints**: 80 GET (matching OfficeRnD reference docs) + 1 POST (sync trigger)
**Utility**: 3 (health, root, docs) + 7 sync management = 10
