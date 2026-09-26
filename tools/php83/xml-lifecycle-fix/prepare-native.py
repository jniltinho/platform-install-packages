"""Stage pinned baseline + held candidate locally; no VM or artifact mutation."""
import hashlib,json,shutil,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
OLD=Path('/tmp/php-xml-lifecycle-prep-r2')
def H(b):return hashlib.sha256(b).hexdigest()
def prepare(out):
 if out.exists():raise ValueError('Refuse existing stage')
 pins=json.loads((HERE.parent/'xml-lifecycle/source-pins.json').read_text())['exp11']
 meta=json.loads((ROOT/'patches/php83/held/xml-lifecycle/manifest.json').read_text())
 if meta['selected_in_artifact'] or len(meta['changes'])!=3:raise ValueError('Wrong held state')
 payload={}
 for p,h in pins['files'].items():
  b=(OLD/'exp11'/p).read_bytes()
  if H(b)!=h:raise ValueError('Baseline source drift')
  payload['baseline/'+p]=b;payload['candidate/'+p]=b
 for change in meta['changes']:
  if change['operation']=='modify' and H(payload['candidate/'+change['path']])!=change['before_sha256']:raise ValueError('Before patch drift')
  b=(HERE/'candidate-tree'/change['path']).read_bytes()
  if H(b)!=change['after_sha256']:raise ValueError('Held candidate drift')
  if H((ROOT/change['patch']).read_bytes())!=change['patch_sha256']:raise ValueError('Patch drift')
  payload['candidate/'+change['path']]=b
 for p in sorted((OLD/'fixtures').iterdir()):payload['fixtures/'+p.name]=p.read_bytes()
 for name in ['behavior.php','scope-probe.php','run-native.sh']:payload[name]=(HERE/name).read_bytes()
 provider=json.loads(Path('/tmp/php-xml-lifecycle-private-prep-r2/providers.json').read_text())['83']
 if provider['package_sha256']!='eeb541e17950d330e01f5d0c47620ad45de92b64517320980691646777e4ad29':raise ValueError('SOAP provider pin')
 payload['provider.json']=(json.dumps(provider,indent=2)+'\n').encode()
 out.mkdir(parents=True)
 for name,b in payload.items():
  p=out/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
 for v in ['baseline','candidate']:
  for d in ['configurations','vendor/ZendFramework/library']:(out/v/d).mkdir(parents=True)
 manifest={'files':{p:H(b) for p,b in sorted(payload.items())},'base_archive_sha256':pins['archive_sha256'],'held_manifest_sha256':H((ROOT/'patches/php83/held/xml-lifecycle/manifest.json').read_bytes()),'phase':'xml-lifecycle-held-A-r1','application_patch_selected':False}
 (out/'identities.json').write_text(json.dumps(manifest,indent=2)+'\n')
 return {'manifest_sha256':H((out/'identities.json').read_bytes()),'files':len(payload),'phase':manifest['phase']}
if __name__=='__main__':print(json.dumps(prepare(Path(sys.argv[1]))))
