import hashlib,json,zipfile
from pathlib import Path
root=Path('/home/vagrant/php-exp3-regression'); archive=root/'exp3.zip'
expected='1c64edb5ff34308cedfcea3c7879187c21417b6bd1a8e083d70d580bedc985e3'
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
