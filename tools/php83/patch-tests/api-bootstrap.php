<?php
// Real public-source API bootstrap; no configured service/DB, credentials or HTTP.
register_shutdown_function(function () {
    $last = error_get_last();
    if ($last && in_array($last['type'], array(E_ERROR, E_PARSE, E_CORE_ERROR, E_COMPILE_ERROR), true)) {
        fwrite(STDERR, 'API_BOOTSTRAP_FATAL ' . json_encode($last) . "\n");
    }
});
$_SERVER['REQUEST_METHOD'] = 'GET';
$_SERVER['REMOTE_ADDR'] = '127.0.0.1';
$_SERVER['HTTP_HOST'] = 'synthetic.invalid';
$_SERVER['REQUEST_URI'] = '/api_v3/index.php?service=system&action=ping';
// These files live only in the runner's private tmpfs, never host config.
if ($root !== '/audit/app' || !function_exists('posix_geteuid') || posix_geteuid() !== (in_array($case, array('api-mysql', 'api-http'), true) ? 1000 : 65534)) {
    throw new RuntimeException('API fixture requires the unprivileged audit runner');
}
$mounts = file('/proc/self/mountinfo');
foreach (array('/audit/app/configurations', '/audit/app/cache') as $requiredMount) {
    $found = false;
    foreach ($mounts as $mount) {
        if (strpos($mount, ' ' . $requiredMount . ' ') !== false && strpos($mount, ' - tmpfs ') !== false) {
            $found = true;
        }
    }
    if (!$found) { throw new RuntimeException('Missing private tmpfs: ' . $requiredMount); }
}
file_put_contents($root . '/configurations/local.ini', "date_default_timezone = UTC\nquery_cache_enabled = false\nenable_cache = false\nmax_num_instances_in_pool = 100\n");
file_put_contents($root . '/configurations/logger.ini', "[api_v3]\nwriters.stream.name = Zend_Log_Writer_Stream\nwriters.stream.stream = php://stderr\nwriters.stream.formatters.simple.name = Zend_Log_Formatter_Simple\nwriters.stream.formatters.simple.format = %message%\n");
if ($case === 'api-http') {
    file_put_contents($root . '/configurations/local.ini', "[api_strict_error_map]\n", FILE_APPEND);
}
require_once $root . '/api_v3/bootstrap.php';
$out[] = array('api-bootstrap-returned', true);
foreach (array('KalturaFrontController', 'KalturaDispatcher', 'SystemService') as $class) {
    if (!class_exists($class)) { throw new RuntimeException('Missing API class: ' . $class); }
    $out[] = array('class', $class);
}

// Anonymous dispatch experiment: real reflection/permission pipeline, no mocks.
if ($case === 'api-mysql' || $case === 'api-http') {
    $dsn = 'mysql:unix_socket=/audit/db/mysql.sock;dbname=php83_api_probe';
    $setup = new PDO('mysql:unix_socket=/audit/db/mysql.sock', 'vagrant');
    $setup->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    $expectedDataDir = getenv('PHP83_PROBE_DATADIR');
    if (!preg_match('~^/tmp/kaltura-pdo-mysql\.[a-zA-Z0-9]+/data/$~', $expectedDataDir) ||
        $setup->query('SELECT @@datadir')->fetchColumn() !== $expectedDataDir) {
        throw new RuntimeException('Refusing non-probe database server');
    }
    // This exact database belongs exclusively to the disposable probe server.
    $setup->exec('DROP DATABASE IF EXISTS php83_api_probe');
    $setup->exec('CREATE DATABASE php83_api_probe');
    $setup->exec('USE php83_api_probe');
    $setup->exec(file_get_contents(__DIR__ . '/api-permission-schema.sql'));
    if ((int) $setup->query('SELECT COUNT(*) FROM permission')->fetchColumn() !== 1) {
        throw new RuntimeException('Expected one synthetic permission');
    }
    $setup = null;
    DbManager::setConfig(array('datasources' => array('default' => 'propel',
        'propel' => array('adapter' => 'mysql', 'connection' => array(
            'classname' => 'KalturaPDO', 'dsn' => $dsn, 'user' => 'vagrant')))));
    DbManager::initialize();
    $connection = Propel::getConnection('propel');
    $out[] = array('database', get_class($connection));
    $row = $connection->query("SELECT 'synthetic' AS marker")->fetch(PDO::FETCH_ASSOC);
    if ($row !== array('marker' => 'synthetic')) { throw new RuntimeException('Query result changed'); }
    $out[] = array('query', $row);
    $native = new PDO($dsn, 'vagrant');
    $native->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    class SyntheticQueryClass {
        public $marker;
        public $tag;
        public function __construct($tag) { $this->tag = $tag; }
    }
    $probes = array('class' => array("SELECT 'synthetic' AS marker", PDO::FETCH_CLASS, 'SyntheticQueryClass', array('constructed')),
        'column' => array("SELECT 'synthetic'", PDO::FETCH_COLUMN, 0),
        'assoc' => array("SELECT 'synthetic' AS marker", PDO::FETCH_ASSOC),
        'missing-query' => array());
    if (PHP_VERSION_ID >= 80000) {
        $probes['named-query'] = array('query' => "SELECT 'synthetic' AS marker", 'fetchMode' => PDO::FETCH_ASSOC);
        $probes['unknown-name'] = array('unknown' => 'synthetic');
        $probes['missing-named-query'] = array('fetchMode' => PDO::FETCH_ASSOC);
    }
    foreach ($probes as $label => $arguments) {
        $observed = array();
        foreach (array($native, $connection) as $pdo) {
            try {
                $statement = $pdo->query(...$arguments);
                $observed[] = $statement === false ? array('returned' => false) :
                    array('rows' => json_decode(json_encode($statement->fetchAll()), true));
            } catch (Throwable $error) {
                $observed[] = array('error' => get_class($error));
            }
        }
        if ($observed[0] !== $observed[1] ||
            (in_array($label, array('class', 'column', 'assoc', 'named-query'), true) && !isset($observed[0]['rows']))) {
            throw new RuntimeException('PDO forwarding mismatch: ' . $label);
        }
        // Version-specific named controls are asserted, not added to cross-version stdout.
        fwrite(STDERR, 'PDO_CONTROL ' . json_encode(array('case' => $label, 'native' => $observed[0], 'kaltura' => $observed[1])) . "\n");
        if (in_array($label, array('class', 'column', 'assoc'), true)) {
            $out[] = array('query-control', $label, $observed[1]);
        }
    }
}
if ($case === 'api-dispatch' || $case === 'api-mysql') {
    $result = KalturaDispatcher::getInstance()->dispatch('system', 'getTime', array());
    if (!is_int($result) || abs(time() - $result) > 5) {
        throw new RuntimeException('Unexpected system.getTime result');
    }
    $out[] = array('system-getTime', 'integer-in-current-window');
    if ($case === 'api-mysql') {
        try {
            KalturaDispatcher::getInstance()->dispatch('system', 'getVersion', array());
            throw new RuntimeException('Ungrantable action unexpectedly succeeded');
        } catch (KalturaAPIException $error) {
            if ($error->getCode() !== 'SERVICE_FORBIDDEN') { throw $error; }
            $out[] = array('ungranted-getVersion', $error->getCode());
        }
    }
}
