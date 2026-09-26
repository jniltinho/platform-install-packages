#!/usr/bin/env python3
"""Four fresh snapshot identities; reject pending/mismatched collector provenance."""
import argparse,hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest()
def compare(before74,after74,before83,after83):
 result={}
 for label,a,b,helper in [('baseline74',before74,after74,'runtime-identity.py'),('native83',before83,after83,'runtime83-identity.py')]:
  for report in [a,b]:
   if type(report['exit']) is not int or report['exit']!=0:raise ValueError('Snapshot status')
   if report['collector_sha256']!=sha((HERE/helper).read_bytes()):raise ValueError('Snapshot collector drift')
  if a['identity']!=b['identity']:raise ValueError('Native identity drift '+label)
  if a['command']!=b['command']:raise ValueError('Snapshot command drift')
  result[label]={'unchanged':True,'identity_sha256':sha(json.dumps(a['identity'],sort_keys=True,separators=(',',':')).encode())}
 if before74['artifact_pin']!=(HERE/'artifact-sha256.txt').read_text().strip() or after74['artifact_pin']!=before74['artifact_pin']:raise ValueError('Artifact pin mismatch')
 return result
if __name__=='__main__':
 p=argparse.ArgumentParser()
 for n in ['before74','after74','before83','after83','output']:p.add_argument(n,type=Path)
 a=p.parse_args();inputs=[a.before74,a.after74,a.before83,a.after83];r=compare(*[json.loads(x.read_text()) for x in inputs])
 with a.output.open('x') as f:json.dump({'identities':r,'inputs':{str(x):sha(x.read_bytes()) for x in inputs},'application_acceptance':False},f,indent=2);f.write('\n')
 print(json.dumps(r))
