<?php
/**
 * Temporary: read debug-650286.log for debugging FETCH_CODES_3
 * Remove after fix is verified.
 */
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
$log = __DIR__ . '/../debug-650286.log';
$lines = file_exists($log) ? file($log, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES) : [];
$out = array_map(function($l) { $d = @json_decode($l, true); return $d ?: ['raw' => substr($l, 0, 200)]; }, array_slice($lines, -50));
echo json_encode(['count' => count($lines), 'recent' => $out], JSON_PRETTY_PRINT);
