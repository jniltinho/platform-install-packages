<?php
// Synthetic native parser policy experiment. No Kaltura/application source loaded.
if ($argc !== 3 || !in_array($argv[1], array('enabled', 'legacy', 'default', 'deny'), true)
    || !in_array($argv[2], array('dom', 'simplexml', 'xmlreader'), true)) {
    fwrite(STDERR, "Invalid experiment arguments\n"); exit(64);
}
if (!((PHP_VERSION_ID >= 70400 && PHP_VERSION_ID < 70500)
    || (PHP_VERSION_ID >= 80300 && PHP_VERSION_ID < 80400))) {
    fwrite(STDERR, "Wrong runtime family\n"); exit(64);
}
foreach (array('libxml', 'dom', 'SimpleXML', 'xmlreader') as $extension) {
    if (!extension_loaded($extension)) { fwrite(STDERR, "Missing XML extension\n"); exit(65); }
}
$policy = $argv[1]; $parser = $argv[2]; $errors = array(); $loaderCalls = array();
set_error_handler(function ($severity, $message, $file, $line) use (&$errors) {
    $errors[] = array('severity'=>$severity, 'message'=>$message,
        'file'=>basename($file), 'line'=>$line);
    return false; // Retain native stderr; do not swallow warnings/deprecations.
});
class FixtureXmlStream {
    public $context;
    private $position = 0;
    public static $events = array();
    private static $value = "SYNTHETIC_XML_ENTITY_MARKER\n";
    public function stream_open($path, $mode, $options, &$opened_path) {
        self::$events[] = array('operation'=>'open', 'path'=>$path);
        return $path === 'xfixture://marker' && $mode === 'rb';
    }
    public function stream_read($count) {
        $s = substr(self::$value, $this->position, $count);
        $this->position += strlen($s); return $s;
    }
    public function stream_eof() { return $this->position >= strlen(self::$value); }
    public function stream_stat() { return array('mode'=>0100444,'size'=>strlen(self::$value)); }
    public function url_stat($path, $flags) {
        self::$events[] = array('operation'=>'stat','path'=>$path);
        return $path === 'xfixture://marker' ? array('mode'=>0100444,'size'=>strlen(self::$value)) : false;
    }
    public function stream_close() {}
}
if (!stream_wrapper_register('xfixture', 'FixtureXmlStream')) { exit(66); }
$policyResult = null;
if ($policy === 'enabled') { $policyResult = libxml_disable_entity_loader(false); }
if ($policy === 'legacy') { $policyResult = libxml_disable_entity_loader(true); }
if ($policy === 'deny') {
    $policyResult = libxml_set_external_entity_loader(function ($public, $system, $context) use (&$loaderCalls) {
        $loaderCalls[] = array('public'=>$public, 'system'=>$system);
        return null;
    });
    if ($policyResult !== true) { throw new RuntimeException('Deny loader registration failed'); }
}
$policyErrors = $errors; $errors = array();
$flags = array('zero'=>0, 'noent'=>LIBXML_NOENT, 'dtdload'=>LIBXML_DTDLOAD,
    'dtdvalid'=>LIBXML_DTDVALID, 'nonet'=>LIBXML_NONET,
    'noent_dtdload'=>LIBXML_NOENT|LIBXML_DTDLOAD,
    'noent_dtdload_nonet'=>LIBXML_NOENT|LIBXML_DTDLOAD|LIBXML_NONET);
$documents = array(
    'plain'=>'<r>PLAIN</r>',
    'internal'=>'<!DOCTYPE r [<!ENTITY x "INTERNAL">]><r>&x;</r>',
    'malformed'=>'<r><broken></r>',
    'file'=>'<!DOCTYPE r [<!ENTITY x SYSTEM "file:///audit/probe/marker.txt">]><r>&x;</r>',
    'wrapper'=>'<!DOCTYPE r [<!ENTITY x SYSTEM "xfixture://marker">]><r>&x;</r>',
    'dtd'=>'<!DOCTYPE r SYSTEM "file:///audit/probe/marker.dtd"><r>&x;</r>'
);
$records = array();
foreach ($documents as $name=>$xml) {
    foreach ($flags as $flag=>$options) {
        $errors = array(); $loaderCalls = array(); FixtureXmlStream::$events = array();
        $ok = false; $value = ''; $exception = null;
        try {
            if ($parser === 'dom') {
                $d = new DOMDocument(); $ok = $d->loadXML($xml, $options);
                if ($ok) { $value = $d->documentElement->textContent; }
            } elseif ($parser === 'simplexml') {
                $d = simplexml_load_string($xml, 'SimpleXMLElement', $options);
                $ok = $d !== false; if ($ok) { $value = (string)$d; }
            } else {
                $d = new XMLReader(); $ok = $d->XML($xml, null, $options);
                if ($ok) {
                    while ($d->read()) {
                        if (in_array($d->nodeType, array(XMLReader::TEXT, XMLReader::CDATA,
                            XMLReader::WHITESPACE, XMLReader::SIGNIFICANT_WHITESPACE), true)) {
                            $value .= $d->value;
                        }
                    }
                    // read() false means both EOF and failure. Preserve parser errors; no success inference.
                    $d->close();
                }
            }
        } catch (Throwable $e) {
            $exception = array('class'=>get_class($e), 'message'=>$e->getMessage());
        }
        $records[] = array('document'=>$name, 'flag'=>$flag, 'options'=>$options,
            'initial_parse_return'=>$ok, 'value'=>$value,
            'marker_seen'=>strpos($value, 'SYNTHETIC_XML_ENTITY_MARKER') !== false,
            'internal_seen'=>strpos($value, 'INTERNAL') !== false,
            'exception'=>$exception, 'diagnostics'=>$errors,
            'loader_calls'=>$loaderCalls, 'wrapper_events'=>FixtureXmlStream::$events);
    }
}
echo json_encode(array('schema'=>1, 'policy'=>$policy, 'parser'=>$parser,
    'runtime'=>array('php'=>PHP_VERSION,'php_id'=>PHP_VERSION_ID,
        'libxml'=>LIBXML_DOTTED_VERSION,'libxml_loaded'=>defined('LIBXML_LOADED_VERSION') ? LIBXML_LOADED_VERSION : null,
        'extensions'=>get_loaded_extensions(),'error_reporting'=>error_reporting(),
        'internal_errors'=>libxml_use_internal_errors(),'no_xxe_available'=>defined('LIBXML_NO_XXE')),
    'source'=>array('probe'=>hash_file('sha256',__FILE__),
        'marker'=>hash_file('sha256',__DIR__.'/marker.txt'),'dtd'=>hash_file('sha256',__DIR__.'/marker.dtd')),
    'policy_return'=>$policyResult, 'policy_diagnostics'=>$policyErrors,
    'records'=>$records,'application_coverage'=>false), JSON_UNESCAPED_SLASHES|JSON_THROW_ON_ERROR), "\n";
