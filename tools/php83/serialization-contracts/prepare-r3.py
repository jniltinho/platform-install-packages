#!/usr/bin/env python3
"""Fresh stage, unchanged R2 product bytes, revised observation closure; no VM."""
import hashlib,importlib.util,json,shutil
from pathlib import Path
HERE=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('collector',HERE/'collect-r2.py');c=importlib.util.module_from_spec(s);s.loader.exec_module(c)
if __name__=='__main__':
 source=HERE/'stage-r2';e=Path('doc/php83/evidence/serialization-contracts')
 old=json.loads((e/'r2-stage-identities.json').read_text());pin=json.loads((e/'r2-stage-pin.json').read_text())
 if hashlib.sha256((source/'identities.json').read_bytes()).hexdigest()!=pin['manifest_sha256']:raise ValueError('Historical stage drift')
 if json.loads((source/'identities.json').read_text())!=old:raise ValueError('Historical source manifest mismatch')
 for name,want in old['files'].items():
  p=source/name
  if p.is_symlink() or not p.resolve().is_relative_to(source.resolve()) or hashlib.sha256(p.read_bytes()).hexdigest()!=want:raise ValueError('Historical file drift '+name)
 dest=HERE/'stage-r3';dest.mkdir()
 for variant in ['original','cachefix','candidate']:shutil.copytree(source/variant,dest/variant)
 for name in ['probe.php','cache-probe.php','reference-wires.json']:shutil.copyfile(source/name,dest/name)
 runner=(source/'run.sh').read_text().replace('php-serialization-wire-cache-r2','php-serialization-wire-cache-r3').replace('serialization-native83-wire-cache-r2','serialization-native83-wire-cache-r3')
 (dest/'run.sh').write_text(runner)
 files={str(p.relative_to(dest)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(dest.rglob('*')) if p.is_file()}
 new=dict(old);new.update({'phase':'serialization-native83-wire-cache-r3','files':files,'collector_closure':c.collector_identity(),'preparer_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()})
 (dest/'identities.json').write_text(json.dumps(new,sort_keys=True,indent=2)+'\n')
 for local,name in [('identities.json','r3-stage-identities.json'),('reference-wires.json','r3-reference-wires.json')]:
  target=e/name
  if target.exists():raise ValueError('Refuse existing evidence '+name)
  shutil.copyfile(dest/local,target)
 target=e/'r3-stage-pin.json'
 if target.exists():raise ValueError('Refuse existing stage pin')
 target.write_text(json.dumps({'manifest_sha256':hashlib.sha256((dest/'identities.json').read_bytes()).hexdigest(),'local_stage':str(dest),'remote_stage':'/home/vagrant/php-serialization-wire-cache-r3'},indent=2)+'\n')
 print(json.dumps({'phase':new['phase'],'files':len(files),'collector_closure':new['collector_closure']}))
