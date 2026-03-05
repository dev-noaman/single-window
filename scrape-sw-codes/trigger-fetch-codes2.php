<?php
/**
 * Trigger discover_codes2.py (curl-based simple fetch).
 * Same progress file as discover_codes - progress.php works for both.
 */

header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');

$progressFile = '/tmp/fetch_progress.json';
$scriptDir = __DIR__;
$pythonScript = "$scriptDir/discover_codes2.py";
$logFile = '/tmp/discover_codes2.log';

try {
    if (!file_exists($pythonScript)) {
        throw new Exception("discover_codes2.py not found at $pythonScript");
    }

    $force = isset($_GET['force']) && $_GET['force'] === '1';
    exec("pgrep -f 'python3.*discover_codes2\.py' 2>/dev/null", $pgrepOutput, $pgrepCode);
    if ($pgrepCode === 0 && !empty($pgrepOutput)) {
        if ($force) {
            exec("pkill -f 'python3.*discover_codes2\.py' 2>/dev/null");
            usleep(500000);
        } else {
            echo json_encode([
                'success' => false,
                'message' => 'Fetch Codes 2 already running (PID: ' . trim($pgrepOutput[0]) . ')',
                'hint' => 'Add ?force=1 to kill and restart'
            ]);
            exit;
        }
    }

    file_put_contents($progressFile, json_encode([
        'status' => 'pending',
        'message' => 'Starting Fetch Codes 2 (curl)...',
        'current_page' => 0, 'total_pages' => 0, 'total_records' => 0,
        'new_inserted' => 0, 'updated' => 0, 'skipped' => 0,
        'timestamp' => microtime(true),
    ]));

    $dbUrl = 'postgresql://codesuser:CodesPass2024@localhost:5432/codesdb';
    $cmd = "DATABASE_URL='$dbUrl' PYTHONUNBUFFERED=1 python3 '$pythonScript' > '$logFile' 2>&1 &";
    exec($cmd, $output, $returnCode);

    usleep(500000);
    exec("pgrep -f 'python3.*discover_codes2\.py' 2>/dev/null", $checkOutput, $checkCode);
    $isRunning = ($checkCode === 0 && !empty($checkOutput));

    $logTail = '';
    if (!$isRunning && file_exists($logFile)) {
        usleep(1500000);
        $logTail = implode("\n", array_slice(file($logFile, FILE_IGNORE_NEW_LINES), -20));
    }

    echo json_encode([
        'success' => true,
        'message' => $isRunning ? 'Fetch Codes 2 started.' : 'Fetch Codes 2 started (may have completed or failed).',
        'container_state' => $isRunning ? 'running' : 'exited',
        'log_tail' => $logTail
    ]);
} catch (Exception $e) {
    http_response_code(500);
    echo json_encode(['success' => false, 'message' => $e->getMessage()]);
}
