#!/usr/bin/env python3
import argparse,io,json,zipfile
from pathlib import Path
import common as c
def prepare(archives,out):
 c.need(not out.exists(),'Refuse existing stage');c.inputs();old=json.loads((c.OLD/'r3-stage-identities.json').read_bytes());payload={};joins=[]
 for archive,variant in [('exp12','original'),('exp13','candidate')]:
  raw=archives[archive].read_bytes();c.need(c.sha(raw)==c.ZIP_PINS[archive],'ZIP pin')
  with zipfile.ZipFile(io.BytesIO(raw)) as z:
   for name,digest in old['files'].items():
    if not name.startswith(variant+'/'):continue
    relative=name.split('/',1)[1];b=z.read('server-Rigel-18.20.0/'+relative);c.need(c.sha(b)==digest,'Actual artifact source differs R3 '+relative);payload[name]=b;joins.append({'path':name,'zip':archive,'sha256':digest})
 for name in ['probe.php','cache-probe.php']:
  b=(c.ROOT/'tools/php83/serialization-contracts'/name).read_bytes();c.need(c.sha(b)==old['files'][name],'Probe drift');payload[name]=b
 b=(c.OLD/'r3-reference-wires.json').read_bytes();c.need(c.sha(b)==old['files']['reference-wires.json'],'Reference wire drift');payload['reference-wires.json']=b
 run=(c.ROOT/'tools/php83/serialization-contracts/run-r2.sh').read_bytes().replace(b'php-serialization-wire-cache-r2',b'php-exp13-serialization-r1').replace(b'serialization-native83-wire-cache-r2',c.PHASE.encode())
 oldbranch=b' kaltura-php74-baseline) lab=baseline74; php=/usr/bin/php7.4; extensions=(-d extension=/usr/lib/php/20190902/json.so); [[ $1 == original ]] || exit 64;;\n';c.need(run.count(oldbranch)==1,'Expected74 guard branch');run=run.replace(oldbranch,b'').replace(b'original|cachefix|candidate',b'original|candidate');payload['run.sh']=run
 manifest={'phase':c.PHASE,'application_selected':False,'artifact_selected_for_experiment':True,'artifact_pins':c.ZIP_PINS,'files':{n:c.sha(b) for n,b in payload.items()},'runtime_files':{'native83':old['runtime_files']['native83']},'source_joins':joins,'historical_R3_manifest_sha256':c.sha((c.OLD/'r3-stage-identities.json').read_bytes())}
 out.mkdir(parents=True)
 for name,b in payload.items():p=out/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
 raw=(json.dumps(manifest,indent=2)+'\n').encode();(out/'identities.json').write_bytes(raw)
 return {'manifest_sha256':c.sha(raw),'local':str(out),'remote':c.REMOTE,'files':len(payload),'source_files':len(joins),'artifact_pins':c.ZIP_PINS,'historical74_NOT_RERUN':True,'application_acceptance':False}
if __name__=='__main__':
 a=argparse.ArgumentParser()
 for n in ['exp12','exp13','output']:a.add_argument('--'+n,type=Path,required=True)
 r=a.parse_args();print(json.dumps(prepare({'exp12':r.exp12,'exp13':r.exp13},r.output),indent=2))
