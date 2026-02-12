#!/bin/bash
set -e

# Ensure PHP-FPM socket directory exists with correct permissions
mkdir -p /run/php
chown www-data:www-data /run/php
chmod 755 /run/php

# Start PHP-FPM in background
echo "Starting PHP-FPM..."
php-fpm -D

# Wait a moment for PHP-FPM to start
sleep 2

# Check if PHP-FPM socket is created
if [ ! -S /run/php/php-fpm.sock ]; then
    echo "ERROR: PHP-FPM socket not created!"
    exit 1
fi

echo "PHP-FPM started successfully"
echo "Starting Nginx..."

# Start Nginx in foreground
nginx -g 'daemon off;'
