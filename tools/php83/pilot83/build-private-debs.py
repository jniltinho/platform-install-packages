"""Local private DEB derivation via fakeroot/dpkg-deb. Never installs or executes hooks."""
import argparse,hashlib,importlib.util,io,json,os,pathlib,stat,subprocess,tarfile
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[2]
BUILD_CONTRACT_PIN='c6f0ac0c3089973746e2a367fae2233c39bf0a89632f4863a3d1591225e73f22' # Exact reviewed local inputs; no installation authorization implied.
def sha(b):return hashlib.sha256(b).hexdigest()
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def verify_freeze(path):
 d=json.loads(pathlib.Path(path).read_text())
 for name,pin in d.items():
  if sha((ROOT/name).read_bytes())!=pin:raise ValueError('FROZEN_INPUT_DRIFT')
 return sha(pathlib.Path(path).read_bytes())
def regular(path,root,absent=False):
 if not path.is_relative_to(root):raise ValueError('OUTSIDE_STAGE')
 for p in [path]+list(path.parents):
  if p==root.parent:break
  if p.is_symlink():raise ValueError('SYMLINK_WRITE')
 if absent:
  if path.exists():raise ValueError('ADDITION_COLLISION')
 elif not path.is_file():raise ValueError('REGULAR_REQUIRED')
def write_delta(path,root,data,mode=None,uid=0,gid=0,absent=False):
 regular(path,root,absent)
 if not absent:
  st=path.stat();mode=stat.S_IMODE(st.st_mode);uid=st.st_uid;gid=st.st_gid
 path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
 os.chmod(path,mode);os.chown(path,uid,gid)
def checksum_bytes(lines):return ('\n'.join(lines)+('\n' if lines else '')).encode()
def run(cmd,**kw):
 p=subprocess.run(cmd,capture_output=True,timeout=600,**kw)
 if p.returncode:raise ValueError('LOCAL_BUILD_COMMAND_FAILED:'+str(p.returncode))
 return p.stdout
