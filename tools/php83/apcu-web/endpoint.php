<?php
// Synthetic experiment only. Never install this endpoint or aliases in Kaltura.
error_reporting(E_ALL);
ini_set('display_errors', '0');
set_error_handler(function ($severity, $message, $file, $line) {
    throw new ErrorException($message, 0, $severity, $file, $line);
});
header('Content-Type: application/json');
header('Cache-Control: no-store');
function respond($status, $value) {
    http_response_code($status);
    echo json_encode($value, JSON_THROW_ON_ERROR);
    exit;
}
try {
    $nonce = getenv('PHP83_HTTP_NONCE');
    if (!is_string($nonce) || !preg_match('/^[a-f0-9]{32}$/D', $nonce)) {
        throw new RuntimeException('Invalid server nonce');
    }
    if ($_SERVER['REQUEST_METHOD'] !== 'GET' || parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH) !== '/probe') {
        respond(400, array('ok' => false, 'error' => 'route'));
    }
    if (!isset($_GET['nonce']) || !is_string($_GET['nonce']) || !hash_equals($nonce, $_GET['nonce'])) {
        respond(403, array('ok' => false, 'error' => 'nonce'));
    }
    $phase = isset($_GET['phase']) ? $_GET['phase'] : null;
    if (!is_string($phase) || !in_array($phase, array('store', 'read', 'read-after-mismatch', 'mismatch', 'delete', 'miss', 'replace', 'read-new'), true)
        || count($_GET) !== 2) {
        respond(400, array('ok' => false, 'error' => 'phase'));
    }
    $mode = getenv('PHP83_EXPECTED_MODE');
    if (!in_array($mode, array('original', 'aliases'), true) || PHP_SAPI !== 'apache2handler'
        || !function_exists('apcu_enabled') || !apcu_enabled() || function_exists('apc_fetch')) {
        throw new RuntimeException('Unexpected mode, SAPI, APCu status or preexisting legacy alias');
    }
    $cacheDir = getenv('PHP83_CACHE_DIR');
    if (!$cacheDir || substr($cacheDir, -1) !== '/' || !is_dir($cacheDir) || !is_writable($cacheDir)
        || file_exists($cacheDir . 'base.reload')) {
        throw new RuntimeException('Cache fixture directory missing, unwritable, or contains reload marker');
    }
    if ($mode === 'aliases') {
        // TEST-ONLY names limited to the three functions used by exact kApcConf.
        function apc_fetch($key) { return apcu_fetch($key); }
        function apc_store($key, $value, $ttl = 0) { return apcu_store($key, $value, $ttl); }
        function apc_delete($key) { return apcu_delete($key); }
    }
    class kEnvironment {
        public static function get($key) {
            if ($key !== 'cache_root_path') {
                throw new RuntimeException('Unexpected environment fixture key');
            }
            return getenv('PHP83_CACHE_DIR');
        }
    }
    $sourceHashes = array();
    foreach (array('kApcConf', 'kBaseConfCache', 'kMapCacheInterface', 'kKeyCacheInterface') as $class) {
        $sourceHashes[$class . '.php'] = hash_file('sha256', '/audit/app/alpha/config/cache/' . $class . '.php');
    }
    require_once '/audit/app/alpha/config/cache/kApcConf.php';
    $cache = new kApcConf();
    $mapName = 'php83-web-' . $nonce;
    $version = 'version-1-' . $nonce;
    $newVersion = 'version-2-' . $nonce;
    $map = array('nonce' => $nonce, 'revision' => 1, 'nested' => array('enabled' => true, 'number' => 17));
    $newMap = $map;
    $newMap['revision'] = 2;
    $result = array();
    switch ($phase) {
        case 'store':
            $result['storeKey'] = $cache->storeKey($version, 300);
            $result['store'] = $cache->store($version, $mapName, $map, 300);
            break;
        case 'read':
        case 'read-after-mismatch':
        case 'read-new':
            $result['loadKey'] = $cache->loadKey();
            $result['load'] = $cache->load($phase !== 'read-new' ? $version : $newVersion, $mapName);
            break;
        case 'mismatch':
            $result['load'] = $cache->load('wrong-' . $nonce, $mapName);
            break;
        case 'delete':
            $result['delete'] = $cache->delete($mapName);
            break;
        case 'miss':
            $result['load'] = $cache->load($version, $mapName);
            break;
        case 'replace':
            $result['storeKey'] = $cache->storeKey($newVersion, 300);
            $result['store'] = $cache->store($newVersion, $mapName, $newMap, 300);
            break;
    }
    respond(200, array('schema' => 1, 'ok' => true, 'php' => PHP_VERSION, 'sapi' => PHP_SAPI,
        'apcu_enabled' => apcu_enabled(), 'apcu_version' => phpversion('apcu'), 'source_hashes' => $sourceHashes,
        'ini' => php_ini_loaded_file(), 'scanned_ini' => php_ini_scanned_files(), 'pid' => getmypid(),
        'nonce' => $nonce, 'phase' => $phase, 'mode' => $mode, 'result' => $result));
} catch (Throwable $error) {
    respond(500, array('ok' => false, 'error' => get_class($error), 'message' => $error->getMessage(),
        'file' => $error->getFile(), 'line' => $error->getLine()));
}
