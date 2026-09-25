<?php
// Synthetic provider probe: no application source, credentials, DB or outbound calls.
error_reporting(E_ALL);
ini_set('display_errors', '0');
set_error_handler(static function ($severity, $message, $file, $line) {
    throw new ErrorException($message, 0, $severity, $file, $line);
});
$isCli = PHP_SAPI === 'cli';
$expected = $isCli ? 'cli' : trim(file_get_contents(__DIR__ . '/expected-sapi'));
$nonce = trim(file_get_contents(__DIR__ . '/nonce'));
$required = ['bcmath', 'ctype', 'curl', 'dom', 'fileinfo', 'filter', 'gd', 'gmp',
    'iconv', 'intl', 'json', 'ldap', 'libxml', 'mbstring', 'mysqli', 'mysqlnd',
    'openssl', 'pcre', 'PDO', 'pdo_mysql', 'posix', 'session', 'SimpleXML',
    'sockets', 'ssh2', 'tokenizer', 'xml', 'xmlreader', 'xmlwriter', 'xsl', 'zip',
    'zlib', 'apcu', 'memcache', 'Zend OPcache'];
if ($isCli) { $required[] = 'pcntl'; }
$failures = [];
$smoke = [];
$method = $isCli ? 'CLI' : ($_SERVER['REQUEST_METHOD'] ?? '');
try {
    if (PHP_MAJOR_VERSION !== 8 || PHP_MINOR_VERSION !== 3) { $failures[] = 'version'; }
    if (PHP_SAPI !== $expected) { $failures[] = 'sapi'; }
    foreach ($required as $module) {
        if (!extension_loaded($module)) { $failures[] = 'extension:' . $module; }
    }
    if (!$isCli) {
        if (!in_array($method, ['GET', 'POST'], true)) { $failures[] = 'method'; }
        if (($_GET['nonce'] ?? null) !== $nonce) { $failures[] = 'nonce'; }
        if ($method === 'POST' && $_POST !== ['marker' => 'php83-provider-synthetic']) {
            $failures[] = 'post';
        }
        if ($method === 'GET' && $_POST !== []) { $failures[] = 'get-body'; }
    }
    if (!$failures) {
        $smoke['pdo_mysql'] = in_array('mysql', PDO::getAvailableDrivers(), true);
        $smoke['json'] = json_decode(json_encode(['a' => 1]), true) === ['a' => 1];
        $smoke['mbstring'] = mb_strlen('ação', 'UTF-8') === 4;
        $smoke['gmp'] = gmp_strval(gmp_add('40', '2')) === '42';
        $smoke['bcmath'] = bcadd('40', '2', 0) === '42';
        $dom = new DOMDocument();
        $smoke['xml'] = $dom->loadXML('<probe/>') && $dom->documentElement->tagName === 'probe';
        $smoke['gd'] = (bool) gd_info()['PNG Support'];
        $smoke['curl'] = is_array(curl_version());
        $smoke['intl'] = Normalizer::normalize("e\u{0301}") === 'é';
        $smoke['zip'] = class_exists('ZipArchive');
        $smoke['ldap'] = function_exists('ldap_connect');
        $smoke['ssh2'] = function_exists('ssh2_connect');
        $smoke['memcache'] = class_exists('Memcache');
        $smoke['apcu'] = function_exists('apcu_fetch');
        $smoke['opcache'] = function_exists('opcache_get_status');
        foreach ($smoke as $name => $ok) { if (!$ok) { $failures[] = 'smoke:' . $name; } }
    }
} catch (Throwable $error) {
    $failures[] = get_class($error) . ':' . $error->getMessage();
}
$modules = get_loaded_extensions(); sort($modules);
$result = ['schema' => 1, 'ok' => !$failures, 'php' => PHP_VERSION, 'sapi' => PHP_SAPI,
    'expected_sapi' => $expected, 'method' => $method, 'nonce' => $nonce,
    'ini' => php_ini_loaded_file(), 'scanned_ini' => php_ini_scanned_files(),
    'modules' => $modules, 'required' => $required, 'smoke' => $smoke, 'failures' => $failures];
if (!$isCli) { header('Content-Type: application/json'); http_response_code($failures ? 500 : 200); }
echo json_encode($result, JSON_UNESCAPED_SLASHES | JSON_THROW_ON_ERROR), "\n";
if ($isCli && $failures) { exit(1); }
