/**
 * Core type definitions for Business Data Scraper V2
 * Defines all interfaces and types used throughout the system
 */

// ============================================================================
// Core Data Types
// ============================================================================

export type DataType = 'business_activity' | 'company_info' | 'license_data';
export type ValidationStatus = 'valid' | 'warning' | 'error';
export type CompanyStatus = 'active' | 'suspended' | 'cancelled';
export type RequestPriority = 'low' | 'normal' | 'high';
export type FreshnessRequirement = 'cached' | 'fresh' | 'any';
export type CacheFreshness = 'fresh' | 'stale' | 'expired';

// ============================================================================
// Request and Response Interfaces
// ============================================================================

export interface ScrapingRequest {
  url: string;
  dataType: DataType;
  freshness: FreshnessRequirement;
  priority: RequestPriority;
  clientId: string;
  requestId?: string;
  timeout?: number;
}

export interface ScrapingResponse {
  success: boolean;
  data?: ScrapedData;
  error?: string;
  requestId: string;
  responseTime: number;
  cacheHit: boolean;
  confidence?: number;
  staleness?: CacheFreshness;
}

// ============================================================================
// Scraped Data Structures
// ============================================================================

export interface ScrapedData {
  id: string;
  sourceUrl: string;
  dataType: DataType;
  content: BusinessActivityData | CompanyInfo | LicenseData;
  extractedAt: Date;
  confidence: number;
  validationStatus: ValidationStatus;
}

export interface BusinessActivityData {
  companyName: string;
  licenseNumber: string;
  activityType: string;
  status: CompanyStatus;
  issueDate: Date;
  expiryDate: Date;
  location: string;
  contactInfo: ContactInfo;
}

export interface CompanyInfo {
  commercialName: string;
  legalName: string;
  registrationNumber: string;
  establishmentDate: Date;
  capital: number;
  shareholders: Shareholder[];
  activities: string[];
}

export interface LicenseData {
  licenseNumber: string;
  licenseType: string;
  companyName: string;
  status: CompanyStatus;
  issueDate: Date;
  expiryDate: Date;
  activities: string[];
  conditions?: string[];
}

export interface ContactInfo {
  address: string;
  phone?: string;
  email?: string;
  website?: string;
}

export interface Shareholder {
  name: string;
  nationality: string;
  sharePercentage: number;
  shareType: string;
}

// ============================================================================
// Cache Layer Interfaces
// ============================================================================

export interface CacheLayer {
  get(key: string): Promise<CachedData | null>;
  set(key: string, data: ScrapedData, ttl: number): Promise<void>;
  invalidate(pattern: string): Promise<void>;
  refreshInBackground(key: string): Promise<void>;
}

export interface CachedData {
  data: ScrapedData;
  timestamp: Date;
  ttl: number;
  freshness: CacheFreshness;
}

export interface CacheEntry {
  key: string;
  data: ScrapedData;
  createdAt: Date;
  expiresAt: Date;
  accessCount: number;
  lastAccessed: Date;
  tags: string[];
}

export interface CacheMetrics {
  hitRate: number;
  missRate: number;
  evictionRate: number;
  averageResponseTime: number;
  totalEntries: number;
  memoryUsage: number;
}

// ============================================================================
// Browser Pool Interfaces
// ============================================================================

export interface BrowserPoolManager {
  acquireBrowser(): Promise<BrowserInstance>;
  releaseBrowser(instance: BrowserInstance): void;
  healthCheck(): Promise<PoolHealth>;
  scaleBrowsers(targetCount: number): Promise<void>;
}

export interface BrowserInstance {
  id: string;
  browser: any; // Playwright Browser type
  isAvailable: boolean;
  lastUsed: Date;
  requestCount: number;
}

export interface PoolHealth {
  totalInstances: number;
  availableInstances: number;
  busyInstances: number;
  unhealthyInstances: number;
  averageRequestsPerInstance: number;
}

// Health monitoring types
export interface HealthCheckResult {
  timestamp: Date;
  success: boolean;
  checkType: 'version' | 'page_creation' | 'navigation' | 'memory';
  responseTime: number;
  error?: string;
}

