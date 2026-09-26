"""Readonly service/provider/forwarding audit, no reload/start/stop or app request."""
import ast,hashlib,json,subprocess
from pathlib import Path
import run

def main():
 if (run.OUT/'environment.json').exists() or (run.OUT/'environment.exit').exists():raise ValueError('Never overwrite')
 old=(run.REPO/'tools/php83/baseline-rehearsal/untimed_driver.py').read_text()
 tree=ast.parse(old);fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='logging_preflight')
 preflight=ast.get_source_segment(old,fn)
 code='import hashlib,json,re,socket,subprocess,os\nfrom pathlib import Path\ndef need(test,code):\n if not test:raise ValueError(code)\n'+preflight+'\n'+r'''
need(socket.gethostname()=='kaltura-php74-baseline','HOST')
a=json.loads(subprocess.check_output(['ip','-j','-4','addr'],timeout=10));ips={x.get('local') for link in a for x in link.get('addr_info',[])}
need('192.168.56.74' in ips and not ips.intersection({'192.168.56.20','192.168.56.21','192.168.56.30','192.168.56.83'}),'IP')
before=logging_preflight()
services=subprocess.check_output(['systemctl','list-units','--type=service','--state=running','--no-legend','--plain'],timeout=10).decode()
units=[line.split()[0] for line in services.splitlines() if line.split()]
need(all(re.fullmatch(r'[A-Za-z0-9_.@:-]+\.service',n) for n in units),'UNITS')
processes=[]
for proc in Path('/proc').iterdir():
 if not proc.name.isdigit():continue
 try:
  comm=(proc/'comm').read_text().strip()
  if comm not in ['apache2','nginx','php','php7.4','php8.3']:continue
  args=(proc/'cmdline').read_bytes().split(b'\0')
  scripts=[a.decode() for a in args if a.startswith(b'/opt/kaltura/app/') and a.endswith(b'.php')]
  maps=(proc/'maps').read_text();phpmods=sorted(set(re.findall(r'/[^\s]+/libphp[^\s]+\.so',maps)))
  cgroup=(proc/'cgroup').read_text();unit=re.findall(r'/([A-Za-z0-9_.@:-]+\.service)',cgroup)
  processes.append({'pid':int(proc.name),'comm':comm,'application_scripts':scripts,'service_units':sorted(set(unit)),
   'php_apache_modules':{p:hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in phpmods}})
 except FileNotFoundError:continue
 # Other failures, including permissions, reject the audit; no alternate access.
after=logging_preflight();need(before==after,'CONFIG_CHANGED')
print(json.dumps({'status':'READONLY_PROVIDER_AND_LOGGING_PREFLIGHT','config_file_count':len(before),'config_stable_private_comparison':True,'config_values_or_hashes_exported':False,'running_units':units,'processes':processes,'forwarder_or_bodylog_rejected_by_existing_preflight':True,'http_requests':0,'service_changes':0},sort_keys=True))
'''
 p=subprocess.run(['ssh','-T','-F','/tmp/kaltura-php74-ssh.conf','baseline74','sudo python3 -'],input=code.encode(),capture_output=True,timeout=60)
 (run.OUT/'environment.exit').write_text(str(p.returncode)+'\n');(run.OUT/'environment-stderr-sha256.txt').write_text(hashlib.sha256(p.stderr).hexdigest()+'\n')
 if p.returncode:raise ValueError('Environment audit failed, no raw configuration output')
 report=json.loads(p.stdout);(run.OUT/'environment.json').write_text(json.dumps({'guest_sha256':hashlib.sha256(code.encode()).hexdigest(),'reused_preflight_sha256':hashlib.sha256(preflight.encode()).hexdigest(),'result':report},indent=2)+'\n');print(report['status'])
if __name__=='__main__':main()
