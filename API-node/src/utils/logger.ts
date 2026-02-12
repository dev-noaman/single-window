/**
 * Logging utility for Business Data Scraper V2
 * Provides structured logging with different levels and formats
 */

import winston from 'winston';
import { serverConfig } from '../config';

/**
 * Custom log format for development
 */
const developmentFormat = winston.format.combine(
  winston.format.timestamp({ format: 'YYYY-MM-DD HH:mm:ss' }),
  winston.format.errors({ stack: true }),
  winston.format.colorize(),
  winston.format.printf(({ timestamp, level, message, stack, ...meta }) => {
    let log = `${timestamp} [${level}]: ${message}`;
    
    if (Object.keys(meta).length > 0) {
      log += ` ${JSON.stringify(meta, null, 2)}`;
    }
    
    if (stack) {
      log += `\n${stack}`;
    }
    
    return log;
  })
);

/**
 * Custom log format for production
 */
const productionFormat = winston.format.combine(
  winston.format.timestamp(),
  winston.format.errors({ stack: true }),
  winston.format.json()
);

/**
 * Create logger instance
 */
const logger = winston.createLogger({
  level: serverConfig.logLevel,
  format: serverConfig.nodeEnv === 'production' ? productionFormat : developmentFormat,
  defaultMeta: {
    service: 'business-data-scraper-v2',
    version: '1.0.0',
    environment: serverConfig.nodeEnv,
  },
  transports: [
    // Console transport
    new winston.transports.Console({
      handleExceptions: true,
      handleRejections: true,
    }),
  ],
});

// Add file transports for production
if (serverConfig.nodeEnv === 'production') {
  logger.add(
    new winston.transports.File({
      filename: 'logs/error.log',
      level: 'error',
      maxsize: 10 * 1024 * 1024, // 10MB
      maxFiles: 5,
    })
  );
  
  logger.add(
    new winston.transports.File({
      filename: 'logs/combined.log',
      maxsize: 10 * 1024 * 1024, // 10MB
      maxFiles: 10,
    })
  );
}

/**
 * Enhanced logger with additional methods
 */
export class Logger {
  private context: string;
  
  constructor(context: string = 'Application') {
    this.context = context;
  }
  
  /**
   * Log debug message
   */
  debug(message: string, meta?: Record<string, any>): void {
    logger.debug(message, { context: this.context, ...meta });
  }
  
  /**
   * Log info message
   */
  info(message: string, meta?: Record<string, any>): void {
    logger.info(message, { context: this.context, ...meta });
  }
  
  /**
   * Log warning message
   */
  warn(message: string, meta?: Record<string, any>): void {
    logger.warn(message, { context: this.context, ...meta });
  }
  
  /**
   * Log error message
   */
  error(message: string, error?: Error, meta?: Record<string, any>): void {
    logger.error(message, {
      context: this.context,
      error: error ? {
        name: error.name,
        message: error.message,
        stack: error.stack,
      } : undefined,
      ...meta,
    });
  }
  
  /**
   * Log performance metric
   */
  performance(operation: string, duration: number, meta?: Record<string, any>): void {
    logger.info(`Performance: ${operation}`, {
      context: this.context,
      operation,
      duration,
      type: 'performance',
      ...meta,
    });
  }
  
  /**
   * Log request information
   */
  request(requestId: string, method: string, url: string, meta?: Record<string, any>): void {
    logger.info(`Request: ${method} ${url}`, {
      context: this.context,
      requestId,
      method,
      url,
      type: 'request',
      ...meta,
    });
  }
  
  /**
   * Log response information
   */
  response(requestId: string, statusCode: number, duration: number, meta?: Record<string, any>): void {
    logger.info(`Response: ${statusCode}`, {
      context: this.context,
      requestId,
      statusCode,
      duration,
      type: 'response',
      ...meta,
    });
  }
  
  /**
   * Log cache operation
   */
  cache(operation: 'hit' | 'miss' | 'set' | 'invalidate', key: string, meta?: Record<string, any>): void {
    logger.debug(`Cache ${operation}: ${key}`, {
      context: this.context,
      operation,
      key,
      type: 'cache',
      ...meta,
    });
  }
  
  /**
   * Log browser pool operation
   */
  browserPool(operation: string, instanceId?: string, meta?: Record<string, any>): void {
    logger.debug(`Browser Pool: ${operation}`, {
      context: this.context,
      operation,
      instanceId,
      type: 'browser-pool',
      ...meta,
    });
  }
  
  /**
   * Log rate limiting event
   */
  rateLimit(clientId: string, action: 'allowed' | 'blocked' | 'queued', meta?: Record<string, any>): void {
    logger.info(`Rate Limit: ${action} for client ${clientId}`, {
      context: this.context,
      clientId,
      action,
      type: 'rate-limit',
      ...meta,
    });
  }
  
  /**
   * Log scraping operation
   */
  scraping(operation: string, url: string, meta?: Record<string, any>): void {
    logger.info(`Scraping: ${operation} - ${url}`, {
      context: this.context,
      operation,
      url,
      type: 'scraping',
      ...meta,
    });
  }
  
  /**
   * Log validation result
   */
  validation(dataType: string, isValid: boolean, confidence: number, meta?: Record<string, any>): void {
    logger.info(`Validation: ${dataType} - ${isValid ? 'VALID' : 'INVALID'} (confidence: ${confidence})`, {
      context: this.context,
      dataType,
      isValid,
      confidence,
      type: 'validation',
      ...meta,
    });
  }
  
  /**
   * Log fallback operation
   */
  fallback(strategy: string, reason: string, meta?: Record<string, any>): void {
    logger.warn(`Fallback: Using ${strategy} - ${reason}`, {
      context: this.context,
      strategy,
      reason,
      type: 'fallback',
      ...meta,
    });
  }
  
  /**
   * Create child logger with additional context
   */
  child(additionalContext: string): Logger {
    return new Logger(`${this.context}:${additionalContext}`);
  }
}

/**
 * Create logger instance for a specific context
 */
export function createLogger(context: string): Logger {
  return new Logger(context);
}

/**
 * Default logger instance
 */
export const defaultLogger = new Logger('Application');

/**
 * Export winston logger for direct access if needed
 */
export { logger as winstonLogger };

export default Logger;