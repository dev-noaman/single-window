FROM node:20-slim

# Install system dependencies for Playwright
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libc6 \
    libcairo2 \
    libcups2 \
    libdbus-1-3 \
    libexpat1 \
    libfontconfig1 \
    libgbm1 \
    libgcc1 \
    libglib2.0-0 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libstdc++6 \
    libx11-6 \
    libx11-xcb1 \
    libxcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxi6 \
    libxrandr2 \
    libxrender1 \
    libxshmfence1 \
    libxtst6 \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user BEFORE installing browsers
RUN groupadd -r scraper && useradd -r -g scraper -m scraper

# Set Playwright to install browsers in a shared location
ENV PLAYWRIGHT_BROWSERS_PATH=/opt/playwright-browsers

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install ALL dependencies (including dev for TypeScript build)
RUN npm ci

# Install Playwright browsers to shared location and make accessible
RUN npx playwright install chromium \
    && chmod -R 755 /opt/playwright-browsers

# Copy application files
COPY . .

# Build TypeScript
RUN npm run build

# Remove dev dependencies after build to reduce image size
RUN npm prune --omit=dev

# Set ownership of app directory
RUN chown -R scraper:scraper /app

# Switch to non-root user
USER scraper

# Expose port (we'll use 3000 internally and map it externally)
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:3000/health || exit 1

# Default command runs the HTTP server
CMD ["npm", "start"]