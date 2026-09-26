// Executed with php -n, trusted/pinned configuration parser only, no bootstrap/cache writes.
set_include_path('/opt/kaltura/app/vendor/ZendFramework/library');
require '/opt/kaltura/app/infra/kEnvironment.php';
require '/opt/kaltura/app/alpha/config/cache/kFileSystemConf.php';
$fs=new kFileSystemConf();
$host=gethostname();$paths=$fs->getFileNames('logger',$host);$fs->orderMap($paths);
$map=$fs->loadByHostName('logger',$host);
if (!isset($map['api_v3'])) throw new Exception('API_LOGGER_MISSING');
$config=$map['api_v3'];$rows=array();$safe=true;
foreach (isset($config['writers'])?$config['writers']:array() as $writer) {
    $stream=isset($writer['stream'])?$writer['stream']:null;
    $local=is_string($stream) && preg_match('~^/opt/kaltura/log/[A-Za-z0-9_.-]+$~D',$stream);
    $kind=$local?'local-file':(in_array($stream,array('php://output','php://stderr'),true)?$stream:'UNREVIEWED');
    $name=isset($writer['name'])?$writer['name']:null;
    $valid=$name==='Zend_Log_Writer_Stream' && $kind!=='UNREVIEWED';
    $formatters=array();$filters=array();
    foreach (isset($writer['formatters'])?$writer['formatters']:array() as $formatter) {
        $f=isset($formatter['name'])?$formatter['name']:null;
        $ok=$f==='Zend_Log_Formatter_Simple';$valid=$valid && $ok;
        $format=isset($formatter['format'])?$formatter['format']:null;
        preg_match_all('/%([A-Za-z0-9_]+)%/',(string)$format,$fields);
        $formatters[]=array('known_simple'=>$ok,'placeholders'=>$fields[1],
            'has_message'=>in_array('message',$fields[1],true),'template_exported'=>false);
    }
    foreach (isset($writer['filters'])?$writer['filters']:array() as $filter) {
        $f=isset($filter['name'])?$filter['name']:null;
        $ok=in_array($f,array('Zend_Log_Filter_Priority','KalturaLogFilterType'),true);$valid=$valid && $ok;
        $filters[]=array('class'=>$ok?$f:'UNREVIEWED','priority'=>isset($filter['priority'])?(int)$filter['priority']:null,
            'operator_known'=>!isset($filter['operator']) || in_array($filter['operator'],array('<=','>=','<','>','==','='),true));
    }
    $rows[]=array('known_stream_writer'=>$name==='Zend_Log_Writer_Stream','core_factory_mapping'=>'KalturaSerializableStream',
        'sink_kind'=>$kind,'local_sink'=>$local?$stream:null,'formatters'=>$formatters,'filters'=>$filters,'reviewed_components'=>$valid);
    $safe=$safe && $valid;
}
$cacheMetadata=array();foreach(array('kLocalMemCacheConf','kRemoteMemCacheConf') as $mapName) {
 $cache=$fs->loadByHostName($mapName,$host);$cacheMetadata[$mapName]=array('nonempty'=>count($cache)>0,'keys'=>array_keys($cache));
}
$extras=array_keys(isset($config['eventItems'])?$config['eventItems']:array());
if(in_array('message',$extras,true))$safe=false;
// Keys only. Do not instantiate the real writers or dump private configuration.
$publicPaths=array();foreach($paths as $path)if(is_file($path))$publicPaths[]=$path;
echo json_encode(array('status'=>'DISK_LOGGER_RESOLUTION_ONLY_NOT_LIVE_CACHE_ATTESTATION','source_paths'=>$publicPaths,
    'cache_config_keys_only'=>$cacheMetadata,'writer_count'=>count($rows),'writers'=>$rows,'extras_keys'=>$extras,'unsafe_message_extra'=>in_array('message',$extras,true),
    'known_disk_components'=>$safe && count($rows)>0,'configuration_values_exported'=>false,'cache_read_or_write'=>false));
