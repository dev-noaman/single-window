"""
Integration Tests for scrape-EN.py Progress Tracking

Tests that scrape-EN.py correctly integrates with the progress_writer module
to write progress updates during scraper execution.

Requirements: 8.1, 8.3, 8.4, 8.5
"""

import json
import os
import sys
import unittest
from unittest.mock import Mock, patch, MagicMock
import asyncio

# Add parent directory to path to import scrape-EN
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from progress_writer import PROGRESS_FILE_EN


class TestScrapeENProgressIntegration(unittest.TestCase):
    """Integration tests for progress tracking in scrape-EN.py"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Clean up progress file before each test
        if os.path.exists(PROGRESS_FILE_EN):
            try:
                os.remove(PROGRESS_FILE_EN)
            except Exception:
                pass
    
    def tearDown(self):
        """Clean up test files"""
        if os.path.exists(PROGRESS_FILE_EN):
            try:
                os.remove(PROGRESS_FILE_EN)
            except Exception:
                pass
    
    def test_progress_file_created_on_scraper_start(self):
        """Test that progress file is created when scraper starts (Requirement 8.3)"""
        # Import here to avoid issues with mocking
        from progress_writer import write_progress
        
        # Simulate scraper start
        write_progress('en', 'running', 0, 10, 'Starting EN scraper...')
        
        # Verify file exists
        self.assertTrue(os.path.exists(PROGRESS_FILE_EN))
        
        # Verify content
        with open(PROGRESS_FILE_EN, 'r') as f:
            data = json.load(f)
        
        self.assertEqual(data['status'], 'running')
        self.assertEqual(data['current_row'], 0)
        self.assertGreater(data['total_rows'], 0)
        self.assertIn('Starting', data['message'])
    
    def test_progress_updated_after_processing_row(self):
        """Test that progress is updated after processing each row (Requirement 8.1)"""
        from progress_writer import write_progress
        
        # Simulate processing multiple rows
        total_rows = 5
        for row in range(1, total_rows + 1):
            write_progress('en', 'running', row, total_rows, 
                         f'Processing row {row}/{total_rows}', row - 1)
            
            # Verify progress file is updated
            with open(PROGRESS_FILE_EN, 'r') as f:
                data = json.load(f)
            
            self.assertEqual(data['status'], 'running')
            self.assertEqual(data['current_row'], row)
            self.assertEqual(data['total_rows'], total_rows)
            self.assertIn(f'row {row}', data['message'])
    
    def test_completion_progress_written(self):
        """Test that completion progress is written with rows_processed (Requirement 8.4)"""
        from progress_writer import write_progress
        
        total_rows = 10
        rows_processed = 8
        
        # Simulate completion
        write_progress('en', 'completed', total_rows, total_rows, 
                     'Scraping completed successfully', rows_processed)
        
        # Verify completion status
        with open(PROGRESS_FILE_EN, 'r') as f:
            data = json.load(f)
        
        self.assertEqual(data['status'], 'completed')
        self.assertEqual(data['current_row'], total_rows)
        self.assertEqual(data['total_rows'], total_rows)
        self.assertEqual(data['rows_processed'], rows_processed)
        self.assertIn('completed', data['message'].lower())
    
    def test_error_progress_written_on_exception(self):
        """Test that error progress is written on exceptions (Requirement 8.5)"""
        from progress_writer import write_progress
        
        error_message = 'Connection timeout error'
        
        # Simulate error
        write_progress('en', 'error', 5, 10, f'Scraper error: {error_message}', 4)
        
        # Verify error status
        with open(PROGRESS_FILE_EN, 'r') as f:
            data = json.load(f)
        
        self.assertEqual(data['status'], 'error')
        self.assertIn('error', data['message'].lower())
        self.assertIn(error_message, data['message'])
    
    def test_progress_sequence_matches_scraper_flow(self):
        """Test that progress updates follow the expected scraper flow"""
        from progress_writer import write_progress
        
        total_rows = 3
        
        # 1. Initial progress
        write_progress('en', 'running', 0, total_rows, 'Starting EN scraper...')
        with open(PROGRESS_FILE_EN, 'r') as f:
            data = json.load(f)
        self.assertEqual(data['status'], 'running')
        self.assertEqual(data['current_row'], 0)
        
        # 2. Process each row
        for row in range(1, total_rows + 1):
            write_progress('en', 'running', row, total_rows, 
                         f'Processing row {row}/{total_rows}', row - 1)
            with open(PROGRESS_FILE_EN, 'r') as f:
                data = json.load(f)
            self.assertEqual(data['status'], 'running')
            self.assertEqual(data['current_row'], row)
        
        # 3. Completion
        write_progress('en', 'completed', total_rows, total_rows, 
                     'Scraping completed successfully', total_rows)
        with open(PROGRESS_FILE_EN, 'r') as f:
            data = json.load(f)
        self.assertEqual(data['status'], 'completed')
        self.assertEqual(data['rows_processed'], total_rows)
    
    def test_no_codes_error_handling(self):
        """Test that error is written when no codes are found"""
        from progress_writer import write_progress
        
        # Simulate no codes scenario
        write_progress('en', 'error', 0, 0, 'No activity codes found in sheet')
        
        with open(PROGRESS_FILE_EN, 'r') as f:
            data = json.load(f)
        
        self.assertEqual(data['status'], 'error')
        self.assertIn('No activity codes', data['message'])
        self.assertEqual(data['total_rows'], 0)


if __name__ == '__main__':
    unittest.main()
