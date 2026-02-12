#!/bin/bash
# Check if SW_CODES cron job ran today

echo "🔍 Checking SW_CODES cron job status..."
echo "Server Time: $(date)"
echo "Qatar Time: $(TZ=Asia/Qatar date)"
echo ""

# Get today's date in Qatar timezone
TODAY_QATAR=$(TZ=Asia/Qatar date +%Y-%m-%d)
CURRENT_HOUR_QATAR=$(TZ=Asia/Qatar date +%H)

echo "📅 Today in Qatar: $TODAY_QATAR"
echo "🕐 Current Qatar Hour: ${CURRENT_HOUR_QATAR}:00"
echo ""

# Check if cron container is running
echo "1️⃣ Checking SW_CODES_CRON container status..."
if docker ps --filter name=SW_CODES_CRON --format "table {{.Names}}\t{{.Status}}" | grep -q SW_CODES_CRON; then
    echo "✅ SW_CODES_CRON container is running"
    docker ps --filter name=SW_CODES_CRON --format "table {{.Names}}\t{{.Status}}\t{{.CreatedAt}}"
else
    echo "❌ SW_CODES_CRON container is NOT running"
    echo "💡 Run: docker-compose -f scrape-sw-codes/docker-compose.yml up -d cron"
    exit 1
fi

echo ""

# Check cron logs for today
echo "2️⃣ Checking cron logs for today ($TODAY_QATAR)..."
CRON_LOGS=$(docker logs SW_CODES_CRON 2>&1 | grep "$TODAY_QATAR" || echo "")

if [ -n "$CRON_LOGS" ]; then
    echo "📋 Cron logs for today:"
    echo "$CRON_LOGS"
else
    echo "⚠️  No cron execution logs found for today"
    if [ "$CURRENT_HOUR_QATAR" -lt 8 ]; then
        echo "   ⏰ Cron hasn't run yet (scheduled for 8:00 AM Qatar time)"
        echo "   ⏳ Next run in approximately $((8 - CURRENT_HOUR_QATAR)) hour(s)"
    else
        echo "   ❌ Cron may have failed or container was restarted"
    fi
fi

echo ""

# Check database for last update
echo "3️⃣ Checking database for last update..."
if command -v curl >/dev/null 2>&1; then
    LAST_UPDATE=$(curl -s http://localhost:8084/check-update.php 2>/dev/null | grep -o '"last_update":"[^"]*"' | cut -d'"' -f4)
    
    if [ -n "$LAST_UPDATE" ] && [ "$LAST_UPDATE" != "null" ]; then
        echo "📊 Last database update: $LAST_UPDATE"
        
        # Extract date part from timestamp
        LAST_UPDATE_DATE=$(echo "$LAST_UPDATE" | cut -d' ' -f1)
        
        if [ "$LAST_UPDATE_DATE" = "$TODAY_QATAR" ]; then
            echo "✅ Database was updated TODAY!"
        else
            echo "⚠️  Database was NOT updated today"
            echo "   📅 Last update was on: $LAST_UPDATE_DATE"
        fi
    else
        echo "❌ Could not retrieve last update info from database"
    fi
else
    echo "⚠️  curl not available, skipping database check"
fi

echo ""

# Check current status
echo "4️⃣ Checking current fetch status..."
if command -v curl >/dev/null 2>&1; then
    STATUS=$(curl -s http://localhost:8084/progress.php 2>/dev/null | grep -o '"status":"[^"]*"' | cut -d'"' -f4)
    
    if [ -n "$STATUS" ]; then
        echo "📈 Current status: $STATUS"
        
        case "$STATUS" in
            "completed")
                echo "✅ Last fetch completed successfully"
                ;;
            "running")
                echo "🔄 Fetch is currently running"
                ;;
            "error")
                echo "❌ Last fetch ended with error"
                ;;
            *)
                echo "ℹ️  Status: $STATUS"
                ;;
        esac
    else
        echo "⚠️  Could not retrieve current status"
    fi
else
    echo "⚠️  curl not available, skipping status check"
fi

echo ""
echo "🎯 SUMMARY:"
echo "═══════════════════════════════════════"

# Determine overall status
if [ -n "$CRON_LOGS" ] && [ "$LAST_UPDATE_DATE" = "$TODAY_QATAR" ]; then
    echo "✅ Cron job appears to have run successfully today"
elif [ "$CURRENT_HOUR_QATAR" -lt 8 ]; then
    echo "⏰ Cron job hasn't run yet (scheduled for 8:00 AM Qatar time)"
    echo "   ⏳ Next run in approximately $((8 - CURRENT_HOUR_QATAR)) hour(s)"
else
    echo "⚠️  Cron job may have failed or not executed today"
    echo "   🔍 Check the logs above for more details"
fi

echo ""
echo "💡 Manual Commands:"
echo "   Check cron logs: docker logs SW_CODES_CRON"
echo "   Manual trigger:  curl http://localhost:8084/trigger-fetch-codes.php"
echo "   Restart cron:    docker-compose -f scrape-sw-codes/docker-compose.yml restart cron"