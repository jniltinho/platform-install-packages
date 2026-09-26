#!/usr/bin/env python3
"""Forty actual artifact processes, exact reviewed functional/diagnostic corpus."""
import argparse
import base64
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def sha(b):return hashlib.sha256(b).hexdigest()
def need(ok,msg):
 if not ok:raise ValueError(msg)
def inputs():
 raw=(HERE/'input-pins.json').read_bytes();need(sha(raw)=='47600e9c590fde735cec6027456f4ee1f8747f237a58d7bc7f6cd81d758a0de8','Input pins drift');pins=json.loads(raw)
 for path,pin in pins.items():need(sha((ROOT/path).read_bytes())==pin,'Frozen contract/reference drift')
 return {k:json.loads((ROOT/k).read_bytes()) for k in pins if k.endswith('.json')}
def same(a,b):return json.dumps(a,sort_keys=True,separators=(',',':'),allow_nan=False)==json.dumps(b,sort_keys=True,separators=(',',':'),allow_nan=False)
def expected_rows():
 refs=inputs();matrix=refs['doc/php83/evidence/xml-lifecycle-fix/primary.json']['records'];chain=refs['doc/php83/evidence/xml-lifecycle-fix/claude-chain-matrix.json']['records']
 return [('matrix',r['kind'],r['variant'],r['case'],r) for r in matrix]+[('chain','behavior',r['variant'],'callback-throw',r) for r in chain]
def validate(row,reference,manifest):
 need(type(row['exit']) is int and row['exit']==0,'Native integer exit0')
 need(row['stdout']==reference['stdout'] and row['stderr']==reference['stderr'],'Reviewed complete native channels differ')
 body=json.loads(row['stdout']);variant=row['variant']
 if row['kind']=='behavior':
  expected={p[len(variant)+1:]:h for p,h in manifest['files'].items() if p.startswith(variant+'/')};need(same(body['loaded'],expected),'Loaded artifact closure')
 else:need(body['helper_sha256']==manifest['files']['candidate/infra/general/kXmlEntityLoaderPolicy.php'],'Loaded artifact helper')
 need(body['probe_sha256']==manifest['files']['behavior.php' if row['kind']=='behavior' else 'scope-probe.php'],'Probe identity')
 return body

def main():
 a=argparse.ArgumentParser();a.add_argument('output',type=Path);r=a.parse_args();need(not r.output.exists(),'Refuse existing report')
 prepraw=(ROOT/'doc/php83/evidence/exp13-xml/preparation.json').read_bytes();need(sha(prepraw)=='30b70f69246cf542853b79dc3fb3e2f175ce25e5810eb813d70f0d5daa99a5c7','Preparation identity');prep=json.loads(prepraw);records=[];failures=[]
 closure={p.name:sha(p.read_bytes()) for p in [Path(__file__),HERE/'input-pins.json']}
 for phase,kind,variant,case,reference in expected_rows():
  stage=prep['stages'][phase];directory=ROOT/stage['local'];mb=(directory/'identities.json').read_bytes();need(sha(mb)==stage['manifest_sha256'],'Local manifest')
  manifest=json.loads(mb)
  for p,h in manifest['files'].items():need(sha((directory/p).read_bytes())==h,'Local payload drift')
  cmd=['ssh','-T','-F','/tmp/kaltura-php83-ssh.conf','php83','bash '+stage['remote']+'/run-native.sh '+kind+' '+variant+' '+case+' '+stage['manifest_sha256']]
  row={'phase':phase,'kind':kind,'variant':variant,'case':case,'command':cmd};records.append(row)
  try:
   native=subprocess.run(cmd,capture_output=True,timeout=75);row['exit']=native.returncode
   for channel,b in [('stdout',native.stdout),('stderr',native.stderr)]:row[channel+'_base64']=base64.b64encode(b).decode();row[channel]=b.decode()
   row['body']=validate(row,reference,manifest);row['status']='MATCHES_REVIEWED_CORPUS'
  except (ValueError,KeyError,TypeError,OSError,subprocess.TimeoutExpired) as e:
   if isinstance(e,subprocess.TimeoutExpired):
    for channel,b in [('stdout',e.stdout or b''),('stderr',e.stderr or b'')]:row[channel+'_base64']=base64.b64encode(b).decode();row[channel]=b.decode(errors='replace')
   row['failure']={'type':type(e).__name__,'message':str(e)};failures.append([phase,kind,variant,case])
 report={'status':'MATCHED_40_ARTIFACT_PROCESSES' if not failures else 'FAIL_RETAINED_OBSERVATIONS','records':records,'failures':failures,'preparation_sha256':sha(prepraw),'collector_closure':closure,'artifact_pins':prep['artifact_pins'],'application_acceptance':False}
 need(closure=={p.name:sha(p.read_bytes()) for p in [Path(__file__),HERE/'input-pins.json']},'Collector changed')
 r.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'status':report['status'],'processes':len(records),'failures':len(failures)}));sys.exit(bool(failures))
if __name__=='__main__':main()
