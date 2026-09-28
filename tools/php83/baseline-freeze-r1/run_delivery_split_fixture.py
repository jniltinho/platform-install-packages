"""Offline native PHP fixture: exact copied methods plus explicit DB/save doubles."""
import hashlib,json,subprocess,tempfile
from pathlib import Path
H=Path(__file__).parent.resolve();ROOT=H.parents[2]
S=ROOT/'doc/php83/evidence/inventory-closure-r1/.extracted'
IMAGES=['sha256:63acd576f56cb75b4eae7f097f876dc1969f0585dfed391ed41f76c4c941ca47','sha256:421e665b3613c9116ee27745f3d983e87b1bd04ca3f80bca6bfa93586e9ee2a3']
def method(path,pin,name):
 data=(S/path).read_bytes();assert hashlib.sha256(data).hexdigest()==pin
 s=data.decode();start=s.index('\tpublic function '+name+'(') if '\tpublic function '+name+'(' in s else s.index('\tpublic function '+name+' (')
 end=s.index('\n\t}',start)+3;return s[start:end]
def composition():
 copy=method('alpha/lib/model/om/BaseDeliveryProfile.php','0bd05e4a212e2e914cb6bc476e3bd85f680b25dcc9e5aca6a908fb68a2e3150a','copyInto')
 url=method('alpha/lib/model/DeliveryProfile.php','2fa1974f9feb7479b00f3c60eb3c44b80039acb187c2e913d4e7bd4fee5c269f','setUrl')
 fields='id,type,created_at,updated_at,partner_id,name,system_name,description,url,host_name,is_default,parent_id,recognizer,tokenizer,status,streamer_type,media_protocols,custom_data,priority'.split(',')
 props=';'.join('protected $'+x+'=null' for x in fields)+';'
 return '''<?php
class FakeBase { protected $url; function setUrl($v){$this->url=$v;} }
class DeliveryProfileVodPackagerHls extends FakeBase {
'''+props+'''
 public static $badDelta=false;
 function __construct($row=array()){foreach($row as $k=>$v)$this->$k=$v;}
 function __call($name,$args){$key=strtolower(preg_replace('/(?<!^)[A-Z]/','_$0',substr($name,3)));if(substr($name,0,3)==='set'){$this->$key=$args[0];return;}return $this->$key;}
 function setNew($v){}
 function save($con){$con->beginTransaction();$new=$this->id===null;if($new){$this->id='2001';$this->created_at='2026-02-01 00:00:00';}$this->updated_at='2026-02-01 00:00:00';$r=array();foreach(split_columns() as $k)$r[$k]=$this->$k;if(self::$badDelta)$r['priority']='9';$con->rows[(int)$this->id]=$r;$con->events++;$con->commit();return 1;}
'''+copy+'\n'+url+'\n}\n'
def run():
 records=[]
 for image in IMAGES:
  p=subprocess.run(['docker','image','inspect',image,'--format','{{.Id}}'],capture_output=True,timeout=15,check=True);assert p.stdout.decode().strip()==image
  with tempfile.TemporaryDirectory(prefix='delivery-split-fixture-') as d:
   f=Path(d)/'real-copy.php';f.write_text(composition())
   args=['docker','run','--rm','--network','none','--read-only','--pids-limit','64','--memory','256m','--cap-drop','ALL','--security-opt','no-new-privileges','--tmpfs','/work:rw,nosuid,nodev,size=4m','-v',str(H)+':/case:ro','-v',str(f)+':/real-copy.php:ro',image,'sh','-c','cp /real-copy.php /work/real-copy.php && php -d display_errors=stderr /case/test_delivery_profile_split.php']
   p=subprocess.run(args,capture_output=True,timeout=60)
   if p.returncode:raise RuntimeError('FIXTURE_FAILED:'+p.stderr.decode()[:2000])
   result=json.loads(p.stdout);assert result['cases']==8 and result['private_values_exported'] is False
   records.append({'image':image,'exit':p.returncode,'stderr_bytes':len(p.stderr),'result':result})
 print(json.dumps({'status':'OFFLINE_COMPOSITION_PASS','runs':records},sort_keys=True))
if __name__=='__main__':run()
