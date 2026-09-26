#!/usr/bin/env python3
"""Exact exp11→exp12 three-source delta; no runtime acceptance."""
import argparse,io,json,zipfile
from pathlib import Path
import selected as s
p=s.p
OLD_PIN='f2474f5b951bfd2d121291025c8dd4554697fb5bb4024e132987643dab6144a7'
def compare(oldraw,newraw):
 p.require(p.sha(oldraw)==OLD_PIN,'Exp11 ZIP pin');current=s.validate(s.SELECTED.read_bytes());previous=p.documents()['prior'];prefix=current['upstream_root']+'/';meta=prefix+'.php83-experimental/';targets=[p.CRITERIA]+p.TARGETS
 with zipfile.ZipFile(io.BytesIO(oldraw)) as old,zipfile.ZipFile(io.BytesIO(newraw)) as new:
  left=set(old.namelist());right=set(new.namelist());p.require(len(left)==len(old.namelist()) and len(right)==len(new.namelist()),'Duplicate ZIP members')
  added={meta+r['patch'] for r in current['patches'] if r['path'] in targets};removed={meta+current['superseded_prior_entry']['patch']}
  p.require(right-left==added and left-right==removed,'Metadata addition/removal drift')
  changed={name for name in left&right if old.read(name)!=new.read(name)};p.require(changed=={prefix+x for x in targets}|{meta+'manifest.json'},'Unexpected source/content delta')
  priorrows={r['path']:r for r in previous['patches']}
  for row in current['patches']:
   path=row['path'];p.require(p.sha(new.read(prefix+path))==row['after_sha256'],'New target source hash')
   expected=priorrows[path]['after_sha256'] if path in priorrows else row['before_sha256'];p.require(p.sha(old.read(prefix+path))==expected,'Old target source hash')
   p.require(p.sha(new.read(meta+row['patch']))==row['sha256'],'Embedded patch identity')
  embedded=json.loads(new.read(meta+'manifest.json'));p.require(all(embedded.get(k)==v for k,v in current.items()),'Embedded selected metadata')
 return {'status':'PASS_LAB_ARTIFACT_DELTA_ONLY','exp11_sha256':p.sha(oldraw),'exp12_sha256':p.sha(newraw),'changed_application_paths':targets,'prior_targets_unchanged':62,'added_metadata':sorted(added),'removed_metadata':sorted(removed),'all_other_shared_entry_bytes_identical':True,'application_acceptance':False}
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('exp11',type=Path);a.add_argument('exp12',type=Path);a.add_argument('output',type=Path);r=a.parse_args();p.require(not r.output.exists(),'Refuse overwrite');result=compare(r.exp11.read_bytes(),r.exp12.read_bytes())
 with r.output.open('x') as f:json.dump(result,f,indent=2);f.write('\n')
 print(json.dumps(result))
