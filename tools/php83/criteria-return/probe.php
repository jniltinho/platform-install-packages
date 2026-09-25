<?php
// Real Criteria/Criterion/Iterator; only the DB lookup boundary is stubbed.
error_reporting(E_ALL);
$diagnostics=[];
set_error_handler(function($severity,$message,$file,$line) use (&$diagnostics) {
    $diagnostics[]=[$severity,$message,basename($file),$line];
    return true;
});
class DBAdapter {}
class Propel { public static function getDB($name) { return new DBAdapter(); } }
require $argv[1];
require '/audit/app/alpha/apps/kaltura/lib/myCriteria.class.php';
require '/audit/app/alpha/apps/kaltura/lib/model/objectfilters/IKalturaDbQuery.php';
require '/audit/app/alpha/apps/kaltura/lib/model/objectfilters/KalturaCriteria.php';
$loadDiagnostics=$diagnostics;$diagnostics=[];
function check($actual,$expected,$label) {
    if ($actual!==$expected) throw new RuntimeException($label);
}
function item($criterion) {
    if ($criterion===null) return null;
    return [get_class($criterion),$criterion->getTable(),$criterion->getColumn(),$criterion->getValue(),$criterion->getComparison()];
}
function drain($iterator) {
    $rows=[];
    while ($iterator->valid()) {
        if (count($rows)>20) throw new RuntimeException('Unbounded iterator');
        $rows[]=[$iterator->key(),item($iterator->current()),$iterator->next()];
    }
    return $rows;
}
function populated($class='Criteria') {
    $c=new $class('fixture');$c->add('a.id',1,Criteria::EQUAL);$c->add('a.name','test',Criteria::NOT_EQUAL);return $c;
}
$rows=[];
$c=new Criteria('fixture');$it=$c->getIterator();
check($it instanceof Traversable,true,'Traversable contract');check($it->valid(),false,'empty validity');
$rows[]=['empty',get_class($it),$it->rewind(),drain($it)];
foreach (['Criteria','myCriteria','KalturaCriteria'] as $class) {
    $c=populated($class);$it=$c->getIterator();
    check($it->current()===$c->getCriterion('a.id'),true,'actual object identity');
    check($it->rewind(),null,'rewind void');$items=drain($it);
    check(array_column($items,0),['a.id','a.name'],'ordered keys');
    check(array_column($items,2),[null,null],'next void');
    check($items[0][1],['Criterion','a','id',1,Criteria::EQUAL],'criterion payload');
    $rows[]=['ordered',$class,$items];
}
$c=populated();$one=$c->getIterator();$two=$c->getIterator();$one->next();
check($two->key(),'a.id','independent cursor');
$rows[]=['independent',drain($one),drain($two)];
$c=populated();$it=$c->getIterator();$c->add('a.extra',3);
$old=drain($it);$new=drain($c->getIterator());
check(array_column($old,0),['a.id','a.name'],'key snapshot');check(count($new),3,'new snapshot');
$rows[]=['append-snapshot',$old,$new];
$c=populated();$it=$c->getIterator();$c->add('a.id',99,Criteria::GREATER_THAN);
check($it->current()->getValue(),99,'live replacement');$rows[]=['replace-live',drain($it)];
$c=populated();$it=$c->getIterator();check($c->remove('a.id'),1,'remove value');
check($it->valid(),true,'removed snapshot key still valid');check($it->current(),null,'removed snapshot value');
$rows[]=['remove-snapshot',drain($it),$c->keys()];
$c=populated();$it=$c->getIterator();$it->next();$clone=clone $it;
check($clone->key(),'a.name','clone position');$c->add('a.name','changed');
$rows[]=['clone-mid',drain($it),drain($clone)];
$c=populated();$it=$c->getIterator();$it->next();$payload=serialize($it);$restored=unserialize($payload);
check(serialize($restored),$payload,'serialization byte roundtrip');check($restored->key(),'a.name','restored position');
$rows[]=['serialize-mid',hash('sha256',$payload),drain($it),drain($restored)];
$c=populated();$it=$c->getIterator();drain($it);$it->rewind();
$rows[]=['rewind-after-end',drain($it)];
$realtable=new ReflectionProperty('Criterion','realtable');$realtable->setAccessible(true);
foreach ([['missing',false,null,'a'],['null',true,null,'a'],['empty',true,'','a'],['table',true,'partner','partner'],['zero',true,'0','0']] as $case) {
    $c=new Criteria('fixture');if ($case[1])$c->addAlias('a',$case[2]);$c->add('a.id',123);
    $value=$realtable->getValue($c->getCriterion('a.id'));check($value,$case[3],'prior alias guard');
    $rows[]=['alias',$case[0],$value,drain($c->getIterator())];
}
check($diagnostics,[],'unexpected valid-operation diagnostics');
// Intentionally invalid access is measured separately, not erased or treated as clean.
$invalid=[];
foreach (['empty','exhausted'] as $label) {
    $c=$label==='empty'?new Criteria('fixture'):populated();$it=$c->getIterator();drain($it);
    $diagnostics=[];$value=[$it->key(),item($it->current())];
    check($value,[null,null],'invalid access legacy value');check(count($diagnostics),2,'invalid access warning control');
    $invalid[]=[$label,$value,$diagnostics];
}
$contracts=[];
foreach (['Criteria'=>['getIterator'],'CriterionIterator'=>['rewind','valid','key','current','next']] as $class=>$methods) {
    foreach ($methods as $method) {
        $r=new ReflectionMethod($class,$method);$contracts[$class.'::'.$method]=$r->hasReturnType()?(string)$r->getReturnType():null;
    }
}
echo json_encode(['php'=>PHP_VERSION,'rows'=>$rows,'contracts'=>$contracts,'load_diagnostics'=>$loadDiagnostics,'invalid_controls'=>$invalid],JSON_THROW_ON_ERROR|JSON_PRETTY_PRINT),"\n";
