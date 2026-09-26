<?php
// Actual kConf/kSoapClient; only __doRequest is a synthetic transport seam.
$cases = array('bootstrap','construct-good','construct-malformed','construct-missing',
    'explicit-ok','magic-ok','explicit-fault','callback-existing',
    'nested-construct','nested-call-ok','nested-call-fault');
if ($argc !== 3 || !in_array($argv[1], array('original','exp11'), true)
    || !in_array($argv[2], $cases, true)) { exit(64); }
if (!((PHP_VERSION_ID>=70400 && PHP_VERSION_ID<70500)
    || (PHP_VERSION_ID>=80300 && PHP_VERSION_ID<80400))) { exit(64); }
foreach (array('soap','dom','libxml') as $ext) { if (!extension_loaded($ext)) { exit(65); } }
$variant=$argv[1]; $case=$argv[2]; $root=__DIR__.'/'.$variant;
$phase='initial';$diagnostics=array();$events=array();$resolverEvents=array();
$transportEvents=array();$nestedResults=array();$transportDepth=0;$nestedResolverActive=false;
set_error_handler(function($severity,$message,$file,$line) use (&$diagnostics,&$phase) {
    $diagnostics[]=array('phase'=>$phase,'severity'=>$severity,'message'=>$message,
        'file'=>str_replace(__DIR__.'/', '', $file),'line'=>$line);
    return false;
});
function wrappers() {
    $list=stream_get_wrappers();sort($list);
    return array('http'=>in_array('http',$list,true),'https'=>in_array('https',$list,true),'all'=>$list);
}
function captureState($label) {
    global $phase,$events,$resolver;
    $previousPhase=$phase; $phase='observer:'.$label;
    try {
    $before=wrappers();
    $xml='<!DOCTYPE r [<!ENTITY e SYSTEM "file:///audit/probe/fixtures/marker.txt">]><r>&e;</r>';
    $d=new DOMDocument();$ok=$d->loadXML($xml,LIBXML_NOENT|LIBXML_NONET);
    $value=$ok ? $d->documentElement->textContent : '';
    $loaderKnown=function_exists('libxml_get_external_entity_loader');
    $events[]=array('phase'=>$label,'wrappers'=>$before,'marker_seen'=>$value==='SYNTHETIC_LIFECYCLE_MARKER',
        'parse_return'=>$ok,'value'=>$value,'callback_identity_available'=>$loaderKnown,
        'callback_same'=>$loaderKnown ? libxml_get_external_entity_loader()===$resolver : null);
    } finally { $phase=$previousPhase; }
}
function normalizeException($e) { return array('class'=>get_class($e),'message'=>$e->getMessage()); }
$options=array('cache_wsdl'=>WSDL_CACHE_NONE,'exceptions'=>true,'trace'=>true);
$resolver=null;
// Callback simulates an existing external loader, never forwards arbitrary identifiers.
if ($case==='callback-existing' || $case==='nested-construct') {
    $resolver=function($public,$system,$context) use (&$resolverEvents,&$nestedResolverActive,&$nestedResults,$case,$options) {
        global $phase;
        $resolverEvents[]=array('phase'=>$phase,'public'=>$public,'system'=>$system,'wrappers'=>wrappers());
        $allowed=array('file:///audit/probe/fixtures/good.wsdl','file:///audit/probe/fixtures/inner.wsdl',
            'file:///audit/probe/fixtures/types.xsd','file:///audit/probe/fixtures/marker.txt');
        $paths=array_map(function($uri) { return substr($uri,7); },$allowed);
        if (!in_array($system,$allowed,true) && !in_array($system,$paths,true)) { return null; }
        if ($case==='nested-construct' && !$nestedResolverActive
            && in_array($system,array('file:///audit/probe/fixtures/good.wsdl','/audit/probe/fixtures/good.wsdl'),true)) {
            $nestedResolverActive=true; $previousPhase=$phase; $phase='nested-resolver:construct';
            try {
                $inner=new kSoapClient('file:///audit/probe/fixtures/inner.wsdl',$options);
                $nestedResults[]=array('site'=>'resolver-inner','functions'=>$inner->__getFunctions(),'exception'=>null,'wrappers_after'=>wrappers());
            } catch(Throwable $e) {
                $nestedResults[]=array('site'=>'resolver-inner','exception'=>normalizeException($e),'wrappers_after'=>wrappers());
            } finally { $phase=$previousPhase; }
        }
        return fopen($system,'rb');
    };
    if (libxml_set_external_entity_loader($resolver)!==true) { throw new RuntimeException('Resolver install failed'); }
}
captureState('before-kConf');
$phase='load-kConf';
require $root.'/alpha/config/kConf.php';
require $root.'/infra/general/kSoapClient.php';
$environment=kConf::getEnvMap(); // Actual environment map only; no DB/cache access.
captureState('after-kConf');
class SyntheticTransportSoap extends kSoapClient {
    public function __doRequest($request,$location,$action,$version,$one_way=0): ?string {
        global $transportEvents,$transportDepth,$case,$options,$nestedResults;
        $transportEvents[]=array('depth'=>$transportDepth,'location'=>$location,'action'=>$action,
            'version'=>$version,'request_sha256'=>hash('sha256',$request),'wrappers'=>wrappers());
        captureState('transport-enter-'.$transportDepth);
        if ($transportDepth===0 && ($case==='nested-call-ok' || $case==='nested-call-fault')) {
            ++$transportDepth;
            try {
                $inner=new SyntheticTransportSoap('file:///audit/probe/fixtures/inner.wsdl',$options);
                $result=$inner->__soapCall($case==='nested-call-fault' ? 'notInFixture' : 'ping',array(array('value'=>'INNER')));
                $nestedResults[]=array('site'=>'transport-inner','value'=>$result,'exception'=>null);
            } catch(Throwable $e) { $nestedResults[]=array('site'=>'transport-inner','exception'=>normalizeException($e)); }
            --$transportDepth;captureState('transport-after-inner');
        }
        $response=file_get_contents(__DIR__.'/fixtures/response.xml');
        if (!is_string($response)) { throw new RuntimeException('Missing synthetic response'); }
        return $response;
    }
}
$result=null;$exception=null;$functions=array();
$phase='operation:construct';
try {
    if ($case!=='bootstrap') {
        $wsdl=$case==='construct-malformed' ? 'malformed.wsdl' : ($case==='construct-missing' ? 'missing.wsdl' : 'good.wsdl');
        $client=new SyntheticTransportSoap('file:///audit/probe/fixtures/'.$wsdl,$options);
        $functions=$client->__getFunctions();captureState('after-constructor');
        if (in_array($case,array('explicit-ok','explicit-fault','nested-call-ok','nested-call-fault'),true)) {
            $phase='operation:explicit-call';
            $result=$client->__soapCall($case==='explicit-fault' ? 'notInFixture' : 'ping',array(array('value'=>'OUTER')));
        } elseif ($case==='magic-ok') {
            $phase='operation:magic-call';$result=$client->ping(array('value'=>'OUTER'));
        }
    }
} catch(Throwable $e) { $exception=normalizeException($e); }
captureState('after-operation');
$loaded=array();
foreach(get_included_files() as $p) {
    if (strpos($p,$root.'/')===0) { $loaded[substr($p,strlen($root)+1)]=hash_file('sha256',$p); }
}
ksort($loaded);
echo json_encode(array('schema'=>1,'runtime'=>array('php'=>PHP_VERSION,'php_id'=>PHP_VERSION_ID,
    'libxml'=>LIBXML_DOTTED_VERSION,'modules'=>get_loaded_extensions(),'error_reporting'=>error_reporting()),
    'variant'=>$variant,'case'=>$case,'classes'=>array('config'=>get_parent_class('kConf'),
    'soap'=>get_parent_class('kSoapClient'),'transport'=>get_parent_class('SyntheticTransportSoap')),
    'environment_keys'=>array_keys($environment),'events'=>$events,'result'=>$result,'exception'=>$exception,
    'functions'=>$functions,'diagnostics'=>$diagnostics,'resolver_events'=>$resolverEvents,
    'transport_events'=>$transportEvents,'nested_results'=>$nestedResults,'loaded'=>$loaded,
    'probe_sha256'=>hash_file('sha256',__FILE__),'real_transport_coverage'=>false,
    'full_application_bootstrap'=>false,'application_patch_selected'=>false),JSON_UNESCAPED_SLASHES|JSON_THROW_ON_ERROR),"\n";
