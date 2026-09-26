<?php
// Complete real classes, no constructors or successful rank-body execution.
if ($argc !== 3 || !in_array($argv[1], array('74', '83'), true) || !in_array($argv[2], array('original', 'candidate'), true)) exit(64);
if (($argv[1] === '74' && (PHP_VERSION_ID < 70400 || PHP_VERSION_ID >= 70500)) || ($argv[1] === '83' && (PHP_VERSION_ID < 80300 || PHP_VERSION_ID >= 80400))) exit(64);
error_reporting(E_ALL);
$diagnostics = array();
$autoloadRequests = array();
spl_autoload_register(function ($class) use (&$autoloadRequests) { $autoloadRequests[] = $class; });
set_error_handler(function ($severity, $message, $file, $line) use (&$diagnostics) {
    $diagnostics[] = array($severity, $message, $file, $line);
    return false;
});
require '/audit/probe/KalturaBaseService.php';
require '/audit/probe/' . $argv[2] . '.php';
$method = new ReflectionMethod('KalturaEntryService', 'anonymousRankEntry');
$method->setAccessible(true);
$parameters = array();
foreach ($method->getParameters() as $parameter) {
    $row = array('name' => $parameter->getName(), 'position' => $parameter->getPosition(),
        'optional' => $parameter->isOptional(), 'default_available' => $parameter->isDefaultValueAvailable(),
        'allows_null' => $parameter->allowsNull(), 'type' => (string) $parameter->getType(),
        'by_reference' => $parameter->isPassedByReference(), 'variadic' => $parameter->isVariadic());
    try { $row['default'] = array('value', $parameter->getDefaultValue()); }
    catch (ReflectionException $error) { $row['default'] = array('unavailable', get_class($error)); }
    $parameters[] = $row;
}
$object = (new ReflectionClass('KalturaEntryService'))->newInstanceWithoutConstructor();
$cases = array('positional0' => array(), 'positional1' => array('safe-id'), 'positional2' => array('safe-id', null));
if ($argv[1] === '83') {
    $cases['named_missing_middle'] = array('entryId' => 'safe-id', 'rank' => 3);
    $cases['named_missing_leading'] = array('rank' => 3);
}
$rows = array(); $failed = false;
foreach ($cases as $name => $arguments) {
    try { $value = $method->invokeArgs($object, $arguments); $rows[] = array($name, 'unexpected-return', $value); $failed = true; }
    catch (Throwable $error) {
        $rows[] = array($name, get_class($error), $error->getMessage());
        if (!($error instanceof ArgumentCountError)) $failed = true;
    }
}
echo json_encode(array('runtime' => PHP_VERSION, 'variant' => $argv[2], 'required' => $method->getNumberOfRequiredParameters(),
    'parameters' => $parameters, 'calls' => $rows, 'diagnostics' => $diagnostics,
    'autoload_requests' => $autoloadRequests, 'entry_peer_loaded' => class_exists('entryPeer', false), 'kvote_loaded' => class_exists('kvote', false),
    'rank_positive_body_tested' => false, 'application_acceptance' => false), JSON_THROW_ON_ERROR) . "\n";
exit($failed ? 2 : 0);
