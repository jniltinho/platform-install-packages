#!/usr/bin/env python3
"""Read-only full-member exp14 verification; no PHP body or runtime acceptance."""
import argparse,hashlib,io,json,zipfile,importlib.util
from pathlib import Path
import prepare as p
s=importlib.util.spec_from_file_location('selected_phase',Path(__file__).with_name('select.py'));selection=importlib.util.module_from_spec(s);s.loader.exec_module(selection)
E=p.ROOT/'doc/php83/evidence/exp14-candidate'
def members(raw):
 with zipfile.ZipFile(io.BytesIO(raw)) as z:
  p.need(len(z.namelist())==len(set(z.namelist())),'Duplicate members');return {i.filename:z.read(i) for i in z.infolist()}
def verify(original,prior,first,second):
 oldraw=original.read_bytes();priorraw=prior.read_bytes();a=first.read_bytes();b=second.read_bytes();docs,pins=p.inputs()
 p.need(p.sha(oldraw)==docs['exp13']['upstream_sha256'] and p.sha(priorraw)==p.EXP13,'Immutable input ZIP identities');p.need(a==b,'Independent ZIP byte mismatch')
 selected=json.loads((E/'selected-r1/manifest.json').read_bytes());p.need(selected==selection.selected(selection.PROPOSAL.read_bytes()),'Selected phase identity')
 old=members(oldraw);previous=members(priorraw);new=members(a);root=selected['upstream_root']+'/';meta=root+'.php83-experimental/'
 p.need(all(n.startswith(root) for n in old),'Unexpected original root')
 rows={r['path']:r for r in selected['patches']};adds={root+r['path'] for r in rows.values() if r.get('operation')=='add'}
 metadata={meta+'manifest.json',meta+'README.txt'}|{meta+r['patch'] for r in rows.values()}
 p.need(set(new)==set(old)|adds|metadata,'Complete archive inventory')
 for name,data in old.items():
  relative=name[len(root):]
  if relative in rows:
   p.need(p.sha(data)==rows[relative]['before_sha256'] and p.sha(new[name])==rows[relative]['after_sha256'],'Changed source identity')
  else:p.need(data==new[name],'Unchanged original member altered')
 for name in adds:p.need(p.sha(new[name])==rows[name[len(root):]]['after_sha256'],'Inherited added helper identity')
 for row in rows.values():p.need(p.sha(new[meta+row['patch']])==row['sha256'],'Embedded patch identity')
 embedded=json.loads(new[meta+'manifest.json']);p.need(all(embedded.get(k)==v for k,v in selected.items()),'Embedded manifest drift')
 p.need(embedded['builder_format']==2 and embedded['builder_sha256']==pins['builder']['sha256'],'Pinned builder-v2 identity')
 expected_readme=b'EXPERIMENTAL PHP 8.3 SOURCE ONLY. NOT A RELEASE.\nKnown incompatibilities remain. Do not deploy to production.\nOriginal library license headers are retained. See patch manifest.\n'
 p.need(new[meta+'README.txt']==expected_readme,'Metadata README identity')
 oldsource={n:b for n,b in previous.items() if not n.startswith(meta)};newsource={n:b for n,b in new.items() if not n.startswith(meta)}
 p.need(set(oldsource)==set(newsource),'No exp13 source additions/removals')
 delta=[n[len(root):] for n in oldsource if oldsource[n]!=newsource[n]];p.need(delta==[p.TARGET],'Exact rank-only delta')
 p.rank_bytes(previous[root+p.TARGET],new[root+p.TARGET])
 preserved=sum(previous[root+r['path']]==new[root+r['path']] for r in docs['exp13']['patches']);p.need(preserved==75,'Prior repairs not all preserved')
 counts={k:sum(n.endswith(('.php','.phtml')) for n in v) for k,v in [('exp13',oldsource),('exp14',newsource)]};p.need(counts=={'exp13':11785,'exp14':11785},'Actual PHP-family inventory')
 for filename in ['build-report.json','SHA256SUMS']:p.need((first.parent/filename).read_bytes()==(second.parent/filename).read_bytes(),'Build metadata repeat mismatch')
 p.need(original.read_bytes()==oldraw and prior.read_bytes()==priorraw,'Input mutation during verify')
 return {'status':'VERIFIED_REPRODUCIBLE_EXP14_NOT_RUNTIME_ACCEPTED','zip_sha256':p.sha(a),'repeat_sha256':p.sha(b),'bytes':len(a),'targets':len(rows),'preserved_exp13_targets':preserved,'delta_paths':delta,'source_additions':0,'source_removals':0,'deleted_bytes':7,'rank_body_bytes_unchanged':True,'php_family_counts':counts,'original_sha256':p.sha(oldraw),'exp13_sha256':p.sha(priorraw),'selected_manifest_sha256':p.sha((E/'selected-r1/manifest.json').read_bytes()),'metadata_files':len(metadata),'verifier_sha256':p.sha(Path(__file__).read_bytes()),'builder_sha256':pins['builder']['sha256'],'metadata74_delta_intentional':True,'positive_rank_body_persistence_tested':False,'application_acceptance':False,'release_approved':False}
if __name__=='__main__':
 a=argparse.ArgumentParser()
 for n in ['original','exp13','primary','repeat']:a.add_argument('--'+n,type=Path,required=True)
 r=a.parse_args();print(json.dumps(verify(r.original,r.exp13,r.primary,r.repeat),indent=2))
