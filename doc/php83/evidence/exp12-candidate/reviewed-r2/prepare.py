#!/usr/bin/env python3
"""Draft cumulative65 proposal only; strict local replay never builds a ZIP."""
import argparse,copy,hashlib,importlib.util,io,json,stat,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
def sha(data):return hashlib.sha256(data).hexdigest()
def require(ok,msg):
 if not ok:raise ValueError(msg)
HELPER=ROOT/'tools/php83/exp11-candidate/stage.py'
require(sha(HELPER.read_bytes())=='d384328e48975c2131643c009e9ced55c251d1f9b387a0884cd158fd06b0bf15','Replay helper drift')
s=importlib.util.spec_from_file_location('prior',HELPER);prior=importlib.util.module_from_spec(s);s.loader.exec_module(prior)
INPUTS={
 'prior':('doc/php83/evidence/exp11-candidate/selected-manifest.json','99f87bf705b0a9c419229fc5c1484919e6de4ebc24dabcccb359b5bb762af2ff'),
 'criteria':('doc/php83/evidence/criteria-selection/composition-preparation.json','15699a771441a231a991ed98e8d649f5690b244c41c6d6e386cb9b5c18dcfe18'),
 'pake':('patches/php83/held/pake-relative-path/manifest.json','a91d8100d824c7c43c4c2a9f285f6904a73dc65c235ea9a0762e170ecc40b51f'),
 'debug':('doc/php83/evidence/template-generation/generator-debug-v1/manifest.json','2c9d61197bbe27c448792d256c93a6645018e022d38eec089c938c9660000f0b')}
CRITERIA='vendor/propel/util/Criteria.php'
TARGETS=['vendor/symfony/vendor/pake/pakeApp.class.php','vendor/symfony-data/tasks/sfPakeGenerator.php']
def documents():
 result={}
 for role,(path,pin) in INPUTS.items():
  b=prior.repo_bytes(path);require(sha(b)==pin,'Metadata drift: '+role);result[role]=json.loads(b)
 return result
def entry(meta,path,patch):
 return {'path':path,'patch':Path(patch).name,'sha256':meta['patch_sha256'],'before_sha256':meta['before_sha256'],'after_sha256':meta['after_sha256'],'source_patch':patch}
def proposal(docs):
 old=docs['prior'];require(old['revision']=='exp11' and old['status']=='EXPERIMENTAL_SELECTED_LAB_ONLY_NOT_FOR_PRODUCTION' and len(old['patches'])==63,'Wrong selected exp11')
 require(old['upstream_sha256']==prior.ORIGINAL and old['upstream_root']==prior.ROOT and old['target_php']=='8.3','Prior identity mismatch')
 rows=copy.deepcopy(old['patches']);indices=[i for i,r in enumerate(rows) if r['path']==CRITERIA];require(len(indices)==1,'Criteria exact once');i=indices[0];superseded=copy.deepcopy(rows[i]);cm=docs['criteria']
 require(cm['path']==CRITERIA and cm['before_sha256']==rows[i]['before_sha256'] and cm['prior_sha256']==rows[i]['after_sha256'] and cm['preserved_prior_bytes_after_removing_attribute'] is True,'Cumulative Criteria mismatch')
 require(cm['next_zip_selected'] is False and cm['application_acceptance'] is False,'Unexpected upstream promotion')
 rows[i]=entry(cm,CRITERIA,'doc/php83/evidence/exp12-candidate/Criteria-dynamic-hierarchy.patch')
 for role,target,patch in [('pake',TARGETS[0],'patches/php83/held/pake-relative-path/pake-relative-path.patch'),('debug',TARGETS[1],'doc/php83/evidence/template-generation/generator-debug-v1/generator-debug.patch')]:
  m=docs[role];require(m['target']==target,'Wrong added target');rows.append(entry(m,target,patch))
 require(docs['debug']['prerequisite']['target']==TARGETS[0] and docs['debug']['prerequisite']['after_sha256']==docs['pake']['after_sha256'],'DEBUG prerequisite mismatch')
 require(len(rows)==len(set(r['path'] for r in rows))==len(set(r['patch'] for r in rows))==65,'Target or leaf collision')
 for j,oldrow in enumerate(old['patches']):
  if j!=i:require(rows[j]==oldrow,'Prior entry drift')
 return {'upstream_sha256':prior.ORIGINAL,'upstream_root':prior.ROOT,'status':'DRAFT_PENDING_CRITERIA_COMPOSITION_NOT_SELECTED','revision':'exp12','target_php':'8.3','patches':rows,'selection_approved':False,'zip_built':False,'application_acceptance':False,'superseded_prior_entry':superseded,'metadata_provenance':[{'role':k,'path':v[0],'sha256':v[1]} for k,v in INPUTS.items()],'preserved_prior_entries_exactly':62,'explicit_cumulative_replacements':1,'additional_unique_targets':2,'pending':['Actual cumulative Criteria source review and native composition','Independent exp12 draft review','Explicit coordinator selection/build approval','Artifact based syntax/API/CLI/additions regressions'],'known_limitations':['Criteria cross-engine serialized layout difference remains a baseline failure; no cache acceptance','Held Pake and DEBUG proofs are bounded source-stage evidence, not built exp12 coverage','No production/package/release/SQL/appboot acceptance']}
def prepare(original):
 docs=documents();manifest=proposal(docs);raw=Path(original).read_bytes();require(sha(raw)==prior.ORIGINAL,'Original ZIP pin mismatch');originals={};patches={}
 with zipfile.ZipFile(io.BytesIO(raw)) as z:
  require(len(z.namelist())==len(set(z.namelist())),'Duplicate ZIP members')
  for row in manifest['patches']:
   prior.safe_relative(row['path']);prior.safe_relative(row['source_patch']);info=z.getinfo(prior.ROOT+'/'+row['path']);require(not info.is_dir() and stat.S_IFMT(info.external_attr>>16) in (0,stat.S_IFREG),'Nonregular upstream')
   data=z.read(info);require(sha(data)==row['before_sha256'],'Upstream source drift');originals[row['path']]=data
   patch=prior.repo_bytes(row['source_patch']);require(sha(patch)==row['sha256'],'Patch drift');patches[row['patch']]=patch
 old=manifest['superseded_prior_entry'];oldpatch=prior.repo_bytes(old['source_patch']);require(sha(oldpatch)==old['sha256'],'Superseded selected patch byte drift');prior.apply_exact([old],{CRITERIA:originals[CRITERIA]},{old['patch']:oldpatch})
 replay=prior.apply_exact(manifest['patches'],originals,patches)
 return manifest,{'status':manifest['status'],'targets':65,'strict_replays':replay,'selection_approved':False,'zip_built':False,'runtime_executed':False,'preparer_sha256':sha(Path(__file__).read_bytes()),'replay_helper_sha256':sha(HELPER.read_bytes())}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--original',type=Path,required=True);p.add_argument('--manifest',type=Path,required=True);p.add_argument('--report',type=Path,required=True);a=p.parse_args();require(not a.manifest.exists() and not a.report.exists(),'Refuse overwrite');m,r=prepare(a.original)
 for path,value in [(a.manifest,m),(a.report,r)]:
  with path.open('x') as f:json.dump(value,f,indent=2);f.write('\n')
 print(json.dumps({'targets':65,'status':m['status']}))
