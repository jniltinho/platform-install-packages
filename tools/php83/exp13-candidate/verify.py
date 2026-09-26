#!/usr/bin/env python3
"""Verify two built ZIPs, full source inventories and exact cumulative/delta hashes."""
import argparse
import hashlib
import io
import json
from pathlib import Path
import zipfile
import importlib.util

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('selected_phase',HERE/'select.py');selection=importlib.util.module_from_spec(spec);spec.loader.exec_module(selection)
ROOT=selection.ROOT
E=ROOT/'doc/php83/evidence/exp13-candidate'
def sha(b):return hashlib.sha256(b).hexdigest()
def need(ok,msg):
 if not ok:raise ValueError(msg)
def members(raw):
 with zipfile.ZipFile(io.BytesIO(raw)) as z:
  need(len(z.namelist())==len(set(z.namelist())),'Duplicate ZIP member')
  return {i.filename:z.read(i) for i in z.infolist()}
def verify(original,prior,first,second):
 originalraw=original.read_bytes();priorraw=prior.read_bytes();a=first.read_bytes();b=second.read_bytes()
 need(sha(originalraw)=='58d534d09b3b75c9a8333957268c884f79032638b2d44a278b1992fda1b0ab28','Original drift')
 need(sha(priorraw)=='de5e61a1b54f472e605ef2e87669302a3915616fd85378e0f05706fcb06a7e8b','Exp12 drift')
 need(a==b,'Two builds not byte-identical')
 selected=json.loads((E/'selected-r1/manifest.json').read_bytes())
 need(selected==selection.selected((selection.PROPOSAL/'manifest.json').read_bytes()),'Selected metadata drift')
 root=selected['upstream_root']+'/';meta=root+'.php83-experimental/'
 old=members(originalraw);previous=members(priorraw);new=members(a)
 patches={r['path']:r for r in selected['patches']};adds={root+r['path'] for r in patches.values() if r.get('operation')=='add'}
 expected_metadata={meta+'manifest.json',meta+'README.txt'}|{meta+r['patch'] for r in patches.values()}
 need(set(new)==set(old)|adds|expected_metadata,'Full ZIP inventory mismatch')
 need(adds=={root+'infra/general/kXmlEntityLoaderPolicy.php'},'Wrong addition')
 for name,data in old.items():
  path=name[len(root):]
  if path in patches:
   need(sha(data)==patches[path]['before_sha256'],'Upstream source hash')
   need(sha(new[name])==patches[path]['after_sha256'],'Cumulative source hash')
  else:need(data==new[name],'Unrelated source changed: '+name)
 for name in adds:need(sha(new[name])==patches[name[len(root):]]['after_sha256'],'Added helper hash')
 for r in patches.values():need(sha(new[meta+r['patch']])==r['sha256'],'Embedded patch drift')
 embedded=json.loads(new[meta+'manifest.json']);need(all(embedded[k]==v for k,v in selected.items()),'Embedded selected manifest drift')
 need(embedded['builder_format']==2 and embedded['builder_sha256']==sha((ROOT/'tools/php83/zip-builder-v2/build.py').read_bytes()),'Builder identity')
 sourceprevious={n:d for n,d in previous.items() if not n.startswith(meta)}
 delta={n[len(root):] for n in new if not n.startswith(meta) and (n not in sourceprevious or new[n]!=sourceprevious[n])}
 proof=json.loads((selection.PROPOSAL/'composition.json').read_bytes());need(delta=={r['path'] for r in proof['delta_targets']},'Exact exp12 delta mismatch')
 for r in proof['delta_targets']:
  name=root+r['path'];need(sha(new[name])==r['final_sha256'],'Delta final pin')
  if r['exp12_sha256'] is not None:need(sha(previous[name])==r['exp12_sha256'],'Delta old pin')
 need(len(delta)==13 and len(patches)==75,'Target counts')
 counts={label:sum(n.endswith(('.php','.phtml')) for n in files if not n.startswith(meta)) for label,files in [('exp12',previous),('exp13',new)]}
 need(counts=={'exp12':11784,'exp13':11785},'Compiler inventory counts')
 need(original.read_bytes()==originalraw and prior.read_bytes()==priorraw,'Input changed during verification')
 return {'status':'VERIFIED_REPRODUCIBLE_EXPERIMENT_NOT_RUNTIME_ACCEPTED','zip_sha256':sha(a),'repeat_sha256':sha(b),'zip_bytes':len(a),'original_sha256':sha(originalraw),'exp12_sha256':sha(priorraw),'targets':75,'preserved_exp12_entries':62,'delta_modified':12,'delta_added':1,'added_paths':sorted(n[len(root):] for n in adds),'delta_paths':sorted(delta),'php_family_counts':counts,'full_source_inventory_verified':True,'metadata_files':len(expected_metadata),'selected_manifest_sha256':sha((E/'selected-r1/manifest.json').read_bytes()),'verifier_sha256':sha(Path(__file__).read_bytes()),'application_acceptance':False,'release_approved':False}
if __name__=='__main__':
 p=argparse.ArgumentParser()
 for n in ['original','exp12','primary','repeat']:p.add_argument('--'+n,type=Path,required=True)
 a=p.parse_args();print(json.dumps(verify(a.original,a.exp12,a.primary,a.repeat),indent=2))
