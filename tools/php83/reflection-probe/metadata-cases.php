<?php
error_reporting(E_ALL);
$warnings=array();set_error_handler(function($n,$m)use(&$warnings){$warnings[]=array($n,$m);return true;});
class ReflectionProbeBase {
    /** @param int $x */ public function inherited(self $x) {}
}
class ReflectionProbeChild extends ReflectionProbeBase {
    /** @param int $x */ public function plain($x) {}
    /** @param int $x */ public function scalar(int $x) {}
    /** @param int $x */ public function arrayType(array $x) {}
    /** @param int $x */ public function callableType(callable $x) {}
    /** @param int $x */ public function objectType(object $x) {}
    /** @param int $x */ public function classType(ReflectionProbeBase $x) {}
    /** @param int $x */ public function nullable(?ReflectionProbeBase $x) {}
    /** @param int $x */ public function defaultNull(ReflectionProbeBase $x=null) {}
    /** @param int $x */ public function selfType(self $x) {}
    /** @param int $x */ public function parentType(parent $x) {}
    /** @param int $x */ public function missing(ReflectionProbeMissing $x) {}
    /** @param int $x */ public function upper(SELF $x) {}
    /** @param int $x */ public function upperParent(PARENT $x) {}
}
$methods=array('plain','scalar','arrayType','callableType','objectType','classType','nullable','defaultNull','selfType','parentType','inherited','missing','upper','upperParent');
$targets=array();foreach($methods as $m)$targets[]=array('ReflectionProbeChild',$m);
if(PHP_VERSION_ID>=80000){
    eval('class ReflectionProbeUnion { /** @param int $x */ public function two(ReflectionProbeBase|ReflectionProbeChild $x) {} /** @param int $x */ public function scalarUnion(ReflectionProbeBase|int $x) {} /** @param int $x */ public function mixedType(mixed $x) {} /** @param int $x */ public function iterableUnion(iterable|ReflectionProbeBase $x) {} /** @param int $x */ public function missingUnion(ReflectionProbeMissing|int $x) {} }');
    foreach(array('two','scalarUnion','mixedType','iterableUnion','missingUnion')as$m)$targets[]=array('ReflectionProbeUnion',$m);
}
if(PHP_VERSION_ID>=80100){
    eval('interface ReflectionProbeI {} interface ReflectionProbeJ {} class ReflectionProbeIntersection { /** @param int $x */ public function both(ReflectionProbeI&ReflectionProbeJ $x) {} }');
    $targets[]=array('ReflectionProbeIntersection','both');
}
if(PHP_VERSION_ID>=80200){
    eval('class ReflectionProbeDNF { /** @param int $x */ public function withScalar((ReflectionProbeI&ReflectionProbeJ)|int $x) {} /** @param int $x */ public function withClass((ReflectionProbeI&ReflectionProbeJ)|ReflectionProbeBase $x) {} }');
    $targets[]=array('ReflectionProbeDNF','withScalar');$targets[]=array('ReflectionProbeDNF','withClass');
}
if(PHP_VERSION_ID<80000){
    eval('class ReflectionProbeOrphan { /** @param int $x */ public function orphan(parent $x) {} }');
    $targets[]=array('ReflectionProbeOrphan','orphan');
}

class ReflectionProbeNoDoc { public function noDoc($x) {} /** @param int $service */ public function reserved($service) {} }
$targets[]=array('ReflectionProbeNoDoc','noDoc');$targets[]=array('ReflectionProbeNoDoc','reserved');
