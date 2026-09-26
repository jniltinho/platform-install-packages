#!/usr/bin/env python3
"""One explicitly authorized exclusive74 untimed lab operation, private inputs stay guest-side."""
import hashlib,io,json,os,secrets,subprocess,tarfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'doc/php83/evidence/baseline-rehearsal'
STAGE='/home/vagrant/baseline-untimed-r2'
SSH=['ssh','-T','-F','/tmp/kaltura-php74-ssh.conf','baseline74']
FILES=['baseline-protocol/guarded_http.py','baseline-protocol/deadline_transport.py','baseline-api/transport.py','baseline-api/protocol.py','baseline-rehearsal/untimed_driver.py','baseline-rehearsal/guest_inventory.py']
MEDIA=ROOT.parent/'platform-install-packages-php83-artifacts/baseline-media-r1/short360.mp4'
SOURCE_PIN='612d179c75f8f2374b7ac59c2dd7edba65e38eb357b870e8ad8c2e83d63b5473'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def remote(command,data=None,timeout=120):
    return subprocess.run(SSH+[command],input=data,capture_output=True,timeout=timeout)
def inventory():
    p=remote('python3 -',(ROOT/'tools/php83/baseline-rehearsal/guest_inventory.py').read_bytes())
    if p.returncode:raise ValueError('Public identity inventory failed')
    value=json.loads(p.stdout)
    expected=json.loads((OUT/'inventory-r2.json').read_text())['observation']
    for key in ['hostname','target_ip','cli_version','public_file_sha256','critical_source_subset_sha256','package_versions']:
        if value[key]!=expected[key]:raise ValueError('Published baseline identity drift')
    return value
# Fixed stage verifier is transferred as stdin, not an alternate private-data read.
def verify(manifest):
    code='''import hashlib,json,pathlib,sys
root=pathlib.Path("/home/vagrant/baseline-untimed-r2")
expected=json.loads(sys.stdin.readline())
actual={}
for rel,digest in expected.items():
 p=root/rel
 if p.is_symlink() or not p.is_file() or p.stat().st_uid!=0 or p.stat().st_mode&0o222:raise SystemExit(1)
 actual[rel]=hashlib.sha256(p.read_bytes()).hexdigest()
if actual!=expected:raise SystemExit(1)
print("STAGE_PINNED")
'''
    # Python program and manifest are both public and caller-pinned.
    import base64
    command="sudo python3 -c "+__import__('shlex').quote(code)
    p=remote(command,json.dumps(manifest).encode()+b'\n')
    if p.returncode or p.stdout.strip()!=b'STAGE_PINNED':raise ValueError('Stage identity mismatch')
def main():
    for suffix in ['json','exit','stderr-sha256']:
        if (OUT/('untimed-r2-primary.'+suffix)).exists():raise ValueError('Refuse overwrite')
    nonce=secrets.token_hex(16);unit='baseline-untimed-'+nonce[:8]
    before=inventory()
    blobs={'tools/php83/'+rel:(ROOT/'tools/php83'/rel).read_bytes() for rel in FILES}
    raw=MEDIA.read_bytes()
    if sha(raw)!=SOURCE_PIN:raise ValueError('Frozen media changed')
    blobs['short360.mp4']=raw
    manifest={rel:sha(data) for rel,data in blobs.items()}
    archive=io.BytesIO()
    with tarfile.open(fileobj=archive,mode='w') as tar:
        for name,data in blobs.items():
            info=tarfile.TarInfo(name);info.size=len(data);info.mode=0o444;info.uid=0;info.gid=0;tar.addfile(info,io.BytesIO(data))
    command="set -eu; test ! -e "+STAGE+"; sudo mkdir -m 0755 "+STAGE+"; sudo tar --no-same-permissions -xf - -C "+STAGE+"; sudo find "+STAGE+" -type f -exec chmod 0444 {} +"
    stage=remote(command,archive.getvalue())
    if stage.returncode:raise ValueError('Fresh staging failed')
    verify(manifest)
    (OUT/'untimed-r2-stage-manifest.json').write_text(json.dumps({'stage':STAGE,'nonce':nonce,'unit':unit,'files':manifest,'runner_sha256':sha(Path(__file__).read_bytes()),'source_sha256':SOURCE_PIN},indent=2)+'\n')
    command='sudo systemd-run --quiet --wait --pipe --collect --unit '+unit+' -p IPAddressDeny=any -p IPAddressAllow=localhost -p IPAddressAllow=192.168.56.74/32 -p NoNewPrivileges=yes -p ProtectSystem=strict -p ProtectHome=read-only -p PrivateTmp=yes -p ReadWritePaths=/root/kaltura-baseline-private -p ReadWritePaths=/opt/kaltura/app/api_v3/web -p RuntimeMaxSec=1100 python3 -B '+STAGE+'/tools/php83/baseline-rehearsal/untimed_driver.py '+nonce+' '+unit+' '+STAGE+'/short360.mp4'
    p=remote(command,timeout=1140)
    (OUT/'untimed-r2-primary.exit').write_text(str(p.returncode)+'\n')
    (OUT/'untimed-r2-primary.stderr-sha256').write_text(sha(p.stderr)+'\n')
    verify(manifest);after=inventory()
    rows=[]
    for line in p.stdout.splitlines():
        value=json.loads(line)
        if type(value) is not dict or value.get('nonce')!=nonce or value.get('baseline_acceptance') is not False or value.get('benchmark_executed') is not False:raise ValueError('Public receipt binding')
        # Secret-bearing fields are forbidden at every nesting depth.
        def check(obj):
            if type(obj) is dict:
                if set(obj)&{'secret','password','ks','dataUrl','response','raw_body'}:raise ValueError('Forbidden receipt field')
                for item in obj.values():check(item)
            elif type(obj) is list:
                for item in obj:check(item)
        check(value);rows.append(value)
    (OUT/'untimed-r2-primary.json').write_text(json.dumps({'exit':p.returncode,'stdout_sha256':sha(p.stdout),'stderr_sha256':sha(p.stderr),'stage':STAGE,'manifest':manifest,'before':before,'after':after,'phase_receipts':rows,'baseline_acceptance':False,'scope':'first untimed short-source API/media observation only'},indent=2)+'\n')
    print('Untimed primary terminal; sanitized receipt retained; exit='+str(p.returncode))
    return p.returncode
if __name__=='__main__':raise SystemExit(main())
