<?php
if(PHP_VERSION_ID < 80300 || PHP_VERSION_ID >= 80400)exit(64);
// Future isolated execution: actual full class, constructor bypass explicitly scoped.
error_reporting(E_ALL);
$path=$argv[1]??'';
if (!in_array($path,['/audit/probe/original.php','/audit/probe/public-comparison.php','/audit/probe/attribute-comparison.php'],true)) exit(64);
$diagnostics=[];
set_error_handler(function($s,$m,$f,$l)use(&$diagnostics){$diagnostics[]=[$s,$m,$f,$l];return false;});
require $path;
function state($object) {
 $class=new ReflectionClass($object);$properties=[];
 foreach((new ReflectionObject($object))->getProperties() as $p)$properties[]=[$p->getName(),$p->isPublic(),$p->isDefault()];
 return ['array'=>(array)$object,'public'=>get_object_vars($object),'exists'=>property_exists($object,'dispatcher'),
 'properties'=>$properties,'serialized'=>serialize($object),'class_attributes'=>array_map(function($a){return $a->getName();},$class->getAttributes())];
}
$r=new ReflectionClass('KalturaFrontController');$o=$r->newInstanceWithoutConstructor();$rows=[['fresh',state($o)]];
$o->dispatcher=(object)['marker'=>'safe-fixture'];$rows[]=['public-write',state($o)];
$copy=unserialize(serialize($o),['allowed_classes'=>['KalturaFrontController','stdClass']]);$rows[]=['round-trip',state($copy)];
unset($o->dispatcher);$rows[]=['unset',state($o)];$o->dispatcher=null;$rows[]=['recreate',state($o)];
$o->unrelatedFixtureProperty=1;$rows[]=['unrelated-property-control',state($o)];
// Real constructor; real helper takes its existing cached-request branch. No parser/HTTP claim.
foreach (['api_v3/lib/KalturaDispatcher.php','alpha/apps/kaltura/lib/requestUtils.class.php','alpha/apps/kaltura/lib/kCurrentContext.class.php'] as $dep) require '/audit/probe/source/'.$dep;
$cache=new ReflectionProperty('infraRequestUtils','requestParams');$cache->setAccessible(true);$cache->setValue(null,['service'=>'system','action'=>'ping']);
if(requestUtils::getRequestParams()!==['service'=>'system','action'=>'ping'])throw new RuntimeException('Real cached request contract failed');
$constructed=KalturaFrontController::getInstance();
$rows[]=['real-constructor-cached-request',state($constructed),$constructed->dispatcher===KalturaDispatcher::getInstance(),KalturaFrontController::getInstance()===$constructed];
// Explicit synthetic descendant only for inherited property policy, no replacement of real classes.
class DispatchRankFixtureChild extends KalturaFrontController {}
$child=(new ReflectionClass('DispatchRankFixtureChild'))->newInstanceWithoutConstructor();
$child->descendantFixtureProperty=1;$rows[]=['descendant-property-policy',state($child)];
$controlClass=new ReflectionClass('KalturaDispatcher');
if($controlClass->hasMethod('__set') || $controlClass->getAttributes('AllowDynamicProperties'))throw new RuntimeException('Invalid unrelated-class control');
$unrelated=KalturaDispatcher::getInstance();$unrelated->unrelatedDiagnosticControl=1;
$controlWarnings=array_filter($diagnostics,function($d){return $d[0]===E_DEPRECATED && strpos($d[1],'KalturaDispatcher::$unrelatedDiagnosticControl')!==false;});
if(count($controlWarnings)!==1)throw new RuntimeException('Unrelated warning missing or duplicated');
$rows[]=['unrelated-class-warning-control',get_class($unrelated)];
echo json_encode(['constructor_executed'=>true,'request_parser_exercised'=>false,'source_sha256'=>hash_file('sha256',$path),'rows'=>$rows,'diagnostics'=>$diagnostics],JSON_THROW_ON_ERROR)."\n";
