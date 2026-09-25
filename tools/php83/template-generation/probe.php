<?php
// Future isolated guest invocation only. Actual complete classes/tasks, no replacement generator.
if ($argc !== 3 || !preg_match('/^(method|generate|negative)$/D', $argv[1])) { exit(64); }
$source='/audit/source'; $root='/tmp/template-audit';
if (file_exists($root) || !mkdir($root,0700)) { exit(65); }
$diagnostics=array();$phase='load';
set_error_handler(function($severity,$message,$file,$line) use (&$diagnostics,&$phase){
 $diagnostics[]=array('phase'=>$phase,'severity'=>$severity,'message'=>$message,'file'=>$file,'line'=>$line);return false;
});
$case=$argv[2];$value=null;$error=null;$logs='';
// Focused tests avoid unrelated YAML registration, but load full actual classes.
require $source.'/vendor/symfony/vendor/pake/pakeGetopt.class.php';
require $source.'/vendor/symfony/vendor/pake/pakeException.class.php';
require $source.'/vendor/symfony/vendor/pake/pakeFinder.class.php';
require $source.'/vendor/symfony/vendor/pake/pakeApp.class.php';
$phase='case';
try {
 if($argv[1]==='method'){
  mkdir($root.'/nested');file_put_contents($root.'/plain.php','fixture');file_put_contents($root.'/nested/item.php','fixture');
  $target=$root;$relative=true;
  switch($case){
   case 'string':$arg='plain.php';break;
   case 'absolute':$arg=$root.'/plain.php';break;
   case 'list':$arg=array($root.'/plain.php',$root.'/nested/item.php');break;
   case 'keys':$arg=array('first'=>$root.'/plain.php',7=>'nested/item.php');break;
   case 'empty-list':$arg=array();break;
   case 'empty-name':$arg='';break;
   case 'zero-name':$arg='0';break;
   case 'leading':$arg='/plain.php';break;
   case 'outside':$arg='/outside/plain.php';break;
   case 'nonrelative':$arg=$root.'/plain.php';$relative=false;break;
   case 'empty-target':$arg='/plain.php';$target='';break;
   case 'finder':$arg=pakeFinder::type('file')->name('*.php');break;
   case 'invalid':$arg=42;break;
   default:throw new Exception('Unknown method case');
  }
  $value=pakeApp::get_files_from_argument($arg,$target,$relative);
 } else {
  $phase='generator-load';
  require_once $source.'/vendor/symfony/vendor/pake/pakeFunction.php';
  require $source.'/vendor/symfony/config/sfConfig.class.php';
  require $source.'/vendor/symfony/config/sfLoader.class.php';
  require $source.'/vendor/symfony-data/tasks/sfPakeGenerator.php';
  require $source.'/vendor/symfony-data/tasks/sfPakePropelAdminGenerator.php';
  require $source.'/vendor/symfony-data/tasks/sfPakePropelCrudGenerator.php';
  pakeApp::get_instance()->set_properties(array('symfony'=>array('name'=>'AuditProject','author'=>'Audit Author')));
  $task=new pakeTask('audit-fixture');
  foreach(array('apps/auditapp/modules','test/functional/auditapp','batch','web','data','plugins') as $dir)mkdir($root.'/'.$dir,0700,true);
  sfConfig::add(array('sf_root_dir'=>$root,'sf_apps_dir_name'=>'apps','sf_app_module_dir_name'=>'modules','sf_data_dir'=>$root.'/data','sf_plugins_dir'=>$root.'/plugins','sf_bin_dir'=>$root.'/batch','sf_web_dir'=>$root.'/web','sf_symfony_data_dir'=>$source.'/vendor/symfony-data'));
  $phase='generation';ob_start();
  if($argv[1]==='negative'){
   switch($case){
    case 'missing-module':run_init_module($task,array('auditapp'));break;
    case 'missing-admin-model':run_propel_init_admin($task,array('auditapp','AuditAdmin'));break;
    case 'unknown-batch':run_init_batch($task,array('unknown'));break;
    case 'existing-module':mkdir($root.'/apps/auditapp/modules/AuditModule');run_init_module($task,array('auditapp','AuditModule'));break;
    case 'missing-skeleton':sfConfig::set('sf_symfony_data_dir',$root.'/missing');run_init_batch($task,array('default','audit_job','auditapp'));break;
    case 'readonly-output':chmod($root.'/batch',0500);run_init_batch($task,array('default','audit_job','auditapp'));break;
    default:throw new Exception('Unknown negative case');
   }
  }elseif($case==='module'){run_init_module($task,array('auditapp','AuditModule'));}
  elseif($case==='admin'){run_propel_init_admin($task,array('auditapp','AuditAdmin','AuditModel','default'));}
  elseif($case==='crud'){run_propel_init_crud($task,array('auditapp','AuditCrud','AuditModel'));}
  else{
   $parts=explode('-',$case,2);$kind=$parts[0];$setting=$parts[1];
   $settings=array('true'=>true,'false'=>false,'zero'=>'0','wordfalse'=>'false');
   if($setting!=='default' && !array_key_exists($setting,$settings))throw new Exception('Invalid debug case');
   if($kind==='default')$args=array('default','audit_job','auditapp','dev');
   elseif($kind==='rotate')$args=array('rotate_log','auditapp','prod','dev');
   elseif($kind==='controller')$args=array('auditapp','dev','audit_front');
   else throw new Exception('Invalid task');
   if($setting!=='default')$args[]=$settings[$setting];
   if($kind==='controller')run_init_controller($task,$args);else run_init_batch($task,$args);
  }
  $logs=ob_get_clean();
 }
} catch(Throwable $e){if(ob_get_level())$logs=ob_get_clean();$error=array('class'=>get_class($e),'message'=>$e->getMessage(),'file'=>$e->getFile(),'line'=>$e->getLine());}
$outputs=array();$it=new RecursiveIteratorIterator(new RecursiveDirectoryIterator($root,FilesystemIterator::SKIP_DOTS));
foreach($it as $file)if($file->isFile()){$rel=substr($file->getPathname(),strlen($root)+1);$bytes=file_get_contents($file->getPathname());$outputs[$rel]=array('sha256'=>hash('sha256',$bytes),'base64'=>base64_encode($bytes));}ksort($outputs);
$loaded=array();foreach(get_included_files() as $f)if(strpos($f,$source.'/')===0)$loaded[substr($f,strlen($source)+1)]=hash_file('sha256',$f);ksort($loaded);
echo json_encode(array('mode'=>$argv[1],'case'=>$case,'runtime'=>PHP_VERSION,'value'=>$value,'exception'=>$error,'diagnostics'=>$diagnostics,'logs'=>$logs,'loaded'=>$loaded,'outputs'=>$outputs),JSON_UNESCAPED_SLASHES|JSON_THROW_ON_ERROR)."\n";
exit($error===null?0:10);
