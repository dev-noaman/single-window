<?php
/**
 * Trigger the fetch_codes Docker container to run
 * This will start the discover_codes.py script to fetch business activity codes
 */

header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');

try {
    // Check if docker is accessible
    exec("which docker 2>&1", $whichOutput, $whichCode);
    $dockerPath = $whichCode === 0 ? trim($whichOutput[0]) : '/usr/bin/docker';
    
    // Use docker restart command - simpler and more reliable
    $command = "$dockerPath restart SW_CODES_PYTHON 2>&1";
    
    // Execute the command
    exec($command, $output, $returnCode);
    
    if ($returnCode === 0) {
        echo json_encode([
            'success' => true,
            'message' => 'SW_CODES_PYTHON container restarted successfully. Check Docker logs for progress.',
            'output' => implode("\n", $output),
            'docker_path' => $dockerPath
        ]);
    } else {
        throw new Exception("Docker command failed with code $returnCode: " . implode("\n", $output));
    }
    
} catch (Exception $e) {
    http_response_code(500);
    echo json_encode([
        'success' => false,
        'message' => $e->getMessage()
    ]);
}
