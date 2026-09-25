<?php
// Real Kaltura bootstrap and dependencies, isolated synthetic DB only.
error_reporting(E_ALL);
ini_set('display_errors', 'stderr');
$variant = $argv[1] ?? '';
if (!in_array($variant, array('exp8', 'exp9'), true) || (PHP_VERSION_ID < 80300 || PHP_VERSION_ID >= 80400)) {
    throw new RuntimeException('Unsupported variant/runtime');
}
$root = '/audit/app'; $case = 'api-http'; $out = array();
set_include_path($root . '/vendor/ZendFramework/library' . PATH_SEPARATOR . $root . '/vendor');
require '/audit/tests/api-bootstrap.php';
function check($actual, $expected, $label) {
    if ($actual !== $expected) { throw new RuntimeException('Contract failed: ' . $label); }
    return array($label, $actual);
}
$rows = array();
$corrected = $variant === 'exp9';
$rows[] = check(get_class($connection), 'KalturaPDO', 'connection');
$native = new PDO('mysql:unix_socket=/audit/db/mysql.sock;dbname=php83_api_probe', 'vagrant');
$native->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
$native->exec('CREATE TABLE bool_probe (id INT PRIMARY KEY, value INT)');
$rows[] = check($native->prepare('SELECT 1')->execute(), true, 'native-success');
$rows[] = check($connection->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_SILENT), $corrected ? true : null, 'set-supported');
$rows[] = check($connection->setAttribute(987654, false), $corrected ? false : null, 'set-unsupported');
foreach (array(true, false) as $enabled) {
    $suffix = $enabled ? 'on' : 'off';
    $rows[] = check($connection->setAttribute(PropelPDO::PROPEL_ATTR_CACHE_PREPARES, $enabled), $corrected ? true : null, 'cache-set-' . $suffix);
    $a = $connection->prepare('SELECT 7'); $b = $connection->prepare('SELECT 7');
    $rows[] = check($a === $b, $enabled, 'cache-identity-' . $suffix);
}
$statement = $connection->prepare('INSERT INTO bool_probe VALUES (1, :p1)');
$rows[] = check(get_class($statement), 'KalturaStatement', 'statement');
$rows[] = check(strpos($statement->queryString, '/* ') === 0, true, 'comment-prefix');
$rows[] = check($statement->bindValue(':p1', 17, PDO::PARAM_INT), true, 'bind-int');
$rows[] = check($statement->execute(), $corrected ? true : null, 'execute-bound');
$rows[] = check((int) $native->query('SELECT value FROM bool_probe WHERE id=1')->fetchColumn(), 17, 'bound-data');
$statement = $connection->prepare('INSERT INTO bool_probe VALUES (2, :p1)');
$rows[] = check($statement->execute(array(23)), $corrected ? true : null, 'execute-array');
$rows[] = check((int) $native->query('SELECT value FROM bool_probe WHERE id=2')->fetchColumn(), 23, 'array-data');
// Default MySQL emulation is made explicit so failure occurs during execute.
$connection->setAttribute(PDO::ATTR_EMULATE_PREPARES, true);
foreach (array(PDO::ERRMODE_SILENT, PDO::ERRMODE_EXCEPTION) as $mode) {
    $native->setAttribute(PDO::ATTR_ERRMODE, $mode);
    $nativeStatement = $native->prepare('SELECT * FROM absent_bool_probe');
    try { $nativeResult = $nativeStatement->execute(); }
    catch (PDOException $error) { $nativeResult = array(get_class($error), $error->getCode()); }
    $rows[] = check($nativeResult, $mode === PDO::ERRMODE_EXCEPTION ? array('PDOException', '42S02') : false, $mode === PDO::ERRMODE_EXCEPTION ? 'native-exception' : 'native-false');
    $connection->setAttribute(PDO::ATTR_ERRMODE, $mode);
    $statement = $connection->prepare('SELECT * FROM absent_bool_probe');
    $observed = null;
    try { $observed = $statement->execute(); }
    catch (PDOException $error) { $observed = array(get_class($error), $error->getCode()); }
    $expected = $mode === PDO::ERRMODE_EXCEPTION ? array('PDOException', '42S02') : ($corrected ? false : null);
    $rows[] = check($observed, $expected, $mode === PDO::ERRMODE_EXCEPTION ? 'execute-exception' : 'execute-false');
}
KalturaStatement::setDryRun(true);
try {
    $statement = $connection->prepare('INSERT INTO bool_probe VALUES (9, 99)');
    $rows[] = check($statement->execute(), $corrected ? true : null, 'dryrun-insert');
    $rows[] = check((int) $native->query('SELECT COUNT(*) FROM bool_probe WHERE id=9')->fetchColumn(), 0, 'dryrun-no-write');
    $statement = $connection->prepare('SELECT 19');
    $rows[] = check($statement->execute(), $corrected ? true : null, 'dryrun-select');
    $rows[] = check((int) $statement->fetchColumn(), 19, 'dryrun-select-data');
} finally { KalturaStatement::setDryRun(false); }
$sources = array();
foreach (array('KalturaPDO', 'PropelPDO', 'KalturaStatement', 'KalturaLog', 'KalturaMonitorClient', 'kApiCache', 'kQueryCache') as $class) {
    $path = (new ReflectionClass($class))->getFileName();
    if (strpos($path, $root . '/') !== 0) { throw new RuntimeException('Non-artifact dependency'); }
    $sources[$class] = array('path' => substr($path, strlen($root) + 1), 'sha256' => hash_file('sha256', $path));
}
echo json_encode(array('variant' => $variant, 'php' => PHP_VERSION, 'rows' => $rows, 'sources' => $sources)), "\n";
