<?php
/**
 * Fetch Codes 3 - Pure PHP: curl to MOCI API, pg to DB.
 * No Python. Uses PHP curl with SSL verify disabled.
 * Run: php fetch_codes_php.php
 */
$PROGRESS_FILE = '/tmp/fetch_progress.json';
$API_URL = 'https://investor.sw.gov.qa/wps/portal/investors/information-center/ba/search-results/' .
    '!ut/p/z1/04_Sj9CPykssy0xPLMnMz0vMAfIjo8zivfxNXA393Q38Dbz9LA3MAt38_UyNDQ0MAk30w_' .
    'EqcDTVjyJJv0VomJFBoLOTaZCju4Wxv6MhcfoNcABHA8L6o_AqAfkAVYG_r4uTgZmjqWeuo0uQobuvOboCLH4A' .
    'K8DjyODEIv2C3NDQCINMT11HRUUAe2qoOw!!/dz/d5/L2dBISEvZ0FBIS9nQSEh/p0/' .
    'IZ7_JO4E1OG0O0KN906QFON5310013=CZ6_JO4E1OG0O0KN906QFON53100Q4=NJbaSearchResource=/';
$PAGE_SIZE = 100;
$DB_DSN = 'host=localhost port=5432 dbname=codesdb user=codesuser password=CodesPass2024';

function write_progress($status, $msg, $page = 0, $total = 0, $rec = 0, $ins = 0, $upd = 0, $skip = 0) {
    global $PROGRESS_FILE;
    file_put_contents($PROGRESS_FILE, json_encode([
        'status' => $status, 'message' => $msg,
        'current_page' => $page, 'total_pages' => $total, 'total_records' => $rec,
        'new_inserted' => $ins, 'updated' => $upd, 'skipped' => $skip,
        'timestamp' => microtime(true)
    ]));
}

function fetch_page($page) {
    global $API_URL, $PAGE_SIZE;
    $url = $API_URL . 'page=' . $page . '&size=' . $PAGE_SIZE;
    $ch = curl_init($url);
    curl_setopt_array($ch, [
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_TIMEOUT => 120,
        CURLOPT_SSL_VERIFYPEER => false,
        CURLOPT_SSL_VERIFYHOST => false,
        CURLOPT_FOLLOWLOCATION => true,
        CURLOPT_HTTPHEADER => [
            'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept: application/json',
        ],
    ]);
    $body = curl_exec($ch);
    $code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);
    if ($code !== 200 || !$body) return [null, 1, 0];
    $data = @json_decode($body, true);
    if (!$data || !isset($data['data']['activities'])) return [null, 1, 0];
    $act = $data['data']['activities'];
    return [$act['content'] ?? [], $act['totalPages'] ?? 1, $act['totalElements'] ?? 0];
}

write_progress('starting', 'Starting PHP fetch...');
echo "Qatar Single Window - Fetch Codes (PHP)\n";

$conn = @pg_connect($DB_DSN);
if (!$conn) {
    write_progress('error', 'Database connection failed');
    exit(1);
}
write_progress('running', 'Database connected');

$content, $total_pages, $total_el = fetch_page(1);
if ($content === null) {
    write_progress('error', 'Could not reach MOCI API');
    pg_close($conn);
    exit(1);
}
echo "Page 1... [$total_el activities, $total_pages pages]\n";

$ins = $upd = $skip = 0;
$all_codes = [];

for ($p = 1; $p <= $total_pages; $p++) {
    if ($p > 1) list($content, , ) = fetch_page($p);
    write_progress('running', "Page $p/$total_pages", $p, $total_pages, 0, $ins, $upd, $skip);
    if (empty($content)) break;
    foreach ($content as $item) {
        $code = $item['activityCode'] ?? null;
        if (!$code) continue;
        $all_codes[] = $code;
        $ind = $item['isicIndustryId'] ?? '';
        $en = $item['nameEn'] ?? '';
        $ar = $item['nameAr'] ?? '';
        $desc = $item['descriptionEn'] ?? '';
        $res = pg_query_params($conn, 'SELECT activity_code, industry_id, name_en, name_ar, description_en FROM business_activity_codes WHERE activity_code = $1', [$code]);
        $row = pg_fetch_assoc($res);
        if ($row) {
            $same = ($ind === ($row['industry_id'] ?? '')) && ($en === ($row['name_en'] ?? '')) && ($ar === ($row['name_ar'] ?? '')) && ($desc === ($row['description_en'] ?? ''));
            if ($same) { $skip++; continue; }
            pg_query_params($conn, 'UPDATE business_activity_codes SET industry_id=$2, name_en=$3, name_ar=$4, description_en=$5, updated_at=NOW() WHERE activity_code=$1', [$code, $ind, $en, $ar, $desc]);
            $upd++;
        } else {
            pg_query_params($conn, 'INSERT INTO business_activity_codes (activity_code, industry_id, name_en, name_ar, description_en, updated_at) VALUES ($1,$2,$3,$4,$5,NOW())', [$code, $ind, $en, $ar, $desc]);
            $ins++;
        }
    }
    echo "  Page $p: +$ins new, ~$upd updated, =$skip unchanged\n";
}

if (!empty($all_codes)) {
    $all_set = array_unique($all_codes);
    $r = pg_query($conn, 'SELECT activity_code FROM business_activity_codes');
    $db_codes = [];
    while ($row = pg_fetch_assoc($r)) $db_codes[] = $row['activity_code'];
    $stale = array_diff($db_codes, $all_set);
    if (!empty($stale)) {
        pg_query_params($conn, 'DELETE FROM business_activity_codes WHERE activity_code = ANY($1)', [array_values($stale)]);
        echo "Deleted " . count($stale) . " stale codes\n";
    }
}
$count = pg_fetch_result(pg_query($conn, 'SELECT COUNT(*) FROM business_activity_codes'), 0, 0);
pg_close($conn);

write_progress('completed', 'Fetch completed successfully', 0, 0, (int)$count, $ins, $upd, $skip);
echo "COMPLETE! $count records\n";