export interface HealthCheckConfig {
  enableVersionCheck: boolean;
  enablePageCreationCheck: boolean;
  enableNavigationCheck: boolean;
  enableMemoryCheck: boolean;
  maxConsecutiveFailures: number;
  healthCheckTimeout: number;
  navigationTestUrl: string;
  memoryThresholdMB: number;
}

// ============================================================================
// Request Batching Interfaces
// ============================================================================

export interface RequestBatcher {
  addRequest(request: ScrapingRequest): Promise<BatchId>;
  processBatch(batchId: BatchId): Promise<BatchResult[]>;
  optimizeBatch(requests: ScrapingRequest[]): BatchGroup[];
}

export type BatchId = string;

export interface BatchGroup {
  targetUrl: string;
  requests: ScrapingRequest[];
  estimatedProcessingTime: number;
}

export interface BatchResult {
  requestId: string;
  success: boolean;
  data?: ScrapedData;
  error?: string;
  responseTime: number;
}

// ============================================================================
// Rate Limiting Interfaces
// ============================================================================

export interface RateLimiter {
  checkLimit(clientId: string): Promise<RateLimitResult>;
  enqueueRequest(request: ScrapingRequest): Promise<QueuePosition>;
  processQueue(): Promise<void>;
}

export interface RateLimitResult {
  allowed: boolean;
  remainingRequests: number;
  resetTime: Date;
  queuePosition?: number;
}

export interface QueuePosition {
  position: number;
  estimatedWaitTime: number;
}

// ============================================================================
// Resource Blocking Interfaces
// ============================================================================

export interface ResourceBlocker {
  configureBlocking(page: any): Promise<void>; // Playwright Page type
  shouldBlock(request: any): boolean; // Playwright Request type
  getBlockedResourceStats(): ResourceStats;
}

export interface ResourceStats {
  totalRequests: number;
  blockedRequests: number;
  savedBandwidth: number;
  timesSaved: number;
}

// ============================================================================
// Performance Monitoring Interfaces
// ============================================================================

export interface PerformanceMonitor {
  recordMetric(metric: Metric): void;
  getMetrics(timeRange: TimeRange): Promise<MetricData[]>;
  checkThresholds(): Promise<Alert[]>;
}

export interface Metric {
  name: string;
  value: number;
  timestamp: Date;
  tags: Record<string, string>;
}

export interface MetricData {
  name: string;
  values: Array<{ timestamp: Date; value: number }>;
  aggregation: {
    avg: number;
    min: number;
    max: number;
    count: number;
  };
}

export interface TimeRange {
  start: Date;
  end: Date;
}

export interface Alert {
  id: string;
  type: string;
  severity: 'info' | 'warning' | 'error' | 'critical';
  message: string;
  timestamp: Date;
  metadata?: Record<string, any>;
}

// ============================================================================
// Fallback Handler Interfaces
// ============================================================================

export interface FallbackHandler {
  handleFailure(request: ScrapingRequest, error: Error): Promise<ScrapingResponse>;
  getAlternativeStrategies(dataType: DataType): ScrapingStrategy[];
  recordFailurePattern(request: ScrapingRequest, error: Error): void;
}

export interface ScrapingStrategy {
  name: string;
  priority: number;
  execute(request: ScrapingRequest): Promise<ScrapedData>;
  canHandle(dataType: DataType): boolean;
}

// ============================================================================
// Data Validation Interfaces
// ============================================================================

export interface DataValidator {
  validate(data: ScrapedData): ValidationResult;
  getValidationRules(dataType: DataType): ValidationRule[];
  calculateConfidence(data: ScrapedData, validationResult: ValidationResult): number;
  detectAnomalies(data: ScrapedData): AnomalyResult[];
}

export interface ValidationResult {
  isValid: boolean;
  errors: ValidationError[];
  warnings: ValidationWarning[];
  confidence: number;
}

export interface ValidationRule {
  name: string;
  description: string;
  validate(data: any): boolean;
  severity: 'error' | 'warning';
}

export interface ValidationError {
  field: string;
  message: string;
  code: string;
}

