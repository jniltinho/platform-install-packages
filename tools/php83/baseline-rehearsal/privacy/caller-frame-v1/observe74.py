"""Separate upstream74 phase; reuse exact frozen probe and guest algorithm, never app."""
import argparse,io,json,shlex,subprocess,tarfile
from pathlib import Path
import prepare,validate
HERE=Path(__file__).resolve().parent;REPO=HERE.parents[4]
OUT=REPO/'doc/php83/evidence/baseline-rehearsal/privacy/caller-frame-v1'
STAGE='/home/vagrant/privacy-caller-frame-v1-74';SSH=['ssh','-T','-F','/tmp/kaltura-php74-ssh.conf','baseline74']
PHP='/usr/bin/php7.4';PHP_PIN='5ed671ea6fe1cfb9f6e7dde2b259ec5821d7e0eae95c31d103d5468f2e617c59'
JSON='/usr/lib/php/20190902/json.so';JSON_PIN='80efe3d6f144e717b9fcef7750f81736cbd55c1e91041d24be58e70c18199343'
def payload():
 blobs,m,patch=prepare.payload('/tmp/kaltura-php83-audit/Rigel-18.20.0.zip',prepare.policy.old.UPSTREAM)
 # Explicit exact-count substitutions: unchanged loop/probe/validation semantics.
 g=blobs['guest.py']
 replacements=[(b'/home/vagrant/privacy-caller-frame-v1',STAGE.encode()),(b'/usr/bin/php8.3',PHP.encode()),(b'kaltura-php83-lab',b'kaltura-php74-baseline'),(b"cmd=[PHP,'-n',",("cmd=[PHP,'-n','-d','extension="+JSON+"',").encode()),(b"if sha(PHP)!=m['php_sha256']:",("if sha('"+JSON+"')!='"+JSON_PIN+"' or sha(PHP)!=m['php_sha256']:").encode()),(b"report['runtime_after']=sha(PHP);",("report['runtime_after']=sha(PHP);report['json_sha256_after']=sha('"+JSON+"');").encode())]
 for old,new in replacements:
  if g.count(old)!=1:raise ValueError('Frozen guest adapter anchor drift')
  g=g.replace(old,new)
 blobs['guest.py']=g;m['files']['guest.py']=prepare.sha(g);m.update(php_sha256=PHP_PIN,json_extension_sha256=JSON_PIN,adapter_sha256=prepare.sha(Path(__file__).read_bytes()),status='PREPARED_UPSTREAM74_ONLY')
 blobs['manifest.json']=json.dumps(m,sort_keys=True).encode();return blobs,m

def reconcile(report,m):
 if report['source_before']!=m['files'] or report['source_after']!=m['files'] or report['runtime_before']!=PHP_PIN or report['runtime_after']!=PHP_PIN or report.get('json_sha256_after')!=JSON_PIN:raise ValueError('Identity drift')
 if [x['variant'] for x in report['processes']]!=['original','overlay','repaired']:raise ValueError('Inventory')
 rows=[]
 for row in report['processes']:
  if type(row['exit']) is not int or row['exit']!=0 or len(row['lints'])!=12 or any(type(x['exit']) is not int or x['exit']!=0 for x in row['lints']):raise ValueError('Native exit/inventory')
  body=json.loads(row['stdout'])
  if body['runtime']!='7.4.33':raise ValueError('Runtime version')
  rows.append(validate.validate(body,row['variant'],{p:m['files'][row['variant']+'/'+p] for p in prepare.pipeline.PATHS}))
 return rows

def main(mode):
 blobs,m=payload();pin=prepare.sha(blobs['manifest.json'])
 if mode=='prepare':
  target=OUT/'preparation74.json'
  if target.exists():raise ValueError('Never overwrite')
  target.write_text(json.dumps({'manifest':m,'manifest_sha256':pin},indent=2)+'\n');return
 prefix='primary74' if mode=='primary' else 'repeat74';unit='privacy-caller-frame-v1-'+prefix
 if (OUT/(prefix+'.json')).exists() or (OUT/(prefix+'.exit')).exists():raise ValueError('Never overwrite')
 recorded=json.loads((OUT/'preparation74.json').read_text())
 if recorded!={'manifest':m,'manifest_sha256':pin}:raise ValueError('Preparation stale')
 if mode=='primary':
  data=io.BytesIO()
  with tarfile.open(fileobj=data,mode='w') as tar:
   for n,b in blobs.items():
    t=tarfile.TarInfo(n);t.size=len(b);t.mode=0o444;tar.addfile(t,io.BytesIO(b))
  guard='import socket,json,subprocess;assert socket.gethostname()=="kaltura-php74-baseline";a=json.loads(subprocess.check_output(["ip","-j","-4","addr"],timeout=10));ips={x.get("local") for i in a for x in i.get("addr_info",[])};assert "192.168.56.74" in ips and not ips.intersection({"192.168.56.20","192.168.56.21","192.168.56.30","192.168.56.83"})'
  p=subprocess.run(SSH+['set -eu; python3 -c '+shlex.quote(guard)+'; test ! -e '+STAGE+'; sudo mkdir -m0755 '+STAGE+'; sudo tar -xf - -C '+STAGE+'; sudo find '+STAGE+' -type d -exec chmod 0555 {} +'],input=data.getvalue(),capture_output=True,timeout=60)
  (OUT/'stage74.exit').write_text(str(p.returncode)+'\n');(OUT/'stage74.stderr').write_bytes(p.stderr)
  if p.returncode:raise ValueError('Stage failed')
 try:
  cmd='sudo systemd-run --quiet --wait --pipe --collect --unit '+unit+' --uid=vagrant -p PrivateNetwork=yes -p PrivateTmp=yes -p ProtectSystem=strict -p ProtectHome=read-only -p NoNewPrivileges=yes -p RuntimeMaxSec=180 python3 -B '+STAGE+'/guest.py '+pin
  p=subprocess.run(SSH+[cmd],capture_output=True,timeout=200)
  for ext,b in [('stdout',p.stdout),('stderr',p.stderr),('exit',(str(p.returncode)+'\n').encode())]:(OUT/(prefix+'.'+ext)).write_bytes(b)
  if p.returncode:raise ValueError('Native incomplete')
  report=json.loads(p.stdout);(OUT/(prefix+'.json')).write_text(json.dumps(report,indent=2)+'\n')
  validation=reconcile(report,m);(OUT/(prefix+'-validation.json')).write_text(json.dumps(validation,indent=2)+'\n')
  if mode=='repeat' and (report!=json.loads((OUT/'primary74.json').read_text()) or p.stdout!=(OUT/'primary74.stdout').read_bytes() or p.stderr!=(OUT/'primary74.stderr').read_bytes()):raise ValueError('Repeat differs')
 finally:
  c=subprocess.run(SSH+['sudo systemctl stop '+unit+'.service; systemctl is-active '+unit+'.service'],capture_output=True,timeout=30)
  (OUT/(prefix+'-cleanup.json')).write_text(json.dumps({'exit':c.returncode,'stdout':c.stdout.decode(),'stderr':c.stderr.decode()},indent=2)+'\n')
  if c.returncode not in (3,4) or c.stdout.strip() not in (b'inactive',b'unknown'):raise ValueError('Cleanup failed')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('mode',choices=['prepare','primary','repeat']);main(p.parse_args().mode)
