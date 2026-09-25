#!/usr/bin/env python3
"""Read-only focused lab rerun; requires pre-staged, hash-matched fixtures."""
import argparse, hashlib, json, subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent
REPO=HERE.parents[2]
def main():
 p=argparse.ArgumentParser();p.add_argument('output',type=Path);a=p.parse_args()
 if a.output.exists():raise RuntimeError('Evidence already exists')
 metadata=json.loads((REPO/'patches/php83/held/Criteria-null-alias.json').read_text())
 expected={'original.php':metadata['before_sha256'],'candidate.php':metadata['after_sha256']}
 expected.update({n:hashlib.sha256((HERE/n).read_bytes()).hexdigest() for n in ['probe.php','run.sh']})
 rows=[]
 for version,alias in [('74','baseline74'),('83','php83')]:
  ssh=['ssh','-T','-F','/tmp/kaltura-php'+version+'-ssh.conf',alias]
  check=subprocess.run(ssh+['cd /home/vagrant/php-criteria-null-probe && sha256sum original.php candidate.php probe.php run.sh'],text=True,capture_output=True,timeout=30)
  assert check.returncode==0
  assert {l.split()[1]:l.split()[0] for l in check.stdout.splitlines()}==expected
  for tree in ['original','candidate']:
   command='bash /home/vagrant/php-criteria-null-probe/run.sh '+tree
   r=subprocess.run(ssh+[command],text=True,capture_output=True,timeout=60)
   assert r.returncode==0,(version,tree,r.stderr)
   result=json.loads(r.stdout)
   assert len(result['rows'])==8
   rows.append(dict(runtime=version,tree=tree,command=command,exit=r.returncode,stderr=r.stderr,result=result))
 baseline=rows[0]['result']['rows']
 assert all(r['result']['rows']==baseline for r in rows)
 null_counts=[]
 for row in rows:
  count=sum('strlen()' in d[1] and 'null' in d[1] for d in row['result']['diagnostics'])
  null_counts.append(count)
 assert null_counts==[0,0,3,0],null_counts
 report={'schema':1,'scope':'real Criteria/Criterion, fixture-only DB adapter, no SQL acceptance','harness':expected,'patch':metadata,'rows':rows,'null_diagnostic_counts':null_counts,'focused_pass':True,'application_acceptance':False}
 a.output.write_text(json.dumps(report,indent=2)+'\n');print('PASS: eight alias contracts on both runtimes, three null deprecations removed; other diagnostics retained')
if __name__=='__main__':main()
