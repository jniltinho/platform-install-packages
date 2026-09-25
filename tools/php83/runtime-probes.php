<?php
// Unpatched library probes only: no network, DB connection or application config.
error_reporting(E_ALL);
ini_set('display_errors', 'stderr');
$root = realpath($argv[1] ?? '');
$probe = $argv[2] ?? '';
if (!$root || !is_file($root . '/vendor/propel/Propel.php')) {
    fwrite(STDERR, "Expected extracted public Kaltura app tree\n");
    exit(64);
}
register_shutdown_function(function () use ($root) {
    $files = array();
    foreach (get_included_files() as $file) {
        if (strpos($file, $root . '/') === 0) {
            $files[substr($file, strlen($root) + 1)] = hash_file('sha256', $file);
        }
    }
    ksort($files);
    echo "\nAUDIT_INCLUDED=", json_encode($files), "\n";
});
set_include_path($root . '/vendor/ZendFramework/library' . PATH_SEPARATOR
    . $root . '/vendor');
switch ($probe) {
    case 'zend_application':
        require_once 'Zend/Application.php';
        $app = new Zend_Application('testing', array());
        echo $app->getEnvironment(), "\n";
        break;
    case 'zend_registry':
        require_once 'Zend/Registry.php';
        Zend_Registry::set('synthetic', 'ok');
        echo Zend_Registry::get('synthetic'), "\n";
        break;
    case 'zend_config':
        require_once 'Zend/Config.php';
        $config = new Zend_Config(array('synthetic' => 'ok'));
        echo $config->get('synthetic'), "\n";
        break;
    case 'propel_load':
        require_once $root . '/vendor/propel/Propel.php';
        echo Propel::VERSION, "\n";
        echo class_exists('PropelPDO') ? "PDO subclass loaded\n" : "PDO subclass absent\n";
        break;
    case 'zend_json_default':
    case 'zend_json_fallback_encode':
    case 'zend_json_fallback_decode':
        require_once 'Zend/Json.php';
        Zend_Json::$useBuiltinEncoderDecoder = ($probe !== 'zend_json_default');
        if ($probe === 'zend_json_fallback_decode') {
            echo json_encode(Zend_Json::decode('{"synthetic":true}')), "\n";
        } else {
            echo Zend_Json::encode(array('synthetic' => true)), "\n";
            if ($probe === 'zend_json_default') {
                echo json_encode(Zend_Json::decode('{"synthetic":true}')), "\n";
            }
        }
        break;
    case 'propel_DebugPDO':
    case 'propel_DebugPDOStatement':
    case 'propel_PropelConfigurationIterator':
    case 'propel_Criteria':
    case 'propel_BasePeer':
    case 'propel_BaseObject':
    case 'propel_PropelPager':
        require_once $root . '/vendor/propel/Propel.php';
        $class = substr($probe, strlen('propel_'));
        if (!class_exists($class)) {
            throw new RuntimeException('Expected class absent: ' . $class);
        }
        echo $class, " loaded\n";
        break;
    case 'legacy_json':
        require_once $root . '/alpha/apps/kaltura/lib/Services_JSON.class.php';
        $json = new Services_JSON();
        echo $json->encode(array('synthetic' => true)), "\n";
        break;
    default:
        fwrite(STDERR, "Unknown probe\n");
        exit(64);
}
