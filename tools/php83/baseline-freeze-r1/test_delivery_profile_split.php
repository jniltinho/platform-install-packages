<?php
require '/case/delivery_profile_split.php';
require '/work/real-copy.php';
class FakeStatement {
 public $rows;function __construct($r){$this->rows=$r;}
 function execute($p){$this->rows=$this->rows->rows[$p[0]]??null;}
 function fetchAll($mode){if($mode===PDO::FETCH_COLUMN)return $this->rows;return $this->rows===null?array():array($this->rows);}
}
class FakeConnection {
 public $rows,$depth=0,$saved,$competing=false,$events=0;
 function __construct($r){$this->rows=array(1001=>$r);}
 function getNestedTransactionCount(){return $this->depth;}
 function beginTransaction(){if(!$this->depth)$this->saved=$this->rows;$this->depth++;}
 function commit(){$this->depth--;}
 function forceRollBack(){$this->rows=$this->saved;$this->depth=0;}
 function prepare($q){if(strpos($q,'SELECT id,type,created_at')!==0)throw new Exception('QUERY');return new FakeStatement($this);}
 function query($q){return new FakeStatement($this->competing?array('1001','1002'):array('1001'));}
}
class FakePartner {function getDeliveryProfileIds(){return PartnerPeer::$override;}}
class PartnerPeer {static $override=array();static function retrieveByPK($id,$con){return new FakePartner;}}
class DeliveryProfilePeer {
 static function clearInstancePool(){}
 static function retrieveByPK($id,$con){return new DeliveryProfileVodPackagerHls($con->rows[$id]);}
}
function row(){return array('id'=>'1001','type'=>'61','created_at'=>'2026-01-01 00:00:00','updated_at'=>'2026-01-01 00:00:00','partner_id'=>'0','name'=>'PRIVATE_SYNTHETIC_NAME','system_name'=>null,'description'=>'PRIVATE_SYNTHETIC_DESCRIPTION','url'=>'192.168.56.74:88/hls','host_name'=>'192.168.56.74','is_default'=>'1','parent_id'=>'0','recognizer'=>null,'tokenizer'=>null,'status'=>'0','streamer_type'=>'applehttp','media_protocols'=>null,'custom_data'=>null,'priority'=>'0');}
function fresh($name){$p='/work/'.$name;mkdir($p,0700);return $p;}
function check($ok){if(!$ok)throw new Exception('TEST_FAILED');}
function rejects($fn){try{$fn();}catch(Throwable $e){return;}throw new Exception('DID_NOT_REJECT');}
$cases=0;
$c=new FakeConnection(row());$p=fresh('positive');$before=$c->rows;
$r=split_transaction($c,$p,'prepare');check($c->rows===$before&&$r['mutation_performed']===false);$cases++;
$r=split_transaction($c,$p,'apply');check($r['https_profile_id']===2001&&count($c->rows)===2&&$c->rows[1001]['media_protocols']==='http'&&$c->rows[2001]['url']==='192.168.56.74:8444/hls'&&$c->rows[2001]['parent_id']==='0'&&$c->rows[2001]['name']==='PRIVATE_SYNTHETIC_NAME'&&$c->events===2&&$c->depth===0);$cases++;
rejects(function()use($c,$p){split_transaction($c,$p,'apply');});$cases++;
$c=new FakeConnection(row());$p=fresh('drift');split_transaction($c,$p,'prepare');$c->rows[1001]['description']='changed';rejects(function()use($c,$p){split_transaction($c,$p,'apply');});check($c->events===0);$cases++;
$c=new FakeConnection(row());$c->rows[1001]['tokenizer']='opaque';$p=fresh('opaque');rejects(function()use($c,$p){split_transaction($c,$p,'prepare');});$cases++;
$c=new FakeConnection(row());$c->competing=true;$p=fresh('competing');rejects(function()use($c,$p){split_transaction($c,$p,'prepare');});$cases++;
$c=new FakeConnection(row());PartnerPeer::$override=array('applehttp'=>array(1001));$p=fresh('override');rejects(function()use($c,$p){split_transaction($c,$p,'prepare');});PartnerPeer::$override=array();$cases++;
$c=new FakeConnection(row());$p=fresh('bad-delta');split_transaction($c,$p,'prepare');DeliveryProfileVodPackagerHls::$badDelta=true;rejects(function()use($c,$p){split_transaction($c,$p,'apply');});check(count($c->rows)===1&&$c->rows[1001]['media_protocols']===null&&file_exists($p.'/apply-intent.json'));$cases++;
echo json_encode(array('status'=>'PAYLOAD_COMPOSITION_PASS','cases'=>$cases,'native_php'=>PHP_VERSION,'real_methods'=>array('copyInto','setUrl'),'orm_save_and_db'=>'TEST_DOUBLE_NOT_NATIVE_DB','private_values_exported'=>false))."\n";
