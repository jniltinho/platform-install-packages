#!/usr/bin/env python3
import argparse,hashlib,json,pathlib,subprocess,sys,zipfile
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[2]
ZIP_SHA='de5e61a1b54f472e605ef2e87669302a3915616fd85378e0f05706fcb06a7e8b'
COMPOSE=ROOT/'tools/php83/return-contracts/compose.py'
COMPOSITION=ROOT/'doc/php83/evidence/return-contracts/composition-preparation-r2.json'
COMPOSITION_SHA='1dc5c3aaefff37ec506434132b20028281f14232219f60b896b3aeca675da024'
EXTRA=['vendor/propel/Propel.php','vendor/propel/PropelException.php','vendor/propel/util/DebugPDOStatement.php','alpha/apps/kaltura/lib/db/KalturaStatement.php']
HARNESS=['probe.php','seams.php','run.sh','start-db.sh','verify.py']
sha=lambda b:hashlib.sha256(b).hexdigest()
def prepare(archive,out):
 out=pathlib.Path(out)
 if out.exists():raise ValueError('Output exists')
 if sha(pathlib.Path(archive).read_bytes())!=ZIP_SHA:raise ValueError('Wrong ZIP')
 raw=COMPOSITION.read_bytes()
 if sha(raw)!=COMPOSITION_SHA:raise ValueError('Composition authority changed')
 expected=json.loads(raw)
 r=subprocess.run([sys.executable,str(COMPOSE),'--zip',str(archive),'--output',str(out)],capture_output=True,text=True)
 if r.returncode:raise ValueError('Composition failed: '+r.stderr)
 ids=json.loads((out/'identities.json').read_text())
 if ids['variants']!=expected['variants']:raise ValueError('Composition differs')
 (out/'identities.json').unlink()
 with zipfile.ZipFile(archive) as z:
  for cohort in ['exp12','prerequisite','candidate']:
   for name in EXTRA:
    p=out/cohort/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(z.read('server-Rigel-18.20.0/'+name))
 for name in HARNESS:(out/name).write_bytes((HERE/name).read_bytes())
 files={str(p.relative_to(out)):sha(p.read_bytes()) for p in sorted(out.rglob('*')) if p.is_file()}
 result={'zip_sha256':ZIP_SHA,'composition_sha256':COMPOSITION_SHA,'files':files,'cohorts':['prerequisite','candidate'],'application_acceptance':False}
 (out/'manifest.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--zip',required=True);p.add_argument('--output',type=pathlib.Path,required=True);a=p.parse_args();print(json.dumps(prepare(a.zip,a.output)))
