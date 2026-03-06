# Data Model: Evolution API + BillionMail + Portainer

**Branch**: `002-evolution-portainer` | **Date**: 2026-03-06

## Overview

This feature adds three external services (Evolution API, BillionMail, Portainer) — each manages its own data internally. The data model here documents the external-facing data boundaries and integration points, not the internal schemas of each service (which are managed by the services themselves).

## Host PostgreSQL (port 5432)

Existing databases remain unchanged. One new database added:

| Database | User | Service | Notes |
|----------|------|---------|-------|
| `officernd` | `officernd_user` | officernd | Existing (unchanged) |
| `codesdb` | `codesuser` | scrape-sw-codes | Existing (unchanged) |
| `evolutiondb` | `evolution_user` | Evolution API | **NEW** — Prisma-managed schema, auto-migrated on startup |

### evolutiondb

Managed entirely by Evolution API's Prisma ORM. Schema is auto-created via migrations on container startup (`deploy_database.sh`). Key tables (managed by Evolution API, not by us):

- **Instance**: WhatsApp connection instances (name, token, status, QR code)
- **Message**: WhatsApp messages (sender, content, timestamp, media references)
- **Contact**: WhatsApp contacts synced from connected instances
- **Chat**: Conversation threads
- **Label**: Organization labels for chats/contacts

We do NOT modify this schema. We only need to:
1. Create the `evolutiondb` database and `evolution_user` role
2. Provide the connection URI to Evolution API via env var

## BillionMail PostgreSQL (port 25432, internal)

BillionMail runs its own PostgreSQL 17.4 container. Database: `billionmail`, user: `billionmail`. Connected via Unix socket internally. Completely isolated from host PostgreSQL.

Key data (managed by BillionMail, not by us):
- **Mailbox**: Email accounts (address, quota, status)
- **Domain**: Mail domains (noaman.cloud)
- **Campaign**: Email marketing campaigns
- **Subscriber**: Campaign subscriber lists
- **Template**: Email templates

## Portainer

Portainer stores its data in a single named volume (`portainer_data`). Contains:
- User accounts and passwords (bcrypt-hashed)
- Environment configurations
- Stack definitions
- Access control settings

No database — Portainer uses BoltDB internally (file-based).

## Volume Map

| Named Volume | Service | Purpose | Backup Priority |
|-------------|---------|---------|-----------------|
| `evolution_instances` | Evolution API | WhatsApp session state, instance data | High |
| `evolution_redis_data` | Evolution Redis | Cache data (regeneratable) | Low |
| `portainer_data` | Portainer | User accounts, settings | Medium |
| `billionmail_postgres` | BillionMail PG | Mailboxes, campaigns, subscribers | High |
| `billionmail_redis` | BillionMail Redis | Cache/sessions | Low |
| `billionmail_vmail` | BillionMail Dovecot | Actual email messages on disk | High |
| `billionmail_postfix` | BillionMail Postfix | Mail queue | Medium |
| `billionmail_rspamd` | BillionMail Rspamd | Spam filter learned data | Low |
| `billionmail_core` | BillionMail Core | Admin panel app data | Medium |
| `billionmail_webmail` | BillionMail RoundCube | Webmail data | Low |
| `billionmail_ssl` | BillionMail | SSL certificates | High |
| `billionmail_conf` | BillionMail | All service configs | High |
| `billionmail_logs` | BillionMail | Service logs | Low |

## Network Topology

```
┌─────────────────────────────────────────────────────────┐
│                   scrapers-network                       │
│  (shared Docker bridge — all services can communicate)   │
│                                                          │
│  api-scraper ─── API-CR ─── Portal ─── Evolution API    │
│  scrape-sw-gsheet ─── Portainer                         │
│                                                          │
│  ┌──────────────────────────────────────┐               │
│  │       billionmail-network            │               │
│  │  (internal: postfix, dovecot,        │               │
│  │   rspamd, roundcube, pgsql, redis)   │               │
│  │                                      │               │
│  │  core-billionmail ◄── connected to   │               │
│  │  both networks                       │               │
│  └──────────────────────────────────────┘               │
└─────────────────────────────────────────────────────────┘
         │                          │
    host.docker.internal:5432   localhost:5432
    (Evolution API → evolutiondb) (PM2 services → officernd, codesdb)
```
