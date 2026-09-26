#!/usr/bin/env python3
import hashlib,json,pathlib,sys
sha=lambda b:hashlib.sha256(b).hexdigest()
def verify(root,pin):
 root=pathlib.Path(root); raw=(root/'identities.json').read_bytes()
 if sha(raw)!=pin:raise ValueError('Manifest drift')
 ids=json.loads(raw)
 if set(ids['variants'])!={'exp12','prerequisite','candidate'}:raise ValueError('Wrong variants')
 expected={'identities.json':pin}
 for variant,files in ids['variants'].items():
  if len(files)!=7:raise ValueError('Wrong source count')
  for p,digest in files.items():
   rel=pathlib.PurePosixPath(p)
   if rel.is_absolute() or '..' in rel.parts:raise ValueError('Unsafe path')
   expected[variant+'/'+p]=digest
 for p,digest in ids['harness'].items():expected[p]=digest
 actual={}
 for p in root.rglob('*'):
  if p.is_symlink():raise ValueError('Symlink stage')
  if p.is_file():actual[str(p.relative_to(root))]=sha(p.read_bytes())
 if actual!=expected:raise ValueError('Stage identity drift')
 return ids
if __name__=='__main__':verify(sys.argv[1],sys.argv[2]);print('SOURCE_HARNESS_IDENTITIES_OK')
