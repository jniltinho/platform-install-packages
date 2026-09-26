<?php
// Synthetic in-memory sink only. Full original classes, no app/bootstrap/auth.
error_reporting(E_ALL);
$diagnostics = array();
set_error_handler(function ($severity, $message, $file, $line) use (&$diagnostics) {
    $diagnostics[] = array('severity'=>$severity, 'message_sha256'=>hash('sha256',$message),
        'file'=>basename($file),'line'=>$line);
    return false;
});
$root = $argv[1];
set_include_path($root.'/vendor/ZendFramework/library'.PATH_SEPARATOR.
    $root.'/vendor/ZendFramework/library/Zend/Log/Formatter');
require $root.'/vendor/ZendFramework/library/Zend/Config.php';
require $root.'/vendor/ZendFramework/library/Zend/Log.php';
require $root.'/vendor/ZendFramework/library/Zend/Log/Writer/Stream.php';
require $root.'/infra/log/KalturaSerializableStream.php';
require $root.'/infra/log/KalturaLogFactory.php';
require $root.'/infra/log/KalturaLog.php';
class PipelineCaptureFilter implements Zend_Log_Filter_Interface {
    public $events=array();
    public function accept($event) { $this->events[]=$event; return true; }
}
class PipelineCaptureFormatter implements Zend_Log_Formatter_Interface {
    public $events=array();
    private $delegate;
    public function __construct($delegate) { $this->delegate=$delegate; }
    public function format($event) { $this->events[]=$event; return $this->delegate->format($event); }
}
function property($object,$name) {
    $p=new ReflectionProperty($object,$name);$p->setAccessible(true);return $p->getValue($object);
}
function syntheticException($synthetic) {
    try { throw new Exception('synthetic diagnostic only'); }
    catch (Exception $e) { return $e; }
}
function capture($message,$format,$extra,$instrument) {
    $config=new Zend_Config(array('writers'=>array('memory'=>array(
        'name'=>'Zend_Log_Writer_Stream','stream'=>'php://memory',
        'formatters'=>array('simple'=>array('name'=>'Zend_Log_Formatter_Simple','format'=>$format)),
        'filters'=>array('priority'=>array('name'=>'Zend_Log_Filter_Priority','priority'=>7))))));
    $logger=KalturaLogFactory::getLogger($config);
    $logger->setEventItem('timestamp','SYNTHETIC_FIXED_TIME');
    $logger->setEventItem('context','SYNTHETIC_CONTEXT');
    if ($extra!==null) $logger->setEventItem('message',$extra);
    $writers=property($logger,'_writers');$writer=$writers[0];
    $formatter=property($writer,'_formatter');
    $observer=null;$wrapped=null;
    if ($instrument) {
        $observer=new PipelineCaptureFilter();$writer->addFilter($observer);
        $wrapped=new PipelineCaptureFormatter($formatter);$writer->setFormatter($wrapped);
    }
    KalturaLog::setLogger($logger);
    // log() preserves a supplied pre-rendered string; err() would wrap it.
    if (is_string($message)) KalturaLog::log($message,KalturaLog::ERR);
    else KalturaLog::err($message);
    $stream=property($writer,'_stream');fflush($stream);rewind($stream);
    $bytes=stream_get_contents($stream);
    $event=$instrument?$observer->events[0]:null;
    $formatted=$instrument?$wrapped->events[0]:null;
    return array('bytes'=>$bytes,'writer_class'=>get_class($writer),
        'formatter_class'=>get_class($formatter),'write_declaring'=>(new ReflectionMethod($writer,'_write'))->getDeclaringClass()->getName(),'writer_event'=>$event,'formatter_event'=>$formatted);
}
try {
    $marker='SYNTHETIC_TRACE_ARGUMENT_4F83_ONLY';
    $exception=syntheticException($marker);
    $previous=new RuntimeException('outer synthetic diagnostic',0,$exception);
    $intrinsic=new Exception('intrinsic synthetic '.$marker);
    $cases=array(
        array('plain',$exception,'%message%',null),
        array('prefix-context',$exception,'PREFIX [%context%] %priorityName% %message%',null),
        array('message-extra',$exception,'%message%','SYNTHETIC_OVERRIDE'),
        array('previous',$previous,'%message%',null),
        array('intrinsic',$intrinsic,'%message%',null),
        array('pre-rendered',(string)$exception,'%message%',null));
    $records=array();
    foreach ($cases as $case) {
        list($name,$message,$format,$extra)=$case;
        $before=is_object($message)?serialize(array($message->getMessage(),$message->getCode(),$message->getFile(),$message->getLine(),$message->getTrace())):$message;
        $plain=capture($message,$format,$extra,false);
        $observed=capture($message,$format,$extra,true);
        $after=is_object($message)?serialize(array($message->getMessage(),$message->getCode(),$message->getFile(),$message->getLine(),$message->getTrace())):$message;
        $event=$observed['writer_event'];$formatter=$observed['formatter_event'];
        $records[]=array('case'=>$name,'writer_class'=>$plain['writer_class'],
            'formatter_class'=>$plain['formatter_class'],'write_declaring'=>$plain['write_declaring'],
            'instrumented_bytes_identical'=>$plain['bytes']===$observed['bytes'],
            'writer_message_type'=>gettype($event['message']),
            'writer_throwable'=>$event['message'] instanceof Throwable,
            'writer_same_message'=>$event['message']===$message,
            'formatter_same_message'=>$formatter['message']===$message,
            'writer_formatter_same_message'=>$formatter['message']===$event['message'],
            'exception_state_unchanged'=>$before===$after,
            'priority'=>$event['priority'],'priority_name'=>$event['priorityName'],
            'context_unchanged'=>$event['context']==='SYNTHETIC_CONTEXT',
            'full_marker_present'=>strpos($plain['bytes'],$marker)!==false,
            'prefix15_present'=>strpos($plain['bytes'],substr($marker,0,15))!==false,
            'has_diagnostic'=>strpos($plain['bytes'],'synthetic diagnostic')!==false,
            'has_frame'=>strpos($plain['bytes'],'syntheticException')!==false,
            'prefix_context_present'=>strpos($plain['bytes'],'PREFIX [SYNTHETIC_CONTEXT]')!==false,
            'message_override_exact'=>$plain['bytes']==='SYNTHETIC_OVERRIDE'.PHP_EOL,
            'sink_sha256'=>hash('sha256',$plain['bytes']));
    }
    $loaded=array();
    foreach (get_included_files() as $file) {
        if (strpos($file,$root.'/')===0) $loaded[substr($file,strlen($root)+1)]=hash_file('sha256',$file);
    }
    ksort($loaded);
    echo json_encode(array('runtime'=>PHP_VERSION,'sapi'=>PHP_SAPI,
        'ignore_args_ini'=>ini_get('zend.exception_ignore_args'),'records'=>$records,
        'diagnostics'=>$diagnostics,'loaded'=>$loaded,'product_changes'=>0,
        'privacy_acceptance'=>false,'application_acceptance'=>false)).PHP_EOL;
} catch (Throwable $e) {
    echo json_encode(array('status'=>'FIXTURE_FAILED','error_class'=>get_class($e),
        'message_sha256'=>hash('sha256',$e->getMessage()))).PHP_EOL;
    exit(2);
}
