"""Authorized readonly config-cache comparison; no application bootstrap/set/delete."""
import hashlib,json,subprocess
from pathlib import Path
import run
MEMCACHE='/usr/lib/php/20190902/memcache.so';PIN='cd5f48204d0752697476fd3488b4a39ac7fe3a75f6ae8ba52e354a1bd38c7616'
def main():
 if (run.OUT/'cache-primary.json').exists() or (run.OUT/'cache-primary.exit').exists():raise ValueError('Never overwrite')
 data=run.payload();data['runtime'][MEMCACHE]=PIN;data['logger_code']=(run.HERE/'cache.php').read_text()
 code=(run.HERE/'guest.py').read_text().replace("'-d','extension=/usr/lib/php/20190902/json.so',", "'-d','extension=/usr/lib/php/20190902/json.so','-d','extension="+MEMCACHE+"',")
 code=('PAYLOAD='+repr(data)+'\n'+code).encode()
 p=subprocess.run(['ssh','-T','-F','/tmp/kaltura-php74-ssh.conf','baseline74','python3 -'],input=code,capture_output=True,timeout=60)
 (run.OUT/'cache-primary.exit').write_text(str(p.returncode)+'\n');(run.OUT/'cache-stderr-sha256.txt').write_text(hashlib.sha256(p.stderr).hexdigest()+'\n')
 if p.returncode:raise ValueError('Read-only cache audit rejected')
 result=json.loads(p.stdout)
 (run.OUT/'cache-primary.json').write_text(json.dumps({'guest_sha256':hashlib.sha256(code).hexdigest(),'result':result},indent=2)+'\n')
 print(result['status'])
if __name__=='__main__':main()
