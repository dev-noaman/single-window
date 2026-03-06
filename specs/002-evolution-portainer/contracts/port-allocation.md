# Port Allocation Contract

All ports used by the platform. No conflicts allowed.

## Host-bound ports (accessible from outside)

| Port | Service | Protocol | Binding |
|------|---------|----------|---------|
| 80 | nginx | HTTP | `0.0.0.0` |
| 443 | nginx (certbot) | HTTPS | `0.0.0.0` |
| 25 | BillionMail Postfix | SMTP | `0.0.0.0` |
| 110 | BillionMail Dovecot | POP3 | `0.0.0.0` |
| 143 | BillionMail Dovecot | IMAP | `0.0.0.0` |
| 465 | BillionMail Postfix | SMTPS | `0.0.0.0` |
| 587 | BillionMail Postfix | Submission | `0.0.0.0` |
| 993 | BillionMail Dovecot | IMAPS | `0.0.0.0` |
| 995 | BillionMail Dovecot | POP3S | `0.0.0.0` |
| 5432 | Host PostgreSQL | TCP | `0.0.0.0` |
| 8080 | api-scraper | HTTP | `0.0.0.0` |
| 8082 | Portal | HTTP | `0.0.0.0` |
| 8084 | scrape-sw-codes (PM2) | HTTP | `0.0.0.0` |
| 8085 | scrape-sw-gsheet | HTTP | `0.0.0.0` |
| 8086 | API-CR | HTTP | `0.0.0.0` |
| 8087 | officernd-api (PM2) | HTTP | `0.0.0.0` |
| 8088 | officernd-bff (PM2) | HTTP | `0.0.0.0` |
| 8089 | Evolution API | HTTP | `0.0.0.0` |
| 8090 | BillionMail Core (HTTP) | HTTP | `0.0.0.0` |
| 8443 | BillionMail Core (HTTPS) | HTTPS | `0.0.0.0` |
| 9000 | Portainer | HTTP | `0.0.0.0` |

## Localhost-only ports (internal/debug)

| Port | Service | Protocol | Binding |
|------|---------|----------|---------|
| 25432 | BillionMail PostgreSQL | TCP | `127.0.0.1` |
| 26379 | BillionMail Redis | TCP | `127.0.0.1` |

## Docker-internal only (not exposed to host)

| Port | Service | Protocol | Notes |
|------|---------|----------|-------|
| 6379 | Evolution Redis | TCP | Only on `scrapers-network` |
