"""Prepare source replacements against exact published payload, never install/build DEBs."""
import argparse, hashlib, importlib.util, io, json, pathlib, subprocess, tarfile, tempfile, zipfile
HERE=pathlib.Path(__file__).resolve().parent; ROOT=HERE.parents[2]
BUNDLE=pathlib.Path('/tmp/kaltura-php83-audit/release/kaltura-server-noble-repo.tar.gz')
BUNDLE_PIN='91629580441f6a896ebf9e51f0256532221715bee57a3e5a64c66ff0c4e3127b'
MANIFEST_PIN='a7c789ae665c7147c2b6101baa282454e3a6e487c20e4827f254a7f103942e7f'
INPUT_PIN='798cee663130d7f2d3e8b626038ccbf5056bb50998ac86c2e62785d8956c9a27'
PRIVACY=ROOT/'tools/php83/baseline-rehearsal/privacy'
def sha(b):return hashlib.sha256(b).hexdigest()
def pinned(path,pin):
 b=pathlib.Path(path).read_bytes()
 if sha(b)!=pin:raise ValueError('INPUT_HASH')
 return b
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
PRIVACY_CONTRACT_PIN='74a6e7e1332e43a2752c4e8d5024555ab0132a5fa3db6c23201f124ec52302ce'
def verify_privacy_inputs():
 c=json.loads(pinned(HERE/'privacy-contract.json',PRIVACY_CONTRACT_PIN))
 for path,pin in dict(c['helpers'],**c['evidence']).items():pinned(ROOT/path,pin)
 return c
CONTRACT=verify_privacy_inputs()
def validate_privacy_outputs(changed):
 for path,pin in CONTRACT['expected_privacy_after'].items():
  if sha(changed[path])!=pin:raise ValueError('PRIVACY_OUTPUT_DRIFT')
def check_target_member(rel,added,regular):
 if rel in added:raise ValueError('ADDITION_EXISTS_PUBLISHED')
 if not regular:raise ValueError('SOURCE_TARGET_NOT_REGULAR')
policy=load('pilot_policy',PRIVACY/'trace-policy-v1/prepare.py')
caller=load('pilot_caller',PRIVACY/'caller-frame-v1/prepare.py')
sql=load('pilot_sql',PRIVACY/'sql-display-v1/prepare.py')
def patch_bytes(path,before,after):
 # GNU diff retains explicit no-newline markers required by cumulative patches.
 with tempfile.TemporaryDirectory(prefix='pilot-source-diff-') as temp:
  a=pathlib.Path(temp)/'before';b=pathlib.Path(temp)/'after';a.write_bytes(before);b.write_bytes(after)
  r=subprocess.run(['diff','-u','--label','a/'+path,'--label','b/'+path,str(a),str(b)],capture_output=True,timeout=10)
  if r.returncode!=1:raise ValueError('EXPECTED_SOURCE_DELTA')
  return r.stdout
def safe_path(name):
 p=pathlib.PurePosixPath(name)
 if p.is_absolute() or '..' in p.parts or str(p)!=name:raise ValueError('PATH')
 return p
def validate_selection(m):
 paths=[r['path'] for r in m['patches']]
 if len(paths)!=76 or len(set(paths))!=76:raise ValueError('TARGET_COUNT')
 for p in paths:safe_path(p)
 return paths
