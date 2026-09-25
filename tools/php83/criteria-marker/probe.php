<?php
// Actual full original Criteria/criterion iterator + actual criteriaFilter.
// DBAdapter and Propel lookup only are synthetic boundaries; no SQL.
error_reporting(E_ALL);
$events = []; $phase = 'load';
set_error_handler(function ($severity,$message,$file,$line) use (&$events,&$phase) {
    $events[]=['phase'=>$phase,'severity'=>$severity,'message'=>$message,'file'=>basename($file),'line'=>$line];
    return false; // Preserve native stderr, do not turn warnings into silent passes.
});
class DBAdapter {}
class Propel { public static function getDB($name) { return new DBAdapter(); } }
require '/audit/probe/'.$argv[1].'.php';
require '/audit/probe/criteriaFilter.php';
function fresh() { $c=new Criteria('fixture'); $c->addAlias('a','a'); return $c; }
function filterWith($value) { $c=fresh();$c->add('a.id',$value);$f=new criteriaFilter();$f->setFilter($c);return $f; }
function node($n) { return [$n->getTable(),$n->getColumn(),$n->getValue(),$n->getComparison(),$n->getConjunctions(),array_map('node',$n->getClauses())]; }
function state($c) {
    $nodes=[]; foreach($c->keys() as $k) $nodes[$k]=node($c->getCriterion($k));
    return ['keys'=>$c->keys(),'nodes'=>$nodes,'order'=>$c->getOrderByColumns(),'isset'=>isset($c->creteria_filter_attached),'marker'=>isset($c->creteria_filter_attached)?$c->creteria_filter_attached:null];
}
function representation($c) {
    $s=serialize($c);$v=get_object_vars($c);
    return ['property_exists'=>property_exists($c,'creteria_filter_attached'),'public_vars'=>$v,'serialized_base64'=>base64_encode($s),'serialized_bytes'=>strlen($s),'serialized_sha256'=>hash('sha256',$s),'roundtrip_bytes_identical'=>serialize(unserialize($s))===$s];
}
$rows=[];
function recordCase($name,$fn) { global $phase,$rows; $phase=$name; $rows[$name]=$fn(); }
recordCase('fresh',function(){ $c=fresh();return ['state'=>state($c),'representation'=>representation($c)]; });
recordCase('disabled',function(){ $c=fresh();$f=filterWith(1);$f->disable();$f->applyFilter($c);return state($c); });
recordCase('once_twice',function(){ $c=fresh();$f=filterWith(1);$f->applyFilter($c);$one=state($c);$f->applyFilter($c);return [$one,state($c),representation($c)]; });
recordCase('two_filters',function(){ $c=fresh();filterWith(1)->applyFilter($c);filterWith(2)->applyFilter($c);return state($c); });
foreach(['true'=>true,'false'=>false,'null'=>null] as $label=>$value) recordCase('preset_'.$label,function()use($value){$c=fresh();$c->creteria_filter_attached=$value;filterWith(1)->applyFilter($c);return state($c);});
recordCase('unset_reapply',function(){ $c=fresh();filterWith(1)->applyFilter($c);unset($c->creteria_filter_attached);filterWith(2)->applyFilter($c);return state($c); });
recordCase('clone',function(){ $c=fresh();filterWith(1)->applyFilter($c);$copy=clone $c;filterWith(2)->applyFilter($copy);return [state($c),state($copy),representation($copy)]; });
recordCase('clear',function(){ $c=fresh();filterWith(1)->applyFilter($c);$c->clear();filterWith(2)->applyFilter($c);return state($c); });
recordCase('empty_filter',function(){ $c=fresh();$f=new criteriaFilter();$f->setFilter(fresh());$f->applyFilter($c);return state($c); });
recordCase('nested_order',function(){ $from=fresh();$n=$from->getNewCriterion('a.id',1);$n->addOr($from->getNewCriterion('a.id',2));$from->add($n);$from->addAscendingOrderByColumn('a.id');$from->addDescendingOrderByColumn('a.name');$f=new criteriaFilter();$f->setFilter($from);$c=fresh();$f->applyFilter($c);return state($c); });
recordCase('duplicate_constraint',function(){ $c=fresh();$c->add('a.id',1);filterWith(1)->applyFilter($c);return state($c); });
recordCase('exception_marker',function(){ $c=fresh();$f=new criteriaFilter();$caught=null;try{$f->applyFilter($c);}catch(Throwable $e){$caught=[get_class($e),$e->getMessage()];}filterWith(2)->applyFilter($c);return [$caught,state($c)]; });
recordCase('serialize_attached',function(){ $c=fresh();filterWith(1)->applyFilter($c);$copy=unserialize(serialize($c));filterWith(2)->applyFilter($copy);return [state($copy),representation($copy)]; });
// Cross-version input is generated only from this synthetic fixed corpus.
$phase='done';
echo json_encode(['schema'=>1,'php'=>PHP_VERSION,'variant'=>$argv[1],'rows'=>$rows,'events'=>$events,'source_sha256'=>['criteria'=>hash_file('sha256','/audit/probe/'.$argv[1].'.php'),'filter'=>hash_file('sha256','/audit/probe/criteriaFilter.php')]],JSON_THROW_ON_ERROR|JSON_PRETTY_PRINT),"\n";
