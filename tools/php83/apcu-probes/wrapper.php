<?php
/** Synthetic fixture only: never load this alias adapter into the application. */
error_reporting(E_ALL);
ini_set('display_errors', '0');
set_error_handler(function ($severity, $message, $file, $line) {
    // Deliberately do not consult error_reporting(): even source @ diagnostics fail.
    throw new ErrorException($message, 0, $severity, $file, $line);
});

function installFixtureAliases()
{
    function apc_fetch($key, &$success = null) { return apcu_fetch($key, $success); }
    function apc_store($key, $value = null, $ttl = 0) { return apcu_store($key, $value, $ttl); }
    function apc_add($key, $value = null, $ttl = 0) { return apcu_add($key, $value, $ttl); }
    function apc_delete($key) { return apcu_delete($key); }
    function apc_inc($key, $step = 1, &$success = null) { return apcu_inc($key, $step, $success); }
    function apc_dec($key, $step = 1, &$success = null) { return apcu_dec($key, $step, $success); }
}

function recordEqual(&$report, $name, $actual, $expected)
{
    $ok = $actual === $expected;
    $report['assertions'][] = array('name' => $name, 'ok' => $ok, 'actual' => $actual, 'expected' => $expected);
    if (!$ok) { $report['ok'] = false; }
}

