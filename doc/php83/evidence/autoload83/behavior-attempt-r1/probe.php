<?php
// Full source entrypoints, never extracted functions or replacement framework loaders.
error_reporting(E_ALL);
$case = $argv[1];
$root = '/audit/source';
$fixtures = '/audit/fixtures';
$report = array('case'=>$case, 'php'=>PHP_VERSION, 'rows'=>array(), 'diagnostics'=>array(), 'loaded'=>array());
$phase = 'setup';
$postExit = null;
function autoloadProbeRow($name, $value) { $GLOBALS['report']['rows'][] = array('case'=>$name, 'value'=>$value); }
function autoloadProbeQueue() {
    $out = array();
    foreach (spl_autoload_functions() ?: array() as $callback) {
        $out[] = is_string($callback) ? $callback : (is_array($callback) ? implode('::', $callback) : 'Closure');
    }
    return $out;
}
function fixtureFirst($class) {
    $GLOBALS['hits'][] = array('first', $class);
    if ($class === 'FixtureFirstHit') require '/audit/fixtures/extra/FixtureFirstHit.php';
}
function fixtureTail($class) { $GLOBALS['hits'][] = array('tail', $class); }
$hits = array();
set_error_handler(function($severity, $message, $file, $line) {
    $GLOBALS['report']['diagnostics'][] = array('phase'=>$GLOBALS['phase'], 'severity'=>$severity,
      'file'=>str_replace('/audit/source/', '', $file), 'line'=>$line, 'message_sha256'=>hash('sha256', $message));
    return false; // Native diagnostics deliberately remain on stderr.
});
function autoloadProbeFinish() {
    foreach (get_included_files() as $file) {
        if (strpos($file, '/audit/source/') === 0 || strpos($file, '/audit/fixtures/') === 0)
            $GLOBALS['report']['loaded'][str_replace('/audit/', '', $file)] = hash_file('sha256', $file);
    }
    ksort($GLOBALS['report']['loaded']);
    echo "\nAUTOLOAD_RESULT ", json_encode($GLOBALS['report'], JSON_UNESCAPED_SLASHES), "\n";
}
register_shutdown_function(function() {
    $last = error_get_last();
    if ($last && in_array($last['type'], array(E_ERROR,E_PARSE,E_CORE_ERROR,E_COMPILE_ERROR), true)) {
        $GLOBALS['report']['fatal'] = array('severity'=>$last['type'], 'file'=>str_replace('/audit/source/', '', $last['file']),
            'line'=>$last['line'], 'message_sha256'=>hash('sha256', $last['message']));
    }
    if (!isset($GLOBALS['report']['fatal']) && is_callable($GLOBALS['postExit'])) {
        try { call_user_func($GLOBALS['postExit']); }
        catch (Throwable $error) {
            $GLOBALS['report']['exception'] = array('class'=>get_class($error), 'message_sha256'=>hash('sha256', $error->getMessage()),
                'file'=>str_replace('/audit/source/', '', $error->getFile()), 'line'=>$error->getLine());
            autoloadProbeFinish();
            exit(255);
        }
    }
    autoloadProbeFinish();
});
if (strpos($case, 'fatal-') === 0) {
    $targets = array('fatal-hp'=>'vendor/htmlpurifier/library/HTMLPurifier.autoload.php',
        'fatal-core'=>'vendor/symfony/util/sfCore.class.php', 'fatal-cli'=>'vendor/symfony-data/bin/symfony.php');
    require $root.'/'.$targets[$case];
    autoloadProbeRow('unexpected-return', true);
} elseif (strpos($case, 'hp') === 0) {
    require $root.'/vendor/htmlpurifier/library/HTMLPurifier/Bootstrap.php';
    if ($case === 'hp-legacy') {
        if (PHP_VERSION_ID >= 80000) throw new RuntimeException('Legacy fixture is only valid under PHP 7.4');
        require $fixtures.'/legacy.php';
    }
    spl_autoload_register('fixtureFirst');
    spl_autoload_register('fixtureTail');
    autoloadProbeRow('queue-before', autoloadProbeQueue());
    $phase = 'load';
    require $root.'/vendor/htmlpurifier/library/HTMLPurifier.autoload.php';
    autoloadProbeRow('queue-after', autoloadProbeQueue());
    $phase = 'hit';
    autoloadProbeRow('actual-class-hit', class_exists('HTMLPurifier_EntityLookup'));
    autoloadProbeRow('actual-class-file', str_replace($root.'/', '', (new ReflectionClass('HTMLPurifier_EntityLookup'))->getFileName()));
    autoloadProbeRow('first-hit', class_exists('FixtureFirstHit'));
    autoloadProbeRow('prefix-miss', class_exists('HTMLPurifier_ProbeMissing'));
    autoloadProbeRow('unrelated-miss', class_exists('ProbeMissing'));
    if ($case === 'hp-legacy') autoloadProbeRow('legacy-hit', class_exists('FixtureLegacyHit'));
    autoloadProbeRow('hits', $hits);
} elseif ($case === 'core-simple' || $case === 'core-full') {
    require $root.'/vendor/symfony/config/sfConfig.class.php';
    require $root.'/vendor/symfony/util/sfContext.class.php';
    $phase = 'load';
    require $root.'/vendor/symfony/util/sfCore.class.php';
    spl_autoload_register('fixtureFirst');
    if ($case === 'core-full') sfCore::initAutoload();
    sfCore::initSimpleAutoload(array($fixtures.'/map'));
    spl_autoload_register('fixtureTail');
    autoloadProbeRow('queue', autoloadProbeQueue());
    autoloadProbeRow('callback', ini_get('unserialize_callback_func'));
    autoloadProbeRow('registered-core-callables', sfCore::getAutoloadCallables());
    $phase = 'hit';
    autoloadProbeRow('first-hit', class_exists('FixtureFirstHit'));
    autoloadProbeRow('mapped-hit', class_exists('FixtureMapped'));
    autoloadProbeRow('mapped-file', (new ReflectionClass('FixtureMapped'))->getFileName());
    autoloadProbeRow('mapped-value', (new FixtureMapped())->value());
    autoloadProbeRow('miss', class_exists('FixtureMissing'));
    $object = unserialize('O:18:"FixtureUnserialize":0:{}');
    autoloadProbeRow('unserialize-class', get_class($object));
    autoloadProbeRow('unserialize-file', (new ReflectionClass($object))->getFileName());
    autoloadProbeRow('unserialize-value', $object->value());
    autoloadProbeRow('hits', $hits);
} elseif (strpos($case, 'cli-') === 0) {
    $sf_symfony_lib_dir = $root.'/vendor/symfony';
    $sf_symfony_data_dir = $root.'/vendor/symfony-data';
    chdir($fixtures.'/project');
    if ($case === 'cli-version-queue') { spl_autoload_register('fixtureFirst'); spl_autoload_register('fixtureTail'); }
    autoloadProbeRow('queue-before', autoloadProbeQueue());
    // Capture actual CLI output separately; shutdown fixture tests are explicitly marked.
    if ($case !== 'cli-tasks') $postExit = function() {
        // Post-version observations do not claim task execution coverage.
        $last = error_get_last();
        if ($last && in_array($last['type'], array(E_ERROR,E_PARSE,E_CORE_ERROR,E_COMPILE_ERROR), true)) return;
        autoloadProbeRow('post-exit-fixture-phase', true);
        $GLOBALS['phase'] = 'post-version';
        autoloadProbeRow('queue', autoloadProbeQueue());
        require_once '/audit/source/vendor/symfony/config/sfConfig.class.php';
        sfConfig::set('sf_symfony_lib_dir', '/audit/source/vendor/symfony');
        autoloadProbeRow('map-initially-empty', count(simpleAutoloader::$class_paths) === 0);
        if ($GLOBALS['case'] === 'cli-version-queue') {
            autoloadProbeRow('first-hit', class_exists('FixtureFirstHit'));
            autoloadProbeRow('map-after-first-empty', count(simpleAutoloader::$class_paths) === 0);
        }
        autoloadProbeRow('fallback-hit', class_exists('FixtureFallback'));
        autoloadProbeRow('missing', class_exists('FixtureMissing'));
        autoloadProbeRow('hits', $GLOBALS['hits']);
    };
    $argv = array('symfony', $case === 'cli-tasks' ? '-T' : '-V');
    $argc = count($argv);
    $phase = 'cli';
    require $root.'/vendor/symfony-data/bin/symfony.php';
} else { throw new RuntimeException('Unknown probe case'); }
