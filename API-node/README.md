# API-node - Qatar Business Activity Scraper

Node.js-based scraper using Playwright for browser automation with TypeScript implementation. This service extracts business activity data from the Qatar Investor Portal.

## Features

✅ **TypeScript Implementation** - Type-safe scraper using FastQatarScraper  
✅ **Playwright Browser Automation** - Reliable headless browser control  
✅ **Dual Language Support** - Extracts both English and Arabic content  
✅ **Clean JSON API** - RESTful endpoints with structured responses  
✅ **Health Monitoring** - Built-in health check endpoints  
✅ **Docker Ready** - Fully containerized for easy deployment  
✅ **Production Optimized** - Proper error handling and timeouts

## Quick Start

### Local Development
```bash
# Install dependencies
npm install

# Build TypeScript
npm run build

# Run the server
npm start

# Test the API
curl http://localhost:3000/health
curl http://localhost:3000/scrape?code=013001
```

### Docker Deployment
```bash
# Build and start with Docker Compose
docker-compose up -d --build

# Check service status
docker-compose ps

# View logs
docker-compose logs -f

# Test the API
curl http://localhost:8081/health
curl http://localhost:8081/scrape?code=013001
```

## API Endpoints

### Health Check
```
GET /health
```
Returns service health status.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-01-24T10:27:07.576Z",
  "service": "api-node"
}
```

### Scrape Business Activity
```
GET /scrape?code={activityCode}
```
Scrapes Qatar business activity data for the specified activity code.

**Parameters:**
- `code` or `activityCode`: Qatar business activity code (default: 013001)

**Example:**
```bash
curl http://localhost:8081/scrape?code=013001
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "activity_code": "013001",
    "status": "Active",
    "name_en": "Cultivation of decoration plants and seedlings",
    "name_ar": "زراعة النباتات الحية لاغراض الغرس والزينة والشتلات (المشاتل)",
    "locations": "Main Location: Qatar\nSub Location: Doha",
    "eligible": "Allowed for GCC nationals\nAllowed for Non-GCC nationals",
    "approvals": "Approval 1: Ministry of Commerce and Industry\nAgency 1: Qatar Chamber of Commerce"
  },
  "error": null
}
```

### Documentation
```
GET /
```
Returns API documentation and available endpoints.

## Docker Configuration

### Ports
- **Internal**: 3000 (container)
- **External**: 8081 (host)

### Environment Variables
- `NODE_ENV=production`
- `LOG_LEVEL=info`
- `PORT=3000`
- `PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=false`

### Health Checks
- **Endpoint**: `/health`
- **Interval**: 30 seconds
- **Timeout**: 10 seconds
- **Retries**: 3
- **Start Period**: 40 seconds

## Architecture

### Components
1. **server.js** - HTTP server wrapper providing REST API
2. **test-json-only.js** - Main scraper script loader
3. **FastQatarScraper** - TypeScript scraper implementation
4. **Playwright** - Browser automation engine

### Data Flow
```
HTTP Request → server.js → FastQatarScraper → Playwright → Qatar Portal
                                                                ↓
HTTP Response ← JSON Format ← Data Extraction ← Browser Content
```

## Files Structure

```
API-node/
├── server.js                  # HTTP server wrapper
├── test-json-only.js          # Scraper script loader
├── package.json               # Dependencies
├── tsconfig.json             # TypeScript configuration
├── Dockerfile                # Docker configuration
├── docker-compose.yml        # Docker Compose configuration
├── .dockerignore             # Docker ignore file
├── dist/                     # Compiled JavaScript
│   └── scrapers/
│       ├── FastQatarScraper.js
│       ├── types.js
│       └── index.js
├── src/                      # TypeScript source files
│   ├── scrapers/
│   │   ├── FastQatarScraper.ts
│   │   ├── types.ts
│   │   └── index.ts
│   ├── types/
│   │   └── index.ts
│   ├── utils/
│   │   └── logger.ts
│   └── config/
│       └── index.ts
└── node_modules/             # Dependencies
```

## VPS Deployment

### Prerequisites
- Docker and Docker Compose installed
- Port 8081 available
- 2GB+ RAM recommended for Playwright

### Deployment Steps

1. **Using the main deployment script:**
   ```powershell
   .\Deploy-to-Docker.ps1
   ```

2. **Manual deployment:**
   ```bash
   # Transfer files to VPS
   scp -r API-node/ user@vps:/path/to/deployment/
   
   # SSH into VPS
   ssh user@vps
   
   # Navigate to directory
   cd /path/to/deployment/API-node
   
   # Build and start
   docker-compose up -d --build
   ```

3. **Verify deployment:**
   ```bash
   # Check service health
   curl http://your-vps-ip:8081/health
   
   # Test scraping
   curl http://your-vps-ip:8081/scrape?code=013001
   ```

### Management Commands
```bash
# Start service
docker-compose up -d

# Stop service
docker-compose down

# Restart service
docker-compose restart

# View logs
docker-compose logs -f

# Check status
docker-compose ps

# Update and redeploy
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## Monitoring

### Health Monitoring
The service includes built-in health checks at `/health`. Monitor with:
```bash
# Simple health check
curl http://localhost:8081/health

# Continuous monitoring
watch -n 5 'curl -s http://localhost:8081/health | jq'
```

### Logs
```bash
# View all logs
docker-compose logs -f

# View last 50 lines
docker logs API-NODE --tail 50

# Follow logs in real-time
docker logs -f API-NODE
```

## Troubleshooting

### Common Issues

**1. Port already in use**
```bash
# Check what's using port 8081
netstat -tlnp | grep :8081

# Change port in docker-compose.yml
ports:
  - "8082:3000"  # Use different external port
```

**2. Memory issues**
```bash
# Increase Docker memory allocation
# In docker-compose.yml:
shm_size: '2gb'
```

**3. Browser launch failures**
```bash
# Rebuild with fresh Playwright installation
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

**4. TypeScript compilation errors**
```bash
# Rebuild TypeScript
npm run build

# Or rebuild in Docker
docker-compose exec api-node npm run build
```

### Debug Mode
```bash
# Run with debug logs
docker-compose down
LOG_LEVEL=debug docker-compose up
```

## Dependencies

### Core Dependencies
- **playwright**: ^1.40.0 - Browser automation
- **winston**: ^3.11.0 - Logging
- **dotenv**: ^16.3.1 - Environment configuration

### Dev Dependencies
- **typescript**: ^5.3.2 - TypeScript compiler
- **@types/node**: ^20.10.0 - Node.js type definitions

## Performance

### Typical Response Times
- Health check: < 50ms
- Scraping (cached): 2-5 seconds
- Scraping (fresh): 10-15 seconds

### Resource Usage
- Memory: ~500MB (with Playwright browser)
- CPU: Low (spikes during scraping)
- Disk: ~500MB (including Playwright browsers)

## Integration

### Portal Integration
The service is automatically integrated into the Portal as **ENGINE_02 (NODE)**:
- Accessible from the engine dropdown
- Same interface as other engines
- Real-time result display

### API Integration
```javascript
// Example integration
const response = await fetch('http://localhost:8081/scrape?code=013001');
const data = await response.json();

if (data.status === 'success') {
  console.log('Activity:', data.data.name_en);
  console.log('Status:', data.data.status);
}
```

## License

MIT

## Author

Noaman - [GitHub](https://github.com/dev-noaman)