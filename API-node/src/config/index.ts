/**
 * Configuration management for Business Data Scraper V2
 * Handles environment-specific settings and validation
 */

import { config } from 'dotenv';
import { SystemConfig } from '../types';

// Load environment variables
config();

/**
 * Get environment variable with type conversion and validation
 */
function getEnvVar<T>(
  key: string,
  defaultValue: T,
  converter?: (value: string) => T
): T {
  const value = process.env[key];
  
  if (value === undefined) {
    return defaultValue;
  }
  
  if (converter) {
    try {
      return converter(value);
    } catch (error) {
      console.warn(`Invalid value for ${key}: ${value}. Using default: ${defaultValue}`);
      return defaultValue;
    }
  }
  
  return value as unknown as T;
}

/**
 * Convert string to number with validation
 */
function toNumber(value: string): number {
  const num = Number(value);
  if (isNaN(num)) {
    throw new Error(`Invalid number: ${value}`);
  }
  return num;
}

/**
 * Convert string to boolean
 */
function toBoolean(value: string): boolean {
  return value.toLowerCase() === 'true';
}

/**
 * Convert comma-separated string to array
 */
function toArray(value: string): string[] {
  return value.split(',').map(item => item.trim()).filter(item => item.length > 0);
}

/**
 * System configuration object
 */
export const systemConfig: SystemConfig = {
  browserPool: {
    minInstances: getEnvVar('BROWSER_POOL_MIN_INSTANCES', 2, toNumber),
    maxInstances: getEnvVar('BROWSER_POOL_MAX_INSTANCES', 10, toNumber),
    idleTimeout: getEnvVar('BROWSER_POOL_IDLE_TIMEOUT', 300000, toNumber),
    maxRequestsPerInstance: getEnvVar('BROWSER_POOL_MAX_REQUESTS_PER_INSTANCE', 100, toNumber),
    healthCheckInterval: getEnvVar('BROWSER_POOL_HEALTH_CHECK_INTERVAL', 30000, toNumber),
  },
  
  cache: {
    defaultTTL: getEnvVar('CACHE_DEFAULT_TTL', 3600, toNumber),
    maxMemory: getEnvVar('CACHE_MAX_MEMORY', '512mb'),
    evictionPolicy: getEnvVar('CACHE_EVICTION_POLICY', 'allkeys-lru') as 'lru' | 'lfu' | 'ttl',
    backgroundRefreshThreshold: getEnvVar('CACHE_BACKGROUND_REFRESH_THRESHOLD', 0.8, toNumber),
  },
  
  rateLimiting: {
    windowMs: getEnvVar('RATE_LIMIT_WINDOW_MS', 60000, toNumber),
    maxRequests: getEnvVar('RATE_LIMIT_MAX_REQUESTS', 100, toNumber),
    queueMaxSize: getEnvVar('RATE_LIMIT_QUEUE_MAX_SIZE', 1000, toNumber),
    priorityLevels: {
      low: 1,
      normal: 2,
      high: 3,
    },
  },
  
  monitoring: (() => {
    const config: any = {
      enabled: getEnvVar('MONITORING_ENABLED', true, toBoolean),
      metricsInterval: getEnvVar('MONITORING_METRICS_INTERVAL_MS', 10000, toNumber),
      thresholds: {
        responseTime: getEnvVar('PERFORMANCE_RESPONSE_TIME_THRESHOLD_MS', 3000, toNumber),
        cacheResponseTime: getEnvVar('PERFORMANCE_CACHE_RESPONSE_TIME_THRESHOLD_MS', 200, toNumber),
        concurrentSuccessRate: getEnvVar('PERFORMANCE_CONCURRENT_REQUEST_SUCCESS_RATE', 0.8, toNumber),
        errorRate: 0.05,
        memoryUsage: 0.85,
        cpuUsage: 0.8,
      },
    };
    
    const webhookUrl = getEnvVar('MONITORING_ALERT_WEBHOOK_URL', undefined);
    if (webhookUrl) {
      config.alertWebhookUrl = webhookUrl;
    }
    
    return config;
  })(),
  
  resourceBlocking: {
    enabled: getEnvVar('RESOURCE_BLOCKING_ENABLED', true, toBoolean),
    blockImages: getEnvVar('RESOURCE_BLOCKING_IMAGES', true, toBoolean),
    blockCSS: getEnvVar('RESOURCE_BLOCKING_CSS', true, toBoolean),
    blockFonts: getEnvVar('RESOURCE_BLOCKING_FONTS', true, toBoolean),
    whitelist: getEnvVar('RESOURCE_BLOCKING_WHITELIST', [] as string[], (value: string) => toArray(value)),
    // Override mechanisms for full page rendering scenarios
    allowOverrides: getEnvVar('RESOURCE_BLOCKING_ALLOW_OVERRIDES', true, toBoolean),
    overrideLogging: getEnvVar('RESOURCE_BLOCKING_OVERRIDE_LOGGING', true, toBoolean),
    overrideScenarios: getEnvVar('RESOURCE_BLOCKING_OVERRIDE_SCENARIOS', [] as any[], (value: string) => {
      try {
        return JSON.parse(value);
      } catch {
        return [];
      }
    }),
  },
  
  scraping: {
    userAgent: getEnvVar('SCRAPING_USER_AGENT', 'BusinessDataScraperV2/1.0'),
    timeout: getEnvVar('SCRAPING_TIMEOUT_MS', 30000, toNumber),
    retryAttempts: getEnvVar('SCRAPING_RETRY_ATTEMPTS', 3, toNumber),
    retryDelay: getEnvVar('SCRAPING_RETRY_DELAY_MS', 1000, toNumber),
  },
  
  fallback: {
    enabled: getEnvVar('FALLBACK_ENABLED', true, toBoolean),
    maxAttempts: getEnvVar('FALLBACK_MAX_ATTEMPTS', 3, toNumber),
    staleDataMaxAge: getEnvVar('FALLBACK_STALE_DATA_MAX_AGE_MS', 86400000, toNumber),
  },
};

