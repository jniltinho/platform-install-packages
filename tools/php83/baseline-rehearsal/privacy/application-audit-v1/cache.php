// Read only two documented config-cache keys, never application/session cache keys.
set_include_path('/opt/kaltura/app/vendor/ZendFramework/library');
require '/opt/kaltura/app/infra/kEnvironment.php';
require '/opt/kaltura/app/alpha/config/cache/kFileSystemConf.php';
$warnings=0;set_error_handler(function() use (&$warnings) { $warnings++;return false; });
$fs=new kFileSystemConf();$host=gethostname();
function privateConfigSnapshot($fs,$host) {
 $snapshot=array();foreach(array('logger','kLocalMemCacheConf','kRemoteMemCacheConf') as $name)
  foreach($fs->getFileNames($name,$host) as $p)if(is_file($p))$snapshot[$p]=hash_file('sha256',$p);
 ksort($snapshot);return $snapshot;
}
$configBefore=privateConfigSnapshot($fs,$host);$disk=$fs->loadByHostName('logger',$host);
function connectConfigCache($config) {
    if (!isset($config['host'],$config['port'])) throw new Exception('MISSING_CACHE_ENDPOINT');
    if (!in_array($config['host'],array('localhost','127.0.0.1','192.168.56.74'),true)) throw new Exception('NONLAB_CACHE_ENDPOINT');
    $port=filter_var($config['port'],FILTER_VALIDATE_INT);
    if (!in_array($port,array(11211,11212),true)) throw new Exception('UNREVIEWED_CACHE_PORT');
    $client=new Memcache();
    if (!$client->connect($config['host']==='localhost'?'127.0.0.1':$config['host'],$port,2)) throw new Exception('CACHE_CONNECT_FAILED');
    return $client;
}
function arraysOnly($value,$depth=0) {
    if ($depth>32 || is_object($value) || is_resource($value)) return false;
    if (is_array($value)) foreach($value as $item)if(!arraysOnly($item,$depth+1))return false;
    return true;
}
try {
    $local=connectConfigCache($fs->loadByHostName('kLocalMemCacheConf',$host));
    $remote=connectConfigCache($fs->loadByHostName('kRemoteMemCacheConf',$host));
    $cached=$local->get('CONF-MAP-logger');
    $version=$remote->get('CONF_CACHE_VERSION_KEY');
    $safe=arraysOnly($cached) && (is_string($version)||$version===false);
    $missing=$cached===false;$valid=false;$same=false;
    if($safe && is_array($cached)) {
        $view=$cached;
        $valid=!isset($view['CONF_CACHE_KEY']) || (is_string($version) && $view['CONF_CACHE_KEY']===$version.'-logger');
        unset($view['CONF_CACHE_KEY']);$same=$view===$disk;
    }
    $stable=$cached===$local->get('CONF-MAP-logger') && $version===$remote->get('CONF_CACHE_VERSION_KEY');
    $local->close();$remote->close();
    $configStable=$configBefore===privateConfigSnapshot($fs,$host);
    if ($warnings || !$configStable) throw new Exception('UNSTABLE_OR_DIAGNOSTIC_CACHE_READ');
    echo json_encode(array('status'=>'READONLY_CONFIG_CACHE_COMPARISON','only_two_named_keys'=>true,'no_values_or_hashes_exported'=>true,
      'local_logger_miss'=>$missing,'logger_value_arrays_only'=>$safe,'cached_version_valid'=>$valid,'cached_logger_equals_disk'=>$same,
      'configuration_stable_private_comparison'=>$configStable,'diagnostic_count'=>$warnings,'two_reads_stable'=>$stable,'post_worker_restart_disk_equivalence'=>$stable && $safe && ($missing || !$valid || $same),
      'existing_web_apc_logger_observed'=>false,'cache_writes'=>0));
} catch(Throwable $e) { echo json_encode(array('status'=>'CACHE_AUDIT_INCOMPLETE','error_class'=>get_class($e),'no_values_exported'=>true));exit(2); }
