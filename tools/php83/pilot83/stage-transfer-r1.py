"""Guest root: promote a verified non-secret artifact stage, no package install."""
import hashlib,json,os,pathlib,socket,stat
assert os.geteuid()==0 and socket.gethostname()=='kaltura-php83-lab'
source=pathlib.Path('/home/vagrant/pilot83-transfer-r1');dest=pathlib.Path('/var/lib/kaltura-php83-pilot')
assert source.is_dir() and not source.is_symlink() and not os.path.lexists(dest)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(source/'transfer-manifest.json')=='da3f5823a919c36fe4db495a424a66d00caab76d8928d2fd0b1cc9f8fd96bee9'
manifest=json.loads((source/'transfer-manifest.json').read_text())
expected=set(manifest['files'])|{'transfer-manifest.json'}
actual=set()
for p in source.rglob('*'):
 st=p.lstat();assert stat.S_ISDIR(st.st_mode) or stat.S_ISREG(st.st_mode)
 if stat.S_ISREG(st.st_mode):assert st.st_nlink==1;actual.add(str(p.relative_to(source)))
assert actual==expected
for n,pin in manifest['files'].items():assert sha(source/n)==pin
os.rename(source,dest);os.chown(dest,0,0);os.chmod(dest,0o755)
for p in sorted(dest.rglob('*')):
 st=p.lstat();assert stat.S_ISDIR(st.st_mode) or stat.S_ISREG(st.st_mode)
 os.chown(p,0,0);os.chmod(p,0o755 if stat.S_ISDIR(st.st_mode) else 0o444)
for n,pin in manifest['files'].items():assert sha(dest/n)==pin
assert sha(dest/'transfer-manifest.json')=='da3f5823a919c36fe4db495a424a66d00caab76d8928d2fd0b1cc9f8fd96bee9'
print(json.dumps({'status':'NONSECRET_ARTIFACT_STAGE_VERIFIED','files':len(actual),'packages_private':17,'package_external':1,'plugin_external':1,'manifest_sha256':sha(dest/'transfer-manifest.json'),'root_owned':True,'private_credentials_generated':False,'installed':False}))
