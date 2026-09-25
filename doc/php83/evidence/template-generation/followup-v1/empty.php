<?php
// Isolated native call only. No includes, eval, autoload, application or config.
$diagnostics=array();
set_error_handler(function($severity,$message,$file,$line) use (&$diagnostics){
 $diagnostics[]=array('severity'=>$severity,'message'=>$message,'line'=>$line);return false;
});
$returned=null;$exception=null;
try {
 $returned = define('SF_DEBUG',       );
} catch(Throwable $e) {$exception=array('class'=>get_class($e),'message'=>$e->getMessage());}
echo json_encode(array('runtime'=>PHP_VERSION,'returned'=>$returned,'returned_type'=>gettype($returned),'defined'=>defined('SF_DEBUG'),'constant'=>defined('SF_DEBUG')?constant('SF_DEBUG'):null,'diagnostics'=>$diagnostics,'exception'=>$exception),JSON_UNESCAPED_SLASHES|JSON_THROW_ON_ERROR)."\n";
exit($exception===null?0:10);
