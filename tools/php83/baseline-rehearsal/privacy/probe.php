<?php
// Synthetic-only probe. No application bootstrap, DB, HTTP, credential files or writes.
if ($argc !== 3 || !in_array($argv[2], array('original', 'privacy'), true)) exit(2);
$root = realpath($argv[1]);
if (!$root || !is_file($root.'/infra/log/KalturaLog.php')) exit(2);
class Zend_Log {
 const EMERG=0, ALERT=1, CRIT=2, ERR=3, WARN=4, NOTICE=5, INFO=6, DEBUG=7;
 public $events=array(); public $items=array();
 function log($message,$priority) {$this->events[]=array('message'=>$message,'priority'=>$priority,'items'=>$this->items);}
 function setEventItem($name,$value) {$this->items[$name]=$value;}
}
class kCurrentContext {
 public static $partner_id=102,$master_partner_id=null,$ks=null,$is_admin_session=false,$uid='fixture-user',$ks_uid=null;
}
class KalturaMonitorClient {public static $calls=array(); static function monitorApiEnd($code){self::$calls[]=$code;}}
class ParamFixture {private $name;function __construct($name){$this->name=$name;}function getName(){return $this->name;}}
class ResourceFixture {public $token='synthetic-upload-token-123456';public $description='ordinary-value';private $privateValue='synthetic-private-field';function __clone(){throw new Exception('Clone forbidden');}function __get($key){throw new Exception('Magic read forbidden');}}
require $root.'/infra/log/KalturaLog.php';
require $root.'/api_v3/lib/KalturaFrontController.php';
$privacy=$argv[2]==='privacy';
if ($privacy !== method_exists('KalturaLog','paramsForLog')) exit(3);
$logger=new Zend_Log();KalturaLog::setLogger($logger);
$secret='synthetic-secret-with-plus+slash/equals=';$ks='synthetic-user-ks-123456789';
$params=array('service'=>'session','secret'=>$secret,'ks'=>$ks,'1:SeCrEt'=>$secret,'nested'=>array('password'=>$secret,'label'=>'unchanged'),'ordinary'=>$secret);
$before=serialize($params);
$copy=$privacy?KalturaLog::paramsForLog($params):$params;
$rows=array();
$rows['request_input_unchanged']=serialize($params)===$before;
$rows['request_sensitive_fields_absent']=$copy['secret']!==$secret&&$copy['ks']!==$ks&&$copy['1:SeCrEt']!==$secret&&$copy['nested']['password']!==$secret;
$rows['ordinary_strings_not_indiscriminately_replaced']=$copy['ordinary']===$secret&&$copy['nested']['label']==='unchanged';
$rows['request_key_order_preserved']=array_keys($copy)===array_keys($params);
parse_str('s%65cret='.rawurlencode($secret).'&1%3Aks='.rawurlencode($ks),$decoded);
$encodedCopy=$privacy?KalturaLog::paramsForLog($decoded):$decoded;
$rows['native_decoded_post_fields_absent']=$encodedCopy['secret']!==$secret&&$encodedCopy['1:ks']!==$ks;
$args=array($secret,'fixture-user',0,102);$metadata=array('secret'=>new ParamFixture('secret'),'userId'=>new ParamFixture('userId'),'type'=>new ParamFixture('type'),'partnerId'=>new ParamFixture('partnerId'));
$argsBefore=serialize($args);$argCopy=$privacy?KalturaLog::argumentsForLog($args,$metadata):$args;
$rows['actual_dispatch_arguments_unchanged']=serialize($args)===$argsBefore;
$rows['positional_secret_absent']=$argCopy[0]!==$secret;
$rows['positional_nonsensitive_types_preserved']=array_slice($argCopy,1)===array_slice($args,1);
$object=new ResourceFixture();$objectBefore=serialize($object);
$objectCopy=$privacy?KalturaLog::argumentsForLog(array($object),array(new ParamFixture('resource'))):array($object);
$rows['real_dto_unchanged']=serialize($object)===$objectBefore;
$rows['dto_token_absent']=strpos(print_r($objectCopy,true),$object->token)===false;
$rows['dto_private_nonsensitive_value_preserved']=strpos(print_r($objectCopy,true),'synthetic-private-field')!==false;
$rows['dto_log_shape']=$privacy?'class-tagged-visibility-field-array':'original-object-print';
class TypedArrayFixture {protected $array;public $count;function __construct($values){$this->array=$values;$this->count=count($values);}}
$typed=new TypedArrayFixture(array(array('otp'=>'synthetic-otp-12345','name'=>'kept-item')));
$typedCopy=$privacy?KalturaLog::argumentsForLog(array($typed),array(new ParamFixture('items'))):array($typed);
$rows['typed_array_items_kept']=strpos(print_r($typedCopy,true),'kept-item')!==false;
$rows['typed_array_otp_absent']=strpos(print_r($typedCopy,true),'synthetic-otp-12345')===false;
$extra=array('tokenHash'=>$secret,'hashKey'=>$secret,'cmsPassword'=>$secret,'otp'=>$secret);
$extraCopy=$privacy?KalturaLog::paramsForLog($extra):$extra;
$rows['additional_auth_fields_absent']=strpos(print_r($extraCopy,true),$secret)===false;
if($privacy) {
 $rows['mapping_failure_visible']=KalturaLog::argumentsForLog(array('x'),array())===array('__log_copy_mapping_mismatch__'=>true);
 $deep=array('secret'=>$secret);for($i=0;$i<35;$i++)$deep=array('next'=>$deep);
 $rows['depth_bounded']=strpos(print_r(KalturaLog::paramsForLog($deep),true),$secret)===false;
}
$ref=new ReflectionClass('KalturaFrontController');$front=$ref->newInstanceWithoutConstructor();
$start=$ref->getProperty('requestStart');$start->setAccessible(true);$start->setValue($front,microtime(true));
foreach(array(null,'',$ks) as $value){
 kCurrentContext::$ks=$value;$logger->events=array();$front->onRequestEnd(true,null,7);$event=$logger->events[0];
 $parts=explode(',',$event['message']);
 $label=$value===null?'null':($value===''?'empty':'string');
 $rows['analytics_'.$label]=array('level'=>$event['priority'],'event_type'=>$event['items']['type'],'field_count'=>count($parts),'request_end'=>$parts[0],'partner'=>$parts[1],'ks_field_expected'=>$value===null||$value===''?($parts[3]===''):($parts[3]===($privacy?'[REDACTED]':$ks)),'context_unchanged'=>kCurrentContext::$ks===$value,'unrelated_fields'=>array($parts[1],$parts[2],$parts[4],$parts[5],$parts[7],$parts[8],$parts[9]));
}
function traceFixture($privateValue){return new Exception('Synthetic diagnostic, no credential message');}
$exception=traceFixture($secret);$logger->events=array();KalturaLog::err($exception);
$formatterRoot=$root.'/vendor/ZendFramework/library/Zend/Log/Formatter';
set_include_path($formatterRoot);require $formatterRoot.'/Simple.php';
$formatter=new Zend_Log_Formatter_Simple('%priorityName%: %message%');
$trace=$formatter->format(array('priorityName'=>'ERR','message'=>$exception));
$rows['exception_object_identity_preserved']=$logger->events[0]['message']===$exception;
$rows['exception_priority_preserved']=$logger->events[0]['priority']===Zend_Log::ERR;
$rows['trace_observation']=array('full_marker_present'=>strpos($trace,$secret)!==false,'prefix15_present'=>strpos($trace,substr($secret,0,15))!==false,'ignore_args_ini'=>ini_get('zend.exception_ignore_args'),'formatter_contains_diagnostic'=>strpos($trace,'Synthetic diagnostic, no credential message')!==false,'formatter_contains_frame'=>strpos($trace,'traceFixture')!==false);
$rows['privacy_accepted']=false; // This synthetic probe is not a native API/log-privacy gate.
echo json_encode(array('variant'=>$argv[2],'php'=>PHP_VERSION,'sapi'=>PHP_SAPI,'sources'=>array('log'=>hash_file('sha256',$root.'/infra/log/KalturaLog.php'),'front'=>hash_file('sha256',$root.'/api_v3/lib/KalturaFrontController.php'),'dispatcher'=>hash_file('sha256',$root.'/api_v3/lib/KalturaDispatcher.php'),'formatter'=>hash_file('sha256',$formatterRoot.'/Simple.php'),'formatter_interface'=>hash_file('sha256',$formatterRoot.'/Interface.php')),'rows'=>$rows),JSON_UNESCAPED_SLASHES)."\n";
