<?php
error_reporting(E_ALL);
ini_set('display_errors', 'stderr');
$root='/audit/app';$case='api-http';$out=array();
set_include_path($root.'/vendor/ZendFramework/library'.PATH_SEPARATOR.$root.'/vendor');
require '/audit/tests/api-bootstrap.php';
// Bootstrap owns/guards and seeds only php83_api_probe in our private MariaDB.
$pdo = new PDO('mysql:unix_socket=/audit/db/mysql.sock;dbname=php83_api_probe', 'vagrant');
$pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
$insert=$pdo->prepare('INSERT INTO permission (id,type,name,partner_id,status) VALUES (900,?,?,?,?)');
$insert->execute(array(PermissionType::PLUGIN,'FEATURE',83002,PermissionStatus::ACTIVE));
function permissionProbe($id,$name,$dependency) {
    $p=new Permission();$p->setId($id);$p->setName($name);$p->setDependsOnPermissionNames($dependency);return $p;
}
$cases=array(
    array('empty',array(),0,array()),
    array('null',array(array(101,'ROOT',null)),0,array('ROOT')),
    array('empty-dependency',array(array(101,'ROOT','')),0,array('ROOT')),
    array('zero-dependency',array(array(101,'ROOT','0')),0,array('ROOT')),
    array('satisfied',array(array(101,'ROOT',null),array(102,'CHILD','ROOT')),0,array('ROOT','CHILD')),
    array('missing',array(array(102,'CHILD','MISSING')),0,array()),
    array('transitive',array(array(102,'CHILD','MISSING'),array(103,'GRANDCHILD','CHILD')),0,array()),
    array('whitespace-csv',array(array(101,'ROOT',null),array(102,'CHILD',' ROOT , ')),0,array('ROOT','CHILD')),
    array('partner-feature',array(array(102,'CHILD','FEATURE')),83002,array('CHILD')),
    array('wrong-partner',array(array(102,'CHILD','FEATURE')),83003,array())
);
$rows=array();
foreach($cases as $caseRow) {
    list($label,$inputs,$partner,$expected)=$caseRow;
    $permissions=array();foreach($inputs as $input)$permissions[]=permissionProbe(...$input);
    $filtered=PermissionPeer::filterDependencies($permissions,$partner);
    $names=array();foreach($filtered as $permission)$names[]=$permission->getName();
    if($names!==$expected)throw new RuntimeException('Dependency contract failed: '.$label);
    $rows[]=array($label,$names);
}
echo json_encode($rows), "\n";
