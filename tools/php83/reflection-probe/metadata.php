<?php
$root='/audit/app';$case='reflection-probe';$out=array();
error_reporting(E_ALL);ini_set('display_errors','stderr');
set_include_path($root.'/vendor/ZendFramework/library'.PATH_SEPARATOR.$root.'/vendor');
require '/audit/tests/api-bootstrap.php';
require '/audit/probe/metadata-cases.php';
$rows=array();foreach($targets as$t){
    $reflector=new KalturaActionReflector('synthetic',$t[1],array($t[0],$t[1],'synthetic',$t[1]));
    try{
        $params=$reflector->getActionParams();
        $serialized=serialize($params);
        if(serialize($reflector->getActionParams())!==$serialized)throw new RuntimeException('Cached parameter metadata changed');
        $types=array();foreach($params as$name=>$p)$types[]=array($name,$p->getType(),$p->isOptional(),$p->getDefaultValue());
        $result=array('params',$types,'serialized_sha256',hash('sha256',$serialized));
    }catch(Throwable$e){
        if($e instanceof RuntimeException)throw $e;
        $result=array('error',get_class($e),$e->getMessage());
    }
    $rows[]=array($t,$result);
}
echo json_encode(array('php'=>PHP_VERSION,'rows'=>$rows,'warnings'=>$warnings)),"\n";
