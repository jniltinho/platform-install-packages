<?php
// In-memory SQLite only; real bundled Propel classes, no application config.
require_once 'propel/Propel.php';
require_once 'propel/util/PropelConfiguration.php';
require_once 'propel/util/PropelPDO.php';
require_once 'propel/util/DebugPDOStatement.php';
require_once 'propel/util/DebugPDO.php';
Propel::setConfiguration(array('debugpdo' => array('logging' => array('enabled' => false))));
$native = new PDO('sqlite::memory:');
$nativeRow = $native->query('SELECT 1 AS id')->fetch(PDO::FETCH_ASSOC);
$out[] = array('native-pdo-control', $nativeRow);
$db = new DebugPDO('sqlite::memory:');
$db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
$db->setAttribute(PDO::ATTR_DEFAULT_FETCH_MODE, PDO::FETCH_ASSOC);
$debugRow = $db->query('SELECT 1 AS id')->fetch(PDO::FETCH_ASSOC);
if ($debugRow !== $nativeRow) {
    throw new RuntimeException('DebugPDO scalar types differ from native PDO');
}
$out[] = array('debug-matches-native-types', $debugRow);
$db->exec('CREATE TABLE fixture (id INTEGER, name TEXT)');
$db->exec("INSERT INTO fixture VALUES (1, 'alpha'), (2, 'beta')");
$sql = 'SELECT id, name FROM fixture ORDER BY id';
$out[] = array('default', $db->query($sql)->fetchAll());
$out[] = array('assoc', $db->query($sql, PDO::FETCH_ASSOC)->fetchAll());
$out[] = array('column', $db->query($sql, PDO::FETCH_COLUMN, 1)->fetchAll());
class Php83FixtureRow
{
    public $id;
    public $name;
    public $marker;
    public function __construct($marker) { $this->marker = $marker; }
}
$rows = $db->query($sql, PDO::FETCH_CLASS, 'Php83FixtureRow', array('ctor'))->fetchAll();
$out[] = array('class', array_map(function ($row) { return (array) $row; }, $rows));
$out[] = array('count-last', $db->getQueryCount(), $db->getLastExecutedQuery());
$statement = $db->prepare('SELECT name FROM fixture WHERE id = :p1');
$statement->bindValue(':p1', 2, PDO::PARAM_INT);
$statement->execute();
$out[] = array('prepared', get_class($statement), $statement->fetchAll(), $db->getQueryCount());
$db->beginTransaction();
$db->exec("INSERT INTO fixture VALUES (3, 'rollback')");
$db->rollBack();
$out[] = array('rollback', $db->query('SELECT COUNT(*) FROM fixture')->fetchColumn());
$before = $db->getQueryCount();
try {
    $db->query('SELECT absent_column FROM fixture');
    throw new RuntimeException('Expected SQL error');
} catch (PDOException $error) {
    $out[] = array('exception', get_class($error), $before === $db->getQueryCount());
}
$db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_SILENT);
$out[] = array('silent-error', $db->query('SELECT absent_column FROM fixture'),
    $db->getQueryCount() - $before, $db->getLastExecutedQuery());
