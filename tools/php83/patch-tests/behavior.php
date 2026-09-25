<?php
// Synthetic differential fixtures; no configured application, DB or network.
error_reporting(E_ALL);
ini_set('display_errors', 'stderr');
$root = $argv[1];
$case = $argv[2];
set_include_path($root . '/vendor/ZendFramework/library' . PATH_SEPARATOR . $root . '/vendor');
$out = array();
if ($case === 'environment') {
    echo json_encode(array('php' => PHP_VERSION, 'sapi' => PHP_SAPI,
        'modules' => get_loaded_extensions(), 'ini' => php_ini_loaded_file(),
        'mbstring_loaded' => extension_loaded('mbstring'),
        'iconv_loaded' => extension_loaded('iconv'))), "\n";
    exit(0);
}
if ($case === 'registry') {
    require_once 'Zend/Registry.php';
    foreach (array(0, 1, 2, 3) as $flags) {
        $registry = new Zend_Registry(array('null' => null, 'false' => false,
            'zero' => 0, 'empty' => '', 0 => 'numeric', '01' => 'padded'), $flags);
        foreach (array('null', 'false', 'zero', 'empty', 0, '0', '01', 'missing') as $key) {
            $out[] = array($flags, $key, $registry->offsetExists($key));
        }
        $registry->dynamicProbe = 'dynamic';
        $out[] = array('property', $flags, $registry->offsetExists('dynamicProbe'), $registry->dynamicProbe);
        $registry->offsetUnset('null');
        $out[] = array('unset', $flags, $registry->offsetExists('null'));
        $registry->exchangeArray(array('replacement' => null));
        $out[] = array('exchange', $flags, $registry->offsetExists('replacement'));
        $registry->append('appended');
        $out[] = array('append', $flags, $registry->offsetExists(0));
    }
    Zend_Registry::_unsetInstance();
    $out[] = array('not-initialized', Zend_Registry::isRegistered('none'));
    Zend_Registry::set('nullable', null);
    $out[] = array('static-null', Zend_Registry::isRegistered('nullable'), Zend_Registry::get('nullable'));
    try {
        Zend_Registry::get('missing');
        throw new RuntimeException('Expected missing-key exception');
    } catch (Zend_Exception $error) {
        $out[] = array('missing-exception', get_class($error));
    }
} elseif ($case === 'api-mysql' || $case === 'api-bootstrap' || $case === 'api-dispatch') {
    require __DIR__ . '/api-bootstrap.php';
} elseif ($case === 'symfony-yaml' || $case === 'symfony' || $case === 'symfony-bootstrap') {
    require __DIR__ . '/symfony.php';
} elseif ($case === 'registry-action-stack') {
    require __DIR__ . '/registry-action-stack.php';
} elseif ($case === 'registry-bootstrap') {
    require __DIR__ . '/registry-bootstrap.php';
} elseif ($case === 'registry-storage') {
    require __DIR__ . '/registry-storage.php';
} elseif ($case === 'analytics-partner') {
    require __DIR__ . '/analytics-partner.php';
} elseif ($case === 'debug-pdo-logging') {
    require __DIR__ . '/debug-pdo-logging.php';
} elseif ($case === 'debug-pdo-edges') {
    require __DIR__ . '/debug-pdo-edges.php';
} elseif ($case === 'debug-pdo' || $case === 'debug-pdo-stringify') {
    require __DIR__ . '/debug-pdo.php';
} elseif ($case === 'legacy-json' || $case === 'zend-json') {
    if ($case === 'legacy-json') {
        require_once $root . '/alpha/apps/kaltura/lib/Services_JSON.class.php';
        $codec = new Services_JSON(SERVICES_JSON_LOOSE_TYPE);
    } else {
        require_once 'Zend/Json.php';
        Zend_Json::$useBuiltinEncoderDecoder = true;
    }
    $values = array(null, true, false, 0, -42, 1.25, '', 'ASCII / \\ "',
        "line\n\t\r", 'ação € 日本語', array(), array(0, false, null),
        array('nullable' => null, 'nested' => array('x' => array(1, 2)), 'unicode' => 'ação'));
    foreach ($values as $value) {
        $encoded = $case === 'legacy-json' ? $codec->encode($value) : Zend_Json::encode($value);
        $decoded = $case === 'legacy-json' ? $codec->decode($encoded) : Zend_Json::decode($encoded);
        if ($decoded !== $value) {
            throw new RuntimeException('Roundtrip mismatch at fixture ' . count($out));
        }
        $out[] = array('encoded' => $encoded, 'decoded' => $decoded);
    }
} else {
    throw new RuntimeException('Unknown fixture');
}
echo json_encode($out, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES), "\n";
