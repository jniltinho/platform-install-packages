<?php
// Three actual standalone classes, each process isolated; never whole-app bootstrap.
error_reporting(E_ALL);
ini_set('display_errors', 'stderr');
$label = $argv[1] ?? '';
$paths = array(
 'google-old' => 'vendor/google-api-php-client/src/service/Google_Utils.php',
 'google-new' => 'vendor/google-api-php-client-1.1.2/src/Google/Utils.php',
 'purifier' => 'vendor/htmlpurifier/library/HTMLPurifier/Encoder.php'
);
if (!isset($paths[$label]) || PHP_VERSION_ID < 70400 || PHP_VERSION_ID >= 80400) {
 throw new RuntimeException('Unsupported class/runtime');
}
$readOnlySource = false;
foreach (file('/proc/self/mountinfo') as $mount) {
 $fields = explode(' ', trim($mount));
 if (isset($fields[5]) && $fields[4] === '/audit/source' && in_array('ro', explode(',', $fields[5]), true)) $readOnlySource = true;
}
if (!$readOnlySource) throw new RuntimeException('Source bind must be read-only');
$phase = 'load'; $diagnostics = array(); $rows = array();
set_error_handler(function($code, $message, $file, $line) use (&$diagnostics, &$phase) {
 $diagnostics[] = array('phase'=>$phase, 'severity'=>$code, 'file'=>basename($file), 'line'=>$line,
  'category'=>strpos($message, 'Uninitialized string offset')!==false ? 'uninitialized-string-offset' : (strpos($message, 'curly braces is deprecated')!==false ? 'curly-offset-deprecated' : 'other'),
  'message_sha256'=>hash('sha256', $message));
 return false; // Record, do not suppress PHP diagnostics.
});
require '/audit/source/'.$paths[$label];
$loadDiagnostics = $diagnostics; $diagnostics = array();
function recordCase($name, $call, $expected, $warningCount=0) {
 global $phase, $diagnostics, $rows;
 $phase=$name; $diagnostics=array();
 $value=$call();
 if ($value !== $expected) throw new RuntimeException('Case result mismatch: '.$name);
 if (count($diagnostics)!==$warningCount) throw new RuntimeException('Case diagnostic count mismatch: '.$name);
 foreach ($diagnostics as $d) {
  if ($d['category']!=='uninitialized-string-offset' || $d['severity']!==(PHP_VERSION_ID<80000 ? E_NOTICE : E_WARNING)) {
   throw new RuntimeException('Unexpected case diagnostic: '.$name);
  }
 }
 $rows[]=array('case'=>$name,'value'=>$value,'diagnostics'=>$diagnostics);
}
if ($label==='google-old' || $label==='google-new') {
 foreach (array(array('empty','',0,0),array('ascii','abc',3,0),array('nul',"A\0B",3,0),array('binary',"\xff\0",2,0),array('two-byte',"\xc3\xa9",3,1),array('four-byte',"\xf0\x9f\x98\x80",7,3),array('mixed',"A\xc3\xa9B",5,1)) as $r) {
  recordCase('length-'.$r[0], function() use($r) {return Google_Utils::getStrLen($r[1]);}, $r[2], $r[3]);
 }
 foreach (array(array('empty','',''),array('ascii','foo','Zm9v'),array('unicode',"\xc3\xa9",'w6k'),array('binary',"\0\xff",'AP8')) as $r) {
  recordCase('base64-encode-'.$r[0],function()use($r){return Google_Utils::urlSafeB64Encode($r[1]);},$r[2]);
  recordCase('base64-decode-'.$r[0],function()use($r){return bin2hex(Google_Utils::urlSafeB64Decode($r[2]));},bin2hex($r[1]));
 }
 recordCase('normalize-map',function(){return Google_Utils::normalize(array('HELLO'=>1,'World'=>null,'hello'=>2));},array('hello'=>2,'world'=>null));
 recordCase('normalize-nonarray',function(){return Google_Utils::normalize('x');},array());
} else {
 foreach (array(array('empty','',''),array('ascii','abc','abc'),array('unicode',"\xc3\xa9\xf0\x9f\x98\x80","\xc3\xa9\xf0\x9f\x98\x80"),array('nul-ascii',"\0A",'A'),array('invalid-lead',"\xffB",'B'),array('stray-continuation',"\x80A",'A'),array('overlong',"\xc0\xaf",''),array('truncated',"\xe2\x82",''),array('surrogate',"\xed\xa0\x80",''),array('unicode-control',"\xc2\x80",''),array('allowed-control',"\t\n\r","\t\n\r"),array('nul-unicode',"\0\xc3\xa9\xf0\x9f\x98\x80","\xc3\xa9\xf0\x9f\x98\x80")) as $r) {
  recordCase('clean-'.$r[0],function()use($r){return bin2hex(HTMLPurifier_Encoder::cleanUTF8($r[1]));},bin2hex($r[2]));
 }
 foreach (array(array(-1,''),array(0,'00'),array(65,'41'),array(127,'7f'),array(128,'c280'),array(233,'c3a9'),array(2047,'dfbf'),array(2048,'e0a080'),array(55296,''),array(128512,'f09f9880'),array(1114111,'f48fbfbf'),array(1114112,'')) as $r) {
  recordCase('unichr-'.$r[0],function()use($r){return bin2hex(HTMLPurifier_Encoder::unichr($r[0]));},$r[1]);
 }
 recordCase('ascii-entities',function(){return HTMLPurifier_Encoder::convertToASCIIDumbLossless("A\xc3\xa9\xf0\x9f\x98\x80");},'A&#233;&#128512;');
}
// Native square-offset controls are fixture-only, not coverage of all 43 files.
recordCase('native-array-types',function(){ $a=array(0=>'zero','name'=>false,-1=>null); return array($a['0'],$a['name'],$a[-1],isset($a['missing'])); },array('zero',false,null,false));
recordCase('native-string-bytes',function(){ $s="A\0\xff"; return array(bin2hex($s[0]),bin2hex($s[1]),bin2hex($s[-1])); },array('41','00','ff'));
recordCase('native-string-overread',function(){ $s='A'; return $s[2]; },'',1);
$class=$label==='purifier'?'HTMLPurifier_Encoder':'Google_Utils';
$file=(new ReflectionClass($class))->getFileName();
if ($file!=='/audit/source/'.$paths[$label]) throw new RuntimeException('Unexpected loaded class source');
echo json_encode(array('case'=>$label,'php'=>PHP_VERSION,'source_path'=>$paths[$label], 'source_sha256'=>hash_file('sha256',$file),'load_diagnostics'=>$loadDiagnostics,'rows'=>$rows)),"\n";
