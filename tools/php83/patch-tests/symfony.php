<?php
// Public-source Symfony preflight. No live configuration, network or database.
if ($case === 'symfony-yaml') {
    require_once $root . '/vendor/symfony/util/Spyc.class.php';
    foreach (array("name: fixture\ncount: 42\n", "list:\n  - one\n  - two\n", "outer:\n  enabled: true\n  empty: null\n", "# comment\n---\ntext: ação\n") as $yaml) {
        $out[] = Spyc::YAMLLoad($yaml);
    }
    // Expose only this protected merge for exact numeric-key/NULL behavior.
    class SyntheticSpycMerge extends Spyc {
        public function merge($a, $b) { return $this->_array_kmerge($a, $b); }
    }
    $merge = new SyntheticSpycMerge();
    foreach (array(array(array(), array()), array(array(2 => 'a'), array(2 => 'b')),
        array(array(2 => null), array(2 => false)), array(array('x' => 1), array('x' => 2)),
        array(null, array('a', 'b'))) as $pair) {
        $out[] = $merge->merge($pair[0], $pair[1]);
    }
    if ($out[0] !== array('name' => 'fixture', 'count' => 42) ||
        $out[5] !== array(2 => 'a', 3 => 'b')) {
        throw new RuntimeException('YAML/merge fixture failed');
    }
    return;
}
require_once $root . '/vendor/symfony/util/sfCore.class.php';
if ($case === 'symfony-bootstrap') {
    register_shutdown_function(function () {
        $last = error_get_last();
        if ($last && in_array($last['type'], array(E_ERROR, E_PARSE, E_CORE_ERROR, E_COMPILE_ERROR), true)) {
            fwrite(STDERR, 'BOOTSTRAP_FATAL ' . json_encode($last) . "\n");
        }
    });
    require_once $root . '/alpha/config/kConf.php';
    define('SF_ROOT_DIR', $root . '/alpha');
    define('SF_APP', 'kaltura');
    define('SF_ENVIRONMENT', 'prod');
    define('SF_DEBUG', false);
    sfCore::bootstrap($root . '/vendor/symfony', $root . '/vendor/symfony-data');
    $out[] = array('bootstrap-returned', true);
    return;
}
require_once $root . '/vendor/symfony/config/sfConfig.class.php';
require_once $root . '/vendor/symfony/controller/sfRouting.class.php';
require_once $root . '/vendor/symfony/helper/UrlHelper.php';
require_once $root . '/vendor/symfony/util/sfToolkit.class.php';
require_once $root . '/vendor/symfony/config/sfConfigHandler.class.php';
sfConfig::set('fixture_text', 'path with spaces');
sfConfig::set('fixture_zero', 0);
$constants = array('%FIXTURE_TEXT%/%unknown%', array('%fixture_zero%', false, null, 42));
$replaced = sfConfigHandler::replaceConstants($constants);
if ($replaced !== array('path with spaces/%unknown%', array('0', false, null, 42))) {
    throw new RuntimeException('Recursive constants changed');
}
$out[] = array('constants', $replaced);
sfConfig::set('sf_logging_enabled', false);
sfConfig::set('sf_suffix', '');
$routing = sfRouting::getInstance();
foreach (array('' , '/', '/media/', '/media/:id', '/media/:id.xml', '/media/*') as $i => $route) {
    $routing->connect('fixture' . $i, $route, array('module' => 'media', 'action' => 'list'));
}
$routes = $routing->getRoutes();
if ($routes['fixture2'][6] !== '/' || $routes['fixture4'][6] !== '.xml') {
    throw new RuntimeException('Route suffix mismatch');
}
$out[] = array('routes', $routes);
foreach (array('fixture2' => array(), 'fixture3' => array('id' => '42'), 'fixture4' => array('id' => '42')) as $name => $params) {
    $url = $routing->generate($name, $params);
    $parsed = $routing->parse($url);
    if (!is_array($parsed) || $parsed['module'] !== 'media' || $parsed['action'] !== 'list') {
        throw new RuntimeException('Route roundtrip failed');
    }
    $out[] = array('roundtrip', $name, $url, $parsed);
}
foreach (array('', 'test@example.invalid', 'ASCII <>&', 'ação 日本語', "a\x00\xff") as $text) {
    mt_srand(12345);
    $encoded = _encodeText($text);
    $decoded = preg_replace_callback('/&#(?:x([0-9a-f]+)|([0-9]+));/i', function ($m) {
        return chr($m[1] !== '' ? hexdec($m[1]) : (int) $m[2]);
    }, $encoded);
    if ($decoded !== $text || strpos($encoded, '@') !== false) {
        throw new RuntimeException('Byte encoding mismatch');
    }
    $out[] = array('encoding', bin2hex($text), bin2hex($encoded));
}
sfCore::initAutoload();
if (ini_get('unserialize_callback_func') !== 'spl_autoload_call' ||
    !in_array(array('sfCore', 'splAutoload'), spl_autoload_functions(), true)) {
    throw new RuntimeException('SPL registration failed');
}
$out[] = array('autoload', sfCore::getAutoloadCallables());
spl_autoload_unregister(array('sfCore', 'splAutoload'));
// Actual directory discovery + SPL class loading, only private temporary files.
$dir = sys_get_temp_dir() . '/symfony-fixture';
if (!mkdir($dir)) { throw new RuntimeException('Cannot create fixture directory'); }
file_put_contents($dir . '/SyntheticAutoloadProbe.php', "<?php\nclass SyntheticAutoloadProbe { public function value() { return 42; } }\n");
sfCore::initSimpleAutoload(array($dir));
$object = new SyntheticAutoloadProbe();
if ($object->value() !== 42 || !sfCore::splSimpleAutoload('SyntheticAutoloadProbe') ||
    sfCore::splSimpleAutoload('MissingSyntheticClass') !== false) {
    throw new RuntimeException('Simple autoload behavior mismatch');
}
$out[] = array('simple-autoload', $object->value(), sfCore::splSimpleAutoload('MissingSyntheticClass'));
unlink($dir . '/SyntheticAutoloadProbe.php');
rmdir($dir);
