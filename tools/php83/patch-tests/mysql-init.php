<?php
// Exercise the bundled connection factory with synthetic configuration only.
error_reporting(E_ALL);
ini_set('display_errors', 'stderr');
set_include_path('/audit/app/vendor');
foreach (array('Propel.php', 'PropelException.php', 'util/PropelConfiguration.php',
    'util/PropelPDO.php', 'util/DebugPDOStatement.php', 'util/DebugPDO.php',
    'adapter/DBAdapter.php', 'adapter/DBMySQL.php') as $file) {
    require_once 'propel/' . $file;
}
Propel::setConfiguration(array('debugpdo' => array('logging' => array('enabled' => false))));
Propel::setDB('php83-probe', new DBMySQL());
require_once 'propel/om/BaseObject.php';
require_once 'propel/om/Persistent.php';
require_once '/audit/app/alpha/lib/model/om/Baseentry.php';
// Concrete test subclass; no override of construction or hydration behavior.
class Php83EntryHydrationProbe extends Baseentry {}
$fixtures = array(
    'unspecified' => array(),
    'constructor-native' => array('options' => array('PDO::ATTR_EMULATE_PREPARES' => array('value' => false))),
    'attribute-native' => array('attributes' => array('ATTR_EMULATE_PREPARES' => array('value' => false))),
    'attribute-stringify' => array('attributes' => array('ATTR_STRINGIFY_FETCHES' => array('value' => true))),
);
$results = array();
foreach ($fixtures as $name => $extra) {
    $params = array('dsn' => 'mysql:unix_socket=/audit/db/mysql.sock;charset=utf8mb4',
        'user' => 'vagrant', 'classname' => 'DebugPDO',
        'settings' => array('charset' => array('value' => 'utf8mb4')));
    $db = Propel::initConnection(array_merge($params, $extra), 'php83-probe');
    $emulate = (bool) $db->getAttribute(PDO::ATTR_EMULATE_PREPARES);
    $stringify = null;
    $stringifyReadback = null;
    try {
        $stringify = (bool) $db->getAttribute(PDO::ATTR_STRINGIFY_FETCHES);
    } catch (PDOException $error) {
        if ($error->getCode() !== 'IM001') { throw $error; }
        $stringifyReadback = array('unsupported', $error->getCode());
    }
    if (strpos($name, 'native') !== false && $emulate) {
        throw new RuntimeException('Requested native prepares not applied');
    }
    if ($name === 'attribute-stringify' && $stringify === false) {
        throw new RuntimeException('Requested stringify not applied');
    }
    $row = $db->query("SELECT CAST(42 AS SIGNED) AS n, 1.25E0 AS f, NULL AS nullable, @@character_set_connection AS charset")
        ->fetch(PDO::FETCH_ASSOC);
    if ($row['charset'] !== 'utf8mb4' || $row['nullable'] !== null) {
        throw new RuntimeException('Connection initialization fixture failed');
    }
    if ($name === 'attribute-stringify' && ($row['n'] !== '42' || $row['f'] !== '1.25')) {
        throw new RuntimeException('Requested stringify not reflected in returned values');
    }
    $entryRow = array_fill(0, 53, null);
    $entryRow[0] = '1_synthetic';
    $entryRow[8] = $row['n']; // views: generated hydrate casts to int
    $entryRow[25] = $row['n']; // partner_id: generated hydrate casts to int
    $entry = new Php83EntryHydrationProbe();
    $endColumn = $entry->hydrate($entryRow);
    $hydrated = array('id' => $entry->getId(), 'views' => $entry->getViews(),
        'partner_id' => $entry->getPartnerId(), 'name' => $entry->getName());
    if ($endColumn !== 53 || $hydrated !== array('id' => '1_synthetic', 'views' => 42,
        'partner_id' => 42, 'name' => null) || $entry->isNew() || $entry->isModified()) {
        throw new RuntimeException('Generated entry hydration fixture failed');
    }
    $results[] = array('case' => $name, 'class' => get_class($db), 'emulate' => $emulate,
        'stringify' => $stringify, 'stringify_readback' => $stringifyReadback,
        'error_mode' => $db->getAttribute(PDO::ATTR_ERRMODE),
        'row' => $row, 'hydrated' => $hydrated);
}
echo json_encode(array('php' => PHP_VERSION, 'results' => $results)), "\n";