export interface ValidationWarning {
  field: string;
  message: string;
  code: string;
}

export interface AnomalyResult {
  field: string;
  anomalyType: string;
  severity: number;
  description: string;
}

// ============================================================================
// API Gateway Interfaces
// ============================================================================

export interface APIGateway {
  handleRequest(request: ScrapingRequest): Promise<ScrapingResponse>;
  validateRequest(request: ScrapingRequest): ValidationResult;
  formatResponse(data: ScrapedData): ScrapingResponse;
}

// ============================================================================
// Configuration Interfaces
// ============================================================================

export interface SystemConfig {
  browserPool: BrowserPoolConfig;
  cache: CacheConfig;
  rateLimiting: RateLimitConfig;
  monitoring: MonitoringConfig;
  resourceBlocking: ResourceBlockingConfig;
  scraping: ScrapingConfig;
  fallback: FallbackConfig;
}

export interface BrowserPoolConfig {
  minInstances: number;
  maxInstances: number;
  idleTimeout: number;
  maxRequestsPerInstance: number;
  healthCheckInterval: number;
}

export interface CacheConfig {
  defaultTTL: number;
  maxMemory: string;
  evictionPolicy: 'lru' | 'lfu' | 'ttl';
  backgroundRefreshThreshold: number;
}

export interface RateLimitConfig {
  windowMs: number;
  maxRequests: number;
  queueMaxSize: number;
  priorityLevels: Record<RequestPriority, number>;
}

export interface MonitoringConfig {
  enabled: boolean;
  metricsInterval: number;
  alertWebhookUrl?: string;
  thresholds: {
    responseTime: number;
    cacheResponseTime: number;
    concurrentSuccessRate: number;
    errorRate: number;
    memoryUsage: number;
    cpuUsage: number;
  };
}

export interface ResourceBlockingConfig {
  enabled: boolean;
  blockImages: boolean;
  blockCSS: boolean;
  blockFonts: boolean;
  whitelist: string[];
  // Override mechanisms for full page rendering scenarios
  allowOverrides: boolean;
  overrideLogging: boolean;
  overrideScenarios: OverrideScenario[];
}

export interface OverrideScenario {
  name: string;
  description: string;
  urlPatterns: string[];
  disableAllBlocking: boolean;
  allowedResourceTypes: string[];
  reason: string;
  enabled: boolean;
}

export interface ScrapingConfig {
  userAgent: string;
  timeout: number;
  retryAttempts: number;
  retryDelay: number;
}

export interface FallbackConfig {
  enabled: boolean;
  maxAttempts: number;
  staleDataMaxAge: number;
}

// ============================================================================
// Database Interfaces
// ============================================================================

export interface DatabaseConnection {
  query<T = any>(sql: string, params?: any[]): Promise<T[]>;
  transaction<T>(callback: (client: DatabaseConnection) => Promise<T>): Promise<T>;
  close(): Promise<void>;
}

// ============================================================================
// Utility Types
// ============================================================================

export type DeepPartial<T> = {
  [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P];
};

export type RequiredFields<T, K extends keyof T> = T & Required<Pick<T, K>>;

export type OptionalFields<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>;

// ============================================================================
// Error Types
// ============================================================================

export class ScrapingError extends Error {
  constructor(
    message: string,
    public code: string,
    public statusCode: number = 500,
    public metadata?: Record<string, any>
  ) {
    super(message);
    this.name = 'ScrapingError';
  }
}

export class CacheError extends Error {
  constructor(
    message: string,
    public operation: string,
    public key?: string
  ) {
    super(message);
    this.name = 'CacheError';
  }
}

export class BrowserPoolError extends Error {
  constructor(
    message: string,
    public instanceId?: string
  ) {
    super(message);
    this.name = 'BrowserPoolError';
  }
}

export class RateLimitError extends Error {
  constructor(
    message: string,
    public clientId: string,
    public retryAfter: number
  ) {
    super(message);
    this.name = 'RateLimitError';
  }
}

export class ValidationError extends Error {
  constructor(
    message: string,
    public field: string,
    public code: string
  ) {
    super(message);
    this.name = 'ValidationError';
  }
}