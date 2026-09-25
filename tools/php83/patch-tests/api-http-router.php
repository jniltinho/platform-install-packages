<?php
// Lab front-controller adapter, NOT the production web/index.php entrypoint.
if ($_SERVER['REMOTE_ADDR'] !== '127.0.0.1' || parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH) !== '/probe') {
    http_response_code(404);
    exit;
}
// cli-server does not define CLI stream constants used by the existing fixture.
if (!defined('STDERR')) { define('STDERR', fopen('php://stderr', 'w')); }
error_reporting(E_ALL);
ini_set('display_errors', '0');
ini_set('log_errors', '1');
ini_set('error_log', '/dev/stderr');
$actualServer = $_SERVER;
$root = '/audit/app';
$case = 'api-http';
$out = array();
set_include_path($root . '/vendor/ZendFramework/library' . PATH_SEPARATOR . $root . '/vendor');
ob_start();
require __DIR__ . '/api-bootstrap.php';
ob_end_clean();
$_SERVER = $actualServer;
if (error_reporting() !== E_ALL || ini_get('display_errors') !== '0' || ini_get('log_errors') !== '1' ||
    extension_loaded('apcu') || extension_loaded('apc')) {
    throw new RuntimeException('HTTP diagnostic/cache configuration changed');
}
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
echo KalturaFrontController::getInstance()->run();
