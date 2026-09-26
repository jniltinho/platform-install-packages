#!/usr/bin/env python3
"""Propose cumulative source patches only. Never builds/selects an artifact."""
import argparse
import copy
import hashlib
import io
import json
from pathlib import Path
import subprocess
import tempfile
import zipfile

ROOT=Path(__file__).resolve().parents[3]
E=ROOT/'doc/php83/evidence/exp13-candidate'
ORIGINAL='58d534d09b3b75c9a8333957268c884f79032638b2d44a278b1992fda1b0ab28'
EXP12='de5e61a1b54f472e605ef2e87669302a3915616fd85378e0f05706fcb06a7e8b'
DEBUG='vendor/propel/util/DebugPDO.php'
def sha(b):return hashlib.sha256(b).hexdigest()
def require(ok,msg):
 if not ok:raise ValueError(msg)
def repo(path):
 p=ROOT/path
 require(not p.is_symlink() and p.resolve().is_relative_to(ROOT),'Unsafe repository path')
 return p.read_bytes()
def metadata():
 pins=json.loads(Path(__file__).with_name('inputs.json').read_bytes());docs={}
 for role,row in pins.items():
  b=repo(row['path']);require(sha(b)==row['sha256'],'Input drift '+role)
  if role!='builder':docs[role]=json.loads(b)
 return docs,pins

def apply(data,path,patch,expected,added=False):
 with tempfile.TemporaryDirectory(prefix='exp13-local-replay-') as directory:
  root=Path(directory);p=root/path;p.parent.mkdir(parents=True,exist_ok=True)
  if not added:p.write_bytes(data)
  proc=subprocess.run(['patch','--batch','--forward','--fuzz=0','--no-backup-if-mismatch','-p1'],input=patch,cwd=root,capture_output=True,timeout=30)
  require(proc.returncode==0 and not any(w in (proc.stdout+proc.stderr).lower() for w in [b'offset',b'fuzz',b'reversed',b'skipping']),'Patch replay not exact '+path)
  require({str(x.relative_to(root)) for x in root.rglob('*') if x.is_file()}=={path},'Unexpected patch outputs')
  out=p.read_bytes();require(sha(out)==expected,'After hash mismatch '+path);return out

def cumulative(before,after,path):
 with tempfile.TemporaryDirectory(prefix='exp13-diff-') as directory:
  a=Path(directory)/'before';b=Path(directory)/'after';a.write_bytes(before);b.write_bytes(after)
  proc=subprocess.run(['diff','-u','--label','a/'+path,'--label','b/'+path,str(a),str(b)],capture_output=True)
  require(proc.returncode==1 and not proc.stderr,'Cannot create cumulative patch')
  return proc.stdout

def entries(d):
 out=[]
 for family in ['xml','aws']:
  for row in d[family]['changes']:out.append(dict(row,family=family))
 row=d['dispatcher'];out.append(dict(row,operation='modify',patch='patches/php83/held/dispatch-rank/FrontController-dynamic-policy.patch',family='dispatcher'))
 for row in d['returns']['files']:
  out.append(dict(row,operation='modify',patch='patches/php83/held/return-contracts/'+row['patch'],family='returns'))
 require(len(out)==13 and len({r['path'] for r in out})==13,'Unexpected proposal targets')
 return out

