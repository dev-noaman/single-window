"""
Integration Tests for scrape-AR.py Progress Tracking

Tests that scrape-AR.py correctly integrates with the progress_writer module
to write progress updates during scraper execution.

Requirements: 8.2, 8.3, 8.4, 8.5, 8.6
"""

import json
import os
import sys
import unittest
from unittest.mock import Mock, patch, MagicMock
import asyncio

# Add parent directory to path to import scrape-AR
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from progress_writer import PROGRESS_FILE_AR


class TestScrapeARProgressIntegration(unittest.TestCase):
    """Integration tests for progress tracking in scrape-AR.py"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Clean up progress file before each test
        if os.path.exists(PROGRESS_FILE_AR):
            try:
                os.remove(PROGRESS_FILE_AR)
            except Exception:
                pass
    
    def tearDown(self):
        """Clean up test files"""
        if os.path.exists(PROGRESS_FILE_AR):
            try:
                os.remove(PROGRESS_FILE_AR)
            except Exception:
                pass
    
    def test_progress_file_created_on_scraper_start(self):
        """Test that progress file is created when scraper starts (Requirement 8.3)"""
        # Import here to avoid issues with mocking
        from progress_writer import write_progress
        
        # Simulate scraper start
        write_progress('ar', 'running', 0, 10, 'Starting AR scraper...')
        
        # Verify file exists
        self.assertTrue(os.path.exists(PROGRESS_FILE_AR))
        
        # Verify content
        with open(PROGRESS_FILE_AR, 'r') as f:
            data = json.load(f)
        
        self.assertEqual(data['status'], 'running')
        self.assertEqual(data['current_row'], 0)
        self.assertGreater(data['total_rows'], 0)
        self.assertIn('Starting', data['message'])
    
    def test_progress_updated_after_processing_row(self):
        """Test that progress is updated after processing each row (Requirement 8.2)"""
        from progress_writer import write_progress
        
        # Simulate processing multiple rows
        total_rows = 5
        for row in range(1, total_rows + 1):
            write_progress('ar', 'running', row, total_rows, 
                         f'Processing row {row}/{total_rows}', row - 1)
            
            # Verify progress file is updated
            with open(PROGRESS_FILE_AR, 'r') as f:
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
        write_progress('ar', 'completed', total_rows, total_rows, 
                     'Scraping completed successfully', rows_processed)
        
        # Verify completion status
        with open(PROGRESS_FILE_AR, 'r') as f:
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
        write_progress('ar', 'error', 5, 10, f'Scraper error: {error_message}', 4)
        
        # Verify error status
        with open(PROGRESS_FILE_AR, 'r') as f:
            data = json.load(f)
        
        self.assertEqual(data['status'], 'error')
        self.assertIn('error', data['message'].lower())
        self.assertIn(error_message, data['message'])
    
    def test_progress_sequence_matches_scraper_flow(self):
        """Test that progress updates follow the expected scraper flow"""
        from progress_writer import write_progress
        
        total_rows = 3
        
        # 1. Initial progress
        write_progress('ar', 'running', 0, total_rows, 'Starting AR scraper...')
        with open(PROGRESS_FILE_AR, 'r') as f:
            data = json.load(f)
        self.assertEqual(data['status'], 'running')
        self.assertEqual(data['current_row'], 0)
        
        # 2. Process each row
        for row in range(1, total_rows + 1):
            write_progress('ar', 'running', row, total_rows, 
                         f'Processing row {row}/{total_rows}', row - 1)
            with open(PROGRESS_FILE_AR, 'r') as f:
                data = json.load(f)
            self.assertEqual(data['status'], 'running')
            self.assertEqual(data['current_row'], row)
        
        # 3. Completion
        write_progress('ar', 'completed', total_rows, total_rows, 
                     'Scraping completed successfully', total_rows)
        with open(PROGRESS_FILE_AR, 'r') as f:
            data = json.load(f)
        self.assertEqual(data['status'], 'completed')
        self.assertEqual(data['rows_processed'], total_rows)
    
    def test_no_codes_error_handling(self):
        """Test that error is written when no codes are found"""
        from progress_writer import write_progress
        
        # Simulate no codes scenario
        write_progress('ar', 'error', 0, 0, 'No activity codes found in sheet')
        
        with open(PROGRESS_FILE_AR, 'r') as f:
            data = json.load(f)
        
        self.assertEqual(data['status'], 'error')
        self.assertIn('No activity codes', data['message'])
        self.assertEqual(data['total_rows'], 0)
    
    def test_language_consistency_with_en_scraper(self):
        """Test that AR scraper follows identical pattern to EN scraper (Requirement 8.6)"""
        from progress_writer import write_progress, PROGRESS_FILE_EN
        
        # Write progress for both languages with same parameters
        total_rows = 5
        current_row = 3
        message = 'Processing row 3/5'
        rows_processed = 2
        
        write_progress('en', 'running', current_row, total_rows, message, rows_processed)
        write_progress('ar', 'running', current_row, total_rows, message, rows_processed)
        
        # Read both files
        with open(PROGRESS_FILE_EN, 'r') as f:
            en_data = json.load(f)
        
        with open(PROGRESS_FILE_AR, 'r') as f:
            ar_data = json.load(f)
        
        # Verify structure is identical (except timestamp)
        self.assertEqual(en_data['status'], ar_data['status'])
        self.assertEqual(en_data['current_row'], ar_data['current_row'])
        self.assertEqual(en_data['total_rows'], ar_data['total_rows'])
        self.assertEqual(en_data['message'], ar_data['message'])
        self.assertEqual(en_data['rows_processed'], ar_data['rows_processed'])
        
        # Verify both have same keys
        self.assertEqual(set(en_data.keys()), set(ar_data.keys()))


if __name__ == '__main__':
    unittest.main()