$report = array(
    'schema' => 1, 'scope' => 'original-wrapper-with-optional-fixture-only-aliases',
    'ok' => true, 'application_acceptance' => false, 'adapter_is_production_solution' => false,
    'runtime' => array('php' => PHP_VERSION, 'sapi' => PHP_SAPI,
        'apcu_version' => phpversion('apcu'), 'ini' => php_ini_loaded_file(),
        'apc.enable_cli' => ini_get('apc.enable_cli'),
        'apc.use_request_time' => ini_get('apc.use_request_time')),
    'counter_contract' => 'missing counters must not create, derived from serialized base behavior; not a measured legacy native APC contract',
    'assertions' => array(), 'diagnostics' => array(), 'source' => array()
);
$keys = array();
try {
    if ($argc !== 3 || !in_array($argv[2], array('control', 'adapter'), true)) {
        throw new RuntimeException('Usage: wrapper.php SOURCE_ROOT control|adapter');
    }
    $adapter = $argv[2] === 'adapter';
    $report['mode'] = $adapter ? 'fixture-alias-experiment' : 'original-control';
    $report['accepted_php_families'] = array('7.4', '8.3');
    if (!in_array(PHP_MAJOR_VERSION . '.' . PHP_MINOR_VERSION, array('7.4', '8.3'), true) || PHP_SAPI !== 'cli') {
        throw new RuntimeException('Requires PHP 7.4 or 8.3 and CLI SAPI');
    }
    $surface = array();
    foreach (array('fetch', 'store', 'add', 'delete', 'inc', 'dec') as $operation) {
        $surface['apc_' . $operation] = function_exists('apc_' . $operation);
        $surface['apcu_' . $operation] = function_exists('apcu_' . $operation);
    }
    $report['runtime']['surface_before'] = $surface;
    $enabled = function_exists('apcu_enabled') && apcu_enabled();
    $report['runtime']['apcu_enabled'] = $enabled;
    if (!$enabled) { throw new RuntimeException('Requires enabled real APCu; use -d apc.enable_cli=1'); }
    foreach ($surface as $function => $exists) {
        if (strpos($function, 'apc_') === 0 && $exists) { throw new RuntimeException('Control requires no pre-existing legacy APC functions'); }
        if (strpos($function, 'apcu_') === 0 && !$exists) { throw new RuntimeException('Incomplete APCu function surface'); }
    }
    // Older APCu can use request-start time, which makes in-process TTL sleep misleading.
    $requestTime = ini_get('apc.use_request_time');
    if ($adapter && $requestTime !== false && !in_array(strtolower((string) $requestTime), array('', '0', 'off'), true)) {
        throw new RuntimeException('TTL fixture requires -d apc.use_request_time=0');
    }
    $root = realpath($argv[1]);
    if ($root === false) { throw new RuntimeException('Missing source root'); }
    foreach (array('kInfraBaseCacheWrapper.php', 'kApcCacheWrapper.php') as $file) {
        $path = $root . '/infra/cache/' . $file;
        if (!is_file($path)) { throw new RuntimeException('Missing original source: ' . $file); }
        $report['source'][$file] = hash_file('sha256', $path);
        require_once $path;
    }
    $control = new kApcCacheWrapper();
    recordEqual($report, 'original_apcu_only_init_false', $control->init(array()), false);
    if ($adapter) {
        installFixtureAliases();
        $prefix = 'php83-wrapper-fixture-' . bin2hex(random_bytes(16)) . '-';
        $report['key_prefix'] = $prefix;
        foreach (array(false, true) as $serialize) {
            $label = $serialize ? 'serialized' : 'native';
            $cache = new kApcCacheWrapper();
            recordEqual($report, $label . '.init', $cache->init(array('serializeData' => $serialize)), true);
            $named = array();
            foreach (array('value', 'object', 'false', 'missing', 'counter', 'inc-missing', 'dec-missing', 'ttl') as $name) {
                $named[$name] = $prefix . $label . '-' . $name;
                $keys[] = $named[$name];
            }
            $value = array('nested' => array('text' => 'Kaltura', 'zero' => 0), 'bool' => false);
            recordEqual($report, $label . '.set', $cache->set($named['value'], $value), true);
            recordEqual($report, $label . '.get', $cache->get($named['value']), $value);
            $object = new stdClass();
            $object->label = 'synthetic-cache-object';
            $object->nested = array('items' => array(0, false, 'Kaltura'), 'empty' => array());
            recordEqual($report, $label . '.object_set', $cache->set($named['object'], $object), true);
            $objectResult = $cache->get($named['object']);
            recordEqual($report, $label . '.object_class', is_object($objectResult) ? get_class($objectResult) : gettype($objectResult), 'stdClass');
            recordEqual($report, $label . '.object_properties', is_object($objectResult) ? get_object_vars($objectResult) : null, get_object_vars($object));
            recordEqual($report, $label . '.object_delete', $cache->delete($named['object']), true);
            recordEqual($report, $label . '.object_deleted_missing', $cache->get($named['object']), false);
            recordEqual($report, $label . '.add_no_overwrite', $cache->add($named['value'], 'overwrite'), false);
            recordEqual($report, $label . '.unchanged', $cache->get($named['value']), $value);
            recordEqual($report, $label . '.store_false', $cache->set($named['false'], false), true);
            recordEqual($report, $label . '.get_false', $cache->get($named['false']), false);
            recordEqual($report, $label . '.get_miss_also_false', $cache->get($named['missing']), false);
            $success = null;
            $rawFalse = apc_fetch($named['false'], $success);
            recordEqual($report, $label . '.fetch_false_success_byref', $success, true);
            recordEqual($report, $label . '.raw_false_encoding', $rawFalse, $serialize ? serialize(false) : false);
            $success = null;
            recordEqual($report, $label . '.raw_miss', apc_fetch($named['missing'], $success), false);
            recordEqual($report, $label . '.fetch_miss_success_byref', $success, false);
            $multi = $cache->multiGet(array($named['value'], $named['false'], $named['missing']));
            recordEqual($report, $label . '.multiget_false_retained_miss_omitted', $multi,
                array($named['value'] => $value, $named['false'] => false));
            recordEqual($report, $label . '.add_new', $cache->add($named['counter'], 10), true);
            recordEqual($report, $label . '.increment', $cache->increment($named['counter'], 3), 13);
            recordEqual($report, $label . '.decrement', $cache->decrement($named['counter'], 4), 9);
            recordEqual($report, $label . '.increment_missing', $cache->increment($named['inc-missing']), false);
            recordEqual($report, $label . '.decrement_missing', $cache->decrement($named['dec-missing']), false);
            recordEqual($report, $label . '.increment_did_not_create', apcu_exists($named['inc-missing']), false);
            recordEqual($report, $label . '.decrement_did_not_create', apcu_exists($named['dec-missing']), false);
            recordEqual($report, $label . '.ttl_set', $cache->set($named['ttl'], 'expires', 1), true);
            recordEqual($report, $label . '.ttl_immediate', $cache->get($named['ttl']), 'expires');
            sleep(3);
            recordEqual($report, $label . '.ttl_expired', $cache->get($named['ttl']), false);
            recordEqual($report, $label . '.delete', $cache->delete($named['value']), true);
            recordEqual($report, $label . '.deleted_missing', $cache->get($named['value']), false);
            recordEqual($report, $label . '.delete_missing', $cache->delete($named['value']), false);
        }
    }
} catch (Throwable $error) {
    $report['ok'] = false;
    $report['diagnostics'][] = array('class' => get_class($error), 'message' => $error->getMessage(),
        'file' => $error->getFile(), 'line' => $error->getLine());
} finally {
    try {
        // Delete only this fixture's random names, never clear a shared APCu cache.
        foreach ($keys as $key) { apcu_delete($key); }
    } catch (Throwable $error) {
        $report['ok'] = false;
        $report['diagnostics'][] = array('cleanup_error' => $error->getMessage());
    }
}
echo json_encode($report, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES | JSON_THROW_ON_ERROR), "\n";
exit($report['ok'] ? 0 : 1);
