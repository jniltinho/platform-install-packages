<?php
error_reporting(E_ALL);ini_set('display_errors','stderr');
$events=array();set_error_handler(function($severity,$message,$file,$line)use(&$events){$events[]=array('severity'=>$severity,'message'=>$message,'file'=>$file,'line'=>$line);return false;});
$root=$argv[1];$case=$argv[2];
if(!in_array($case,array('hit','expired','malformed','refresh-hit','refresh-miss','invalid-utf8','read-C','read-O'),true))exit(64);
require $root.'/vendor/aws/aws-autoloader.php';
$dir='/tmp/aws-serialization-cache';
if(file_exists($dir))throw new RuntimeException('Cache directory already exists');
$results=array();$phase='construct';$target=null;
function credentialState($value){
 if(!is_object($value))return array('type'=>gettype($value),'value'=>$value);
 $out=array('class'=>get_class($value));
 foreach(array('getAccessKeyId','getSecretKey','getSecurityToken','getExpiration','isExpired')as $m){$v=$value->$m();$out[$m]=array('type'=>gettype($v),'value'=>$v);}
 return $out;
}
try{
 $cache=new Doctrine\Common\Cache\FilesystemCache($dir);
 $adapter=new Guzzle\Cache\DoctrineCacheAdapter($cache);
 $id='SYNTHETIC_CREDENTIALS';
 $phase='namespace';
 $namespaced=new ReflectionMethod('Doctrine\\Common\\Cache\\CacheProvider','getNamespacedId');$namespaced->setAccessible(true);
 $filename=new ReflectionMethod('Doctrine\\Common\\Cache\\FileCache','getFilename');$filename->setAccessible(true);
 $target=$filename->invoke($cache,$namespaced->invoke($cache,$id));
 $credentials=new Aws\Common\Credentials\Credentials('SYNTHETIC_KEY','SYNTHETIC_SECRET','SYNTHETIC_TOKEN',4102444800);
 if($case==='refresh-miss'){
  $phase='refresh';$expired=new Aws\Common\Credentials\Credentials('EXPIRED_KEY','EXPIRED_SECRET','EXPIRED_TOKEN',1);
  $wrapped=new Aws\Common\Credentials\CacheableCredentials($expired,$adapter,$id);
  $results['state']=credentialState($wrapped);$results['direct']=$wrapped->serialize();$results['cache_after']=$adapter->fetch($id);
 }else{
  if($case==='invalid-utf8')$credentials->setSecurityToken("\xff");
  $phase='save';$results['save']=$adapter->save($id,$credentials,$case==='expired'?-1:0);
  if($case==='malformed'){file_put_contents($target,"0\nNOT_A_SERIALIZED_VALUE");}
  if($case==='read-C'||$case==='read-O'){
   $wire=base64_decode(stream_get_contents(STDIN,22000),true);
   if($wire===false||strlen($wire)>16384||substr($wire,0,1)!==substr($case,-1))throw new RuntimeException('Wrong frozen wire input');
   file_put_contents($target,"0\n".$wire);$results['input_sha256']=hash('sha256',$wire);
  }
  $phase='fetch';$results['fetch']=credentialState($adapter->fetch($id));
  if($case==='refresh-hit'){
   $phase='refresh';$expired=new Aws\Common\Credentials\Credentials('EXPIRED_KEY','EXPIRED_SECRET','EXPIRED_TOKEN',1);
   $wrapped=new Aws\Common\Credentials\CacheableCredentials($expired,$adapter,$id);
   $results['state']=credentialState($wrapped);$results['direct']=$wrapped->serialize();
  }
 }
}catch(Throwable $e){$results['exception']=array('class'=>get_class($e),'message'=>$e->getMessage(),'phase'=>$phase);}
$results['target_exists']=$target!==null&&is_file($target);
$files=array();if(is_dir($dir)){foreach(new RecursiveIteratorIterator(new RecursiveDirectoryIterator($dir,FilesystemIterator::SKIP_DOTS))as $f){if($f->isFile()){$bytes=file_get_contents($f->getPathname());$files[substr($f->getPathname(),strlen($dir)+1)]=array('sha256'=>hash('sha256',$bytes),'base64'=>base64_encode($bytes));}}}ksort($files);
$loaded=array();foreach(get_included_files()as $f)if(strpos($f,$root.'/')===0)$loaded[substr($f,strlen($root)+1)]=hash_file('sha256',$f);ksort($loaded);
echo json_encode(array('runtime'=>PHP_VERSION,'probe_sha256'=>hash_file('sha256',__FILE__),'kind'=>'cache','operation'=>$case,'result'=>$results,'cache_files'=>$files,'diagnostics'=>$events,'loaded'=>$loaded),JSON_INVALID_UTF8_SUBSTITUTE|JSON_UNESCAPED_SLASHES),"\n";
