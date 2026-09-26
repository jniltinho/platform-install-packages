<?php
if(PHP_VERSION_ID<80300||PHP_VERSION_ID>=80400)exit(64);
error_reporting(E_ALL);$diagnostics=[];
set_error_handler(function($s,$m,$f,$l)use(&$diagnostics){$diagnostics[]=[$s,$m,$f,$l];return false;});
require '/audit/probe/seams.php';
foreach(['vendor/propel/Propel.php','vendor/propel/PropelException.php','vendor/propel/util/PropelConfiguration.php','vendor/propel/util/PropelPDO.php','vendor/propel/util/DebugPDOStatement.php','vendor/propel/util/DebugPDO.php','alpha/apps/kaltura/lib/db/KalturaStatement.php','alpha/apps/kaltura/lib/db/KalturaPDO.php'] as $p)require_once '/audit/app/'.$p;
Propel::setConfiguration(['debugpdo'=>['logging'=>['enabled'=>false]]]);
function typed($v){return is_object($v)?['object',get_class($v)]:[gettype($v),$v];}
function outcome($f){try{return ['return',typed($f())];}catch(Throwable $e){return ['throw',get_class($e),typed($e->getCode())];}}
function guard($x,$m){if(!$x)throw new RuntimeException($m);}
$expected=getenv('PHP83_PROBE_DATADIR');
guard(is_string($expected)&&preg_match('~^/tmp/kaltura-return-sql\.[a-f0-9]{32}/data/$~D',$expected)===1,'Invalid owned path');
$dsn='mysql:unix_socket=/audit/db/mysql.sock;charset=utf8mb4';
$admin=new PDO($dsn,'vagrant','',[PDO::ATTR_ERRMODE=>PDO::ERRMODE_EXCEPTION]);
guard($admin->query('SELECT @@datadir')->fetchColumn()===$expected,'Refusing non-probe database');
$admin->exec('CREATE DATABASE php83_return_sql');$admin->exec('CREATE TABLE php83_return_sql.probe (id INT PRIMARY KEY) ENGINE=InnoDB');
$dsn.=';dbname=php83_return_sql';$rows=[];
foreach(['PDO','PropelPDO','KalturaPDO','DebugPDO'] as $class){
 foreach([PDO::ERRMODE_SILENT,PDO::ERRMODE_EXCEPTION] as $mode){
  $db=new $class($dsn,'vagrant','',[PDO::ATTR_ERRMODE=>$mode,PDO::ATTR_EMULATE_PREPARES=>true]);
  if($class==='KalturaPDO')$db->setCommentsEnabled(false);
  $admin->exec('DELETE FROM php83_return_sql.probe');
  foreach(['exec-zero'=>function()use($db){return $db->exec('DELETE FROM probe');},'exec-one'=>function()use($db){return $db->exec('INSERT INTO probe VALUES(1)');},'exec-failure'=>function()use($db){return $db->exec('INSERT INTO absent VALUES(1)');},'query-positive'=>function()use($db){$s=$db->query('SELECT id FROM probe');return [get_class($s),typed($s->fetchColumn())];},'query-failure'=>function()use($db){return $db->query('SELECT * FROM absent');},'prepare-positive'=>function()use($db){$s=$db->prepare('SELECT ? AS marker');return [get_class($s),$s->bindValue(1,17,PDO::PARAM_INT),$s->execute(),typed($s->fetchColumn())];},'prepare-invalid'=>function()use($db){$s=$db->prepare('SELECT * FROM absent');return [$s===false?false:get_class($s),$s===false?null:$s->execute()];},'unsupported-attribute'=>function()use($db){return $db->setAttribute(987654,true);} ] as $case=>$fn)$rows[]=[$class,$mode,$case,outcome($fn)];
  $rows[]=[$class,$mode,'persisted',typed($admin->query('SELECT id FROM php83_return_sql.probe ORDER BY id')->fetchAll(PDO::FETCH_COLUMN))];
 }
 $db=new $class($dsn,'vagrant','',[PDO::ATTR_ERRMODE=>PDO::ERRMODE_EXCEPTION]);if($class==='KalturaPDO')$db->setCommentsEnabled(false);
 $admin->exec('DELETE FROM php83_return_sql.probe');
 $trace=[];$trace[]=outcome(function()use($db){return $db->beginTransaction();});$trace[]=outcome(function()use($db){return $db->exec('INSERT INTO probe VALUES(2)');});$trace[]=outcome(function()use($db){return $db->beginTransaction();});$trace[]=typed($db->inTransaction());$trace[]=outcome(function()use($db){return $db->commit();});$trace[]=outcome(function()use($db){return $db->commit();});$trace[]=typed($db->inTransaction());$rows[]=[$class,'nested-commit',$trace,typed($admin->query('SELECT id FROM php83_return_sql.probe ORDER BY id')->fetchAll(PDO::FETCH_COLUMN))];
 if($class!=='PDO'){
  $trace=[];$trace[]=outcome(function()use($db){return $db->beginTransaction();});$trace[]=outcome(function()use($db){return $db->exec('INSERT INTO probe VALUES(3)');});$trace[]=outcome(function()use($db){return $db->beginTransaction();});$trace[]=outcome(function()use($db){return $db->rollBack();});$trace[]=outcome(function()use($db){return $db->commit();});$trace[]=typed($db->getNestedTransactionCount());$trace[]=outcome(function()use($db){return $db->forceRollBack();});$trace[]=typed($db->inTransaction());$rows[]=[$class,'nested-rollback',$trace,typed($admin->query('SELECT id FROM php83_return_sql.probe ORDER BY id')->fetchAll(PDO::FETCH_COLUMN))];
  foreach([true,false] as $enabled){$v=$db->setAttribute(PropelPDO::PROPEL_ATTR_CACHE_PREPARES,$enabled);$a=$db->prepare('SELECT 7');$b=$db->prepare('SELECT 7');$rows[]=[$class,'cache',$enabled,typed($v),$a===$b,typed($db->getAttribute(PropelPDO::PROPEL_ATTR_CACHE_PREPARES))];}
 }
 $rows[]=[$class,'no-active',outcome(function()use($db){return $db->commit();}),outcome(function()use($db){return $db->rollBack();})];
}
$db=new KalturaPDO($dsn,'vagrant','',[PDO::ATTR_ERRMODE=>PDO::ERRMODE_EXCEPTION]);$db->setCommentsEnabled(false);KalturaStatement::setDryRun(true);
try{$s=$db->prepare('INSERT INTO probe VALUES(9)');$rows[]=['KalturaStatement','dry-write',get_class($s),outcome(function()use($s){return $s->execute();}),typed($admin->query('SELECT id FROM php83_return_sql.probe WHERE id=9')->fetchAll(PDO::FETCH_COLUMN))];$s=$db->prepare('SELECT 19');$rows[]=['KalturaStatement','dry-select',outcome(function()use($s){return $s->execute();}),typed($s->fetchColumn())];}finally{KalturaStatement::setDryRun(false);}
$loaded=[];foreach(get_included_files() as $p)if(strpos($p,'/audit/app/')===0)$loaded[substr($p,11)]=hash_file('sha256',$p);ksort($loaded);ksort($GLOBALS['seam_calls']);
echo json_encode(['rows'=>$rows,'diagnostics'=>$diagnostics,'loaded'=>$loaded,'seams'=>$GLOBALS['seam_calls'],'runtime'=>PHP_VERSION,'application_acceptance'=>false],JSON_THROW_ON_ERROR)."\n";
