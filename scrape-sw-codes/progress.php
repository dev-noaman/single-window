<?php
/**
 * Real-time progress endpoint - reads from progress file
 * No buffering, instant updates
 */

header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');

$progressFile = '/tmp/fetch_progress.json';

try {
    if (!file_exists($progressFile)) {
        // No progress file yet - container might not be running
        echo json_encode([
            'success' => false,
            'status' => 'idle',
            'message' => 'No active fetch process'
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
        'current_page' => $progress['current_page'] ?? 0,
        'total_pages' => $progress['total_pages'] ?? 0,
        'total_records' => $progress['total_records'] ?? 0,
        'new_inserted' => $progress['new_inserted'] ?? 0,
        'updated' => $progress['updated'] ?? 0,
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
