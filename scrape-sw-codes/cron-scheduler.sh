#!/bin/sh
# Smart sync scheduler - runs hourly, only fetches if API has new codes

echo "$(date): Smart sync check starting..."

# Step 1: Check if update is needed (compares API total vs DB total)
CHECK_RESPONSE=$(curl -s -w "\n%{http_code}" http://SW_CODES_WEB:8000/check-update.php)
CHECK_HTTP=$(echo "$CHECK_RESPONSE" | tail -n1)
CHECK_BODY=$(echo "$CHECK_RESPONSE" | head -n-1)

if [ "$CHECK_HTTP" != "200" ]; then
    echo "$(date): ✗ Smart check failed (HTTP $CHECK_HTTP), triggering fetch anyway..."
else
    # Parse needs_update from JSON response
    NEEDS_UPDATE=$(echo "$CHECK_BODY" | grep -o '"needs_update":[a-z]*' | cut -d: -f2)

    if [ "$NEEDS_UPDATE" = "false" ]; then
        echo "$(date): ✓ Already up to date - no new codes found"
        echo "$CHECK_BODY"
        exit 0
    fi

    echo "$(date): New codes detected, triggering fetch..."
    echo "$CHECK_BODY"
fi

# Step 2: Trigger the full fetch
RESPONSE=$(curl -s -w "\n%{http_code}" http://SW_CODES_WEB:8000/trigger-fetch-codes.php)
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | head -n-1)

if [ "$HTTP_CODE" = "200" ]; then
    echo "$(date): ✓ Fetch codes triggered successfully"
    echo "$BODY"
else
    echo "$(date): ✗ Failed to trigger fetch codes (HTTP $HTTP_CODE)"
    echo "$BODY"
fi