def build(out,payload_dir,control_dir):
 if not os.environ.get('FAKEROOTKEY') or os.geteuid()!=0:raise ValueError('RUN_UNDER_FAKEROOT')
 if out.exists():raise ValueError('FRESH_OUTPUT')
 if BUILD_CONTRACT_PIN is None:raise ValueError('BUILD_NOT_READY')
 contract_bytes=(HERE/'build-input-contract.json').read_bytes()
 if sha(contract_bytes)!=BUILD_CONTRACT_PIN:raise ValueError('BUILD_CONTRACT_DRIFT')
 for n,pin in json.loads(contract_bytes).items():
  if sha((ROOT/n).read_bytes())!=pin:raise ValueError('BUILD_INPUT_DRIFT')
 freezes={n:verify_freeze(ROOT/'doc/php83/evidence/pilot83'/n) for n in ('payload-freeze-r2.json','control-freeze-r1.json','hooks-freeze-r2.json')}
 source=load('build_payload',HERE/'compose-payload.py');controls=load('build_controls',HERE/'control-policy.py');hooks=load('build_hooks',HERE/'transform-hooks.py')
 payload=json.loads((payload_dir/'manifest.json').read_text());reference=json.loads((ROOT/'doc/php83/evidence/pilot83/payload-preparation-r4.json').read_text())
 if payload!=reference:raise ValueError('PAYLOAD_MANIFEST')
 cm=json.loads((control_dir/'manifest.json').read_text());cref=json.loads((ROOT/'doc/php83/evidence/pilot83/control-preparation-r1.json').read_text())
 if cm!=cref:raise ValueError('CONTROL_MANIFEST')
 hook_reference=json.loads((ROOT/'doc/php83/evidence/pilot83/hooks-transformation-r2.json').read_text())
 hook_pins={(r.get('package',''),r.get('hook',r.get('path'))):r['after_sha256'] for r in hook_reference['rows']}
 inputs=json.loads(source.pinned(ROOT/'doc/php83/evidence/pilot83/published-control-inputs.json',source.INPUT_PIN))
 out.mkdir();(out/'input').mkdir();(out/'packages').mkdir();(out/'stages').mkdir();results=[]
 with tarfile.open(fileobj=io.BytesIO(source.pinned(source.BUNDLE,source.BUNDLE_PIN)),mode='r:gz') as bundle:
  for pkg in inputs['packages']:
   name=pkg['control']['Package'];raw=bundle.extractfile(pkg['member']).read()
   if sha(raw)!=pkg['sha256']:raise ValueError('DEB_INPUT')
   inp=out/'input'/(name+'.deb');inp.write_bytes(raw);stage=out/'stages'/name
   run(['dpkg-deb','--raw-extract',str(inp),str(stage)])
   deltas=[]
   def apply(rel,data,reason,absent=False,mode=0o644):
    target=stage/rel;regular(target,stage,absent);before=None if absent else sha(target.read_bytes())
    write_delta(target,stage,data,mode=mode,absent=absent)
    st=target.stat();deltas.append({'path':rel,'reason':reason,'before_sha256':before,'after_sha256':sha(data),'mode':stat.S_IMODE(st.st_mode),'uid':st.st_uid,'gid':st.st_gid})
   before=(stage/'DEBIAN/control').read_bytes();after,_=controls.transform(before,name)
   if after!=(control_dir/name/'control').read_bytes():raise ValueError('CONTROL_BYTES')
   apply('DEBIAN/control',after,'private version/native83 dependency selection')
   for hook in ('preinst','postinst','prerm','postrm','config'):
    f=stage/'DEBIAN'/hook
    if not f.exists():continue
    regular(f,stage);before=f.read_bytes();after,meta=hooks.transform(name,hook,before)
    if sha(after)!=hook_pins[(name,hook)]:raise ValueError('HOOK_OUTPUT')
    if after!=before:apply('DEBIAN/'+hook,after,'reviewed private hook transport')
   for row in payload['source_changes']:
    if row['package']!=name:continue
    rel='opt/kaltura/app/'+row['path'];target=stage/rel
    if row['operation']=='replace' and sha(target.read_bytes())!=row['published_sha256']:raise ValueError('PUBLISHED_JOIN')
    data=(payload_dir/'replacements'/name/rel).read_bytes()
    if sha(data)!=row['after_sha256']:raise ValueError('PAYLOAD_OUTPUT')
    apply(rel,data,'selected exp14/privacy composition',row['operation']=='add',row['mode'])
   helper=stage/hooks.PAYLOAD_PATH
   if helper.exists():
    regular(helper,stage);after,meta=hooks.transform_payload(hooks.PAYLOAD_PATH,helper.read_bytes())
    if sha(after)!=hook_pins[('',hooks.PAYLOAD_PATH)]:raise ValueError('PAYLOAD_HELPER_OUTPUT')
    apply(hooks.PAYLOAD_PATH,after,'reviewed reached installation helper')
   if name=='kaltura-postinst':
    for filename in ('private-hook-functions.sh','private-argv.php'):
     apply('opt/kaltura/bin/pilot83-'+filename,(HERE/filename).read_bytes(),'private installer transport',True)
   sums=[]
   for f in sorted(stage.rglob('*')):
    if f.is_file() and not f.is_symlink() and not f.is_relative_to(stage/'DEBIAN'):
     sums.append(hashlib.md5(f.read_bytes()).hexdigest()+'  '+str(f.relative_to(stage)))
   checksum=stage/'DEBIAN/md5sums';apply('DEBIAN/md5sums',checksum_bytes(sums),'regenerated package file checksums',not checksum.exists())
   version=next(r['after_version'] for r in cm['packages'] if r['package']==name)
   output=out/'packages'/f"{name}_{version}_{pkg['control']['Architecture']}.deb"
   env=dict(os.environ,SOURCE_DATE_EPOCH='1758844800',TZ='UTC',LC_ALL='C')
   run(['dpkg-deb','--build','--uniform-compression','-Zxz','-z6',str(stage),str(output)],env=env)
   results.append({'package':name,'input_sha256':pkg['sha256'],'file':str(output),'sha256':sha(output.read_bytes()),'bytes':output.stat().st_size,'deltas':deltas})
 report={'status':'PRIVATE_DEBS_BUILT_NOT_VERIFIED_NOT_INSTALLED','freeze_hashes':freezes,'packages':results,'installed':False,'hooks_executed':False,'published':False}
 (out/'build-report.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('output',type=pathlib.Path);p.add_argument('--payload',type=pathlib.Path,required=True);p.add_argument('--controls',type=pathlib.Path,required=True);a=p.parse_args();print(json.dumps(build(a.output,a.payload,a.controls),indent=2))
