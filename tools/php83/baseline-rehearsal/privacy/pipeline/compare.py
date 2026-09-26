"""Replay existing native receipts only; never execute PHP/SSH."""
import argparse,hashlib,json
from pathlib import Path
import validate
def compare(folder):
 stage=json.loads((folder/'stage.json').read_text())['manifest']
 reports=[json.loads((folder/(n+'.json')).read_text()) for n in ['primary','claude']]
 if (folder/'primary.json').read_bytes()!=(folder/'claude.json').read_bytes():raise ValueError('Native report bytes differ')
 for label,r in zip(['primary','claude'],reports):
  if r['exit']!=0 or len(r['lints'])!=12 or any(x['exit']!=0 for x in r['lints']):raise ValueError('Native exits')
  if r['source_before']!=stage['files'] or r['source_after']!=stage['files'] or r['php_sha256_after']!=stage['php_sha256']:raise ValueError('Source/runtime drift')
  validate.validate(json.loads(r['stdout']),stage)
  cleanup=json.loads((folder/(label+'-cleanup.json')).read_text())
  if cleanup['unit']!='php83-privacy-pipeline-r1-'+label or not cleanup['inactive'] or cleanup['state'] not in ['inactive','unknown']:raise ValueError('Cleanup')
 identities=[json.loads((folder/(n+'.json')).read_text()) for n in ['primary-before','primary-after','claude-before','claude-after']]
 if any(x['exit']!=0 or x['identity']!=identities[0]['identity'] for x in identities):raise ValueError('Runtime snapshots')
 return {'status':'EXACT_REPEATED_SYNTHETIC_EXPECTED_LEAK','cases':6,'native_diagnostics':len(json.loads(reports[0]['stdout'])['diagnostics']),'native_stderr_bytes':len(reports[0]['stderr'].encode()),'privacy_acceptance':False,'application_acceptance':False}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('folder',type=Path);a=p.parse_args();print(json.dumps(compare(a.folder),sort_keys=True))
