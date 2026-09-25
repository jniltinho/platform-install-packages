import hashlib,json,zipfile
if not __debug__:raise RuntimeError("Optimized Python is not supported by this verifier")
from pathlib import Path
root=Path('/home/vagrant/php-exp6-regression'); archive=root/'exp6.zip'
expected='da11cbb9cc58e4e67d4eb8c875d651f272941c7d37d1209c63a02a48e4ba30be'
assert hashlib.sha256(archive.read_bytes()).hexdigest()==expected
source=root/'source'
assert not source.is_symlink()
assert all(not p.is_symlink() for p in source.rglob('*'))
with zipfile.ZipFile(archive) as z:
 names=[]
 for i in z.infolist():
  assert not Path(i.filename).is_absolute() and '..' not in Path(i.filename).parts
  if not i.is_dir():
   assert (root/'source'/i.filename).read_bytes()==z.read(i)
   names.append(i.filename)
 assert sorted(names)==sorted(str(p.relative_to(root/'source')) for p in (root/'source').rglob('*') if p.is_file())
print(json.dumps({'zip_sha256':expected,'verified_extracted_files':len(names)}))
