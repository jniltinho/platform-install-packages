<?php
// Preparation only. Execute only inside a coordinator-approved immutable lab sandbox.
error_reporting(E_ALL);
ini_set('display_errors', 'stderr');
$events = array();
set_error_handler(function ($severity, $message, $file, $line) use (&$events) {
    $events[] = array('severity'=>$severity, 'message'=>$message, 'file'=>$file, 'line'=>$line);
    return false; // retain native channel, including known baseline diagnostics
});
$root = $argv[1]; $kind = $argv[2]; $operation = $argv[3];
$names = array('plain'=>'Aws\\Common\\Credentials\\Credentials', 'null'=>'Aws\\Common\\Credentials\\NullCredentials',
    'decorator'=>'Aws\\Common\\Credentials\\AbstractCredentialsDecorator', 'role'=>'RefreshableRole',
    'profile'=>'Aws\\Common\\Credentials\\RefreshableInstanceProfileCredentials', 'cacheable'=>'Aws\\Common\\Credentials\\CacheableCredentials');
if (!isset($names[$kind]) || !in_array($operation,array('roundtrip','read','malformed','invalid-utf8'),true)) { exit(64); }
require $root.'/vendor/aws/aws-autoloader.php';
if ($kind==='role') require $root.'/infra/storage/RefreshableRole.class.php';
function state($object) {
    $values=array();
    foreach (array('getAccessKeyId','getSecretKey','getSecurityToken','getExpiration','isExpired') as $method) {
        try {$value=$object->$method(); $values[$method]=array('type'=>gettype($value),'value'=>$value);}
        catch (Throwable $e) {$values[$method]=array('exception'=>get_class($e),'message'=>$e->getMessage());}
    }
    $properties=array(); $reflection=new ReflectionObject($object);
    foreach ($reflection->getProperties() as $p) {
        $p->setAccessible(true);$v=$p->getValue($object);
        $properties[$p->getDeclaringClass()->getName().'::'.$p->getName()]=array('type'=>gettype($v),'value'=>is_object($v)?get_class($v):$v);
    }
    ksort($properties);return array('class'=>get_class($object),'getters'=>$values,'properties'=>$properties);
}
$result=array();
try {
    $class=$names[$kind];
    if ($operation==='read') {
        // Trusted coordinator-produced synthetic wire only, never external/user payloads.
        $payload=base64_decode(stream_get_contents(STDIN, 22000),true);
        if ($payload===false || strlen($payload)>16384) throw new RuntimeException('Invalid bounded fixture');
        $decoded=unserialize($payload,array('allowed_classes'=>array_values($names)));
        $result=array('input_sha256'=>hash('sha256',$payload),'restored'=>is_object($decoded)?state($decoded):array('type'=>gettype($decoded),'value'=>$decoded));
    } else {
        $credentials=new Aws\Common\Credentials\Credentials(' SYNTHETIC_KEY ',' SYNTHETIC_SECRET ','SYNTHETIC_TOKEN',null);
        if ($operation==='invalid-utf8') $credentials->setSecurityToken("\xff");
        if ($kind==='plain') $object=$credentials;
        elseif ($kind==='null') $object=new $class();
        elseif ($kind==='profile' || $kind==='cacheable') {
            // Avoid constructors that create network clients/cache. Actual full class, not replacement subclass.
            $object=(new ReflectionClass($class))->newInstanceWithoutConstructor();
            $p=new ReflectionProperty('Aws\\Common\\Credentials\\AbstractCredentialsDecorator','credentials');$p->setAccessible(true);$p->setValue($object,$credentials);
        } else $object=new $class($credentials);
        if ($kind==='role') {$object->setRoleArn('SYNTHETIC_ROLE');$object->setS3Region('SYNTHETIC_REGION');}
        $result['before']=state($object);
        if ($operation==='malformed') {
            $object->unserialize('{malformed');$result['after']=state($object);
        } else {
            $direct=$object->serialize();
            $result['direct']=array('type'=>gettype($direct),'value'=>$direct);
            $wire=serialize($object);
            $result['wire']=array('format'=>substr($wire,0,1),'sha256'=>hash('sha256',$wire),'base64'=>base64_encode($wire));
            $restored=unserialize($wire,array('allowed_classes'=>array_values($names)));
            $result['restored']=is_object($restored)?state($restored):array('type'=>gettype($restored),'value'=>$restored);
        }
    }
} catch (Throwable $e) {$result['exception']=array('class'=>get_class($e),'message'=>$e->getMessage());}
$loaded=array();foreach (get_included_files() as $f) if (strpos($f,$root.'/')===0) $loaded[substr($f,strlen($root)+1)]=hash_file('sha256',$f);
ksort($loaded);
echo json_encode(array('runtime'=>PHP_VERSION,'probe_sha256'=>hash_file('sha256',__FILE__),'kind'=>$kind,'operation'=>$operation,'result'=>$result,'diagnostics'=>$events,'loaded'=>$loaded),JSON_INVALID_UTF8_SUBSTITUTE|JSON_UNESCAPED_SLASHES),"\n";
