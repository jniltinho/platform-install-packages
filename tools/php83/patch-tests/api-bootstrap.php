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
if ($root !== '/audit/app' || !function_exists('posix_geteuid') || posix_geteuid() !== 65534) {
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
file_put_contents($root . '/configurations/local.ini', "date_default_timezone = UTC\nquery_cache_enabled = false\nenable_cache = false\n");
file_put_contents($root . '/configurations/logger.ini', "[api_v3]\nwriters.stream.name = Zend_Log_Writer_Stream\nwriters.stream.stream = php://stderr\nwriters.stream.formatters.simple.name = Zend_Log_Formatter_Simple\nwriters.stream.formatters.simple.format = %message%\n");
require_once $root . '/api_v3/bootstrap.php';
$out[] = array('api-bootstrap-returned', true);
foreach (array('KalturaFrontController', 'KalturaDispatcher', 'SystemService') as $class) {
    if (!class_exists($class)) { throw new RuntimeException('Missing API class: ' . $class); }
    $out[] = array('class', $class);
}

// Anonymous dispatch experiment: real reflection/permission pipeline, no mocks.
if ($case === 'api-dispatch') {
    $result = KalturaDispatcher::getInstance()->dispatch('system', 'getTime', array());
    if (!is_int($result) || abs(time() - $result) > 5) {
        throw new RuntimeException('Unexpected system.getTime result');
    }
    $out[] = array('system-getTime', 'integer-in-current-window');
}