/**
 * Database configuration
 */
export const databaseConfig = {
  postgres: {
    url: getEnvVar('POSTGRES_URL', 'postgresql://scraper:password@localhost:5432/business_scraper'),
    maxConnections: getEnvVar('POSTGRES_MAX_CONNECTIONS', 20, toNumber),
    idleTimeout: getEnvVar('POSTGRES_IDLE_TIMEOUT', 30000, toNumber),
    connectionTimeout: getEnvVar('POSTGRES_CONNECTION_TIMEOUT', 5000, toNumber),
  },
  redis: {
    url: getEnvVar('REDIS_URL', 'redis://localhost:6379'),
    password: getEnvVar('REDIS_PASSWORD', undefined),
    maxRetries: getEnvVar('REDIS_MAX_RETRIES', 3, toNumber),
    retryDelay: getEnvVar('REDIS_RETRY_DELAY', 1000, toNumber),
  },
};

/**
 * Server configuration
 */
export const serverConfig = {
  port: getEnvVar('PORT', 3000, toNumber),
  nodeEnv: getEnvVar('NODE_ENV', 'development'),
  logLevel: getEnvVar('LOG_LEVEL', 'info'),
  corsOrigin: getEnvVar('CORS_ORIGIN', '*'),
  helmetEnabled: getEnvVar('HELMET_ENABLED', true, toBoolean),
  apiKeyRequired: getEnvVar('API_KEY_REQUIRED', false, toBoolean),
  apiKey: getEnvVar('API_KEY', undefined),
};

/**
 * Validate configuration on startup
 */
export function validateConfig(): void {
  const errors: string[] = [];
  
  // Validate browser pool configuration
  if (systemConfig.browserPool.minInstances < 1) {
    errors.push('Browser pool minimum instances must be at least 1');
  }
  
  if (systemConfig.browserPool.maxInstances < systemConfig.browserPool.minInstances) {
    errors.push('Browser pool maximum instances must be greater than or equal to minimum instances');
  }
  
  // Validate cache configuration
  if (systemConfig.cache.defaultTTL < 1) {
    errors.push('Cache default TTL must be at least 1 second');
  }
  
  if (systemConfig.cache.backgroundRefreshThreshold < 0 || systemConfig.cache.backgroundRefreshThreshold > 1) {
    errors.push('Cache background refresh threshold must be between 0 and 1');
  }
  
  // Validate rate limiting configuration
  if (systemConfig.rateLimiting.maxRequests < 1) {
    errors.push('Rate limit max requests must be at least 1');
  }
  
  if (systemConfig.rateLimiting.windowMs < 1000) {
    errors.push('Rate limit window must be at least 1000ms');
  }
  
  // Validate monitoring thresholds
  const thresholds = systemConfig.monitoring.thresholds;
  if (thresholds.responseTime < 100) {
    errors.push('Response time threshold must be at least 100ms');
  }
  
  if (thresholds.cacheResponseTime < 10) {
    errors.push('Cache response time threshold must be at least 10ms');
  }
  
  if (thresholds.concurrentSuccessRate < 0 || thresholds.concurrentSuccessRate > 1) {
    errors.push('Concurrent success rate threshold must be between 0 and 1');
  }
  
  // Validate scraping configuration
  if (systemConfig.scraping.timeout < 1000) {
    errors.push('Scraping timeout must be at least 1000ms');
  }
  
  if (systemConfig.scraping.retryAttempts < 0) {
    errors.push('Scraping retry attempts must be non-negative');
  }
  
  // Validate database URLs
  if (!databaseConfig.postgres.url.startsWith('postgresql://')) {
    errors.push('PostgreSQL URL must start with postgresql://');
  }
  
  if (!databaseConfig.redis.url.startsWith('redis://')) {
    errors.push('Redis URL must start with redis://');
  }
  
  // Validate server configuration
  if (serverConfig.port < 1 || serverConfig.port > 65535) {
    errors.push('Server port must be between 1 and 65535');
  }
  
  if (errors.length > 0) {
    throw new Error(`Configuration validation failed:\n${errors.join('\n')}`);
  }
}

/**
 * Get configuration for specific environment
 */
export function getEnvironmentConfig(): {
  isDevelopment: boolean;
  isProduction: boolean;
  isTest: boolean;
} {
  const env = serverConfig.nodeEnv.toLowerCase();
  
  return {
    isDevelopment: env === 'development',
    isProduction: env === 'production',
    isTest: env === 'test',
  };
}

/**
 * Export all configurations
 */
export default {
  system: systemConfig,
  database: databaseConfig,
  server: serverConfig,
  validate: validateConfig,
  environment: getEnvironmentConfig(),
};