"""
Unit Tests for Progress Writer Module

Tests the progress_writer module to ensure it correctly writes progress data
to JSON files with all required fields.

Requirements: 5.3, 5.4, 6.1, 6.2, 6.3, 6.4, 6.5, 6.6
"""

import json
import os
import tempfile
import unittest
from unittest.mock import patch, mock_open
import time

# Import the module to test
from progress_writer import write_progress, PROGRESS_FILE_EN, PROGRESS_FILE_AR


class TestProgressWriter(unittest.TestCase):
    """Unit tests for the progress writer module"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up test files"""
        # Clean up temp files if they exist
        for file_path in [PROGRESS_FILE_EN, PROGRESS_FILE_AR]:
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except Exception:
                    pass
    
    def test_write_progress_en_creates_file(self):
        """Test that write_progress creates a file for EN language"""
        write_progress('en', 'running', 1, 10, 'Test message')
        
        self.assertTrue(os.path.exists(PROGRESS_FILE_EN))
    
    def test_write_progress_ar_creates_file(self):
        """Test that write_progress creates a file for AR language"""
        write_progress('ar', 'running', 1, 10, 'Test message')
        
        self.assertTrue(os.path.exists(PROGRESS_FILE_AR))
    
    def test_progress_data_structure_running(self):
        """Test that progress data contains all required fields for 'running' status"""
        write_progress('en', 'running', 5, 100, 'Processing row 5/100', 0)
        
        with open(PROGRESS_FILE_EN, 'r') as f:
            data = json.load(f)
        
        # Requirement 6.1: JSON format
        self.assertIsInstance(data, dict)
        
        # Requirement 6.2: status field with correct value
        self.assertIn('status', data)
        self.assertEqual(data['status'], 'running')
        
        # Requirement 6.3: current_row field
        self.assertIn('current_row', data)
        self.assertEqual(data['current_row'], 5)
        
        # Requirement 6.4: total_rows field
        self.assertIn('total_rows', data)
        self.assertEqual(data['total_rows'], 100)
        
        # Requirement 6.5: message field
        self.assertIn('message', data)
        self.assertEqual(data['message'], 'Processing row 5/100')
        
        # Timestamp field
        self.assertIn('timestamp', data)
        self.assertIsInstance(data['timestamp'], int)
        
        # Requirement 6.6: rows_processed field (present but 0 during running)
        self.assertIn('rows_processed', data)
        self.assertEqual(data['rows_processed'], 0)
    
    def test_progress_data_structure_completed(self):
        """Test that progress data contains rows_processed on completion"""
        write_progress('en', 'completed', 100, 100, 'Scraping completed successfully', 95)
        
        with open(PROGRESS_FILE_EN, 'r') as f:
            data = json.load(f)
        
        # Requirement 6.2: status field with 'completed' value
        self.assertEqual(data['status'], 'completed')
        
        # Requirement 6.6: rows_processed field with final count
        self.assertIn('rows_processed', data)
        self.assertEqual(data['rows_processed'], 95)
        
        self.assertEqual(data['current_row'], 100)
        self.assertEqual(data['total_rows'], 100)
        self.assertEqual(data['message'], 'Scraping completed successfully')
    
    def test_progress_data_structure_error(self):
        """Test that progress data contains error message on error status"""
        error_msg = 'Connection timeout error'
        write_progress('en', 'error', 10, 100, error_msg, 0)
        
        with open(PROGRESS_FILE_EN, 'r') as f:
            data = json.load(f)
        
        # Requirement 6.2: status field with 'error' value
        self.assertEqual(data['status'], 'error')
        
        # Requirement 6.5: message field contains error description
        self.assertEqual(data['message'], error_msg)
        
        self.assertEqual(data['current_row'], 10)
        self.assertEqual(data['total_rows'], 100)
    
    def test_status_values_are_valid(self):
        """Test that only valid status values are accepted"""
        valid_statuses = ['running', 'completed', 'error']
        
        for status in valid_statuses:
            write_progress('en', status, 0, 10, f'Testing {status}')
            
            with open(PROGRESS_FILE_EN, 'r') as f:
                data = json.load(f)
            
            self.assertEqual(data['status'], status)
    
    def test_language_case_insensitive(self):
        """Test that language parameter is case-insensitive"""
        # Test uppercase
        write_progress('EN', 'running', 1, 10, 'Test EN')
        self.assertTrue(os.path.exists(PROGRESS_FILE_EN))
        
        # Test mixed case
        write_progress('Ar', 'running', 1, 10, 'Test AR')
        self.assertTrue(os.path.exists(PROGRESS_FILE_AR))
    
    def test_timestamp_is_current(self):
        """Test that timestamp reflects current time"""
        before = int(time.time())
        write_progress('en', 'running', 1, 10, 'Test')
        after = int(time.time())
        
        with open(PROGRESS_FILE_EN, 'r') as f:
            data = json.load(f)
        
        timestamp = data['timestamp']
        self.assertGreaterEqual(timestamp, before)
        self.assertLessEqual(timestamp, after)
    
    def test_progress_file_overwrites_previous(self):
        """Test that new progress overwrites previous progress"""
        # Write first progress
        write_progress('en', 'running', 1, 10, 'First message')
        
        with open(PROGRESS_FILE_EN, 'r') as f:
            data1 = json.load(f)
        
        # Write second progress
        write_progress('en', 'running', 2, 10, 'Second message')
        
        with open(PROGRESS_FILE_EN, 'r') as f:
            data2 = json.load(f)
        
        # Verify data was overwritten
        self.assertEqual(data2['current_row'], 2)
        self.assertEqual(data2['message'], 'Second message')
        self.assertNotEqual(data1['message'], data2['message'])
    
    def test_en_and_ar_files_are_separate(self):
        """Test that EN and AR progress files are independent"""
        write_progress('en', 'running', 5, 100, 'EN message')
        write_progress('ar', 'running', 10, 200, 'AR message')
        
        with open(PROGRESS_FILE_EN, 'r') as f:
            en_data = json.load(f)
        
        with open(PROGRESS_FILE_AR, 'r') as f:
            ar_data = json.load(f)
        
        # Verify files contain different data
        self.assertEqual(en_data['current_row'], 5)
        self.assertEqual(en_data['total_rows'], 100)
        self.assertEqual(en_data['message'], 'EN message')
        
        self.assertEqual(ar_data['current_row'], 10)
        self.assertEqual(ar_data['total_rows'], 200)
        self.assertEqual(ar_data['message'], 'AR message')
    
    def test_write_progress_handles_write_errors_gracefully(self):
        """Test that write errors don't crash the function"""
        # Mock open to raise an exception
        with patch('builtins.open', side_effect=PermissionError('Access denied')):
            # Should not raise an exception
            try:
                write_progress('en', 'running', 1, 10, 'Test')
            except Exception as e:
                self.fail(f"write_progress raised an exception: {e}")
    
    def test_json_format_is_valid(self):
        """Test that written JSON is valid and parseable"""
        write_progress('en', 'running', 1, 10, 'Test message')
        
        # Should be able to parse without errors
        with open(PROGRESS_FILE_EN, 'r') as f:
            data = json.load(f)
        
        # Verify it's a dictionary
        self.assertIsInstance(data, dict)
    
    def test_default_parameters(self):
        """Test that function works with minimal parameters"""
        write_progress('en', 'running')
        
        with open(PROGRESS_FILE_EN, 'r') as f:
            data = json.load(f)
        
        # Verify defaults are applied
        self.assertEqual(data['current_row'], 0)
        self.assertEqual(data['total_rows'], 0)
        self.assertEqual(data['message'], '')
        self.assertEqual(data['rows_processed'], 0)
    
    def test_special_characters_in_message(self):
        """Test that special characters in messages are handled correctly"""
        special_msg = 'Error: "Connection failed" at row #5 (50%)'
        write_progress('en', 'error', 5, 10, special_msg)
        
        with open(PROGRESS_FILE_EN, 'r') as f:
            data = json.load(f)
        
        self.assertEqual(data['message'], special_msg)
    
    def test_unicode_characters_in_message(self):
        """Test that Unicode characters (Arabic) are handled correctly"""
        arabic_msg = 'معالجة الصف 5/100'
        write_progress('ar', 'running', 5, 100, arabic_msg)
        
        with open(PROGRESS_FILE_AR, 'r') as f:
            data = json.load(f)
        
        self.assertEqual(data['message'], arabic_msg)


if __name__ == '__main__':
    unittest.main()
