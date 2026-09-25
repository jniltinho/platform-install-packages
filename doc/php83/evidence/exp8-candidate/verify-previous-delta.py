"""Verify cumulative selection and exact exp7-to-exp8 application-byte delta."""
import hashlib,json,zipfile
from pathlib import Path

def require(value):
    if not value:raise RuntimeError('Previous artifact comparison failed')
base=Path('/home/nilton/Projetos/nilton/NOVOS/platform-install-packages-php83-artifacts')
path='server-Rigel-18.20.0/vendor/propel/util/Criteria.php'
meta='server-Rigel-18.20.0/.php83-experimental/'
with zipfile.ZipFile(base/'exp7/Rigel-18.20.0-php83-experimental.exp7.zip') as a, zipfile.ZipFile(base/'exp8/Rigel-18.20.0-php83-experimental.exp8.zip') as b:
    names_a={n for n in a.namelist() if not n.startswith(meta)}
    names_b={n for n in b.namelist() if not n.startswith(meta)}
    require(names_a==names_b)
    changed=[n for n in sorted(names_a) if a.read(n)!=b.read(n)]
    require(changed==[path])
    m=json.loads(Path('patches/php83/held/Criteria-native-returns.json').read_text())
    previous,candidate=a.read(path),b.read(path)
    require(hashlib.sha256(previous).hexdigest()==m['prior_candidate_sha256'])
    require(hashlib.sha256(candidate).hexdigest()==m['after_sha256'])
    # Use the exact existing patch line, including source whitespace.
    added=[l[1:] for l in Path('patches/php83/held/Criteria-null-alias.patch').read_bytes().splitlines() if l.startswith(b'+') and not l.startswith(b'+++')]
    require(len(added)==1 and added[0] in previous and added[0] in candidate)
    reverted=candidate
    for method,typ in {'getIterator':'Traversable','rewind':'void','valid':'bool','key':'mixed','current':'mixed','next':'void'}.items():
        old=('public function '+method+'()').encode();new=old+b': '+typ.encode()
        require(reverted.count(new)==1);reverted=reverted.replace(new,old)
    require(reverted==previous)
    manifest=json.loads(Path('doc/php83/evidence/exp8-candidate/manifest.json').read_text())
    require(len(manifest['patches'])==len({p['path'] for p in manifest['patches']})==14)
    require(all(p['patch']!='Criteria-null-alias.patch' for p in manifest['patches']))
    require(sum(p['patch']=='Criteria-native-returns.patch' for p in manifest['patches'])==1)
report={'previous':'exp7','candidate':'exp8','changed_application_files':changed,'all_other_application_bytes_identical':True,'only_six_return_declarations_changed':True,'prior_criteria_sha256':m['prior_candidate_sha256'],'candidate_criteria_sha256':m['after_sha256'],'prior_null_alias_guard_retained':True,'manifest_unique_targets':14,'cumulative_patch_replaces_old_entry':True,'verifier_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'application_acceptance':False}
Path(__file__).with_name('previous-delta.json').write_text(json.dumps(report,indent=2)+'\n')
print('Exact previous-to-candidate delta verified')
