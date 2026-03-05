<?php
/**
 * Trigger fetch_codes_php.php (pure PHP fetch).
 */
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');

$progressFile = '/tmp/fetch_progress.json';
$scriptPath = __DIR__ . '/fetch_codes_php.php';
$logFile = '/tmp/discover_codes_php.log';

try {
    if (!file_exists($scriptPath)) {
        throw new Exception("fetch_codes_php.php not found");
    }
    $force = isset($_GET['force']) && $_GET['force'] === '1';
    exec("pgrep -f 'php.*fetch_codes_php' 2>/dev/null", $out, $c);
    if ($c === 0 && !empty($out)) {
        if (!$force) {
            echo json_encode(['success' => false, 'message' => 'PHP fetch already running (add ?force=1 to restart)']);
            exit;
        }
        exec("pkill -f 'php.*fetch_codes_php' 2>/dev/null");
        usleep(500000);
    }
    file_put_contents($progressFile, json_encode([
        'status' => 'pending', 'message' => 'Starting PHP fetch...',
        'current_page' => 0, 'total_pages' => 0, 'total_records' => 0,
        'new_inserted' => 0, 'updated' => 0, 'skipped' => 0, 'timestamp' => microtime(true),
    ]));
    exec("php " . escapeshellarg($scriptPath) . " > " . escapeshellarg($logFile) . " 2>&1 &");
    usleep(500000);
    exec("pgrep -f 'php.*fetch_codes_php' 2>/dev/null", $check, $cc);
    $running = ($cc === 0 && !empty($check));
    echo json_encode([
        'success' => true,
        'message' => $running ? 'PHP fetch started.' : 'PHP fetch started (check progress).',
        'container_state' => $running ? 'running' : 'unknown',
    ]);
} catch (Exception $e) {
    http_response_code(500);
    echo json_encode(['success' => false, 'message' => $e->getMessage()]);
}
