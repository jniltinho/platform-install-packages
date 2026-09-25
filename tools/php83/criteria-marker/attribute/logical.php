<?php
// Separate read-only typed snapshot; does not rewrite serialization/cache keys.
error_reporting(E_ALL);$events=[];
set_error_handler(function($severity,$message,$file,$line)use(&$events){$events[]=[$severity,$message,basename($file),$line];return false;});
class DBAdapter {}
class Propel { public static function getDB($name){return new DBAdapter();} }
require '/audit/source/'.$argv[1].'.php';
require '/audit/source/myCriteria.php';require '/audit/source/IKalturaDbQuery.php';require '/audit/source/KalturaCriteria.php';
function typed($value,&$seen,&$budget,$depth=0){
    if(--$budget<0||$depth>64)throw new RuntimeException('Snapshot bound exceeded');
    if(is_object($value)){
        $id=spl_object_id($value);
        if(isset($seen[$id]))return ['type'=>'object-reference','id'=>$seen[$id]];
        $canonical=count($seen);$seen[$id]=$canonical;
        $vars=get_mangled_object_vars($value);ksort($vars,SORT_STRING);$props=[];
        foreach($vars as $name=>$v)$props[]=[base64_encode($name),typed($v,$seen,$budget,$depth+1)];
        return ['type'=>'object','class'=>get_class($value),'id'=>$canonical,'properties'=>$props];
    }
    if(is_array($value)){
        $items=[];foreach($value as $key=>$v)$items[]=[is_int($key)?['int',$key]:['string',base64_encode($key)],typed($v,$seen,$budget,$depth+1)];
        return ['type'=>'array','items'=>$items]; // keep actual array ordering
    }
    if(is_string($value))return ['type'=>'string','base64'=>base64_encode($value)];
    if(is_float($value))return ['type'=>'float','ieee754_big_endian'=>bin2hex(pack('E',$value))];
    if(is_int($value)||is_bool($value)||is_null($value))return ['type'=>gettype($value),'value'=>$value];
    throw new RuntimeException('Unsupported fixture type');
}
$payloads=json_decode(file_get_contents('/audit/probe/legacy.json'),true,512,JSON_THROW_ON_ERROR);$rows=[];
foreach($payloads as $name=>$encoded){
    $raw=base64_decode($encoded,true);if($raw===false)throw new RuntimeException('Bad fixture');
    $obj=unserialize($raw,['allowed_classes'=>['Criteria','Criterion','DBAdapter','myCriteria','KalturaCriteria']]);
    if(!($obj instanceof Criteria))throw new RuntimeException('Unexpected object');
    $seen=[];$budget=10000;$snapshot=typed($obj,$seen,$budget);
    $rows[$name]=['input_sha256'=>hash('sha256',$raw),'logical'=>$snapshot,'reserialized_sha256'=>hash('sha256',serialize($obj))];
}
echo json_encode(['schema'=>1,'php'=>PHP_VERSION,'variant'=>$argv[1],'rows'=>$rows,'events'=>$events],JSON_THROW_ON_ERROR|JSON_PRETTY_PRINT),"\n";
