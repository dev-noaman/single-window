# Business Activity Codes SW_GSHEET

Automatically fetches business activity codes from Qatar Single Window portal and stores them in MySQL database.

## Features

- ✅ Scrapes all 2806+ business activity codes
- ✅ Stores in MySQL database with **optimized batch inserts**
- ✅ **Real-time progress monitoring** (no buffering)
- ✅ **Smart skip logic** (stops if no changes detected)
- ✅ REST API endpoints
- ✅ **Automatic daily updates at 8 AM Qatar time**
- ✅ **Auto-check before fetch** (only fetches if needed)

## Services

### 1. Database (SW_CODES_DB)
- MySQL 8 database
- Port: 3306
- Database: `codesdb`
- User: `codesuser`

### 2. Fetch Codes (SW_CODES_PYTHON)
- Python SW_GSHEET that fetches codes from Qatar Single Window API
- Runs on-demand or via cron schedule
- **Optimized batch inserts** (100 items per query)
- **Smart skip**: Stops after 3 consecutive pages with no changes
- Writes progress to `/tmp/fetch_progress.json` for real-time monitoring

### 3. Web Interface (SW_CODES_WEB)
- PHP web server on port 8084
- Provides API endpoints (no UI - use Portal instead)

### 4. Cron Scheduler (SW_CODES_CRON)
- **Automatically triggers fetch daily at 8:00 AM Qatar time (GMT+3)**
- Runs in background
- Logs all executions

## Usage

### Portal Interface (Recommended)
Access via Portal at `http://your-vps-ip:8082/`

Features:
- Click "SW_CODES_PYTHON" button
- **Auto-checks** MOCI API vs Database before fetching
- Shows real-time progress (page-by-page)
- Displays completion summary
- Clean terminal output

### API Endpoints

#### Check for Updates (Smart Check)
```bash
curl http://your-vps-ip:8084/check-update.php
```

Response:
```json
{
  "success": true,
  "needs_update": true,
  "api_total": 2806,
  "db_total": 800,
  "difference": 2006,
  "last_update": "2026-01-24 14:30:00"
}
```

#### Trigger Fetch
```bash
curl http://your-vps-ip:8084/trigger-fetch-codes.php
```

Response:
```json
{
  "success": true,
  "message": "SW_CODES_PYTHON container restarted successfully"
}
```

#### Real-Time Progress
```bash
curl http://your-vps-ip:8084/progress.php
```

Response:
```json
{
  "success": true,
  "status": "running",
  "current_page": 15,
  "total_pages": 29,
  "total_records": 2806,
  "new_inserted": 500,
  "updated": 1000
}
```

## Automatic Daily Updates

The cron scheduler automatically triggers the fetch process **every day at 8:00 AM Qatar time**.

**Smart Behavior**: The cron job first checks if updates are needed before fetching.

### View Cron Logs
```bash
docker logs SW_CODES_CRON
```

### Disable Automatic Updates
To disable daily automatic updates, stop the cron container:
```bash
docker stop SW_CODES_CRON
```

### Change Schedule Time
Edit `Dockerfile.cron` and change the cron expression:
```dockerfile
# Current: Daily at 8:00 AM
RUN echo "0 8 * * * /usr/local/bin/cron-scheduler.sh >> /var/log/cron.log 2>&1" > /etc/crontabs/root

# Examples:
# Every 6 hours: "0 */6 * * *"
# Twice daily (8 AM and 8 PM): "0 8,20 * * *"
# Every Monday at 9 AM: "0 9 * * 1"
```

Then rebuild:
```bash
docker compose up -d --build cron
```

## Performance Optimizations

### Batch Inserts
- **Old**: 100 individual INSERT queries per page (slow)
- **New**: 1 batch INSERT per page (3-5x faster)

### Smart Skip
- Monitors consecutive pages with no changes
- After 3 pages with "(no changes)", skips remaining pages
- Example: If pages 10-12 have no changes, skips pages 13-29
- Saves time when database is mostly up-to-date

### Real-Time Progress
- Writes to `/tmp/fetch_progress.json` file
- No Docker log buffering
- Instant updates (no delays)
- Portal polls every 3 seconds for smooth progress display

## Database Schema

Table: `business_activity_codes`

| Column | Type | Description |
|--------|------|-------------|
| id | INT | Auto-increment primary key |
| activity_code | VARCHAR(50) | Unique activity code |
| industry_id | VARCHAR(50) | ISIC industry ID |
| name_en | TEXT | English name |
| name_ar | TEXT | Arabic name |
| description_en | TEXT | English description |
| created_at | TIMESTAMP | Record creation time |
| updated_at | TIMESTAMP | Last update time |

## Deployment

Deploy to VPS:
```powershell
.\Deploy-to-Docker.ps1
```

Or manually:
```bash
cd /root/scrapers/scrape-sw-codes
docker compose up -d
```

## Monitoring

### Check all containers
```bash
docker ps | grep -E "SW_CODES_DB|SW_CODES_PYTHON|SW_CODES"
```

### View fetch logs
```bash
docker logs SW_CODES_PYTHON
```

### View cron logs
```bash
docker logs SW_CODES_CRON
```

### Check database records
```bash
docker exec SW_CODES_DB mysql -ucodesuser -pStrongPasswordHere -e "SELECT COUNT(*) FROM codesdb.business_activity_codes;"
```

## Troubleshooting

### Cron not running
```bash
# Check if cron container is running
docker ps | grep SW_CODES_CRON

# Restart cron
docker restart SW_CODES_CRON

# Check cron logs
docker logs SW_CODES_CRON --tail 50
```

### Manual trigger not working
```bash
# Check web container
docker logs SW_CODES_WEB

# Test endpoint
curl http://localhost:8084/trigger-fetch-codes.php
```

### Progress not updating
```bash
# Check if progress file exists
docker exec SW_CODES_PYTHON cat /tmp/fetch_progress.json

# Check if /tmp is mounted
docker inspect SW_CODES_PYTHON | grep -A 5 Mounts
```

### Database connection issues
```bash
# Check database health
docker exec SW_CODES_DB mysqladmin ping -ucodesuser -pStrongPasswordHere

# Check database logs
docker logs SW_CODES_DB --tail 50
```

## Qatar Time Zone

The cron scheduler uses **Asia/Qatar timezone (GMT+3)**.

Current Qatar time in container:
```bash
docker exec SW_CODES_CRON date
```

## Notes

- First run may take 1-2 minutes to fetch all 2806 codes
- **Optimized batch inserts** make subsequent runs 3-5x faster
- **Smart skip** stops early if no changes detected (saves time)
- Database automatically handles duplicates
- Cron runs even if previous fetch is still running (container restart handles this)
- **Real-time progress** updates instantly (no buffering)
- Portal provides the best user experience for monitoring
