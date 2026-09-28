"""Read-only host/guest public observation, never full baseline attestation."""
import hashlib,json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
UUID='9e954729-16f3-4eda-9db5-b94e5ada9e44'
NAME='kaltura-php74-noble-baseline'
GUEST='tools/php83/baseline-rehearsal/guest_inventory.py'
GUEST_SHA='5ddb8bbbb1b6fdc4e77c93bd7833c31b046196dc44c42f6874de279aed70b0a6'
def sha(b):return hashlib.sha256(b).hexdigest()
def host_projection(text):
    fields={}
    for line in text.splitlines():
        k,sep,v=line.partition('=')
        if not sep:continue
        k=k.strip('"');v=v.strip('"')
        if k in {'name','UUID','memory','cpus','chipset','firmware','VMState','CurrentSnapshotUUID'} or re.fullmatch(r'storagecontroller(?:name|type|hostiocache)\d+',k):
            if k in fields:raise ValueError('DUPLICATE_HOST_FIELD')
            fields[k]=v
    if fields.get('UUID')!=UUID or fields.get('name')!=NAME:raise ValueError('HOST_IDENTITY')
    if fields.get('memory')!='8192' or fields.get('cpus')!='4' or fields.get('VMState')!='running':raise ValueError('HOST_RESOURCES')
    return fields

def main(output):
    path=Path(output)
    if path.exists():raise ValueError('OUTPUT_EXISTS')
    if (ROOT/'deb/php74-baseline/.vagrant/machines/baseline74/virtualbox/id').read_text().strip()!=UUID:raise ValueError('VAGRANT_IDENTITY')
    before=subprocess.run(['VBoxManage','showvminfo',UUID,'--machinereadable'],capture_output=True,timeout=20,check=True)
    host=host_projection(before.stdout.decode())
    code=(ROOT/GUEST).read_bytes()
    if sha(code)!=GUEST_SHA:raise ValueError('GUEST_PIN')
    r=subprocess.run(['ssh','-T','-F','/tmp/kaltura-php74-ssh.conf','baseline74','python3 -B -'],input=code,capture_output=True,timeout=120)
    if r.returncode:raise ValueError('GUEST_INVENTORY_REJECTED')
    observation=json.loads(r.stdout)
    if observation.get('hostname')!='kaltura-php74-baseline' or observation.get('target_ip')!='192.168.56.74' or observation.get('status')!='READ_ONLY_PUBLIC_INVENTORY_NOT_ATTESTATION':raise ValueError('GUEST_IDENTITY')
    after=subprocess.run(['VBoxManage','showvminfo',UUID,'--machinereadable'],capture_output=True,timeout=20,check=True)
    if host_projection(after.stdout.decode())!=host:raise ValueError('HOST_DRIFT')
    result={'schema':1,'collector_sha256':sha(Path(__file__).read_bytes()),'guest_program_sha256':GUEST_SHA,'status':'PUBLIC_READ_ONLY_OBSERVATION_NOT_FULL_ATTESTATION','host_fields':host,'guest':observation,'guest_exit':r.returncode,'guest_stderr_sha256':sha(r.stderr),'limitations':['Box checksum and complete disk settings not attested','No guest RAM, web runtime, private config, full source or current profile attestation','No benchmark, upload, worker release, VM configuration or snapshot mutation'],'baseline_acceptance':False}
    with path.open('x') as f:json.dump(result,f,indent=2);f.write('\n')
    print(json.dumps({'status':result['status'],'vm_uuid':UUID,'cli_version':observation['cli_version'],'sha256':sha(path.read_bytes())}))
if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);a=p.parse_args()
    try:main(a.output)
    except Exception as e:
        print(json.dumps({'status':'REJECTED','error_type':type(e).__name__}))
        raise SystemExit(1)
