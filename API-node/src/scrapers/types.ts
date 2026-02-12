/**
 * Types specific to Qatar government website scraping
 */

import { 
  ScrapedData, 
  BusinessActivityData, 
  CompanyInfo, 
  LicenseData, 
  BrowserInstance,
  ScrapingRequest,
  DataType
} from '../types';

export interface QatarScrapingStrategy {
  name: string;
  description: string;
  supportedDataTypes: DataType[];
  urlPatterns: RegExp[];
  priority: number;
  
  canHandle(url: string, dataType: DataType): boolean;
  scrape(context: QatarScrapingContext): Promise<QatarScrapingResult>;
  validateData(data: any): boolean;
}

export interface QatarScrapingContext {
  request: ScrapingRequest;
  browserInstance: BrowserInstance;
  page?: any; // Playwright Page
  timeout: number;
  retryCount: number;
  maxRetries: number;
}

export interface QatarScrapingResult {
  success: boolean;
  data?: ScrapedData;
  error?: QatarScrapingError;
  metadata: {
    strategy: string;
    responseTime: number;
    retryCount: number;
    extractedFields: string[];
    confidence: number;
  };
}

export interface QatarScrapingError {
  code: string;
  message: string;
  type: 'NETWORK_ERROR' | 'PARSING_ERROR' | 'VALIDATION_ERROR' | 'TIMEOUT_ERROR' | 'CAPTCHA_ERROR' | 'ACCESS_DENIED';
  details?: any;
  recoverable: boolean;
}

// Qatar-specific data structures
export interface QatarBusinessActivity extends BusinessActivityData {
  qatarSpecific: {
    crNumber?: string;
    establishmentCard?: string;
    municipalityLicense?: string;
    ministryApproval?: string;
    qatarId?: string;
  };
}

export interface QatarCompanyInfo extends CompanyInfo {
  qatarSpecific: {
    crNumber: string;
    qatarId?: string;
    paidUpCapital: number;
    authorizedCapital: number;
    companyType: string;
    legalForm: string;
    registrationOffice: string;
    qatarianPartnership?: {
      required: boolean;
      percentage?: number;
      partnerName?: string;
    };
  };
}

export interface QatarLicenseData extends LicenseData {
  qatarSpecific: {
    issuingAuthority: string;
    licenseCategory: string;
    qatarId?: string;
    crNumber?: string;
    fees: {
      amount: number;
      currency: string;
      paymentStatus: string;
    };
    renewalRequirements?: string[];
  };
}

// Scraper configuration
export interface QatarScraperConfig {
  userAgent: string;
  timeout: number;
  retryAttempts: number;
  retryDelay: number;
  captchaSolver?: {
    enabled: boolean;
    apiKey?: string;
    service: string;
  };
  rateLimit: {
    requestsPerMinute: number;
    burstLimit: number;
  };
  headers: Record<string, string>;
}

// URL patterns for Qatar government sites
export const QATAR_GOVERNMENT_PATTERNS = {
  PORTAL_GOV_QA: /^https?:\/\/(www\.)?portal\.gov\.qa/,
  COMMERCIAL_REGISTRY: /^https?:\/\/(www\.)?cr\.gov\.qa/,
  LICENSING_PORTAL: /^https?:\/\/(www\.)?license\.gov\.qa/,
  MINISTRY_COMMERCE: /^https?:\/\/(www\.)?moci\.gov\.qa/,
  MUNICIPALITY: /^https?:\/\/(www\.)?municipality\.qa/,
  GENERAL_AUTHORITY: /^https?:\/\/(www\.)?gaa\.gov\.qa/,
  INVESTOR_SW: /^https?:\/\/investor\.sw\.gov\.qa/
} as const;

// Common selectors for Qatar government sites
export const QATAR_SELECTORS = {
  BUSINESS_NAME: [
    '[data-field="company-name"]',
    '.company-name',
    '#companyName',
    '.business-name',
    '[name="businessName"]'
  ],
  LICENSE_NUMBER: [
    '[data-field="license-number"]',
    '.license-number',
    '#licenseNumber',
    '[name="licenseNumber"]'
  ],
  CR_NUMBER: [
    '[data-field="cr-number"]',
    '.cr-number',
    '#crNumber',
    '[name="crNumber"]'
  ],
  STATUS: [
    '[data-field="status"]',
    '.status',
    '#status',
    '[name="status"]'
  ],
  ISSUE_DATE: [
    '[data-field="issue-date"]',
    '.issue-date',
    '#issueDate',
    '[name="issueDate"]'
  ],
  EXPIRY_DATE: [
    '[data-field="expiry-date"]',
    '.expiry-date',
    '#expiryDate',
    '[name="expiryDate"]'
  ]
} as const;

// Error codes specific to Qatar government sites
export const QATAR_ERROR_CODES = {
  CAPTCHA_REQUIRED: 'QATAR_CAPTCHA_REQUIRED',
  SESSION_EXPIRED: 'QATAR_SESSION_EXPIRED',
  RATE_LIMITED: 'QATAR_RATE_LIMITED',
  MAINTENANCE_MODE: 'QATAR_MAINTENANCE_MODE',
  INVALID_CREDENTIALS: 'QATAR_INVALID_CREDENTIALS',
  DATA_NOT_FOUND: 'QATAR_DATA_NOT_FOUND',
  ACCESS_RESTRICTED: 'QATAR_ACCESS_RESTRICTED'
} as const;