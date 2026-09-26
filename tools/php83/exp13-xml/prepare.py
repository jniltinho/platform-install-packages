#!/usr/bin/env python3
"""Join exact built experiment ZIP members to existing reviewed XML corpus."""
import argparse
import hashlib
import io
import json
from pathlib import Path
import zipfile
ROOT=Path(__file__).resolve().parents[3]
PINS={'exp12':'de5e61a1b54f472e605ef2e87669302a3915616fd85378e0f05706fcb06a7e8b','exp13':'6d0bc4947207e6c5457b7843948d263aa8d5f251480e58cbf9086c0add79a944'}
STAGES={'matrix':('/tmp/php-xml-lifecycle-fix-prep-r1','c06f54b7dff9035ea1680d96416ab29d7b4669a5dbe26e417bedccf27d742a08','php-xml-lifecycle-fix-r1','xml-lifecycle-held-A-r1'),'chain':('/tmp/php-xml-lifecycle-fix-chain-prep-r1','5feb006310c2a7da6e790570f71b069738c127bd3374c52aebbf1ee81eed8017','php-xml-lifecycle-fix-chain-r1','xml-lifecycle-held-A-chain-r1')}
def sha(b):return hashlib.sha256(b).hexdigest()
def need(ok,msg):
 if not ok:raise ValueError(msg)
def prepare(archives,output):
 need(not output.exists(),'Refuse existing phase');zips={}
 for name,path in archives.items():
  b=path.read_bytes();need(sha(b)==PINS[name],'Artifact pin '+name);zips[name]=zipfile.ZipFile(io.BytesIO(b))
 report={'artifact_pins':PINS,'artifact_selected_for_experiment':True,'application_acceptance':False,'stages':{}}
 for kind,(oldpath,pin,oldremote,oldphase) in STAGES.items():
  ref=Path(__file__).resolve().parent/'reference';raw=(ref/(kind+'-manifest.json')).read_bytes();need(sha(raw)==pin,'Historical stage manifest')
  oldm=json.loads(raw);payload={};joins=[]
  for name,digest in oldm['files'].items():
   if name.startswith(('baseline/','candidate/')):
    variant,path=name.split('/',1);archive='exp12' if variant=='baseline' else 'exp13';b=zips[archive].read('server-Rigel-18.20.0/'+path);need(sha(b)==digest,'Actual artifact differs reviewed source '+path)
    joins.append({'stage_path':name,'archive':archive,'sha256':digest})
   elif name.startswith('fixtures/') or name=='provider.json':b=(ref/name).read_bytes()
   else:
    source='behavior-chain.php' if kind=='chain' and name=='behavior.php' else name
    b=(ROOT/'tools/php83/xml-lifecycle-fix'/source).read_bytes()
    if kind=='chain' and name=='run-native.sh':b=b.replace(b'php-xml-lifecycle-fix-r1',b'php-xml-lifecycle-fix-chain-r1').replace(b'xml-lifecycle-held-A-r1',b'xml-lifecycle-held-A-chain-r1')
   need(sha(b)==digest,'Frozen fixture drift '+name)
   payload[name]=b
  phase='exp13-xml-'+kind+'-r1';remote='php-'+phase
  payload['run-native.sh']=payload['run-native.sh'].replace(oldremote.encode(),remote.encode()).replace(oldphase.encode(),phase.encode())
  dest=output/kind;dest.mkdir(parents=True)
  for name,b in payload.items():p=dest/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
  for v in ['baseline','candidate']:
   for p in ['configurations','vendor/ZendFramework/library']:(dest/v/p).mkdir(parents=True,exist_ok=True)
  manifest=dict(oldm);manifest.update(phase=phase,files={n:sha(b) for n,b in payload.items()},artifact_pins=PINS,artifact_source_joins=joins,historical_manifest_sha256=pin)
  mb=(json.dumps(manifest,indent=2)+'\n').encode();(dest/'identities.json').write_bytes(mb)
  report['stages'][kind]={'manifest_sha256':sha(mb),'remote':'/home/vagrant/'+remote,'local':str(dest),'source_joins':joins}
 for z in zips.values():z.close()
 (output/'preparation.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--exp12',type=Path,required=True);a.add_argument('--exp13',type=Path,required=True);a.add_argument('--output',type=Path,required=True);r=a.parse_args();print(json.dumps(prepare({'exp12':r.exp12,'exp13':r.exp13},r.output),indent=2))
