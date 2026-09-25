<?php
// Lab config/DB adapter that enters the unmodified real web/index.php.
if ($_SERVER['REMOTE_ADDR'] !== '127.0.0.1' || parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH) !== '/probe') {
    http_response_code(404);
    exit;
}
error_reporting(E_ALL);
ini_set('display_errors', '0');
ini_set('log_errors', '1');
$root = '/audit/app';
if (posix_geteuid() !== 1000) { throw new RuntimeException('Expected isolated runner UID'); }
$mounts = file('/proc/self/mountinfo');
foreach (array('/audit/app/configurations', '/audit/app/cache') as $requiredMount) {
    $valid = false;
    foreach ($mounts as $mount) {
        $parts = explode(' - ', trim($mount), 2);
        $fields = explode(' ', $parts[0]);
        if (isset($fields[4]) && $fields[4] === $requiredMount) {
            $valid = isset($parts[1]) && strpos($parts[1], 'tmpfs ') === 0 && strpos($parts[0], ' shared:') === false;
        }
    }
    if (!$valid) { throw new RuntimeException('Missing private tmpfs'); }
}
ini_set('error_log', '/audit/app/cache/probe-diagnostics.log');
if (getenv('PHP83_EXPECTED_INI') &&
    (php_ini_loaded_file() !== getenv('PHP83_EXPECTED_INI') || php_ini_scanned_files())) {
    throw new RuntimeException('Unexpected Apache INI');
}
error_log('PROBE_RUNTIME ' . json_encode(array('php' => PHP_VERSION, 'sapi' => PHP_SAPI,
    'modules' => get_loaded_extensions(), 'ini_is_expected' => !getenv('PHP83_EXPECTED_INI') || php_ini_loaded_file() === getenv('PHP83_EXPECTED_INI'))));
header('X-Probe-Nonce: ' . getenv('PHP83_HTTP_NONCE'));
if (extension_loaded('apcu') || extension_loaded('apc')) { throw new RuntimeException('Unexpected cache extension'); }
file_put_contents($root . '/configurations/local.ini', "date_default_timezone = UTC\nquery_cache_enabled = false\nenable_cache = false\nmax_num_instances_in_pool = 100\n[api_strict_error_map]\n");
file_put_contents($root . '/configurations/logger.ini', "[api_v3]\nwriters.stream.name = Zend_Log_Writer_Stream\nwriters.stream.stream = /audit/app/cache/probe-diagnostics.log\nwriters.stream.formatters.simple.name = Zend_Log_Formatter_Simple\nwriters.stream.formatters.simple.format = %message%\n");
file_put_contents($root . '/configurations/db.ini', "[datasources]\ndefault = propel\npropel.adapter = mysql\npropel.connection.classname = KalturaPDO\npropel.connection.user = vagrant\npropel.connection.dsn = \"mysql:unix_socket=/audit/db/mysql.sock;dbname=php83_api_probe\"\n");
$connection = new PDO('mysql:unix_socket=/audit/db/mysql.sock', 'vagrant');
$connection->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
$expected = getenv('PHP83_PROBE_DATADIR');
if (!preg_match('~^/tmp/kaltura-pdo-mysql\.[a-zA-Z0-9]+/data/$~', $expected) ||
    $connection->query('SELECT @@datadir')->fetchColumn() !== $expected) {
    throw new RuntimeException('Refusing non-probe database server');
}
$connection->exec('DROP DATABASE IF EXISTS php83_api_probe');
$connection->exec('CREATE DATABASE php83_api_probe');
$connection->exec('USE php83_api_probe');
$connection->exec(file_get_contents(__DIR__ . '/api-permission-schema.sql'));
header('X-Probe-PHP: ' . PHP_VERSION);
header('X-Probe-SAPI: ' . PHP_SAPI);
file_put_contents($root . '/configurations/cache.ini', "[mapping]\npartnerSecrets = disabledProbe\nqueryCacheKeys = \"\"\n");
$connection->exec(file_get_contents(__DIR__ . '/api-session-schema.sql'));
$connection->exec("INSERT INTO partner (id,partner_name,status,secret,admin_secret) VALUES (83001,'Synthetic HTTP partner',1,'synthetic-user-only','synthetic-admin-only')");
$connection->exec("INSERT INTO permission (id,type,name,partner_id,status) VALUES (2,1,'SYNTHETIC_SESSION_READ',0,1),(3,1,'SYNTHETIC_SESSION_START',0,1)");
$connection->exec("INSERT INTO permission_item (id,type,partner_id,param_1,param_2,param_3,param_4,param_5) VALUES (2,'kApiActionPermissionItem',0,'session','get','','',''),(3,'kApiActionPermissionItem',0,'session','start','','','')");
$connection->exec("INSERT INTO permission_to_permission_item (id,permission_id,permission_item_id) VALUES (2,2,2),(3,3,3)");
$connection->exec("UPDATE user_role SET permission_names='ALWAYS_ALLOWED_ACTIONS,SYNTHETIC_SESSION_START' WHERE id=1");
$connection->exec("INSERT INTO user_role (id,str_id,name,partner_id,status,permission_names) VALUES (2,'BASE_USER_SESSION_ROLE','Synthetic user',0,1,'SYNTHETIC_SESSION_READ'),(3,'PARTNER_ADMIN_ROLE','Synthetic admin',0,1,'SYNTHETIC_SESSION_READ')");
if ((int)$connection->query('SELECT COUNT(*) FROM user_role')->fetchColumn() !== 3 ||
    (int)$connection->query('SELECT COUNT(*) FROM permission_item')->fetchColumn() !== 3 ||
    (int)$connection->query('SELECT COUNT(*) FROM invalid_session')->fetchColumn() !== 0) {
    throw new RuntimeException('Unexpected HTTP fixture schema or seed');
}
// No Kaltura class or bootstrap is loaded before the real entrypoint.
unset($root, $connection, $mounts, $expected, $requiredMount, $mount, $parts, $fields, $valid);
require '/audit/app/api_v3/web/index.php';
