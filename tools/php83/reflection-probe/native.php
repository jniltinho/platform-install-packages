<?php
error_reporting(E_ALL);
$warnings=array();set_error_handler(function($n,$m)use(&$warnings){$warnings[]=array($n,$m);return true;});
class ReflectionProbeBase {
    public function inherited(self $x) {}
}
class ReflectionProbeChild extends ReflectionProbeBase {
    public function plain($x) {}
    public function scalar(int $x) {}
    public function arrayType(array $x) {}
    public function callableType(callable $x) {}
    public function objectType(object $x) {}
    public function classType(ReflectionProbeBase $x) {}
    public function nullable(?ReflectionProbeBase $x) {}
    public function defaultNull(ReflectionProbeBase $x=null) {}
    public function selfType(self $x) {}
    public function parentType(parent $x) {}
    public function missing(ReflectionProbeMissing $x) {}
    public function upper(SELF $x) {}
    public function upperParent(PARENT $x) {}
}
$methods=array('plain','scalar','arrayType','callableType','objectType','classType','nullable','defaultNull','selfType','parentType','inherited','missing','upper','upperParent');
$targets=array();foreach($methods as $m)$targets[]=array('ReflectionProbeChild',$m);
if(PHP_VERSION_ID>=80000){
    eval('class ReflectionProbeUnion { public function two(ReflectionProbeBase|ReflectionProbeChild $x) {} public function scalarUnion(ReflectionProbeBase|int $x) {} public function mixedType(mixed $x) {} public function iterableUnion(iterable|ReflectionProbeBase $x) {} public function missingUnion(ReflectionProbeMissing|int $x) {} }');
    foreach(array('two','scalarUnion','mixedType','iterableUnion','missingUnion')as$m)$targets[]=array('ReflectionProbeUnion',$m);
}
if(PHP_VERSION_ID>=80100){
    eval('interface ReflectionProbeI {} interface ReflectionProbeJ {} class ReflectionProbeIntersection { public function both(ReflectionProbeI&ReflectionProbeJ $x) {} }');
    $targets[]=array('ReflectionProbeIntersection','both');
}
if(PHP_VERSION_ID>=80200){
    eval('class ReflectionProbeDNF { public function withScalar((ReflectionProbeI&ReflectionProbeJ)|int $x) {} public function withClass((ReflectionProbeI&ReflectionProbeJ)|ReflectionProbeBase $x) {} }');
    $targets[]=array('ReflectionProbeDNF','withScalar');$targets[]=array('ReflectionProbeDNF','withClass');
}
if(PHP_VERSION_ID<80000){
    eval('class ReflectionProbeOrphan { public function orphan(parent $x) {} }');
    $targets[]=array('ReflectionProbeOrphan','orphan');
}
$helper=null;
if(isset($argv[1])){
    class KalturaReflector {}
    require $argv[1];
    $helper=new ReflectionMethod('KalturaActionReflector','getParameterClass');$helper->setAccessible(true);
}
$rows=array();foreach($targets as$t){
    $p=(new ReflectionMethod($t[0],$t[1]))->getParameters()[0];
    try{$c=$helper?$helper->invoke(null,$p):$p->getClass();$result=array('class',$c?$c->getName():null);}
    catch(Throwable$e){$result=array('error',get_class($e),$e->getMessage());}
    $rows[]=array($t,$result,$p->isOptional(),$p->allowsNull());
}
echo json_encode(array('php'=>PHP_VERSION,'rows'=>$rows,'warnings'=>$warnings)),"\n";
