<?php
// Actual full logger pipeline, synthetic memory sink; never application/bootstrap/auth.
error_reporting(E_ALL);
$diagnostics=array();
set_error_handler(function($s,$m,$f,$l)use(&$diagnostics){$diagnostics[]=array('severity'=>$s,'message_sha256'=>hash('sha256',$m),'file'=>basename($f),'line'=>$l);return false;});
$root=$argv[1];
set_include_path($root.'/vendor/ZendFramework/library'.PATH_SEPARATOR.$root.'/vendor/ZendFramework/library/Zend/Log/Formatter');
require $root.'/vendor/ZendFramework/library/Zend/Config.php';
require $root.'/vendor/ZendFramework/library/Zend/Log.php';
require $root.'/vendor/ZendFramework/library/Zend/Log/Writer/Stream.php';
require $root.'/infra/log/KalturaSerializableStream.php';
require $root.'/infra/log/KalturaLogFactory.php';
require $root.'/infra/log/KalturaLog.php';
class CallerObserver implements Zend_Log_Filter_Interface {
 public $event;
 public function accept($event){$this->event=$event;return true;}
}
class UsefulEmitter {public function emit($message){KalturaLog::log($message,KalturaLog::ERR);}}
class OtherStream {public function _write($message){KalturaLog::log($message,KalturaLog::ERR);}}
class KalturaSerializableStreamSibling {public function _write($message){KalturaLog::log($message,KalturaLog::ERR);}}
function prop($o,$name){$r=new ReflectionProperty($o,$name);$r->setAccessible(true);return $r->getValue($o);}
$records=array();
foreach(array(array(new UsefulEmitter(),'emit'),array(new OtherStream(),'_write'),array(new KalturaSerializableStreamSibling(),'_write')) as $emitter){
 foreach(array('string','throwable') as $kind){
  $message=$kind==='string'?'synthetic plain':new Exception('synthetic exception',31);
  $before=$kind==='throwable'?array($message->getMessage(),$message->getCode(),$message->getFile(),$message->getLine(),$message->getTrace()):$message;
  $config=new Zend_Config(array('eventItems'=>array('logMethod'=>'LogMethod'),'writers'=>array('memory'=>array('name'=>'Zend_Log_Writer_Stream','stream'=>'php://memory','formatters'=>array('simple'=>array('name'=>'Zend_Log_Formatter_Simple','format'=>'%logMethod%|%context%|%priority%|%message%')),'filters'=>array('priority'=>array('name'=>'Zend_Log_Filter_Priority','priority'=>7))))));
  $logger=KalturaLogFactory::getLogger($config);$logger->setEventItem('context','SYNTHETIC_EXTRA');
  $writers=prop($logger,'_writers');$writer=$writers[0];$observer=new CallerObserver();$writer->addFilter($observer);
  KalturaLog::setLogger($logger);$emitter[0]->{$emitter[1]}($message);
  $stream=prop($writer,'_stream');fflush($stream);rewind($stream);$bytes=stream_get_contents($stream);$parts=explode('|',$bytes,4);
  $after=$kind==='throwable'?array($message->getMessage(),$message->getCode(),$message->getFile(),$message->getLine(),$message->getTrace()):$message;
  $records[]=array('case'=>get_class($emitter[0]).'::'.$emitter[1].'/'.$kind,'caller'=>$parts[0], 'extra'=>$parts[1], 'priority'=>$parts[2], 'message_present'=>strpos($parts[3],$kind==='string'?'synthetic plain':'synthetic exception')!==false,'observer_same_message'=>$observer->event['message']===$message,'observer_extra'=>$observer->event['context'],'observer_logMethod_class'=>get_class($observer->event['logMethod']),'message_unchanged'=>$before===$after,'writer_class'=>get_class($writer),'formatter_class'=>get_class(prop($writer,'_formatter')));
 }
}
$loaded=array();foreach(get_included_files() as $path){if(strpos($path,$root.'/')===0)$loaded[substr($path,strlen($root)+1)]=hash_file('sha256',$path);}ksort($loaded);
echo json_encode(array('runtime'=>PHP_VERSION,'records'=>$records,'loaded'=>$loaded,'diagnostics'=>$diagnostics),JSON_THROW_ON_ERROR)."\n";
