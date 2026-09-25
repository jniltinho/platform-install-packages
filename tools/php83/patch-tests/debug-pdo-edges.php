<?php
// Diagnostic comparison against native PDO, not a cross-version acceptance gate.
require_once 'propel/Propel.php';
require_once 'propel/util/PropelConfiguration.php';
require_once 'propel/util/PropelPDO.php';
require_once 'propel/util/DebugPDOStatement.php';
require_once 'propel/util/DebugPDO.php';
Propel::setConfiguration(array('debugpdo' => array('logging' => array('enabled' => false))));
$out[] = array('runtime', PHP_VERSION, phpversion('pdo_sqlite'), PDO::getAvailableDrivers());
$calls = array(
    'positional-column' => function ($db) { return $db->query("SELECT 'alpha' AS name", PDO::FETCH_COLUMN, 0)->fetchAll(); },
    'null-mode' => function ($db) { return $db->query("SELECT 'alpha' AS name", null)->fetchAll(); },
    'no-args' => function ($db) { return $db->query(); },
    'null-query' => function ($db) { return $db->query(null); }
);
if (PHP_VERSION_ID >= 80000) {
    // Keep the fixture parseable on 7.4. These are fixed test strings, not input.
    $calls['named-num'] = eval('return function ($db) { return $db->query(query: "SELECT \'alpha\' AS name", fetchMode: PDO::FETCH_NUM)->fetchAll(); };');
    $calls['unknown-name'] = eval('return function ($db) { return $db->query(query: "SELECT \'alpha\' AS name", unknown: 123)->fetchAll(); };');
}
foreach (array(PDO::ERRMODE_EXCEPTION, PDO::ERRMODE_SILENT) as $mode) {
    foreach ($calls as $name => $call) {
        $values = array();
        foreach (array('PDO', 'DebugPDO') as $class) {
            $db = new $class('sqlite::memory:');
            $db->setAttribute(PDO::ATTR_ERRMODE, $mode);
            $db->setAttribute(PDO::ATTR_DEFAULT_FETCH_MODE, PDO::FETCH_ASSOC);
            try {
                $value = $call($db);
                $values[$class] = array('return', $value);
            } catch (Throwable $error) {
                $values[$class] = array('throw', get_class($error));
            }
            if ($class === 'DebugPDO') {
                $accounting = array($db->getQueryCount(), $db->getLastExecutedQuery());
            }
        }
        $out[] = array($mode, $name, $values, 'matches_native' => $values['PDO'] === $values['DebugPDO'],
            'debug_accounting' => $accounting);
    }
}
