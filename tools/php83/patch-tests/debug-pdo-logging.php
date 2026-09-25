<?php
// Synthetic in-memory logging; never write a log file or load app configuration.
require_once 'propel/Propel.php';
require_once 'propel/util/PropelConfiguration.php';
require_once 'propel/util/PropelPDO.php';
require_once 'propel/util/DebugPDOStatement.php';
require_once 'propel/util/DebugPDO.php';
class Php83MemoryLogger
{
    public $messages = array();
    public function debug($message) { $this->messages[] = $message; }
}
$logger = new Php83MemoryLogger();
Propel::setLogger($logger);
Propel::setConfiguration(array('debugpdo' => array('logging' => array(
    'enabled' => true, 'onlyslow' => false, 'methods' => array('DebugPDO::query'),
    'details' => array('method' => array('enabled' => true, 'pad' => 0),
        'querycount' => array('enabled' => true, 'pad' => 0))
))));
$db = new DebugPDO('sqlite::memory:');
$db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
$sql = "SELECT 'alpha' AS name";
$out[] = array('row', $db->query($sql, PDO::FETCH_COLUMN, 0)->fetchAll());
$expected = array('method: DebugPDO::query | querycount: 0 | ' . $sql);
if ($logger->messages !== $expected || $db->getQueryCount() !== 1 || $db->getLastExecutedQuery() !== $sql) {
    throw new RuntimeException('Successful query logging/accounting mismatch');
}
try {
    $db->query('SELECT missing FROM absent');
    throw new RuntimeException('Expected query exception');
} catch (PDOException $error) {
    if ($logger->messages !== $expected || $db->getQueryCount() !== 1 || $db->getLastExecutedQuery() !== $sql) {
        throw new RuntimeException('Exception changed log/accounting');
    }
}
$db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_SILENT);
$failed = $db->query('SELECT missing FROM absent');
$expected[] = 'method: DebugPDO::query | querycount: 1 | SELECT missing FROM absent';
if ($failed !== false || $logger->messages !== $expected || $db->getQueryCount() !== 2
    || $db->getLastExecutedQuery() !== 'SELECT missing FROM absent') {
    throw new RuntimeException('Silent failure logging/accounting mismatch');
}
$out[] = array('messages', $logger->messages, 'count', $db->getQueryCount());
