<?php
/**
 * Real-time progress endpoint for EN scraper - reads from progress file
 * No buffering, instant updates
 */

header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');

$progressFile = '/tmp/scrape_progress_en.json';

try {
    if (!file_exists($progressFile)) {
        // No progress file yet - container might not be running
        echo json_encode([
            'success' => false,
            'status' => 'idle',
            'message' => 'No active scrape process'
        ], JSON_PRETTY_PRINT);
        exit;
    }
    
    // Read progress file
    $progressData = file_get_contents($progressFile);
    $progress = json_decode($progressData, true);
    
    if (!$progress) {
        throw new Exception('Failed to parse progress data');
    }
    
    // Return progress
    echo json_encode([
        'success' => true,
        'status' => $progress['status'] ?? 'unknown',
        'message' => $progress['message'] ?? '',
        'current_row' => $progress['current_row'] ?? 0,
        'total_rows' => $progress['total_rows'] ?? 0,
        'rows_processed' => $progress['rows_processed'] ?? 0,
        'elapsed_time' => $progress['elapsed_time'] ?? 0,
        'timestamp' => $progress['timestamp'] ?? time()
    ], JSON_PRETTY_PRINT);
    
} catch (Exception $e) {
    http_response_code(500);
    echo json_encode([
        'success' => false,
        'status' => 'error',
        'message' => $e->getMessage()
    ], JSON_PRETTY_PRINT);
}
