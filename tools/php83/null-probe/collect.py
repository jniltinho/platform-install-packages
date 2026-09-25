#!/usr/bin/env python3
"""Focused actual-class contract checks; no DB, server, or production writes."""
import argparse, hashlib, json, subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent

def require(condition, message):
    if not condition: raise RuntimeError(message)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('output',type=Path);args=parser.parse_args()
    require(not args.output.exists(), 'Refusing to overwrite evidence')
    expected={'null-probe/'+name:hashlib.sha256((HERE/name).read_bytes()).hexdigest() for name in ['probe.php','run.sh']}
    expected['tests/api-bootstrap.php']=hashlib.sha256((HERE.parent/'patch-tests/api-bootstrap.php').read_bytes()).hexdigest()
    rows=[]
    for version,alias in [('74','baseline74'),('83','php83')]:
        ssh=['ssh','-T','-F','/tmp/kaltura-php'+version+'-ssh.conf',alias]
        def remote(command):
            return subprocess.run(ssh+[command],text=True,capture_output=True,timeout=90)
        check=remote('cd /home/vagrant/php-exp5-regression && sha256sum '+' '.join(expected))
        require(check.returncode==0, 'Hash command failed')
        require({line.split()[1]:line.split()[0] for line in check.stdout.splitlines()}==expected, 'Fixture drift')
        for source in ['exp4','exp5']:
            verified=remote('python3 /home/vagrant/php-'+source+'-regression/api/verify-source.py')
            require(verified.returncode==0,'Artifact source drift')
            result=remote('bash /home/vagrant/php-exp5-regression/null-probe/run.sh '+source)
            require(result.returncode==0,'Focused fixture failed: '+version+'/'+source)
            observed=json.loads(result.stdout)
            require(len(observed['rows'])==41, 'Missing cases')
            rows.append({'runtime':version,'source':source,'artifact':json.loads(verified.stdout),'exit':result.returncode,'result':observed,'bootstrap_stderr':result.stderr})
    comparisons=[]
    for version in ['74','83']:
        before=next(row for row in rows if row['runtime']==version and row['source']=='exp4')
        after=next(row for row in rows if row['runtime']==version and row['source']=='exp5')
        same=json.dumps(before['result']['rows'],sort_keys=True)==json.dumps(after['result']['rows'],sort_keys=True)
        require(same,'Same-runtime contract drift')
        comparisons.append({'runtime':version,'all_41_contract_rows_equal':same})
    report={'schema':1,'scope':'41 actual-class cases, real bootstrap, in-memory logging sink; no PermissionPeer SQL dependency branches','harness':expected,'collector_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'rows':rows,'comparisons':comparisons,'functional_checks_passed':True,'application_acceptance':False}
    args.output.write_text(json.dumps(report,indent=2)+'\n');print('PASS: 41 actual-class cases preserve same-runtime behavior on PHP7.4/8.3; diagnostics retained')
if __name__=='__main__':main()
