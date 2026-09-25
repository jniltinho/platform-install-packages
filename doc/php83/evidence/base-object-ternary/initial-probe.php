<?php
// Actual full classes; only the model data source below is synthetic and never persists.
$diagnostics = array(); $phase = 'load';
set_error_handler(function ($severity, $message, $file, $line) use (&$diagnostics, &$phase) {
    $diagnostics[] = array('phase'=>$phase, 'severity'=>$severity, 'message'=>$message, 'file'=>basename($file), 'line'=>$line);
    return true; // Captured, not discarded; collector compares every diagnostic.
});
$files = array('vendor/propel/om/BaseObject.php','vendor/propel/util/BasePeer.php','alpha/apps/kaltura/lib/myBaseObject.class.php','infra/general/kString.class.php','infra/general/BaseEnum.php','alpha/lib/enums/entryStatus.php','alpha/apps/kaltura/lib/baseObjectUtils.class.php','alpha/apps/kaltura/lib/kAssetUtils.class.php');
$hashes=array();foreach($files as $file){$hashes[$file]=hash_file('sha256','/audit/source/'.$file);require '/audit/source/'.$file;}
class TernaryModel extends BaseObject {
    public $trace=array(); public $duration=12000;public $credit='credit&';public $ready=true;
    public function getByName($name,$type){$this->trace[]=array('getByName',$name,$type);return $name==='name' ? '<&"\'>' : 'value-'.$name;}
    public function getName(){$this->trace[]=array('getName');return '<&"\'>';}
    public function getChild(){$this->trace[]=array('getChild');return $this;}
    public function getStatus(){return $this->ready ? entryStatus::READY : -999;}
    public function getDataPath(){return '/fixture?x=1&y=2';}
    public function getLengthInMsecs(){return $this->duration;}
    public function getCredit(){return $this->credit;}
    public function getSourceLink(){return 'https://fixture.invalid/?a=1&b=2';}
    public function getThumbnailPath(){return '/thumb&';}
    public function getKuser(){return $this;}
    public function getScreenName(){return 'fixture&';}
}
$rows=array();$phase='cases';
$names=array(null,false,0,0.0,'','0','node',true,1,-1);
$closes=array(null,false,0,0.0,'','0',true,1,-1,'yes',array(),array(1),new stdClass());
foreach($names as $i=>$name)foreach($closes as $j=>$close){
 $obj=new TernaryModel();$rows[]=array('case'=>'matrix-'.$i.'-'.$j,'value'=>baseObjectUtils::objToXml($obj,array(),$name,$close),'trace'=>$obj->trace);
}
foreach(array('flat','alias','map','invoke','nested') as $case){
 $obj=new TernaryModel();$params=$case==='alias'?array('name'=>'alias'):array('name');$map=$case==='map'?array('extra'=>'<&"\'>'):null;
 if($case==='nested')$params=array('child.name'=>'nested');
 $rows[]=array('case'=>$case,'value'=>baseObjectUtils::objToXml($obj,$params,'node',true,$map,in_array($case,array('invoke','nested'),true)),'trace'=>$obj->trace);
}
foreach(array(0,12000,-1) as $duration)foreach(array(null,'credit&') as $credit)foreach(array(false,true) as $ready){
 $obj=new TernaryModel();$obj->duration=$duration;$obj->credit=$credit;$obj->ready=$ready;
 ob_start();kAssetUtils::createAssets(array($obj),'fixture-list');$value=ob_get_clean();
 $rows[]=array('case'=>'caller-'.count($rows),'value'=>$value,'trace'=>$obj->trace);
}
echo json_encode(array('version'=>PHP_VERSION,'hashes'=>$hashes,'rows'=>$rows,'diagnostics'=>$diagnostics),JSON_UNESCAPED_SLASHES|JSON_THROW_ON_ERROR)."\n";
