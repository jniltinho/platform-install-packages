<?php
// Synthetic SELECTs against a disposable Unix-socket-only MariaDB instance.
error_reporting(E_ALL);
ini_set('display_errors', 'stderr');
$root = '/audit/app';
set_include_path($root . '/vendor');
require_once 'propel/Propel.php';
require_once 'propel/util/PropelConfiguration.php';
require_once 'propel/util/PropelPDO.php';
require_once 'propel/util/DebugPDOStatement.php';
require_once 'propel/util/DebugPDO.php';
Propel::setConfiguration(array('debugpdo' => array('logging' => array('enabled' => false))));
$dsn = 'mysql:unix_socket=/audit/db/mysql.sock;charset=utf8mb4';
$results = array();
$matches = true;
foreach (array(false, true) as $emulate) {
    foreach (array(false, true) as $stringify) {
        $rows = array();
        foreach (array('PDO', 'DebugPDO') as $class) {
            $db = new $class($dsn, 'vagrant', '', array(PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION));
            $db->setAttribute(PDO::ATTR_EMULATE_PREPARES, $emulate);
            $db->setAttribute(PDO::ATTR_STRINGIFY_FETCHES, $stringify);
            $db->setAttribute(PDO::ATTR_DEFAULT_FETCH_MODE, PDO::FETCH_ASSOC);
            $sql = "SELECT CAST(42 AS SIGNED) AS whole_number, CAST(1.25 AS DECIMAL(8,2)) AS decimal_number, 1.25E0 AS floating_number, 'alpha' AS text_value, NULL AS null_value";
            $direct = $db->query($sql)->fetchAll();
            $statement = $db->prepare($sql . ' WHERE ? = 42');
            $statement->bindValue(1, 42, PDO::PARAM_INT);
            $statement->execute();
            $prepared = $statement->fetchAll();
            if (count($direct) !== 1 || count($prepared) !== 1 || $direct[0]['text_value'] !== 'alpha'
                || $prepared[0]['null_value'] !== null) {
                throw new RuntimeException('Synthetic query did not return expected fixture');
            }
            $rows[$class] = array('direct' => $direct, 'prepared' => $prepared);
            $server = $db->getAttribute(PDO::ATTR_SERVER_VERSION);
            $client = $db->getAttribute(PDO::ATTR_CLIENT_VERSION);
        }
        $same = $rows['PDO'] === $rows['DebugPDO'];
        $matches = $matches && $same;
        $results[] = array('emulate' => $emulate, 'stringify' => $stringify,
            'rows' => $rows, 'matches_native' => $same);
    }
}
echo json_encode(array('php' => PHP_VERSION, 'pdo_mysql' => phpversion('pdo_mysql'),
    'server' => $server, 'client' => $client, 'results' => $results), JSON_UNESCAPED_SLASHES), "\n";
exit($matches ? 0 : 1);
