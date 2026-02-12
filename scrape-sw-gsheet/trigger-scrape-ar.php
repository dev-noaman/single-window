<?php
/**
 * Trigger the GSHEET_SCRAPER_AR Docker container to run
 * This will start the scrape-AR.py script to scrape Arabic data from Qatar investor website
 */

header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');

try {
    // Check if Google credentials exist
    $credentialsPath = __DIR__ . '/drive/google-credentials.json';
    
    if (!file_exists($credentialsPath)) {
        throw new Exception('Google credentials not found');
    }
    
    // Check if docker is accessible
    exec("which docker 2>&1", $whichOutput, $whichCode);
    $dockerPath = $whichCode === 0 ? trim($whichOutput[0]) : '/usr/bin/docker';
    
    // Use docker restart command - simpler and more reliable
    $command = "$dockerPath restart GSHEET_SCRAPER_AR 2>&1";
    
    // Execute the command
    exec($command, $output, $returnCode);
    
    if ($returnCode === 0) {
        echo json_encode([
            'success' => true,
            'message' => 'GSHEET_SCRAPER_AR container restarted successfully. Check progress for updates.',
            'output' => implode("\n", $output),
            'docker_path' => $dockerPath
        ], JSON_PRETTY_PRINT);
    } else {
        throw new Exception("Failed to start scraper container: Docker command failed with code $returnCode: " . implode("\n", $output));
    }
    
} catch (Exception $e) {
    http_response_code(500);
    echo json_encode([
        'success' => false,
        'message' => $e->getMessage()
    ], JSON_PRETTY_PRINT);
}