def compose(out):
 if out.exists():raise ValueError('FRESH_OUTPUT')
 m=json.loads(pinned(ROOT/'doc/php83/evidence/exp14-candidate/selected-r1/manifest.json',MANIFEST_PIN))
 inputs=json.loads(pinned(ROOT/'doc/php83/evidence/pilot83/published-control-inputs.json',INPUT_PIN))
 selected=validate_selection(m); targets=list(dict.fromkeys(selected+policy.TARGETS+[sql.TARGET]))
 added={r['path'] for r in m['patches'] if r.get('operation')=='add'}
 original=policy.old.archive('/tmp/kaltura-php83-audit/Rigel-18.20.0.zip',policy.old.UPSTREAM,[p for p in targets if p not in added])
 with zipfile.ZipFile(io.BytesIO(pinned('/tmp/kaltura-php83-audit/Rigel-18.20.0.zip',policy.old.UPSTREAM))) as z:
  if any('server-Rigel-18.20.0/'+p in z.namelist() for p in added):raise ValueError('ADDITION_EXISTS_UPSTREAM')
 original.update({p:b'' for p in added})
 candidate=policy.old.archive(ROOT.parent/'platform-install-packages-php83-artifacts/exp14/Rigel-18.20.0-php83-experimental.exp14.zip',policy.PIN,targets)
 for row in m['patches']:
  p=row['path']
  if (None if p in added else sha(original[p]))!=row['before_sha256'] or sha(candidate[p])!=row['after_sha256']:raise ValueError('SOURCE_JOIN')
  pinned(ROOT/row['source_patch'],row['sha256'])
 changed={p:candidate[p] for p in targets}
 for p in policy.TARGETS:changed[p]=policy.transform(p,changed[p])
 changed[caller.TARGET]=caller.transform(changed[caller.TARGET]);changed[sql.TARGET]=sql.transform(changed[sql.TARGET])
 validate_privacy_outputs(changed)
 published={}; inventory=[]
 with tarfile.open(fileobj=io.BytesIO(pinned(BUNDLE,BUNDLE_PIN)),mode='r:gz') as bundle:
  for pkg in inputs['packages']:
   item=bundle.getmember(pkg['member'])
   if not item.isfile() or item.size!=pkg['bytes']:raise ValueError('PACKAGE_MEMBER')
   raw=bundle.extractfile(item).read()
   if sha(raw)!=pkg['sha256']:raise ValueError('PACKAGE_HASH')
   with tempfile.TemporaryDirectory(prefix='pilot-payload-read-') as temp:
    deb=pathlib.Path(temp)/'input.deb';deb.write_bytes(raw)
    r=subprocess.run(['dpkg-deb','--fsys-tarfile',str(deb)],capture_output=True,timeout=90)
    if r.returncode:raise ValueError('DEB_READ')
    with tarfile.open(fileobj=io.BytesIO(r.stdout),mode='r:*') as archive:
     seen=set()
     for f in archive.getmembers():
      n=f.name.removeprefix('./').rstrip('/')
      if n in ('','.'):continue
      safe_path(n)
      if n in seen:raise ValueError('DUPLICATE_PAYLOAD')
      seen.add(n)
      record={'package':pkg['control']['Package'],'path':n,'mode':f.mode,'uid':f.uid,'gid':f.gid,'type':f.type.decode(),'link':f.linkname}
      rel=n.removeprefix('opt/kaltura/app/')
      if n.startswith('opt/kaltura/app/') and rel in targets:check_target_member(rel,added,f.isfile())
      if f.isfile():
       b=archive.extractfile(f).read();record['sha256']=sha(b)
       rel=n.removeprefix('opt/kaltura/app/')
       if n.startswith('opt/kaltura/app/') and rel in targets:
        if rel in added:raise ValueError('ADDITION_EXISTS_PUBLISHED')
        if rel in published:raise ValueError('MULTIPLE_OWNERS')
        if b!=original[rel]:raise ValueError('PUBLISHED_OVERLAY_COLLISION:'+rel)
        published[rel]={'package':record['package'],'record':record,'before':b}
      inventory.append(record)
 if set(published)!=set(targets)-added:raise ValueError('MISSING_SOURCE_TARGET')
 for p in added:published[p]={'package':'kaltura-base','record':{'mode':0o644,'uid':0,'gid':0},'before':b''}
 out.mkdir(parents=True);rows=[]
 for p in targets:
  item=published[p]; b=changed[p]
  try:policy.old.strict_replay(p,item['before'],patch_bytes(p,item['before'],b),b)
  except ValueError as e:raise ValueError('STRICT_REPLAY:'+p) from e
  destination=out/'replacements'/item['package']/'opt/kaltura/app'/p
  destination.parent.mkdir(parents=True,exist_ok=True);destination.write_bytes(b)
  rows.append({'package':item['package'],'path':p,'operation':'add' if p in added else 'replace','published_sha256':None if p in added else sha(item['before']),'exp14_sha256':sha(candidate[p]),'after_sha256':sha(b),'privacy':p in policy.TARGETS or p==sql.TARGET,'mode':item['record']['mode'],'uid':item['record']['uid'],'gid':item['record']['gid']})
 (out/'published-inventory.json').write_text(json.dumps(inventory,sort_keys=True,indent=2)+'\n')
 verify_privacy_inputs()
 result={'privacy_contract_sha256':PRIVACY_CONTRACT_PIN,'status':'PAYLOAD_PREPARED_NOT_BUILT_NOT_INSTALLED','bundle_sha256':BUNDLE_PIN,'selected_manifest_sha256':MANIFEST_PIN,'candidate_sha256':policy.PIN,'source_changes':rows,'published_inventory_sha256':sha((out/'published-inventory.json').read_bytes()),'published_inventory_count':len(inventory),'outside_allowlist_replacements':False,'hooks_reviewed':False,'package_build_allowed':False}
 (out/'manifest.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('output',type=pathlib.Path);a=p.parse_args();print(json.dumps(compose(a.output),indent=2))
