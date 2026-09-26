#!/usr/bin/env python3
"""Conditional exp14 source proposal; no builder invocation or selection."""
import argparse,copy,hashlib,importlib.util,io,json,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
TARGET='api_v3/lib/KalturaEntryService.php'
EXP13='6d0bc4947207e6c5457b7843948d263aa8d5f251480e58cbf9086c0add79a944'
BEFORE=b'protected function anonymousRankEntry($entryId, $entryType = null, $rank)'
AFTER=b'protected function anonymousRankEntry($entryId, $entryType, $rank)'
def sha(b):return hashlib.sha256(b).hexdigest()
def need(ok,msg):
 if not ok:raise ValueError(msg)
def inputs():
 pins=json.loads((HERE/'input-pins.json').read_bytes());docs={}
 for role,row in pins.items():
  b=(ROOT/row['path']).read_bytes();need(sha(b)==row['sha256'],'Frozen input drift '+role)
  if role in ['exp13','rank']:docs[role]=json.loads(b)
 return docs,pins
def rank_bytes(original,candidate):
 need(original.count(BEFORE)==1,'Exact rank declaration')
 need(candidate==original.replace(BEFORE,AFTER,1) and len(original)-len(candidate)==7,'Only seven-byte deletion allowed')
 need(original.count(b'\n')==candidate.count(b'\n'),'Line count drift')
def native_proof():
 path=HERE/'proof-pins.json';need(path.exists(),'Native rank repeat terminal proof not frozen yet')
 pins=json.loads(path.read_bytes())
 for name,digest in pins.items():need(sha((ROOT/name).read_bytes())==digest,'Native rank evidence drift '+name)
 E=ROOT/'doc/php83/evidence/rank-signature-repair'
 need((E/'claude-repeat.exit').read_text().strip()=='0','Actual Claude repeat not terminal0')
 primary=json.loads((E/'primary-r2.json').read_bytes());repeat=json.loads((E/'claude-repeat.json').read_bytes())
 need(json.dumps(primary['records'],sort_keys=True)==json.dumps(repeat['records'],sort_keys=True) and len(primary['records'])==4,'Independent four-row mismatch')
 for report in [primary,repeat]:
  need(report['source_before']==report['source_after']==primary['source_before'],'Source snapshot drift')
 snapshots=[(E/n).read_bytes() for n in ['primary-r2-runtime-before.json','primary-r2-runtime-after.json','claude-repeat-runtime-before.json','claude-repeat-runtime-after.json']]
 need(all(b==snapshots[0] for b in snapshots),'Native runtime snapshot drift')
 for row in primary['records']:need(type(row['exit']) is int and row['exit']==0,'Native process failure')
 for name in ['primary-r2-validation.json','claude-repeat-validation.json']:
  m=json.loads((E/name).read_bytes());need(m['status']=='BOUNDED_SIGNATURE_CONTRACT_PASS' and m['processes']==4 and m['omission_calls']==16 and m['metadata83_unchanged'] is True and m['original83_deprecations']==1 and m['candidate83_deprecations']==0,'Signature contract')
  need(m['metadata74_delta']=={'parameter':'entryType','default_available':[True,False],'default':[['value',None],['unavailable','ReflectionException']]},'Explicit74 metadata delta')
  need(m['rank_positive_body_tested'] is False and m['application_acceptance'] is False,'No false rank body acceptance')
 return pins

def prepare(original,artifact,output):
 need(not output.exists(),'Refuse existing proposal');docs,pins=inputs();proof=native_proof();prior=docs['exp13'];rank=docs['rank']
 need(prior['revision']=='exp13' and prior['selection_approved'] is True and len(prior['patches'])==75,'Wrong prior selection')
 need(TARGET not in {r['path'] for r in prior['patches']},'Rank target unexpectedly overlaps prior repair')
 need(sha(original)==prior['upstream_sha256'] and sha(artifact)==EXP13,'Archive identity')
 rows=copy.deepcopy(prior['patches']);root=prior['upstream_root']+'/'
 spec=importlib.util.spec_from_file_location('strict_replay',ROOT/pins['replay']['path']);replay=importlib.util.module_from_spec(spec);spec.loader.exec_module(replay)
 with zipfile.ZipFile(io.BytesIO(original)) as old,zipfile.ZipFile(io.BytesIO(artifact)) as z:
  for archive in [old,z]:need(len(archive.namelist())==len(set(archive.namelist())),'Duplicate source members')
  for row in rows:
   need(sha(z.read(root+row['path']))==row['after_sha256'],'Prior artifact repair missing')
   need(sha((ROOT/row['source_patch']).read_bytes())==row['sha256'],'Preserved patch drift')
  source=old.read(root+TARGET);need(source==z.read(root+TARGET) and sha(source)==rank['before_sha256'],'Rank original/exp13 identity')
 patch=(ROOT/pins['patch']['path']).read_bytes();need(sha(patch)==rank['patch_sha256'],'Rank patch identity')
 candidate=replay.apply(source,TARGET,patch,rank['after_sha256']);rank_bytes(source,candidate)
 rows.append({'path':TARGET,'operation':'replace','patch':'rank-signature.patch','sha256':sha(patch),'before_sha256':sha(source),'after_sha256':sha(candidate),'source_patch':pins['patch']['path']})
 need(len(rows)==len({r['path'] for r in rows})==len({r['patch'] for r in rows})==76,'Target/leaf collision')
 need(rows[:75]==prior['patches'],'Prior entry lost')
 manifest={'revision':'exp14','upstream_root':prior['upstream_root'],'upstream_sha256':prior['upstream_sha256'],'target_php':'8.3','status':'PROPOSED_ONLY_NOT_SELECTED','selection_approved':False,'zip_built':False,'application_acceptance':False,'patches':rows,'base_artifact_sha256':EXP13,'prior_selected_manifest_sha256':pins['exp13']['sha256'],'preserved_prior_entries_exactly':75,'delta_modified':1,'delta_added':0,'new_source_files':[],'builder_format_required':2,'rank_body_persistence_tested':False,'metadata74_intentional_delta':True,'pending':['Explicit coordinator experiment selection/build authorization','Built artifact compiler/API/regressions','Full rank body and persistence workflow','Remaining cache/recovery/application/package/release gates']}
 report={'status':manifest['status'],'input_pins':pins,'native_proof_pins':proof,'target':TARGET,'before_sha256':sha(source),'after_sha256':sha(candidate),'patch_sha256':sha(patch),'deleted_bytes':' = null','deleted_byte_count':7,'body_and_all_other_bytes_preserved':True,'metadata83_unchanged':True,'metadata74_intentional_delta':True,'preserved_targets':75,'total_targets':76,'expected_php_family_files':11785,'zip_built':False,'runtime_executed_by_proposer':False}
 output.mkdir(parents=True)
 for name,obj in [('manifest.json',manifest),('composition.json',report)]: (output/name).write_text(json.dumps(obj,indent=2)+'\n')
 return report
if __name__=='__main__':
 p=argparse.ArgumentParser()
 for n in ['original','exp13','output']:p.add_argument('--'+n,type=Path,required=True)
 a=p.parse_args();print(json.dumps(prepare(a.original.read_bytes(),a.exp13.read_bytes(),a.output),indent=2))
