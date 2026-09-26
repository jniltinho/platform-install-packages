"""Instrumentation-only fork of frozen held stage; product bytes cannot change."""
import hashlib,json,shutil,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
OLD=Path('/tmp/php-xml-lifecycle-fix-prep-r1')
def prepare(out):
 if out.exists():raise ValueError('Refuse existing chain stage')
 mb=(OLD/'identities.json').read_bytes()
 if hashlib.sha256(mb).hexdigest()!='c06f54b7dff9035ea1680d96416ab29d7b4669a5dbe26e417bedccf27d742a08':raise ValueError('Base stage drift')
 m=json.loads(mb)
 for p,h in m['files'].items():
  if hashlib.sha256((OLD/p).read_bytes()).hexdigest()!=h:raise ValueError('Frozen base payload drift')
 shutil.copytree(OLD,out)
 (out/'behavior.php').write_bytes((HERE/'behavior-chain.php').read_bytes())
 run=(OLD/'run-native.sh').read_text().replace('php-xml-lifecycle-fix-r1','php-xml-lifecycle-fix-chain-r1').replace('xml-lifecycle-held-A-r1','xml-lifecycle-held-A-chain-r1')
 (out/'run-native.sh').write_text(run)
 for p in ['behavior.php','run-native.sh']:m['files'][p]=hashlib.sha256((out/p).read_bytes()).hexdigest()
 m['phase']='xml-lifecycle-held-A-chain-r1';(out/'identities.json').write_text(json.dumps(m,indent=2)+'\n')
 return {'manifest_sha256':hashlib.sha256((out/'identities.json').read_bytes()).hexdigest(),'files':len(m['files']),'changed_stage_payload':['behavior.php','run-native.sh'],'product_files_changed':False}
if __name__=='__main__':print(json.dumps(prepare(Path(sys.argv[1]))))
