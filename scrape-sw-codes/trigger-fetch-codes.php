<?php
/**
 * Trigger the fetch_codes Docker container to run
 * This will start the discover_codes.py script to fetch business activity codes
 */

header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');

try {
    // Check if docker binary is accessible
    exec("which docker 2>&1", $whichOutput, $whichCode);
    $dockerPath = $whichCode === 0 ? trim($whichOutput[0]) : '/usr/bin/docker';

    // Verify the binary actually exists and is executable
    if (!file_exists($dockerPath)) {
        throw new Exception("Docker binary not found at $dockerPath. Is /usr/bin/docker mounted into the container?");
    }

    // Test docker connectivity (ps is non-destructive)
    exec("$dockerPath ps --format '{{.Names}}' 2>&1", $psOutput, $psCode);
    if ($psCode !== 0) {
        throw new Exception("Docker socket not accessible (exit $psCode): " . implode("\n", $psOutput));
    }

    // Check if SW_CODES_PYTHON container exists (running or stopped)
    $runningContainers = implode("\n", $psOutput);
    exec("$dockerPath ps -a --format '{{.Names}}' 2>&1", $allOutput, $allCode);
    $allContainers = implode("\n", $allOutput);

    if (strpos($allContainers, 'SW_CODES_PYTHON') === false) {
        throw new Exception("SW_CODES_PYTHON container does not exist. Run 'docker-compose up -d' first to create it.");
    }

    // Restart the container (works whether stopped or running)
    exec("$dockerPath restart SW_CODES_PYTHON 2>&1", $output, $returnCode);

    if ($returnCode === 0) {
        // Reset the progress file immediately so the Portal doesn't read the
        // previous run's "completed" status and stop monitoring prematurely.
        $progressFile = '/tmp/fetch_progress.json';
        file_put_contents($progressFile, json_encode([
            'status'        => 'pending',
            'message'       => 'Container restarted, waiting for fetch to begin...',
            'current_page'  => 0,
            'total_pages'   => 0,
            'total_records' => 0,
            'new_inserted'  => 0,
            'updated'       => 0,
            'skipped'       => 0,
            'timestamp'     => microtime(true),
        ]));

        echo json_encode([
            'success' => true,
            'message' => 'SW_CODES_PYTHON container restarted successfully.',
            'output' => implode("\n", $output),
            'docker_path' => $dockerPath
        ]);
    } else {
        throw new Exception("docker restart failed (exit $returnCode): " . implode("\n", $output));
    }

} catch (Exception $e) {
    http_response_code(500);
    echo json_encode([
        'success' => false,
        'message' => $e->getMessage()
    ]);
}
