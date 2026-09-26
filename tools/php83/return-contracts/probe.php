<?php
// Real full class files; no constructors with network/database dependencies run.
error_reporting(E_ALL);
$case = $argv[1] ?? '';
if (!in_array($case, ['hierarchy', 'configuration', 'exception'], true)) exit(64);
$root='/audit/app/';
$diagnostics=[];
set_error_handler(function($level,$message,$file,$line) use (&$diagnostics) {
    $diagnostics[]=[$level,$message,$file,$line];
    return false; // retain native stderr, never hide a diagnostic
});
$rows=[];
if ($case==='hierarchy') {
    foreach (['vendor/propel/Propel.php','vendor/propel/util/PropelPDO.php',
              'alpha/apps/kaltura/lib/db/KalturaPDO.php','vendor/propel/util/DebugPDO.php',
              'vendor/propel/adapter/MSSQL/MssqlPropelPDO.php',
              'vendor/propel/adapter/MSSQL/MssqlDebugPDO.php',
              'vendor/propel/util/PropelConfiguration.php',
              'api_v3/lib/exceptions/KalturaAPIException.php'] as $path) require_once $root.$path;
    foreach (['PDO'=>['beginTransaction','commit','rollBack','getAttribute','prepare','exec','query'],
              'PropelPDO'=>['beginTransaction','commit','rollBack','getAttribute','prepare'],
              'KalturaPDO'=>['beginTransaction','prepare','exec','query'],
              'DebugPDO'=>['prepare','query'],
              'MssqlPropelPDO'=>['beginTransaction','commit','rollBack'],
              'MssqlDebugPDO'=>['beginTransaction','commit','rollBack'],
              'PropelConfiguration'=>['offsetExists','offsetSet','offsetGet','offsetUnset'],
              'KalturaAPIException'=>['__wakeup']] as $class=>$methods) {
        foreach ($methods as $method) {
            $r=new ReflectionMethod($class,$method);
            $rows[]=[$class,$method,(string)$r->getReturnType(),(string)$r->getTentativeReturnType(),
                array_map(function($a){return $a->getName();},$r->getAttributes()),
                $r->getDeclaringClass()->getName()];
        }
    }
} elseif ($case==='configuration') {
    require_once $root.'vendor/propel/util/PropelConfiguration.php';
    foreach ([null,false,0,'0','',1,'known','missing'] as $key) {
        $o=new PropelConfiguration(['known'=>'old',0=>null,''=>false]);
        $before=$o->offsetExists($key);
        $get=$o->offsetGet($key);
        $set=$o->offsetSet($key,'new');
        $after=$o->offsetExists($key);
        $afterGet=$o->offsetGet($key);
        $unset=$o->offsetUnset($key);
        $rows[]=[$key,$before,$get,$set,$after,$afterGet,$unset,$o->offsetExists($key),$o->getParameters()];
    }
} else {
    require_once $root.'api_v3/lib/exceptions/KalturaAPIException.php';
    // Explicit fixture boundary: bypass constructor/APIErrors; test real wakeup/sleep only.
    foreach ([null,false,0,'0','CODE_SAMPLE',17] as $value) {
        $r=new ReflectionClass('KalturaAPIException');$o=$r->newInstanceWithoutConstructor();
        foreach (['codeStr'=>$value,'code'=>23,'message'=>'synthetic-safe','args'=>['n'=>false]] as $p=>$v) {
            $rp=$r->getProperty($p);$rp->setValue($o,$v);
        }
        try {
            $result=$o->__wakeup();$serialized=serialize($o);$copy=unserialize($serialized,['allowed_classes'=>['KalturaAPIException']]);
            $rows[]=[$value,$result,$o->getCode(),$o->getArgs(),$serialized,$copy->getCode(),$copy->getArgs(),$copy->getMessage()];
        } catch (Throwable $e) {$rows[]=[$value,'exception',get_class($e),$e->getMessage()];}
    }
}
$loaded=[];
foreach (get_included_files() as $file) if (strpos($file,$root)===0) $loaded[substr($file,strlen($root))]=hash_file('sha256',$file);
ksort($loaded);
echo json_encode(['case'=>$case,'rows'=>$rows,'diagnostics'=>$diagnostics,'loaded'=>$loaded],JSON_THROW_ON_ERROR)."\n";
