<?php
// Actual held helper only; synthetic callbacks/wrappers, no backend or SOAP dispatch.
error_reporting(E_ALL);
$cases = array('default', 'custom-allow', 'custom-deny', 'custom-throw', 'nested',
    'custom-wrapper', 'foreign-mutation', 'non-lifo', 'invalid-token',
    'primary-exception-chain', 'idempotent-init', 'standalone');
if ($argc !== 2 || !in_array($argv[1], $cases, true) ||
    PHP_VERSION_ID < 80300 || PHP_VERSION_ID >= 80400) { exit(64); }
$case = $argv[1];
$diagnostics = array();
set_error_handler(function ($severity, $message, $file, $line) use (&$diagnostics) {
    $diagnostics[] = array('severity' => $severity, 'message' => $message,
        'file' => str_replace(__DIR__ . '/', '', $file), 'line' => $line);
    return false;
});
require __DIR__ . '/candidate/infra/general/kXmlEntityLoaderPolicy.php';
$initial = libxml_get_external_entity_loader();
$foreign = null;
$hits = 0;
if (in_array($case, array('custom-allow','custom-deny','custom-throw','standalone'), true)) {
    $foreign = function ($public, $system, $context) use (&$hits, $case) {
        ++$hits;
        if ($case === 'custom-throw') { throw new RuntimeException('SYNTHETIC_LOADER_FAILURE'); }
        if (($case === 'custom-allow' || $case === 'standalone') &&
            $system === 'file:///audit/probe/fixtures/marker.txt') {
            return fopen('/audit/probe/fixtures/marker.txt', 'rb');
        }
        return null;
    };
    libxml_set_external_entity_loader($foreign);
}
$previous = libxml_get_external_entity_loader();
$states = array();
function state($label) {
    global $states, $previous;
    $names = stream_get_wrappers();
    $loader = libxml_get_external_entity_loader();
    $error = null; $value = '';
    try {
        $xml = '<!DOCTYPE r [<!ENTITY e SYSTEM "file:///audit/probe/fixtures/marker.txt">]><r>&e;</r>';
        $dom = new DOMDocument();
        if ($dom->loadXML($xml, LIBXML_NOENT | LIBXML_NONET)) {
            $value = $dom->documentElement->textContent;
        }
    } catch (Throwable $failure) {
        $error = array('class' => get_class($failure), 'message' => $failure->getMessage());
    }
    $states[] = array('phase'=>$label,'prior_callback_active'=>$loader===$previous,
        'http'=>in_array('http',$names,true),'https'=>in_array('https',$names,true),
        'marker'=>$value==='SYNTHETIC_LIFECYCLE_MARKER','error'=>$error);
}
class XmlLifecycleCustomHttp {
    public $context;
    public static $hits = 0;
    public function stream_open($path, $mode, $options, &$opened_path) {
        ++self::$hits;
        return false; // A visible fixture miss, not a real HTTP transport.
    }
}
$error = null; $primary = null; $customHits = null;
try {
    if ($case !== 'standalone') {
        kXmlEntityLoaderPolicy::installDefaultDeny();
        foreach (array('http','https') as $scheme) {
            if (in_array($scheme, stream_get_wrappers(), true)) { stream_wrapper_unregister($scheme); }
        }
    }
    $deny = libxml_get_external_entity_loader();
    state('outside-before');
    if ($case === 'idempotent-init') {
        kXmlEntityLoaderPolicy::installDefaultDeny();
        if (libxml_get_external_entity_loader() !== $deny) { throw new LogicException('Init changed deny identity'); }
    }
    if ($case === 'custom-wrapper') {
        if (!stream_wrapper_register('http', 'XmlLifecycleCustomHttp')) { throw new RuntimeException('Custom wrapper failed'); }
    }
    $outer = kXmlEntityLoaderPolicy::beginSoapScope();
    state('outer');
    if ($case === 'nested' || $case === 'non-lifo') {
        $inner = kXmlEntityLoaderPolicy::beginSoapScope();
        state('inner');
        kXmlEntityLoaderPolicy::endSoapScope($case === 'non-lifo' ? $outer : $inner);
        state('after-inner');
    }
    if ($case === 'foreign-mutation' || $case === 'primary-exception-chain') {
        libxml_set_external_entity_loader(static function ($public, $system, $context) { return null; });
    }
    if ($case === 'primary-exception-chain') {
        $primary = new SoapFault('Client', 'SYNTHETIC_PRIMARY_SOAPFAULT');
    }
    kXmlEntityLoaderPolicy::endSoapScope($case === 'invalid-token' ? new stdClass() : $outer, $primary);
    if ($case === 'custom-wrapper') {
        fopen('http://synthetic-wrapper-control', 'rb');
        $customHits = XmlLifecycleCustomHttp::$hits;
    }
} catch (Throwable $failure) {
    $error = array('class'=>get_class($failure),'message'=>$failure->getMessage(),
        'previous_class'=>$failure->getPrevious() ? get_class($failure->getPrevious()) : null,
        'previous_message'=>$failure->getPrevious() ? $failure->getPrevious()->getMessage() : null);
}
state('outside-after');
echo json_encode(array('schema'=>1,'scope'=>'actual held helper only; not full application or real transport',
    'case'=>$case,'php'=>PHP_VERSION,'libxml'=>LIBXML_DOTTED_VERSION,
    'states'=>$states,'error'=>$error,'callback_hits'=>$hits,'custom_wrapper_hits'=>$customHits,
    'diagnostics'=>$diagnostics,'helper_sha256'=>hash_file('sha256',__DIR__.'/candidate/infra/general/kXmlEntityLoaderPolicy.php'),
    'probe_sha256'=>hash_file('sha256',__FILE__),'native_error_reporting'=>error_reporting(),
    'application_patch_selected'=>false), JSON_UNESCAPED_SLASHES | JSON_THROW_ON_ERROR), "\n";