def prepare(original,exp12,output):
 require(not output.exists(),'Refuse existing output')
 docs,pins=metadata();prior=docs['exp12'];rows=copy.deepcopy(prior['patches'])
 require(len(rows)==65 and prior['revision']=='exp12' and prior['selection_approved'] is True,'Wrong exp12 manifest')
 require(sha(original)==ORIGINAL and sha(exp12)==EXP12,'Archive identity mismatch')
 require(docs['composition']['composition_commutes'] is True,'Unproven DebugPDO composition')
 root=prior['upstream_root'];modified=[];patchbytes={};superseded=[]
 with zipfile.ZipFile(io.BytesIO(original)) as z0,zipfile.ZipFile(io.BytesIO(exp12)) as z12:
  require(len(z0.namelist())==len(set(z0.namelist())) and len(z12.namelist())==len(set(z12.namelist())),'Duplicate archive members')
  for row in rows:
   p=repo(row['source_patch']);require(sha(p)==row['sha256'],'Prior patch drift')
   source=z0.read(root+'/'+row['path']);require(sha(source)==row['before_sha256'],'Prior upstream drift')
   replay=apply(source,row['path'],p,row['after_sha256']);require(replay==z12.read(root+'/'+row['path']),'Prior repair absent in exp12')
   patchbytes[row['patch']]=p
  for delta in entries(docs):
   path=delta['path'];add=delta['operation']=='add';name=root+'/'+path
   if add:
    require(name not in z0.namelist() and name not in z12.namelist() and delta['before_sha256'] is None,'Added helper collision')
    before=b''
   else:
    before=z12.read(name);require(sha(before)==delta['before_sha256'],'Delta base mismatch '+path)
   patch=repo(delta['patch']);require(sha(patch)==delta['patch_sha256'],'Delta patch drift')
   after=apply(before,path,patch,delta['after_sha256'],add)
   chain=[{'patch':delta['patch'],'sha256':delta['patch_sha256'],'before_sha256':delta['before_sha256'],'after_sha256':delta['after_sha256']}]
   if path==DEBUG:
    debug=docs['debug'];dp='patches/php83/held/'+debug['patch'];p=repo(dp);require(sha(p)==debug['sha256'],'Debug prerequisite drift')
    final=docs['composition']['variants']['candidate'][DEBUG]
    after=apply(after,path,p,final)
    alternate=apply(before,path,p,debug['after_sha256']);alternate=apply(alternate,path,patch,final)
    require(after==alternate,'Debug order mismatch')
    chain.append({'patch':dp,'sha256':debug['sha256'],'after_sha256':final,'both_orders_equal':True})
   old=next((r for r in rows if r['path']==path),None)
   source=b'' if add else z0.read(name)
   if old:
    superseded.append(copy.deepcopy(old));patchbytes.pop(old['patch']);rows.remove(old)
   if add:finalpatch=patch
   else:finalpatch=cumulative(source,after,path)
   require(apply(source,path,finalpatch,sha(after),add)==after,'Cumulative verification')
   leaf='exp13-'+path.replace('/','__')+'.patch'
   row={'path':path,'operation':'add' if add else 'replace','patch':leaf,'sha256':sha(finalpatch),'before_sha256':None if add else sha(source),'after_sha256':sha(after),'source_patch':str((output/leaf).relative_to(ROOT))}
   rows.append(row);patchbytes[leaf]=finalpatch
   modified.append({'path':path,'family':delta['family'],'exp12_sha256':None if add else sha(before),'final_sha256':sha(after),'chain':chain,'superseded_prior':old,'conditional_on_sql':delta['family']=='returns'})
 require(len(rows)==len({r['path'] for r in rows})==75 and len(superseded)==3,'Cumulative inventory mismatch')
 require(len({r['patch'] for r in rows})==75,'Patch leaf collision')
 manifest={'revision':'exp13','upstream_root':root,'upstream_sha256':ORIGINAL,'target_php':'8.3','status':'PROPOSED_ONLY_PENDING_SQL_AND_COORDINATOR_SELECTION','selection_approved':False,'zip_built':False,'application_acceptance':False,'patches':rows,'prior_manifest_sha256':pins['exp12']['sha256'],'base_artifact_sha256':EXP12,'preserved_prior_entries_exactly':62,'cumulative_replacements':superseded,'new_unique_targets':10,'new_source_files':['infra/general/kXmlEntityLoaderPolicy.php'],'conditional_families':['returns plus DebugPDO-query-v3'],'privacy_included':False,'builder_format_required':2,'pending':['Real SQL primary and independent repeat','Explicit coordinator source selection/build approval','Built artifact compiler/runtime regression','Cache namespace and snapshot/rollback rehearsal; original readers reject AWS O payloads','Aggregate application/package/release gates']}
 report={'status':manifest['status'],'input_pins':pins,'preparer_sha256':sha(Path(__file__).read_bytes()),'strict_prior_replays':65,'delta_targets':modified,'target_count':75,'expected_php_family_count':11785,'zip_built':False,'runtime_executed':False,'selected':False}
 output.mkdir(parents=True)
 for name,b in patchbytes.items():(output/name).write_bytes(b)
 (output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 (output/'composition.json').write_text(json.dumps(report,indent=2)+'\n')
 return report
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--original',type=Path,required=True);p.add_argument('--exp12',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 r=prepare(a.original.read_bytes(),a.exp12.read_bytes(),a.output.resolve());print(json.dumps({'status':r['status'],'targets':r['target_count']}))
