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
set_include_path($root . '/vendor/ZendFramework/library' . PATH_SEPARATOR
    . $root . '/vendor' . PATH_SEPARATOR . get_include_path());
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
    case 'legacy_json':
        require_once $root . '/alpha/apps/kaltura/lib/Services_JSON.class.php';
        $json = new Services_JSON();
        echo $json->encode(array('synthetic' => true)), "\n";
        break;
    default:
        fwrite(STDERR, "Unknown probe\n");
        exit(64);
}
