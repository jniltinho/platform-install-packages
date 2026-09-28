<?php
/* Native model lifecycle only; outer reviewed envelope owns source/target/privacy,
 * TLS readiness, exclusive state, private capture, timeout and backup fsync. */
function split_need($ok, $code) { if (!$ok) throw new RuntimeException($code); }
function split_columns() {
    return array('id','type','created_at','updated_at','partner_id','name','system_name','description','url','host_name','is_default','parent_id','recognizer','tokenizer','status','streamer_type','media_protocols','custom_data','priority');
}
function split_row($con, $id, $lock=false) {
    split_need(is_int($id) && $id>0, 'ROW_ID');
    $q=$con->prepare('SELECT '.implode(',',split_columns()).' FROM delivery_profile WHERE id=? LIMIT 2'.($lock?' FOR UPDATE':''));
    $q->execute(array($id));$rows=$q->fetchAll(PDO::FETCH_ASSOC);
    split_need(count($rows)===1 && array_keys($rows[0])===split_columns(), 'ROW_CARDINALITY');
    $row=$rows[0];
    foreach ($row as &$value) { split_need(is_null($value)||is_string($value)||is_int($value), 'ROW_TYPE'); if(!is_null($value))$value=(string)$value; }
    unset($value);split_need(strlen(json_encode($row))<=32768,'ROW_CAP');return $row;
}
function split_original($r) {
    $exact=array('id'=>'1001','type'=>'61','partner_id'=>'0','url'=>'192.168.56.74:88/hls','host_name'=>'192.168.56.74','is_default'=>'1','parent_id'=>'0','recognizer'=>null,'tokenizer'=>null,'status'=>'0','streamer_type'=>'applehttp','media_protocols'=>null,'custom_data'=>null,'priority'=>'0');
    foreach($exact as $k=>$v)split_need(array_key_exists($k,$r)&&$r[$k]===$v,'ORIGINAL_STATE');
}
function split_state($state) {
    clearstatcache(true,$state);$s=lstat($state);
    split_need($s && ($s['mode']&0170000)===0040000 && ($s['mode']&0777)===0700 && $s['uid']===0 && $s['gid']===0,'STATE_METADATA');
}
function split_write($path,$value) {
    $data=json_encode($value,JSON_UNESCAPED_SLASHES|JSON_THROW_ON_ERROR)."\n";
    split_need(strlen($data)<=65536,'BACKUP_CAP');$f=fopen($path,'x');split_need($f!==false,'EXCLUSIVE_FILE');
    try {split_need(chmod($path,0600)&&fwrite($f,$data)===strlen($data)&&fflush($f),'PRIVATE_WRITE');} finally {fclose($f);}
}
function split_backup($state) {
    $p=$state.'/before.json';clearstatcache(true,$p);$s=lstat($p);
    split_need($s && ($s['mode']&0170000)===0100000 && ($s['mode']&0777)===0600 && $s['uid']===0 && $s['gid']===0 && $s['nlink']===1 && $s['size']<=65536,'BACKUP_METADATA');
    $v=json_decode(file_get_contents($p),true,32,JSON_THROW_ON_ERROR);
    split_need(is_array($v)&&array_keys($v)===array('schema','row')&&$v['schema']===1&&is_array($v['row'])&&array_keys($v['row'])===split_columns(),'BACKUP_SCHEMA');
    split_original($v['row']);return $v['row'];
}
function split_selection_guard($con) {
    $q=$con->query('SELECT id FROM delivery_profile WHERE partner_id=0 AND type=61 AND is_default=1 ORDER BY id LIMIT 129');
    $ids=$q->fetchAll(PDO::FETCH_COLUMN);split_need(count($ids)===1&&(string)$ids[0]==='1001','COMPETING_DEFAULT');
    $partner=PartnerPeer::retrieveByPK(102,$con);split_need($partner!==null && $partner->getDeliveryProfileIds()===array(),'PARTNER_OVERRIDE');
}
function split_verify_delta($before,$after,$isNew,$newId=null) {
    split_need(array_keys($before)===split_columns() && array_keys($after)===split_columns(),'DELTA_SCHEMA');
    $expected=$before;$expected['media_protocols']=$isNew?'https':'http';
    if($isNew) {$expected['id']=(string)$newId;$expected['url']='192.168.56.74:8444/hls';}
    foreach(split_columns() as $key) {
        if($key==='updated_at'||($isNew&&$key==='created_at')) {
            split_need(is_string($after[$key])&&preg_match('/^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$/D',$after[$key])===1,'NATIVE_TIMESTAMP');
        } else split_need($after[$key]===$expected[$key],'UNEXPECTED_MODEL_DELTA');
    }
}
function split_transaction($con,$state,$mode) {
    split_state($state);split_need(in_array($mode,array('prepare','apply'),true),'MODE');
    split_need($con->getNestedTransactionCount()===0,'TRANSACTION_ACTIVE');
    $con->beginTransaction();
    try {
        $before=split_row($con,1001,true);split_original($before);split_selection_guard($con);
        if($mode==='prepare') {
            split_write($state.'/before.json',array('schema'=>1,'row'=>$before));
            $con->commit();return array('status'=>'PRIVATE_ROW_BACKUP_PREPARED','profile_id'=>1001,'mutation_performed'=>false,'full_acceptance'=>false);
        }
        split_need(split_backup($state)===$before,'BACKUP_DRIFT');
        split_write($state.'/apply-intent.json',array('schema'=>1,'profile_id'=>1001,'no_retry'=>true));
        DeliveryProfilePeer::clearInstancePool();
        $original=DeliveryProfilePeer::retrieveByPK(1001,$con);
        split_need($original instanceof DeliveryProfileVodPackagerHls,'MODEL_TYPE');
        $new=new DeliveryProfileVodPackagerHls();$original->copyInto($new);
        $new->setUrl('192.168.56.74:8444/hls');$new->setMediaProtocols('https');
        split_need($new->save($con)===1,'NEW_SAVE');$newId=$new->getId();
        split_need((is_int($newId)||ctype_digit((string)$newId))&&(int)$newId>0&&(int)$newId!==1001,'NEW_ID');$newId=(int)$newId;
        $original->setMediaProtocols('http');split_need($original->save($con)===1,'ORIGINAL_SAVE');
        $after=split_row($con,1001);$created=split_row($con,$newId);
        split_verify_delta($before,$after,false);split_verify_delta($before,$created,true,$newId);
        split_need($con->getNestedTransactionCount()===1,'NESTED_TRANSACTION');
        split_write($state.'/after-before-commit.json',array('schema'=>1,'original'=>$after,'created'=>$created));
        $con->commit();
        return array('status'=>'NATIVE_PROFILE_SPLIT_COMMITTED','original_profile_id'=>1001,'https_profile_id'=>$newId,'http_preserved'=>true,'native_model_save_used'=>true,'selection_runtime_verified'=>false,'external_cache_rollback_available'=>false,'full_acceptance'=>false);
    } catch(Throwable $e) {
        if($con->getNestedTransactionCount()>0)$con->forceRollBack();throw $e;
    }
}
function split_main($argv) {
    $phase='TARGET';$allowed=array('TARGET','BOOTSTRAP','DB_IDENTITY','NATIVE_TRANSACTION');
    try {
        umask(0077);split_need(PHP_SAPI==='cli'&&function_exists('posix_geteuid')&&posix_geteuid()===0&&gethostname()==='kaltura-php74-baseline','TARGET');
        split_need(count($argv)===2&&in_array($argv[1],array('prepare','apply'),true),'MODE');
        $state='/var/lib/kaltura-baseline-delivery-split-r1';split_state($state);
        $phase='BOOTSTRAP';require '/opt/kaltura/app/deployment/bootstrap.php';
        set_time_limit(45);ini_set('memory_limit','256M');
        myDbHelper::$use_alternative_con=myDbHelper::DB_HELPER_CONN_MASTER;
        $con=Propel::getConnection(DeliveryProfilePeer::DATABASE_NAME,Propel::CONNECTION_WRITE);
        $phase='DB_IDENTITY';$id=$con->query('SELECT @@hostname,@@datadir,DATABASE()')->fetch(PDO::FETCH_NUM);
        split_need($id===array('kaltura-php74-baseline','/var/lib/mysql/','kaltura'),'DB_IDENTITY');
        $con->exec('SET SESSION max_statement_time=3');$con->exec('SET SESSION innodb_lock_wait_timeout=3');
        $phase='NATIVE_TRANSACTION';$out=split_transaction($con,$state,$argv[1]);
    } catch(Throwable $e) {
        $codes=array('ROW_ID','ROW_CARDINALITY','ROW_TYPE','ROW_CAP','ORIGINAL_STATE','STATE_METADATA','BACKUP_CAP','EXCLUSIVE_FILE','PRIVATE_WRITE','BACKUP_METADATA','BACKUP_SCHEMA','COMPETING_DEFAULT','PARTNER_OVERRIDE','DELTA_SCHEMA','NATIVE_TIMESTAMP','UNEXPECTED_MODEL_DELTA','MODE','TRANSACTION_ACTIVE','BACKUP_DRIFT','MODEL_TYPE','NEW_SAVE','NEW_ID','ORIGINAL_SAVE','NESTED_TRANSACTION','TARGET','DB_IDENTITY');
        $code=in_array($e->getMessage(),$codes,true)?$e->getMessage():'NATIVE_LIFECYCLE_FAILURE';
        $out=array('status'=>'FAILED_CLOSED','failure_stage'=>$phase,'failure_code'=>$code,'recovery_required'=>true,'full_acceptance'=>false);
    }
    echo json_encode($out,JSON_UNESCAPED_SLASHES)."\n";return $out['status']==='FAILED_CLOSED'?2:0;
}
if(realpath($_SERVER['SCRIPT_FILENAME'])===__FILE__)exit(split_main($argv));
