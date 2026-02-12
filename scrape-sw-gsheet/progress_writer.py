"""
Progress Writer Module for Google Sheets Scraper

This module provides functionality to write progress updates to JSON files
for real-time monitoring of scraper execution through the Portal interface.

Requirements: 5.3, 5.4, 6.1, 6.2, 6.3, 6.4, 6.5, 6.6
"""

import json
import time
from typing import Dict, Any, Literal

# Progress file paths
PROGRESS_FILE_EN = '/tmp/scrape_progress_en.json'
PROGRESS_FILE_AR = '/tmp/scrape_progress_ar.json'

# Type definitions for status values
ProgressStatus = Literal['running', 'completed', 'error']


def write_progress(
    language: str,
    status: ProgressStatus,
    current_row: int = 0,
    total_rows: int = 0,
    message: str = '',
    rows_processed: int = 0,
    start_time: float = None
) -> None:
    """
    Write progress data to JSON file for monitoring by the Portal.
    
    Args:
        language: Language identifier ('en' or 'ar')
        status: Current status ('running', 'completed', or 'error')
        current_row: Current row being processed (0-based or 1-based depending on context)
        total_rows: Total number of rows to process
        message: Status message or error description
        rows_processed: Number of rows successfully processed (used on completion)
        start_time: Unix timestamp when scraping started (for elapsed time calculation)
    
    Requirements:
        - 5.3: Write progress updates to /tmp/scrape_progress_en.json
        - 5.4: Write progress updates to /tmp/scrape_progress_ar.json
        - 6.1: Progress data in JSON format
        - 6.2: Include "status" field with values: "running", "completed", or "error"
        - 6.3: Include "current_row" field
        - 6.4: Include "total_rows" field
        - 6.5: Include "message" field
        - 6.6: Include "rows_processed" field on completion
    
    Example:
        # Starting scraper
        start = time.time()
        write_progress('en', 'running', 0, 100, 'Starting EN scraper...', start_time=start)
        
        # Processing rows
        write_progress('en', 'running', 5, 100, 'Processing row 5/100', start_time=start)
        
        # Completion
        write_progress('en', 'completed', 100, 100, 'Scraping completed successfully', 95, start_time=start)
        
        # Error
        write_progress('en', 'error', 10, 100, 'Connection timeout error', start_time=start)
    """
    # Determine progress file path based on language
    progress_file = PROGRESS_FILE_EN if language.lower() == 'en' else PROGRESS_FILE_AR
    
    # Build progress data structure with all required fields
    progress_data: Dict[str, Any] = {
        'status': status,
        'current_row': current_row,
        'total_rows': total_rows,
        'message': message,
        'timestamp': int(time.time())
    }
    
    # Include rows_processed field (always present, but most relevant on completion)
    progress_data['rows_processed'] = rows_processed
    
    # Include start_time if provided (for elapsed time calculation)
    if start_time is not None:
        progress_data['start_time'] = start_time
        progress_data['elapsed_time'] = time.time() - start_time
    
    # Write to JSON file
    try:
        with open(progress_file, 'w') as f:
            json.dump(progress_data, f, indent=2)
    except Exception as e:
        # If we can't write progress, print to console but don't crash the scraper
        print(f"Warning: Could not write progress to {progress_file}: {e}")
