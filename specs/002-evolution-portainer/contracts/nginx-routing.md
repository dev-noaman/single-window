# Nginx Routing Contract

## noaman.cloud (existing server block — extended)

| Path | Upstream | Service | Notes |
|------|----------|---------|-------|
| `/` | `127.0.0.1:8082` | Portal | Existing (unchanged) |
| `/api-scraper/` | `127.0.0.1:8080` | api-scraper | Existing (unchanged) |
| `/api-cr/` | `127.0.0.1:8086` | API-CR | Existing (unchanged) |
| `/sw-codes/` | `127.0.0.1:8084` | scrape-sw-codes | Existing (unchanged) |
| `/gsheet-scraper/` | `127.0.0.1:8085` | scrape-sw-gsheet | Existing (unchanged) |
| `/officernd/` | `127.0.0.1:8088` | officernd-bff | Existing (unchanged) |
| `/officernd-api/` | `127.0.0.1:8087` | officernd-api | Existing (unchanged) |
| `/health` | `127.0.0.1:8082/health` | Portal health | Existing (unchanged) |
| `/evolution/` | `127.0.0.1:8089` | Evolution API | **NEW** |
| `/portainer/` | `127.0.0.1:9000` | Portainer | **NEW** — requires WebSocket upgrade headers |

### Portainer location block (WebSocket required)

```nginx
location /portainer/ {
    proxy_pass http://127.0.0.1:9000/;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

## mail.noaman.cloud (new server block)

| Path | Upstream | Service | Notes |
|------|----------|---------|-------|
| `/` | `127.0.0.1:8090` | BillionMail Core | Admin panel + default route |
| `/roundcube/` | `127.0.0.1:8090` | BillionMail Core | RoundCube webmail (served by same container) |

```nginx
server {
    listen 80;
    server_name mail.noaman.cloud;

    location / {
        proxy_pass http://127.0.0.1:8090/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300;
    }
}
```

## DNS Records Required

| Type | Name | Value | Notes |
|------|------|-------|-------|
| A | `mail.noaman.cloud` | `<VPS_IP>` | Points to VPS |
| MX | `noaman.cloud` | `mail.noaman.cloud` (priority 10) | Mail routing |
| TXT | `noaman.cloud` | `v=spf1 a mx ip4:<VPS_IP> -all` | SPF record |
| TXT | `_dmarc.noaman.cloud` | `v=DMARC1; p=quarantine; rua=mailto:admin@noaman.cloud` | DMARC policy |
| TXT | `dkim._domainkey.noaman.cloud` | `<DKIM public key from BillionMail>` | DKIM signing |
