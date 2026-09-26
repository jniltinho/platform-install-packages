#!/usr/bin/env python3
import hashlib,json,pathlib,re,sys
sha=lambda b:hashlib.sha256(b).hexdigest()
def verify(root,pin):
 root=pathlib.Path(root)
 if root.is_symlink() or re.fullmatch('[a-f0-9]{64}',pin) is None:raise ValueError('Unsafe root/pin')
 raw=(root/'manifest.json').read_bytes()
 if sha(raw)!=pin:raise ValueError('Manifest drift')
 d=json.loads(raw);files=d['files']
 if not isinstance(files,dict) or not files:raise ValueError('Empty file map')
 actual={}
 for p in root.rglob('*'):
  if p.is_symlink():raise ValueError('Symlink')
  if p.is_file() and str(p.relative_to(root))!='manifest.json':actual[str(p.relative_to(root))]=sha(p.read_bytes())
 for name,pin in files.items():
  if pathlib.PurePosixPath(name).is_absolute() or '..' in pathlib.PurePosixPath(name).parts or re.fullmatch('[a-f0-9]{64}',pin) is None:raise ValueError('Unsafe entry')
 if actual!=files:raise ValueError('File map drift')
 return d
if __name__=='__main__':verify(sys.argv[1],sys.argv[2]);print('verified')
