FROM php:8.4-fpm

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    nginx \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /var/www/html

# Copy application files
COPY index.php /var/www/html/index.php
COPY php-health.php /var/www/html/php-health.php

# Copy Nginx configuration
COPY nginx.conf /etc/nginx/sites-available/default

# Create PHP-FPM socket directory and set permissions
RUN mkdir -p /run/php \
    && chown -R www-data:www-data /run/php \
    && chmod 755 /run/php

# Configure PHP-FPM to use socket
RUN echo '[www]' > /usr/local/etc/php-fpm.d/www.conf \
    && echo 'user = www-data' >> /usr/local/etc/php-fpm.d/www.conf \
    && echo 'group = www-data' >> /usr/local/etc/php-fpm.d/www.conf \
    && echo 'listen = /run/php/php-fpm.sock' >> /usr/local/etc/php-fpm.d/www.conf \
    && echo 'listen.owner = www-data' >> /usr/local/etc/php-fpm.d/www.conf \
    && echo 'listen.group = www-data' >> /usr/local/etc/php-fpm.d/www.conf \
    && echo 'listen.mode = 0660' >> /usr/local/etc/php-fpm.d/www.conf \
    && echo 'pm = dynamic' >> /usr/local/etc/php-fpm.d/www.conf \
    && echo 'pm.max_children = 5' >> /usr/local/etc/php-fpm.d/www.conf \
    && echo 'pm.start_servers = 2' >> /usr/local/etc/php-fpm.d/www.conf \
    && echo 'pm.min_spare_servers = 1' >> /usr/local/etc/php-fpm.d/www.conf \
    && echo 'pm.max_spare_servers = 3' >> /usr/local/etc/php-fpm.d/www.conf

# Remove any non-PHP index files (ensure terminal-style index.php is the only landing page)
RUN rm -f /var/www/html/index.html

# Set permissions
RUN chown -R www-data:www-data /var/www/html

# Expose port
EXPOSE 80

# Copy the entrypoint script and fix Windows line endings
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN sed -i 's/\r$//' /docker-entrypoint.sh && chmod +x /docker-entrypoint.sh

CMD ["/docker-entrypoint.sh"]
