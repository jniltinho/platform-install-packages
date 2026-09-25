<?php
// Real PDO/Propel factory + exact analytics functions. Criteria/peer remain
// explicit adapters for synthetic literal SELECTs, not real endpoint routing.
error_reporting(E_ALL);
ini_set('display_errors', 'stderr');
$root = '/audit/app';
set_include_path($root . '/vendor');
foreach (array('Propel.php', 'PropelException.php', 'util/PropelConfiguration.php',
    'util/PropelPDO.php', 'util/DebugPDOStatement.php', 'util/DebugPDO.php',
    'adapter/DBAdapter.php', 'adapter/DBMySQL.php') as $file) {
    require_once 'propel/' . $file;
}
Propel::setConfiguration(array('debugpdo' => array('logging' => array('enabled' => false))));
Propel::setDB('analytics-probe', new DBMySQL());
$analyticsFunctionsOnly = true;
require __DIR__ . '/analytics-partner.php';
$results = array();
foreach (array('unspecified' => array(),
    'native' => array('ATTR_EMULATE_PREPARES' => array('value' => false)),
    'stringify' => array('ATTR_STRINGIFY_FETCHES' => array('value' => true))) as $mode => $attributes) {
    $db = Propel::initConnection(array('dsn' => 'mysql:unix_socket=/audit/db/mysql.sock;charset=utf8mb4',
        'user' => 'vagrant', 'classname' => 'DebugPDO', 'attributes' => $attributes), 'analytics-probe');
    foreach (array('positive' => array('42', '7'), 'zero' => array('0', '0'),
        'nullable' => array('NULL', 'NULL')) as $shape => $values) {
        $customData = $db->quote(serialize(array('crmId' => 'synthetic')));
        $columns = "'SYNTHETIC_NOT_A_SECRET' AS ADMIN_SECRET, $customData AS CUSTOM_DATA, "
            . "CAST($values[0] AS SIGNED) AS PARTNER_PARENT_ID, CAST($values[1] AS SIGNED) AS PARTNER_PACKAGE, "
            . "'2020-01-01 00:00:00' AS UPDATED_AT";
        $sql = 'SELECT 101 AS ID, 1 AS STATUS, ' . $columns
            . ' UNION ALL SELECT 102 AS ID, 99 AS STATUS, ' . $columns;
        $control = $db->query($sql)->fetchAll(PDO::FETCH_ASSOC);
        PartnerPeer::$statementFactory = function () use ($db, $sql) { return $db->query($sql); };
        $result = getPartnerUpdates(0);
        $info = json_decode($result['items'][101], true);
        if ($info['pp'] !== $control[0]['PARTNER_PARENT_ID'] || $info['se'] !== $control[0]['PARTNER_PACKAGE']
            || $result['items'][102] !== '' || $result['totalCount'] !== 2
            || $result['updatedAt'] !== 1577836800 || !PartnerPeer::$filter) {
            throw new RuntimeException('Real driver to analytics contract mismatch');
        }
        $results[] = array('mode' => $mode, 'shape' => $shape,
            'emulate' => (bool) $db->getAttribute(PDO::ATTR_EMULATE_PREPARES),
            'input_types' => array(gettype($control[0]['PARTNER_PARENT_ID']), gettype($control[0]['PARTNER_PACKAGE'])),
            'output' => $result);
    }
}
echo json_encode(array('php' => PHP_VERSION, 'mysqlnd' => phpversion('mysqlnd'),
    'source_sha256' => $sourceHash, 'results' => $results)), "\n";
