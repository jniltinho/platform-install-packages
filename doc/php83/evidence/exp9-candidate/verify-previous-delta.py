"""Verify that exp9 adds exactly the two reviewed boolean-result repairs."""
import hashlib, json, zipfile
from pathlib import Path

def require(value):
    if not value:
        raise RuntimeError('Previous artifact comparison failed')

base = Path('/home/nilton/Projetos/nilton/NOVOS/platform-install-packages-php83-artifacts')
root = 'server-Rigel-18.20.0/'
meta = root + '.php83-experimental/'
entries = [json.loads(Path('patches/php83/held/' + n + '.json').read_text())
           for n in ['PropelPDO-bool-setAttribute', 'KalturaStatement-bool-results']]
with zipfile.ZipFile(base/'exp8/Rigel-18.20.0-php83-experimental.exp8.zip') as old, zipfile.ZipFile(base/'exp9/Rigel-18.20.0-php83-experimental.exp9.zip') as new:
    names = {n for n in old.namelist() if not n.startswith(meta)}
    require(names == {n for n in new.namelist() if not n.startswith(meta)})
    changed = [n for n in sorted(names) if old.read(n) != new.read(n)]
    require(changed == sorted(root + e['path'] for e in entries))
    for e in entries:
        require(hashlib.sha256(old.read(root + e['path'])).hexdigest() == e['before_sha256'])
        require(hashlib.sha256(new.read(root + e['path'])).hexdigest() == e['after_sha256'])
    prior = json.loads(Path('doc/php83/evidence/exp8-candidate/manifest.json').read_text())
    current = json.loads(Path('doc/php83/evidence/exp9-candidate/manifest.json').read_text())
    require(current['patches'][:len(prior['patches'])] == prior['patches'])
    require(len(current['patches']) == len({p['path'] for p in current['patches']}) == 16)
report = {'previous':'exp8', 'candidate':'exp9', 'changed_application_files':changed,
          'all_other_application_bytes_identical':True, 'prior_fourteen_entries_preserved':True,
          'manifest_unique_targets':16, 'public_null_to_bool_change_intentional':True,
          'verifier_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
          'application_acceptance':False}
Path(__file__).with_name('previous-delta.json').write_text(json.dumps(report,indent=2)+'\n')
print('Exact previous-to-candidate delta verified')
