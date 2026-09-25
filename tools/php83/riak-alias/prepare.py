#!/usr/bin/env python3
"""Prepare held alias-only source in a fresh directory; never select an artifact."""
import argparse,hashlib,json,subprocess,zipfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
REPO=HERE.parents[2]
PINS=json.loads((HERE/'source-pins.json').read_text())
def sha(data):return hashlib.sha256(data).hexdigest()
def prepare(archive,out):
 if out.exists():raise ValueError('Refuse existing stage')
 if sha(archive.read_bytes())!=PINS['original_zip_sha256']:raise ValueError('Original ZIP drift')
 patch=REPO/'patches/php83/held/riak-object-alias/RiakCache-alias.patch'
 if sha(patch.read_bytes())!=PINS['patch_sha256']:raise ValueError('Patch drift')
 payload={}
 with zipfile.ZipFile(archive) as z:
  for name,want in PINS['files'].items():
   data=z.read('server-Rigel-18.20.0/'+name)
   if sha(data)!=want:raise ValueError('Source drift')
   payload[name]=data
 out.mkdir(parents=True)
 for variant in ['original','candidate']:
  for name,data in payload.items():
   p=out/variant/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
 r=subprocess.run(['patch','--batch','--fuzz=0','-p1','-i',str(patch)],cwd=out/'candidate',capture_output=True,text=True)
 if r.returncode or 'fuzz' in r.stdout.lower() or 'offset' in r.stdout.lower():raise ValueError('Nonexact patch')
 files={}
 for variant in ['original','candidate']:
  for name,want in PINS['files'].items():
   p=out/variant/name;actual=sha(p.read_bytes())
   if actual!=(PINS['candidate_sha256'] if variant=='candidate' and name.endswith('/RiakCache.php') else want):raise ValueError('Unexpected source delta')
   files[str(p.relative_to(out))]=actual
 for name in ['probe.php','run.sh']:
  (out/name).write_bytes((HERE/name).read_bytes());files[name]=sha((HERE/name).read_bytes())
 report={'files':files,'original_zip_sha256':PINS['original_zip_sha256'],'patch_sha256':PINS['patch_sha256'],'source_delta':'only Riak Object import alias, two new sites and one argument type','backend_acceptance':False}
 (out/'identities.json').write_text(json.dumps(report,indent=2)+'\n')
 return {'manifest_sha256':sha((out/'identities.json').read_bytes()),'files':len(files),'backend_acceptance':False}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('archive',type=Path);p.add_argument('out',type=Path);a=p.parse_args();print(json.dumps(prepare(a.archive,a.out)))
