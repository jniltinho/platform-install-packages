<?php
error_reporting(E_ALL);
$case=$argv[1]; $root='/audit/source'; $events=array(); $afterExit=null; $mode='normal';
$family=strpos($case,'hp-')===0?'hp':(strpos($case,'core-')===0?'core':'cli');
$paths=array('hp'=>'vendor/htmlpurifier/library/HTMLPurifier.autoload.php','core'=>'vendor/symfony/util/sfCore.class.php','cli'=>'vendor/symfony-data/bin/symfony.php');
$result=array('case'=>$case,'php'=>PHP_VERSION,'target'=>array('path'=>$paths[$family],'sha256'=>hash_file('sha256',$root.'/'.$paths[$family])),'rows'=>array(),'diagnostics'=>array());
function row($name,$value){$GLOBALS['result']['rows'][]=array('case'=>$name,'value'=>$value);}
function queue(){ $out=array();foreach(spl_autoload_functions()?:array() as $c)$out[]=is_string($c)?$c:(is_array($c)?implode('::',$c):'Closure');return $out; }
function laterLoader($class){
    $GLOBALS['events'][]=array('later',$class);
    if($GLOBALS['mode']==='throw')throw new RuntimeException('composition-fixture-exception');
    if($class==='HTMLPurifier_EntityLookup')require '/audit/composition-fixtures/hp-shadow.php';
    if($class==='FixtureFallback')require '/audit/composition-fixtures/cli-shadow.php';
}
function finalLoader($class){$GLOBALS['events'][]=array('final',$class);}
function tryClass($class){
    try{return array('loaded'=>class_exists($class),'exception'=>null);}
    catch(Throwable $e){return array('loaded'=>class_exists($class,false),'exception'=>array('class'=>get_class($e),'message'=>$e->getMessage()));}
}
function loadedFile($class){return class_exists($class,false)?(new ReflectionClass($class))->getFileName():null;}
set_error_handler(function($n,$m,$f,$l){$GLOBALS['result']['diagnostics'][]=array('severity'=>$n,'file'=>str_replace('/audit/source/','',$f),'line'=>$l,'message_sha256'=>hash('sha256',$m));return false;});
function finish(){
    static $reported=false;if($reported)return;$reported=true;
    $loaded=array();foreach(get_included_files() as $f)if(strpos($f,'/audit/')===0)$loaded[$f]=hash_file('sha256',$f);
    ksort($loaded);$GLOBALS['result']['loaded']=(object)$loaded;
    $last=error_get_last();if($last&&in_array($last['type'],array(E_ERROR,E_PARSE,E_CORE_ERROR,E_COMPILE_ERROR),true))$GLOBALS['result']['fatal']=array('severity'=>$last['type'],'file'=>$last['file'],'line'=>$last['line'],'message_sha256'=>hash('sha256',$last['message']));
    echo "\nCOMPOSITION_RESULT ",json_encode($GLOBALS['result'],JSON_UNESCAPED_SLASHES),"\n";
}
register_shutdown_function(function(){
    $last=error_get_last();
    if(!($last&&in_array($last['type'],array(E_ERROR,E_PARSE,E_CORE_ERROR,E_COMPILE_ERROR),true))&&is_callable($GLOBALS['afterExit'])){
        // Register terminal evidence first, so an intentional second-include fatal is retained.
        register_shutdown_function('finish');
        call_user_func($GLOBALS['afterExit']);
    }else finish();
});
function composition($family){
    $case=$GLOBALS['case'];row('queue-before',queue());
    if($case==='hp-repeat'){
        spl_autoload_register('laterLoader');
        HTMLPurifier_Bootstrap::registerAutoload();
        require '/audit/source/vendor/htmlpurifier/library/HTMLPurifier.autoload.php';
    }elseif($case==='core-repeat'){
        sfCore::initAutoload();sfCore::initAutoload();
        sfCore::initSimpleAutoload(array('/audit/fixtures/map'));sfCore::initSimpleAutoload(array('/audit/fixtures/map'));
        row('internal-callables',sfCore::getAutoloadCallables());
    }elseif($case==='cli-repeat'){
        row('about-to-repeat-entire-cli',true);
        row('events',$GLOBALS['events']);
        finish(); // Flush pre-include provenance; native stderr/exit determines redeclaration outcome.
        $sf_symfony_lib_dir='/audit/source/vendor/symfony';$sf_symfony_data_dir='/audit/source/vendor/symfony-data';
        require '/audit/source/vendor/symfony-data/bin/symfony.php';
        row('unexpected-second-return',true);return;
    }else{
        $prepend=strpos($case,'prepend')!==false||strpos($case,'throw-front')!==false;
        if(strpos($case,'throw')!==false)$GLOBALS['mode']='throw';
        spl_autoload_register('laterLoader',true,$prepend);
    }
    spl_autoload_register('finalLoader');row('queue-after',queue());
    $class=$family==='hp'?'HTMLPurifier_EntityLookup':($family==='core'?'FixtureMapped':'FixtureFallback');
    row('hit',tryClass($class));row('winner',loadedFile($class));
    row('miss',tryClass('FixtureMissing'));row('events',$GLOBALS['events']);
}
if($family==='hp'){
 require $root.'/vendor/htmlpurifier/library/HTMLPurifier/Bootstrap.php';require $root.'/'.$paths['hp'];composition('hp');
}elseif($family==='core'){
 require $root.'/vendor/symfony/config/sfConfig.class.php';require $root.'/vendor/symfony/util/sfContext.class.php';require $root.'/'.$paths['core'];composition('core');
}else{
 chdir('/audit/fixtures/project');$sf_symfony_lib_dir=$root.'/vendor/symfony';$sf_symfony_data_dir=$root.'/vendor/symfony-data';
 $afterExit=function(){require_once '/audit/source/vendor/symfony/config/sfConfig.class.php';sfConfig::set('sf_symfony_lib_dir','/audit/source/vendor/symfony');row('phase','post-version-composition');composition('cli');};
 $argv=array('symfony','-V');$argc=2;require $root.'/'.$paths['cli'];
}
