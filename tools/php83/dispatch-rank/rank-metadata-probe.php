<?php
if(PHP_VERSION_ID < 80300 || PHP_VERSION_ID >= 80400)exit(64);
// Actual complete service hierarchy; no method-body or database success claim.
error_reporting(E_ALL);
$diagnostics=[];
set_error_handler(function($s,$m,$f,$l)use(&$diagnostics){$diagnostics[]=[$s,$m,$f,$l];return false;});
require '/audit/probe/source/api_v3/lib/KalturaBaseService.php';
require '/audit/probe/source/api_v3/lib/KalturaEntryService.php';
$r=new ReflectionMethod('KalturaEntryService','anonymousRankEntry');$r->setAccessible(true);
$params=[];
foreach($r->getParameters() as $p){
 $row=[$p->getName(),$p->isOptional(),$p->isDefaultValueAvailable(),$p->allowsNull(),(string)$p->getType()];
 try{$row[]=['default',$p->getDefaultValue()];}catch(ReflectionException $e){$row[]=['unavailable',get_class($e)];}
 $params[]=$row;
}
$failed=false;
$o=(new ReflectionClass('KalturaEntryService'))->newInstanceWithoutConstructor();$calls=[];
$cases=[[],['safe-id'],['safe-id',null]];
if(PHP_VERSION_ID>=80000){$cases[]=['entryId'=>'safe-id','rank'=>3];$cases[]=['rank'=>3];}
foreach($cases as $args){
 try{$value=$r->invokeArgs($o,$args);$calls[]=[$args,'unexpected-return',$value];$failed=true;}
 catch(Throwable $e){$calls[]=[$args,get_class($e),$e->getMessage()];if(!($e instanceof ArgumentCountError))$failed=true;}
}
echo json_encode(['parameters'=>$params,'required'=>$r->getNumberOfRequiredParameters(),'calls'=>$calls,'diagnostics'=>$diagnostics,'rank_body_success_exercised'=>false,'rank_patch_created'=>false,'missing_binding_contract_ok'=>!$failed],JSON_THROW_ON_ERROR)."\n";

if($failed)exit(2);
