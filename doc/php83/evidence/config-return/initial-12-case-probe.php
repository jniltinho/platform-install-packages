<?php
// Synthetic, network-denied fixture; never load production configuration.
error_reporting(E_ALL);
$warnings = [];
set_error_handler(function ($severity, $message, $file, $line) use (&$warnings) {
    $warnings[] = [$severity, $message, $file, $line];
    return true; // Captured in the report, not ignored or classified as success.
});
set_include_path('/audit/app/vendor/ZendFramework/library');
require_once 'Zend/Config.php';
require_once 'Zend/Config/Ini.php';
require_once 'Zend/Config/Xml.php';
require_once '/audit/app/batch/scheduler/KSchedulerConfig.class.php';
require_once '/audit/app/batch/scheduler/KSchedularTaskConfig.class.php';
function expectValue($actual, $expected, $label) {
    if ($actual !== $expected) throw new RuntimeException($label);
}
function plain($value) {
    if ($value instanceof Zend_Config) return ['config', $value->toArray()];
    return [gettype($value), $value];
}
function walkConfig($config) {
    $result = ['rewind' => $config->rewind(), 'count' => $config->count(), 'builtin_count' => count($config), 'items' => []];
    for ($i = 0; $config->valid() && $i < 20; $i++) {
        $result['items'][] = [$config->key(), plain($config->current()), $config->next()];
    }
    if ($i === 20) throw new RuntimeException('Unbounded iteration');
    $result['end'] = [$config->valid(), $config->key(), plain($config->current()), $config->next()];
    return $result;
}
$rows = [];
foreach (['empty'=>[], 'values'=>['null'=>null,'false'=>false,'zero'=>0,'str'=>'0','nested'=>['leaf'=>17]], 'keys'=>[7=>'seven','08'=>'eight',-1=>'minus']] as $label=>$data) {
    $c = new Zend_Config($data, true);
    expectValue(count($c), count($data), 'constructor count');
    expectValue($c->toArray(), $data, 'constructor roundtrip');
    $walk = walkConfig($c);
    expectValue(count($walk['items']), count($data), 'iterator count');
    expectValue($walk['rewind'], null, 'void rewind');
    foreach ($walk['items'] as $item) expectValue($item[2], null, 'void next');
    expectValue($walk['end'], [false, null, ['boolean', false], null], 'end state');
    $rows[] = [$label, $walk, $c->toArray()];
}
$c = new Zend_Config(['a'=>1,'b'=>2,'c'=>3], true);
$c->rewind(); unset($c->a); $skip = $c->next();
expectValue($c->key(), 'b', 'unset skip branch');
$c->d = 4; $c->b = 20;
expectValue(count($c), 3, 'mutation count');
$rows[] = ['mutation', $skip, walkConfig($c), $c->toArray()];
$c = new Zend_Config(['nested'=>['a'=>1],'x'=>2], true);
$merged = $c->merge(new Zend_Config(['nested'=>['b'=>3],'y'=>4]));
expectValue($merged === $c, true, 'merge identity');
expectValue($c->toArray(), ['nested'=>['a'=>1,'b'=>3],'x'=>2,'y'=>4], 'merge result');
$clone = clone $c; $clone->nested->a = 99;
expectValue($c->nested->a, 1, 'clone isolation');
$payload = serialize($c); $restored = unserialize($payload);
expectValue($restored->toArray(), $c->toArray(), 'serialize values');
expectValue(serialize($restored), $payload, 'serialize byte roundtrip');
$rows[] = ['merge-clone-serialize', walkConfig($restored), hash('sha256',$payload), $clone->toArray()];
$c->setReadOnly();
foreach (['set','unset','nested-set'] as $op) {
    try {
        if ($op==='set') $c->x=8;
        elseif ($op==='unset') unset($c->x);
        else $c->nested->a=8;
        throw new RuntimeException('Read-only operation accepted');
    } catch (Zend_Config_Exception $e) { $rows[]=['read-only',$op,get_class($e),$e->getMessage()]; }
}
$ini = tempnam(sys_get_temp_dir(), 'config-return-');
file_put_contents($ini, "[base]\nx = 1\nnested.a = first\n[child : base]\nx = 2\nnested.b = second\n");
try {
    $c = new Zend_Config_Ini($ini, 'child', true);
    expectValue($c->toArray(), ['x'=>'2','nested'=>['a'=>'first','b'=>'second']], 'INI inheritance');
    $rows[]=['ini',walkConfig($c),$c->toArray(),$c->getSectionName()];
} finally { unlink($ini); }
$c = new Zend_Config_Xml('<?xml version="1.0"?><config><base><x>1</x></base><child extends="base"><y>2</y></child></config>', 'child', true);
expectValue($c->toArray(), ['x'=>'1','y'=>'2'], 'XML inheritance');
$rows[]=['xml',walkConfig($c),$c->toArray(),$c->getSectionName()];
foreach (['KSchedulerConfig','KSchedularTaskConfig'] as $class) {
    // Constructors perform external orchestration; test inherited storage/iteration only.
    $r=new ReflectionClass($class);$c=$r->newInstanceWithoutConstructor();
    (new ReflectionMethod('Zend_Config','__construct'))->invoke($c,['task'=>['enabled'=>true]],true);
    foreach (['count','current','key','next','rewind','valid'] as $method) expectValue((new ReflectionMethod($class,$method))->getDeclaringClass()->getName(),'Zend_Config','inherited method');
    expectValue(count($c),1,'scheduler inherited count');
    $rows[]=['inherited',$class,walkConfig($c)];
}
$contracts=[];
foreach (['count','current','key','next','rewind','valid'] as $method) {
    $r=new ReflectionMethod('Zend_Config',$method);$contracts[$method]=$r->hasReturnType()?(string)$r->getReturnType():null;
}
echo json_encode(['php'=>PHP_VERSION,'rows'=>$rows,'contracts'=>$contracts,'warnings'=>$warnings],JSON_THROW_ON_ERROR|JSON_PRETTY_PRINT),"\n";
