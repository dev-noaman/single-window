/**
 * Simple HTTP server wrapper for FastQatarScraper
 * Provides HTTP endpoints to run the scraper using the compiled TypeScript code
 */

const http = require('http');
const { chromium } = require('playwright');
const url = require('url');
const path = require('path');

const PORT = process.env.PORT || 3000;

// Function to run the scraper using the compiled TypeScript code
async function runScraper(activityCode = '013001') {
  let browser = null;
  
  try {
    console.log(`Starting scraper for activity code: ${activityCode}`);
    
    // Set environment to suppress excessive logging
    process.env.LOG_LEVEL = process.env.LOG_LEVEL || 'error';
    
    // Launch browser
    browser = await chromium.launch({ 
      headless: true,
      args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-logging']
    });
    
    // Mock browser instance for the scraper
    const mockBrowserInstance = {
      browser: browser,
      id: 'api-browser',
      isHealthy: true,
      requestCount: 0,
      lastUsed: new Date(),
      createdAt: new Date()
    };
    
    // Import the compiled scraper
    const { FastQatarScraper } = require('./dist/scrapers/FastQatarScraper.js');
    const scraper = new FastQatarScraper();
    
    // Build test URL with the activity code
    const testUrl = `https://investor.sw.gov.qa/wps/portal/investors/information-center/ba/details?bacode=${activityCode}`;
    
    // Check if scraper can handle this URL
    if (!scraper.canHandle(testUrl, 'business_activity')) {
      return {
        status: "error",
        data: null,
        error: "Scraper cannot handle this URL"
      };
    }
    
    // Create scraping context
    const context = {
      request: {
        url: testUrl,
        dataType: 'business_activity',
        priority: 'high',
        freshness: 'fresh'
      },
      browserInstance: mockBrowserInstance
    };
    
    // Perform scraping
    const result = await scraper.scrape(context);
    
    // Return the result
    if (result.success && result.data) {
      return result.data.content;
    } else {
      return {
        status: "error",
        data: null,
        error: result.error ? result.error.message : "Unknown error occurred"
      };
    }
    
  } catch (error) {
    console.error('Scraper error:', error);
    return {
      status: "error",
      data: null,
      error: error.message || 'Scraping failed'
    };
  } finally {
    if (browser) {
      try {
        await browser.close();
      } catch (e) {
        console.error('Error closing browser:', e);
      }
    }
  }
}

// Create HTTP server
const server = http.createServer(async (req, res) => {
  const parsedUrl = url.parse(req.url, true);
  const path = parsedUrl.pathname;
  const query = parsedUrl.query;

  // Set CORS headers
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  res.setHeader('Content-Type', 'application/json');

  // Handle OPTIONS request
  if (req.method === 'OPTIONS') {
    res.writeHead(200);
    res.end();
    return;
  }

  try {
    if (path === '/health') {
      // Health check endpoint
      res.writeHead(200);
      res.end(JSON.stringify({
        status: 'healthy',
        timestamp: new Date().toISOString(),
        service: 'api-node'
      }));
    } else if (path === '/scrape') {
      // Scraping endpoint
      const activityCode = query.code || query.activityCode || '013001';
      
      console.log('Scraping request for activity code: ' + activityCode);
      
      const result = await runScraper(activityCode);
      
      res.writeHead(200);
      res.end(JSON.stringify(result, null, 2));
    } else if (path === '/') {
      // Root endpoint - documentation
      res.writeHead(200);
      res.end(JSON.stringify({
        service: 'API-node',
        version: '1.0.0',
        endpoints: {
          '/health': 'Health check endpoint',
          '/scrape?code=013001': 'Scrape Qatar business activity data',
          '/': 'This documentation'
        },
        example: 'GET /scrape?code=013001'
      }, null, 2));
    } else {
      // 404 Not Found
      res.writeHead(404);
      res.end(JSON.stringify({
        status: 'error',
        message: 'Endpoint not found',
        availableEndpoints: ['/health', '/scrape', '/']
      }));
    }
  } catch (error) {
    console.error('Server error:', error);
    res.writeHead(500);
    res.end(JSON.stringify({
      status: 'error',
      message: 'Internal server error',
      error: error.message
    }));
  }
});

server.listen(PORT, '0.0.0.0', () => {
  console.log('API-node server running on port ' + PORT);
  console.log('Health check: http://localhost:' + PORT + '/health');
  console.log('Scrape endpoint: http://localhost:' + PORT + '/scrape?code=013001');
});