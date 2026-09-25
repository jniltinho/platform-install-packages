<?php
// Synthetic SQL only. Record values/types, never DSN/passwords or SQL error text.
error_reporting(E_ALL);
$diagnostics=[];
set_error_handler(function($severity,$message,$file,$line) use (&$diagnostics) {
    $diagnostics[]=[$severity,basename($file),$line];return true;
});
require '/audit/app/vendor/propel/PropelException.php';
require '/audit/app/vendor/propel/util/PropelPDO.php';
// Only logging/cache/monitor side-effect boundaries are stubbed; PDO and statement are real.
class KalturaLog { public static function debug($message) {} public static function alert($message) {} }
class kQueryCache { public static function isCurrentQueryHandled() { return false; } }
class kApiCache { public static function disableConditionalCache() {} }
class KalturaMonitorClient { public static function monitorDatabaseAccess($sql,$duration) {} }
require '/audit/app/alpha/apps/kaltura/lib/db/KalturaStatement.php';
function checked($ok,$label) { if (!$ok) throw new RuntimeException($label); }
function resultOf($fn) {
    try { $v=$fn();return ['return',gettype($v),$v]; }
    catch (PDOException $e) { return ['throw',get_class($e),(string)$e->getCode()]; }
    catch (PropelException $e) { return ['throw',get_class($e),(string)$e->getCode()]; }
}
$dsn='mysql:unix_socket=/audit/db/mysql.sock;charset=utf8mb4';
$admin=new PDO($dsn,'vagrant','',[PDO::ATTR_ERRMODE=>PDO::ERRMODE_EXCEPTION]);
checked($admin->query('SELECT @@datadir')->fetchColumn()===getenv('PHP83_PROBE_DATADIR'),'Refusing unowned database');
$admin->exec('DROP DATABASE IF EXISTS php83_pdo_return_probe');
$admin->exec('CREATE DATABASE php83_pdo_return_probe');
$dsn.=';dbname=php83_pdo_return_probe';
$admin->exec('CREATE TABLE php83_pdo_return_probe.probe (id INT PRIMARY KEY) ENGINE=InnoDB');
$rows=[];
foreach (['PDO','PropelPDO'] as $class) {
    $db=new $class($dsn,'vagrant','',[PDO::ATTR_ERRMODE=>PDO::ERRMODE_SILENT]);
    $rows[]=['set-attribute',$class,resultOf(function()use($db){return $db->setAttribute(PDO::ATTR_EMULATE_PREPARES,true);}),$db->getAttribute(PDO::ATTR_EMULATE_PREPARES)];
    $rows[]=['unsupported-attribute',$class,resultOf(function()use($db){return $db->setAttribute(987654,true);})];
}
$db=new PropelPDO($dsn,'vagrant','',[PDO::ATTR_ERRMODE=>PDO::ERRMODE_EXCEPTION]);
$cacheReturn=$db->setAttribute(PropelPDO::PROPEL_ATTR_CACHE_PREPARES,true);
$a=$db->prepare('SELECT ? AS marker');$b=$db->prepare('SELECT ? AS marker');
checked($a===$b,'Expected same cached prepare');checked($db->getAttribute(PropelPDO::PROPEL_ATTR_CACHE_PREPARES)===true,'Cache attribute missing');
$rows[]=['cache-attribute',gettype($cacheReturn),$cacheReturn,$a===$b];
$db->setAttribute(PropelPDO::PROPEL_ATTR_CACHE_PREPARES,false);
$a=$db->prepare('SELECT ? AS marker');$b=$db->prepare('SELECT ? AS marker');checked($a!==$b,'Cache disable failed');
$rows[]=['cache-disabled',$a!==$b];
$trace=[];$trace[]=$db->beginTransaction();$db->exec('INSERT INTO probe VALUES(1)');$trace[]=$db->beginTransaction();
$trace[]=[$db->getNestedTransactionCount(),$db->inTransaction()];$trace[]=$db->commit();$trace[]=[$db->getNestedTransactionCount(),$db->inTransaction()];$trace[]=$db->commit();
$trace[]=[$db->getNestedTransactionCount(),$db->inTransaction(),(int)$db->query('SELECT COUNT(*) FROM probe')->fetchColumn()];
checked($trace===[true,true,[2,true],true,[1,true],true,[0,false,1]],'Nested commit state changed');$rows[]=['nested-commit',$trace];
$trace=[];$trace[]=$db->beginTransaction();$db->exec('INSERT INTO probe VALUES(2)');$trace[]=$db->beginTransaction();$trace[]=$db->rollBack();
$trace[]=resultOf(function()use($db){return $db->commit();});$trace[]=[$db->getNestedTransactionCount(),$db->inTransaction()];$trace[]=$db->forceRollBack();
$trace[]=[$db->getNestedTransactionCount(),$db->inTransaction(),(int)$db->query('SELECT COUNT(*) FROM probe')->fetchColumn()];
checked($trace===[true,true,true,['throw','PropelException','0'],[1,true],true,[0,false,1]],'Nested rollback state changed');$rows[]=['nested-rollback',$trace];
$rows[]=['no-active-propel',resultOf(function()use($db){return $db->commit();}),resultOf(function()use($db){return $db->rollBack();})];
foreach ([PDO::ERRMODE_SILENT,PDO::ERRMODE_EXCEPTION] as $mode) {
    foreach (['PDOStatement','KalturaStatement'] as $class) {
        $db=new PDO($dsn,'vagrant','',[PDO::ATTR_ERRMODE=>$mode,PDO::ATTR_EMULATE_PREPARES=>true]);
        if ($class==='KalturaStatement') $db->setAttribute(PDO::ATTR_STATEMENT_CLASS,[$class]);
        $s=$db->prepare('SELECT ? AS marker');$bound=$s->bindValue(1,17,PDO::PARAM_INT);$r=resultOf(function()use($s){return $s->execute();});
        $value=(int)$s->fetchColumn();checked($bound===true && $value===17,'Bound SELECT result');
        $rows[]=['statement-success',$mode,$class,$bound,$r,$value];
        $s=$db->prepare('SELECT * FROM missing_fixture_table');$r=resultOf(function()use($s){return $s->execute();});
        $rows[]=['statement-failure',$mode,$class,$r,$s->errorCode()];
    }
}
$db=new PDO($dsn,'vagrant','',[PDO::ATTR_ERRMODE=>PDO::ERRMODE_EXCEPTION,PDO::ATTR_EMULATE_PREPARES=>true]);
$db->setAttribute(PDO::ATTR_STATEMENT_CLASS,['KalturaStatement']);KalturaStatement::setDryRun(true);
try {
    $s=$db->prepare('INSERT INTO probe VALUES(9)');$r=resultOf(function()use($s){return $s->execute();});
    $native=new PDO($dsn,'vagrant','',[PDO::ATTR_ERRMODE=>PDO::ERRMODE_EXCEPTION]);
    $count=(int)$native->query('SELECT COUNT(*) FROM probe WHERE id=9')->fetchColumn();checked($count===0,'Dry run wrote a row');
    $rows[]=['dry-run-write',$r,$count];
    $s=$db->prepare('SELECT 19 AS marker');$r=resultOf(function()use($s){return $s->execute();});$value=(int)$s->fetchColumn();checked($value===19,'Dry-run SELECT blocked');$rows[]=['dry-run-select',$r,$value];
} finally { KalturaStatement::setDryRun(false); }
echo json_encode(['php'=>PHP_VERSION,'driver'=>phpversion('pdo_mysql'),'rows'=>$rows,'diagnostics'=>$diagnostics],JSON_THROW_ON_ERROR|JSON_PRETTY_PRINT),"\n";
