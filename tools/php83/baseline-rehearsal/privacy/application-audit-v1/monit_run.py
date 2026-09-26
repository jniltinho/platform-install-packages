"""Read only Monit control identities; never run start/stop or export arbitrary command values."""
import hashlib,json,subprocess
import run
CODE=r'''
import json,re,socket,subprocess
from pathlib import Path
assert socket.gethostname()=='kaltura-php74-baseline'
a=json.loads(subprocess.check_output(['ip','-j','-4','addr'],timeout=10));ips={x.get('local') for link in a for x in link.get('addr_info',[])}
assert '192.168.56.74' in ips and not ips.intersection({'192.168.56.20','192.168.56.21','192.168.56.30','192.168.56.83'})
rows=[]
for p in Path('/etc/monit').rglob('*'):
 if not p.is_file():continue
 raw=p.read_bytes()
 if len(raw)>1024*1024:raise ValueError('Large Monit file')
 text=raw.decode()
 blocks=re.split(r'(?im)^\s*check\s+process\s+',text)
 for block in blocks[1:]:
  name=block.split()[0]
  if not re.fullmatch('[A-Za-z0-9_.-]+',name):raise ValueError('Unsafe control name')
  signals={x:x in block for x in ['KGenericBatchMgr','populateElasticFromLog','apache2','httpd']}
  if not any(signals.values()):continue
  commands=[]
  for action,value in re.findall(r'(?im)^\s*(start|stop)\s+program\s*=\s*"([^"\n]+)"',block):
   parts=value.split()
   safe=bool(parts) and re.fullmatch(r'/(?:etc/init.d|opt/kaltura/bin)/[A-Za-z0-9_.-]+',parts[0]) and all(v in ['start','stop','restart'] for v in parts[1:])
   commands.append({'action':action,'safe_control_command':bool(safe),'command':parts if safe else None})
  rows.append({'config_path':str(p),'control_name':name,'source_signals':signals,'commands':commands})
print(json.dumps({'status':'READONLY_MONIT_CONTROL_IDENTITIES','controls':rows,'services_changed':0,'arbitrary_command_values_exported':False},sort_keys=True))
'''
def main():
 if (run.OUT/'monit.json').exists():raise ValueError('Never overwrite')
 p=subprocess.run(['ssh','-T','-F','/tmp/kaltura-php74-ssh.conf','baseline74','sudo python3 -'],input=CODE.encode(),capture_output=True,timeout=30)
 (run.OUT/'monit.exit').write_text(str(p.returncode)+'\n');(run.OUT/'monit-stderr-sha256.txt').write_text(hashlib.sha256(p.stderr).hexdigest()+'\n')
 if p.returncode:raise ValueError('Monit readonly audit failed')
 report=json.loads(p.stdout);(run.OUT/'monit.json').write_text(json.dumps({'guest_sha256':hashlib.sha256(CODE.encode()).hexdigest(),'result':report},indent=2)+'\n');print(report['status'])
if __name__=='__main__':main()
