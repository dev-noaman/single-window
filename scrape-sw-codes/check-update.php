<?php
/**
 * Check if database needs updating by comparing with MOCI API
 * Returns: needs_update (true/false) and comparison data
 */

header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');

try {
    // MOCI API endpoint
    $apiUrl = "https://investor.sw.gov.qa/wps/portal/investors/information-center/ba/search-results/!ut/p/z1/04_Sj9CPykssy0xPLMnMz0vMAfIjo8zivfxNXA393Q38Dbz9LA3MAt38_UyNDQ0MAk30w_EqcDTVjyJJv0VomJFBoLOTaZCju4Wxv6MhcfoNcABHA8L6o_AqAfkAVYG_r4uTgZmjqWeoo0uQobuvOboCLH4AK8DjyODEIv2C3NDQCINMT11HRUUAe2qoOw!!/dz/d5/L2dBISEvZ0FBIS9nQSEh/p0/IZ7_JO4E1OG0O0KN906QFON5310013=CZ6_JO4E1OG0O0KN906QFON53100Q4=NJbaSearchResource=/?page=1&size=1";
    
    // Fetch from MOCI API
    $context = stream_context_create([
        'http' => [
            'method' => 'GET',
            'header' => "User-Agent: Mozilla/5.0\r\n" .
                       "Accept: application/json\r\n",
            'timeout' => 10
        ],
        'ssl' => [
            'verify_peer' => false,
            'verify_peer_name' => false
        ]
    ]);
    
    $response = @file_get_contents($apiUrl, false, $context);
    
    if ($response === false) {
        throw new Exception("Failed to fetch data from MOCI API");
    }
    
    $data = json_decode($response, true);
    
    // Extract total from API
    $apiTotal = 0;
    if (isset($data['data']['activities']['totalElements'])) {
        $apiTotal = (int)$data['data']['activities']['totalElements'];
    }
    
    if ($apiTotal === 0) {
        throw new Exception("Could not get total count from MOCI API");
    }
    
    // Get count from database
    $dbTotal = 0;
    $lastUpdate = null;
    
    // Connect to PostgreSQL (host or container: PGHOST from env when using host Postgres)
    $pgHost = getenv('PGHOST') ?: 'db';
    $pgPort = getenv('PGPORT') ?: '5432';
    $pgDb   = getenv('PGDATABASE') ?: 'codesdb';
    $pgUser = getenv('PGUSER') ?: 'codesuser';
    $pgPass = getenv('PGPASSWORD') ?: 'StrongPasswordHere';
    $dsn = "pgsql:host={$pgHost};port={$pgPort};dbname={$pgDb}";
    $pdo = new PDO($dsn, $pgUser, $pgPass, [
        PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
        PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC
    ]);
    
    // Get database count
    $stmt = $pdo->query("SELECT COUNT(*) as total FROM business_activity_codes");
    $row = $stmt->fetch();
    if ($row) {
        $dbTotal = (int)$row['total'];
    }
    
    // Get last update time
    $stmt = $pdo->query("SELECT MAX(updated_at) as last_update FROM business_activity_codes");
    $row = $stmt->fetch();
    if ($row) {
        $lastUpdate = $row['last_update'];
    }
    
    // Close connection
    $pdo = null;
    
    // Compare
    $needsUpdate = ($apiTotal !== $dbTotal);
    $difference = $apiTotal - $dbTotal;
    
    echo json_encode([
        'success' => true,
        'needs_update' => $needsUpdate,
        'api_total' => $apiTotal,
        'db_total' => $dbTotal,
        'difference' => $difference,
        'last_update' => $lastUpdate,
        'message' => $needsUpdate 
            ? "Database needs update: MOCI has $apiTotal codes, you have $dbTotal" 
            : "Database is up to date: $dbTotal codes (same as MOCI)"
    ], JSON_PRETTY_PRINT);
    
} catch (Exception $e) {
    http_response_code(500);
    echo json_encode([
        'success' => false,
        'needs_update' => null,
        'message' => $e->getMessage()
    ], JSON_PRETTY_PRINT);
}
