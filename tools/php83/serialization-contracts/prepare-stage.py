#!/usr/bin/env python3
import importlib.util,json,hashlib,shutil
from pathlib import Path
here=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('prep',here/'prepare.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
root=Path('/home/nilton/Projetos/nilton/NOVOS/kaltura-rigel-18.20.0-source/graph-view')
original=m.read_sources(m.ORIGINAL);exp12=m.read_sources(m.EXP12)
# Only copy pre-existing source files after exact archive comparison, never extract archives.
for name in m.PATHS:
 if original[name]!=exp12[name] or (root/name).read_bytes()!=original[name]:raise RuntimeError('source mismatch '+name)
out=here/'stage-r1';out.mkdir() # fail on existing stage
for variant in ['original','candidate']:
 for name in m.PATHS:
  target=out/variant/name;target.parent.mkdir(parents=True,exist_ok=True)
  value=(root/name).read_bytes()
  if variant=='candidate' and name in m.TARGETS:value=m.candidate(value)
  target.write_bytes(value)
for name in ['probe.php','run.sh']:shutil.copyfile(here/name,out/name)
reference=Path('doc/php83/evidence/exp12-runtime/runtime83-before.json')
x=json.loads(reference.read_text())['identity'];runtime=dict(x['files'])
for row in x['linked_libraries'].values():runtime.update(row)
files={str(p.relative_to(out)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(out.rglob('*')) if p.is_file()}
manifest={'phase':'serialization-native83-wire-r1','application_selected':False,'source_archives':m.PINS,'files':files,'runtime_files':runtime,'runtime_reference_sha256':hashlib.sha256(reference.read_bytes()).hexdigest()}
(out/'identities.json').write_text(json.dumps(manifest,sort_keys=True,indent=2)+'\n')
public=Path('doc/php83/evidence/serialization-contracts');shutil.copyfile(out/'identities.json',public/'stage-identities.json')
(public/'stage-pin.json').write_text(json.dumps({'manifest_sha256':hashlib.sha256((out/'identities.json').read_bytes()).hexdigest(),'local_stage':str(out),'remote_stage':'/home/vagrant/php-serialization-wire-r1'},indent=2)+'\n')
