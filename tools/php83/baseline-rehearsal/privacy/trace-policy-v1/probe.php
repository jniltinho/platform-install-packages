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
function capture($message,$format,$extra,$instrument,$level='err',$roundtrip=false,$reject=false) {
    $config=new Zend_Config(array('writers'=>array('memory'=>array(
        'name'=>'Zend_Log_Writer_Stream','stream'=>'php://memory',
        'formatters'=>array('simple'=>array('name'=>'Zend_Log_Formatter_Simple','format'=>$format)),
        'filters'=>array('priority'=>array('name'=>'Zend_Log_Filter_Priority','priority'=>7))))));
    $logger=KalturaLogFactory::getLogger($config);
    $logger->setEventItem('timestamp','SYNTHETIC_FIXED_TIME');
    $logger->setEventItem('context','SYNTHETIC_CONTEXT');
    if ($extra!==null) $logger->setEventItem('message',$extra);
    $writers=property($logger,'_writers');$writer=$writers[0];
    if ($roundtrip) {
        $writer=unserialize(serialize($writer));
        $wp=new ReflectionProperty($logger,'_writers');$wp->setAccessible(true);$wp->setValue($logger,array($writer));
    }
    if ($reject) $writer->addFilter(new Zend_Log_Filter_Priority(2));
    $formatter=property($writer,'_formatter');
    $observer=null;$wrapped=null;
    if ($instrument) {
        $observer=new PipelineCaptureFilter();$writer->addFilter($observer);
        $wrapped=new PipelineCaptureFormatter($formatter);$writer->setFormatter($wrapped);
    }
    KalturaLog::setLogger($logger);
    // log() preserves a supplied pre-rendered string; err() would wrap it.
    if (is_string($message)) KalturaLog::log($message,KalturaLog::ERR);
    else KalturaLog::$level($message);
    $stream=property($writer,'_stream');fflush($stream);rewind($stream);
    $bytes=stream_get_contents($stream);
    $event=$instrument && count($observer->events)?$observer->events[0]:null;
    $formatted=$instrument && count($wrapped->events)?$wrapped->events[0]:null;
    return array('bytes'=>$bytes,'writer_class'=>get_class($writer),
        'formatter_class'=>get_class($formatter),'write_declaring'=>(new ReflectionMethod($writer,'_write'))->getDeclaringClass()->getName(),'writer_event'=>$event,'formatter_event'=>$formatted);
}
class ExplosiveDisplay { public function __toString() { throw new RuntimeException('MUST_NOT_STRINGIFY'); } }
function mixedArguments($s,$i,$b,$a,$o,$n) { return new Exception('mixed safe',31); }
function syntheticError($secret) { return new Error('safe engine error', 29); }
function stateOf($error) {
    $states=array();
    while ($error!==null) {
        $states[]=array(get_class($error),$error->getMessage(),$error->getCode(),$error->getFile(),$error->getLine(),$error->getTrace());
        $error=$error->getPrevious();
    }
    return $states;
}
try {
    $marker='SYNTHETIC_TRACE_ARGUMENT_4F83_ONLY';
    $exception=syntheticException($marker);
    $previous=new RuntimeException('safe outer',17,$exception);
    $intrinsic=new Exception('intrinsic '.$marker);
    $policy=method_exists('KalturaSerializableStream','throwableForLog');
    $mixed=mixedArguments($marker,42,true,array($marker),new ExplosiveDisplay(),null);
    $cases=array(
      array('mixed-arguments',$mixed,null,'err'),
      array('writer-roundtrip',$exception,null,'err'),
      array('exception',$exception,null,'err'),
      array('previous',$previous,null,'err'),
      array('error-err',syntheticError($marker),null,'err'),
      array('error-alert',syntheticError($marker),null,'alert'),
      array('error-crit',syntheticError($marker),null,'crit'),
      array('intrinsic-control',$intrinsic,null,'err'),
      array('prerendered-control',(string)$exception,null,'err'),
      array('extras-control',$exception,$marker,'err'),
      array('plain-control','ordinary message',null,'err'));
    $records=array();
    foreach ($cases as $case) {
      list($name,$message,$extra,$level)=$case;
      $before=is_object($message)?stateOf($message):$message;
      $plain=capture($message,'PREFIX [%context%] %priorityName% %message%',$extra,false,$level,$name==='writer-roundtrip');
      $observed=capture($message,'PREFIX [%context%] %priorityName% %message%',$extra,true,$level,$name==='writer-roundtrip');
      $after=is_object($message)?stateOf($message):$message;
      $event=$observed['writer_event'];$formatted=$observed['formatter_event'];
      $structural=true;
      if ($message instanceof Throwable && $extra===null && $policy) {
        $projection=array();
        for ($e=$message;$e!==null;$e=$e->getPrevious()) {
          $frames=array();
          foreach ($e->getTrace() as $index=>$frame) {
            $types=array();foreach (isset($frame['args'])?$frame['args']:array() as $arg)$types[]=gettype($arg);
            $frames[]=array('index'=>$index,'location'=>isset($frame['file'])?$frame['file'].':'.$frame['line']:'[internal function]',
              'call'=>(isset($frame['class'])?$frame['class']:'').(isset($frame['type'])?$frame['type']:'').(isset($frame['function'])?$frame['function']:''),'types'=>$types);
          }
          $projection[]=array('header'=>get_class($e).': '.$e->getMessage().' [code='.$e->getCode().'] in '.$e->getFile().':'.$e->getLine(),'frames'=>$frames);
        }
        $expected=array();foreach(array_reverse($projection) as $item) {
          $lines=array($item['header'],'Stack trace:');
          foreach($item['frames'] as $frame) {
            $tokens=array();foreach($frame['types'] as $type)$tokens[]='[REDACTED:'.$type.']';
            $lines[]='#'.$frame['index'].' '.$frame['location'].': '.$frame['call'].'('.implode(', ',$tokens).')';
          }
          $lines[]='#'.count($item['frames']).' {main}';$expected[]=implode("\n",$lines);
        }
        $structural=$formatted['message']===implode("\n\nNext ",$expected);
      }
      $records[]=array('case'=>$name,'exception_state_unchanged'=>$before===$after,
        'observed_same_bytes'=>$plain['bytes']===$observed['bytes'],
        'writer_same_message'=>$event['message']===$message,
        'formatter_type'=>gettype($formatted['message']),
        'full_marker'=>strpos($plain['bytes'],$marker)!==false,
        'prefix_marker'=>strpos($plain['bytes'],substr($marker,0,15))!==false,
        'mixed_types_exact'=>strpos($plain['bytes'],'mixedArguments([REDACTED:string], [REDACTED:integer], [REDACTED:boolean], [REDACTED:array], [REDACTED:object], [REDACTED:NULL])')!==false,
        'redaction_marker'=>strpos($plain['bytes'],'[REDACTED:string]')!==false,
        'structural_preserved'=>$structural,'priority'=>$event['priority'],
        'context_preserved'=>$event['context']==='SYNTHETIC_CONTEXT',
        'sink_sha256'=>hash('sha256',$plain['bytes']));
    }
    $rejected=capture($exception,'%message%',null,true,'err',false,true);
    $filter=array('empty_sink'=>$rejected['bytes']==='', 'observer_not_called'=>$rejected['writer_event']===null,
        'formatter_not_called'=>$rejected['formatter_event']===null);
    $loaded=array();foreach(get_included_files() as $f)if(strpos($f,$root.'/')===0)$loaded[substr($f,strlen($root)+1)]=hash_file('sha256',$f);ksort($loaded);
    echo json_encode(array('runtime'=>PHP_VERSION,'policy'=>$policy,'records'=>$records,
      'reject_filter'=>$filter,'diagnostics'=>$diagnostics,'loaded'=>$loaded,'privacy_acceptance'=>false,
      'negative_controls_expected_to_leak'=>array('intrinsic-control','prerendered-control','extras-control'))).PHP_EOL;
} catch(Throwable $e) {
    echo json_encode(array('status'=>'FIXTURE_FAILED','class'=>get_class($e),'message_sha256'=>hash('sha256',$e->getMessage()))).PHP_EOL;exit(2);
}
