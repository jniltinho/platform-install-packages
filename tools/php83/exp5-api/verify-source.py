import hashlib,json,zipfile
if not __debug__:raise RuntimeError("Optimized Python is not supported by this verifier")
from pathlib import Path
root=Path('/home/vagrant/php-exp5-regression'); archive=root/'exp5.zip'
expected='ef4d3e67c077014ba4837c83eec57ee7e0bf3548e444337ee92b19dad27bbcf5'
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
