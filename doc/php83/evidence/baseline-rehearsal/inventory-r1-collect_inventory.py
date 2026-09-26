#!/usr/bin/env python3
"""Authorized exclusive74 read-only inventory; no guest staging or credential reads."""
import hashlib,json,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent
OUT=HERE.parents[2]/'doc/php83/evidence/baseline-rehearsal'
def main():
    paths=[OUT/('inventory-primary'+s) for s in ['.json','.stderr-sha256','.exit']]
    if any(p.exists() for p in paths):raise ValueError('Refuse existing inventory')
    code=(HERE/'guest_inventory.py').read_bytes()
    r=subprocess.run(['ssh','-T','-F','/tmp/kaltura-php74-ssh.conf','baseline74','python3 -'],input=code,capture_output=True,timeout=120)
    paths[1].write_text(hashlib.sha256(r.stderr).hexdigest()+'\n');paths[2].write_text(str(r.returncode)+'\n')
    if r.returncode:raise ValueError('Read-only inventory failed; raw stderr not exported')
    result=json.loads(r.stdout)
    if result.get('status')!='READ_ONLY_PUBLIC_INVENTORY_NOT_ATTESTATION' or result.get('hostname')!='kaltura-php74-baseline':raise ValueError('Inventory binding')
    report={'collector_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'guest_program_sha256':hashlib.sha256(code).hexdigest(),'exit':r.returncode,'observation':result,'raw_stdout_sha256':hashlib.sha256(r.stdout).hexdigest(),'native_attestation_complete':False}
    paths[0].write_text(json.dumps(report,indent=2)+'\n')
    print('Public inventory recorded; native web/source/config and media attestation remain pending.')
if __name__=='__main__':main()
