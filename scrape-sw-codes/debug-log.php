<?php
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');

$logFile = '/tmp/discover_codes.log';
$progressFile = '/tmp/fetch_progress.json';

$result = [];

// Check if discover_codes.py is running
exec("pgrep -f 'python3.*discover_codes.py' 2>/dev/null", $pgrepOutput, $pgrepCode);
$result['process_running'] = ($pgrepCode === 0 && !empty($pgrepOutput));
$result['pids'] = $pgrepOutput ?: [];

// Read progress file
if (file_exists($progressFile)) {
    $result['progress'] = json_decode(file_get_contents($progressFile), true);
} else {
    $result['progress'] = 'file not found';
}

// Read last 50 lines of log
if (file_exists($logFile)) {
    $result['log_size'] = filesize($logFile);
    $result['log_tail'] = array_slice(file($logFile, FILE_IGNORE_NEW_LINES), -50);
} else {
    $result['log_tail'] = 'file not found';
}

// Read debug log
$debugLog = '/tmp/debug_discover.log';
if (file_exists($debugLog)) {
    $result['debug_log'] = array_slice(file($debugLog, FILE_IGNORE_NEW_LINES), -30);
} else {
    $result['debug_log'] = 'file not found';
}

// Check python3 and scrapling availability
exec("python3 -c 'import scrapling; print(scrapling.__version__)' 2>&1", $pyOut, $pyCode);
$result['scrapling_check'] = ['exit_code' => $pyCode, 'output' => $pyOut];

exec("python3 -c 'from scrapling.fetchers import AsyncFetcher; print(\"OK\")' 2>&1", $fetcherOut, $fetcherCode);
$result['asyncfetcher_check'] = ['exit_code' => $fetcherCode, 'output' => $fetcherOut];

echo json_encode($result, JSON_PRETTY_PRINT);
