"""Readonly init source joins and effective Monit summary; no service actions."""
import hashlib,json,subprocess
import run

def main():
 if (run.OUT/'controls.json').exists():raise ValueError('Never overwrite')
 sources={'/etc/init.d/kaltura-batch':run.REPO/'deb/kaltura-batch/debian/kaltura-batch.init','/etc/init.d/kaltura-elastic-populate':run.REPO/'deb/kaltura-elasticsearch/debian/kaltura-elastic-populate.init'}
 expected={p:hashlib.sha256(f.read_bytes()).hexdigest() for p,f in sources.items()}
 code='EXPECTED='+repr(expected)+'\n'+r'''
import hashlib,json,re,socket,subprocess
from pathlib import Path
assert socket.gethostname()=='kaltura-php74-baseline'
a=json.loads(subprocess.check_output(['ip','-j','-4','addr'],timeout=10));ips={x.get('local') for link in a for x in link.get('addr_info',[])}
assert '192.168.56.74' in ips and not ips.intersection({'192.168.56.20','192.168.56.21','192.168.56.30','192.168.56.83'})
files={p:{'sha256':hashlib.sha256(Path(p).read_bytes()).hexdigest(),'matches_reviewed_repository':hashlib.sha256(Path(p).read_bytes()).hexdigest()==h} for p,h in EXPECTED.items()}
p=subprocess.run(['monit','summary'],capture_output=True,timeout=10)
rows=[]
if p.returncode==0:
 for line in p.stdout.decode().splitlines():
  m=re.match(r"^Process\s+'([A-Za-z0-9_.-]+)'\s+(.*)$",line.strip())
  if m:rows.append({'control_name':m[1],'running':m[2].strip()=='Running','other_status':m[2].strip()!='Running'})
print(json.dumps({'status':'READONLY_CONTROL_SOURCE_JOIN','files':files,'monit_summary_exit':p.returncode,'monit_processes':rows,'raw_monit_text_exported':False,'service_changes':0},sort_keys=True))
'''
 p=subprocess.run(['ssh','-T','-F','/tmp/kaltura-php74-ssh.conf','baseline74','sudo python3 -'],input=code.encode(),capture_output=True,timeout=30)
 (run.OUT/'controls.exit').write_text(str(p.returncode)+'\n')
 if p.returncode:raise ValueError('Read-only control join failed')
 (run.OUT/'controls.json').write_text(json.dumps({'guest_sha256':hashlib.sha256(code.encode()).hexdigest(),'result':json.loads(p.stdout)},indent=2)+'\n');print('Read-only controls joined')
if __name__=='__main__':main()
