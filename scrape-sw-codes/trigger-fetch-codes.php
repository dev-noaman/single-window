<?php
/**
 * Trigger discover_codes.py to fetch business activity codes.
 * Runs directly on the host (no Docker).
 */

header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');

$progressFile = '/tmp/fetch_progress.json';
$scriptDir = __DIR__;
$pythonScript = "$scriptDir/discover_codes.py";
$logFile = '/tmp/discover_codes.log';

try {
    // Verify the Python script exists
    if (!file_exists($pythonScript)) {
        throw new Exception("discover_codes.py not found at $pythonScript");
    }

    // Check if a fetch is already running
    exec("pgrep -f 'python3.*discover_codes.py' 2>/dev/null", $pgrepOutput, $pgrepCode);
    if ($pgrepCode === 0 && !empty($pgrepOutput)) {
        echo json_encode([
            'success' => false,
            'message' => 'Fetch is already running (PID: ' . trim($pgrepOutput[0]) . ')'
        ]);
        exit;
    }

    // Reset the progress file BEFORE starting the script.
    // Prevents the Portal from reading a stale "completed" from the previous run.
    file_put_contents($progressFile, json_encode([
        'status'        => 'pending',
        'message'       => 'Starting fetch process...',
        'current_page'  => 0,
        'total_pages'   => 0,
        'total_records' => 0,
        'new_inserted'  => 0,
        'updated'       => 0,
        'skipped'       => 0,
        'timestamp'     => microtime(true),
    ]));

    // Run discover_codes.py as a background process on the host
    $dbUrl = 'postgresql://codesuser:CodesPass2024@localhost:5432/codesdb';
    $cmd = "DATABASE_URL='$dbUrl' PYTHONUNBUFFERED=1 python3 '$pythonScript' > '$logFile' 2>&1 &";
    exec($cmd, $output, $returnCode);

    // Brief wait then check if the process started
    usleep(500000); // 0.5s
    exec("pgrep -f 'python3.*discover_codes.py' 2>/dev/null", $checkOutput, $checkCode);
    $isRunning = ($checkCode === 0 && !empty($checkOutput));

    // Also check if the progress file has been updated (script started writing)
    $containerState = $isRunning ? 'running' : 'unknown';
    $logTail = '';

    if (!$isRunning) {
        // Script may have started and exited already — check log
        usleep(1500000); // 1.5s more
        if (file_exists($logFile)) {
            $logTail = implode("\n", array_slice(file($logFile, FILE_IGNORE_NEW_LINES), -20));
        }
        // Check progress file for error status
        if (file_exists($progressFile)) {
            $progress = json_decode(file_get_contents($progressFile), true);
            if (isset($progress['status'])) {
                $containerState = $progress['status'];
            }
        }
        if ($containerState === 'pending' || $containerState === 'unknown') {
            $containerState = 'exited';
        }
    }

    echo json_encode([
        'success' => true,
        'message' => $isRunning
            ? 'Fetch process started successfully.'
            : 'Fetch process started (may have completed quickly or failed).',
        'container_state' => $containerState,
        'log_tail' => $logTail
    ]);

} catch (Exception $e) {
    http_response_code(500);
    echo json_encode([
        'success' => false,
        'message' => $e->getMessage()
    ]);
}
