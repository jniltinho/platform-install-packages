"""Closed stage plus exact runtime identities; never prints source or credentials."""
import hashlib,json,pathlib,re,sys
sha=lambda b:hashlib.sha256(b).hexdigest()
def verify(root,pin,check_runtime=True):
 root=pathlib.Path(root)
 if root.is_symlink() or re.fullmatch('[a-f0-9]{64}',pin) is None:raise ValueError('ROOT_PIN')
 raw=(root/'runner-manifest.json').read_bytes()
 if sha(raw)!=pin:raise ValueError('MANIFEST_DRIFT')
 m=json.loads(raw);files=m['files']
 if type(files) is not dict or not files:raise ValueError('EMPTY_FILES')
 for name,h in files.items():
  p=pathlib.PurePosixPath(name)
  if p.is_absolute() or '..' in p.parts or re.fullmatch('[a-f0-9]{64}',h) is None:raise ValueError('ENTRY')
 actual={}
 for p in root.rglob('*'):
  if p.is_symlink():raise ValueError('SYMLINK')
  if p.is_file() and str(p.relative_to(root))!='runner-manifest.json':actual[str(p.relative_to(root))]=sha(p.read_bytes())
 if actual!=files:raise ValueError('STAGE_DRIFT')
 if type(m.get('runtime_files')) is not dict or not m['runtime_files']:raise ValueError('EMPTY_RUNTIME')
 if check_runtime:
  for name,h in m['runtime_files'].items():
   if not pathlib.Path(name).is_absolute() or re.fullmatch('[a-f0-9]{64}',h) is None or sha(pathlib.Path(name).read_bytes())!=h:raise ValueError('RUNTIME_DRIFT')
 return m
if __name__=='__main__':verify(sys.argv[1],sys.argv[2]);print('VERIFIED')
