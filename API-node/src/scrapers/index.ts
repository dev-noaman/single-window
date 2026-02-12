/**
 * Qatar Government Website Scrapers
 * Specialized scrapers for extracting business data from Qatar government portals
 */

export { FastQatarScraper } from './FastQatarScraper';

// Re-export types
export type {
  QatarScrapingStrategy,
  QatarScrapingContext,
  QatarScrapingResult,
  QatarScrapingError
} from './types';