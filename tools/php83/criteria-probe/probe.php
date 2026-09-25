<?php
// Actual Criteria/Criterion classes; only DB lookup is a fixture boundary.
error_reporting(E_ALL);
$diagnostics = array();
set_error_handler(function ($severity, $message, $file, $line) use (&$diagnostics) {
    $diagnostics[] = array($severity, $message, basename($file), $line);
    return true;
});
class DBAdapter {}
class Propel {
    public static function getDB($name) { return new DBAdapter(); }
}
require $argv[1];
$property = new ReflectionProperty('Criterion', 'realtable');
$property->setAccessible(true);
$cases = array(
    array('missing', 'a.id', false, null, 'a'),
    array('null', 'a.id', true, null, 'a'),
    array('empty', 'a.id', true, '', 'a'),
    array('table', 'a.id', true, 'partner', 'partner'),
    array('zero-string', 'a.id', true, '0', '0'),
    array('unqualified', 'id', false, null, null),
    array('false', 'a.id', true, false, 'a'),
    array('zero-int', 'a.id', true, 0, 0)
);
$rows = array();
foreach ($cases as $case) {
    list($name, $column, $add, $alias, $expected) = $case;
    $criteria = new Criteria('fixture');
    if ($add) $criteria->addAlias('a', $alias);
    $criterion = new Criterion($criteria, $column, 123);
    $actual = $property->getValue($criterion);
    if ($actual !== $expected) throw new RuntimeException('Alias mismatch: '.$name);
    $rows[] = array($name, $actual, $criterion->getColumn(), $criterion->getValue());
}
echo json_encode(array('php'=>PHP_VERSION,'rows'=>$rows,'diagnostics'=>$diagnostics)), "\n";
