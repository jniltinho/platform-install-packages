<?php
// Real PDO/MySQL + full source KalturaStatement. Only application side effects are named seams.
error_reporting(E_ALL);
$diagnostics=array();
set_error_handler(function($s,$m,$f,$l)use(&$diagnostics){$diagnostics[]=array('severity'=>$s,'message'=>$m,'file'=>basename($f),'line'=>$l);return false;});
class KalturaLog {public static $events=array();static function debug($m){self::$events[]=$m;}static function alert($m){self::$events[]=$m;}}
class KalturaMonitorClient {public static $queries=array();static function monitorDatabaseAccess($sql,$time,$host=null){self::$queries[]=$sql;}}
class kQueryCache {public static $handled=false;static function isCurrentQueryHandled(){return self::$handled;}}
class kApiCache {public static $disabled=0;static function disableConditionalCache(){self::$disabled++;}}
class PropelException extends Exception {}
function need($v,$code){if(!$v)throw new RuntimeException($code);}
function typed($v){return array(gettype($v),$v);}
function invoke($f){try{return array('return',typed($f()));}catch(Throwable $e){return array('throw',get_class($e),typed($e->getCode()));}}
need(count($argv)===3,'ARGS');$source=$argv[1];$policy=$argv[2]==='display';need($policy||$argv[2]==='before','VARIANT');
require $source;
$expected=getenv('PHP83_PROBE_DATADIR');need(is_string($expected)&&preg_match('~^/tmp/kaltura-display-sql\.[a-f0-9]{32}/data/$~D',$expected)===1,'OWNED_PATH');
$db=new PDO('mysql:unix_socket=/audit/db/mysql.sock;charset=utf8mb4','vagrant','',array(PDO::ATTR_ERRMODE=>PDO::ERRMODE_EXCEPTION,PDO::ATTR_EMULATE_PREPARES=>true));
need($db->query('SELECT @@datadir')->fetchColumn()===$expected,'PRIVATE_DATABASE_ONLY');
$db->exec('CREATE DATABASE sql_display');$db->exec('USE sql_display');$db->exec('CREATE TABLE track_entry (id INT PRIMARY KEY, ks LONGTEXT NULL) ENGINE=InnoDB');
$db->setAttribute(PDO::ATTR_STATEMENT_CLASS,array('KalturaStatement'));
$marker='SYNTHETIC_SQL_KS_PRIVATE_VALUE_4962';$payload=serialize(array('ks'=>$marker,'other'=>'preserved'));
$rows=array();$cases=array(array('session-string',$marker,PDO::PARAM_STR),array('serialized',$payload,PDO::PARAM_STR),array('quote',"quote'back\\slash",PDO::PARAM_STR),array('null',null,PDO::PARAM_NULL),array('integer',17,PDO::PARAM_INT),array('boolean',true,PDO::PARAM_BOOL));
$id=0;
foreach(array('bound','array') as $mode)foreach($cases as $case){
 $id++;$sql='INSERT INTO track_entry (id, ks) VALUES (:p1, :p2)';$s=$db->prepare($sql);$value=$case[1];
 $binding=array();if($mode==='bound'){$binding[]=typed($s->bindValue(':p1',$id,PDO::PARAM_INT));$binding[]=typed($s->bindValue(':p2',$value,$case[2]));}
 KalturaLog::$events=array();KalturaMonitorClient::$queries=array();$prior=kApiCache::$disabled;
 $outcome=invoke(function()use($s,$mode,$id,$value){return $mode==='bound'?$s->execute():$s->execute(array(':p1'=>$id,':p2'=>$value));});
 $debug=KalturaLog::$events[0];$expectedTypes=array(':p1'=>'integer',':p2'=>gettype($value));
 if($policy)need($debug===$sql.' [bind-types:'.json_encode($expectedTypes).']','EXACT_DISPLAY_TYPES');
 if(in_array($case[0],array('serialized','session-string'),true))need((strpos($debug,$marker)===false)===$policy,'POSITIVE_AND_NEGATIVE_LEAK_CONTROL');
 $q=$db->query('SELECT ks FROM track_entry WHERE id='.$id);$stored=$q->fetchColumn();
 need($stored===($value===null?null:(string)$value),'STORED_BYTES');
 $rows[]=array('case'=>$mode.'-'.$case[0],'binding'=>$binding,'outcome'=>$outcome,'stored'=>typed($stored),'cache_delta'=>kApiCache::$disabled-$prior,'monitor'=>KalturaMonitorClient::$queries,'display_exact'=>$policy?true:null,'original_leak'=>in_array($case[0],array('serialized','session-string'),true)?!$policy:null);
}
// UPDATE + repeated same statement uses existing bind metadata and unchanged original native effects.
$sql='UPDATE track_entry SET ks=:p1 WHERE id=:p2';$s=$db->prepare($sql);$s->bindValue(':p1',$payload,PDO::PARAM_STR);$s->bindValue(':p2',1,PDO::PARAM_INT);
foreach(array(false,true) as $handled){kQueryCache::$handled=$handled;KalturaLog::$events=array();KalturaMonitorClient::$queries=array();$prior=kApiCache::$disabled;$r=invoke(function()use($s){return $s->execute();});
 if($policy)need(KalturaLog::$events[0]===$sql.' [bind-types:{":p1":"string",":p2":"integer"}]','UPDATE_DISPLAY');
 need($db->query('SELECT ks FROM track_entry WHERE id=1')->fetchColumn()===$payload,'UPDATE_BYTES');
 $rows[]=array('case'=>'update-repeat','handled'=>$handled,'outcome'=>$r,'cache_delta'=>kApiCache::$disabled-$prior,'monitor'=>KalturaMonitorClient::$queries);
}
// Dry-run and error are observations; no repaired return-contract semantics introduced by this overlay.
KalturaStatement::setDryRun(true);$s=$db->prepare('INSERT INTO track_entry (id, ks) VALUES (:p1, :p2)');$dry=invoke(function()use($s,$payload){return $s->execute(array(':p1'=>99,':p2'=>$payload));});need($db->query('SELECT COUNT(*) FROM track_entry WHERE id=99')->fetchColumn()==0,'DRY_RUN_UNCHANGED');KalturaStatement::setDryRun(false);
$s=$db->prepare('INSERT INTO absent (id) VALUES (:p1)');$error=invoke(function()use($s){return $s->execute(array(':p1'=>1));});need($error[0]==='throw'&&$error[1]==='PDOException','NATIVE_ERROR');
// Explicit negative control: SQL literals were never bound and remain visible.
$s=$db->prepare("SELECT '".$marker."' AS inline_value");KalturaLog::$events=array();$inline=invoke(function()use($s){return $s->execute();});
$inlineVisible=strpos(KalturaLog::$events[0],$marker)!==false;need($inlineVisible,'INLINE_LITERAL_LIMIT_RETAINED');need($s->fetchColumn()===$marker,'INLINE_NATIVE_VALUE');
// Reports contain synthetic fixed fixtures only. No application connection or user credentials.
echo json_encode(array('runtime'=>PHP_VERSION,'source_sha256'=>hash_file('sha256',$source),'policy'=>$policy,'rows'=>$rows,'dry_run'=>$dry,'error'=>$error,'inline_literal_visible'=>$inlineVisible,'inline_outcome'=>$inline,'diagnostics'=>$diagnostics,'application_acceptance'=>false),JSON_THROW_ON_ERROR)."\n";
