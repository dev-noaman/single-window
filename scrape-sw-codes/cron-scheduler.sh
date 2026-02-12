#!/bin/sh
# Cron scheduler to trigger SW_CODES_PYTHON daily at 8 AM Qatar time

echo "$(date): Starting daily fetch codes job..."

# Trigger the fetch via HTTP endpoint
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
