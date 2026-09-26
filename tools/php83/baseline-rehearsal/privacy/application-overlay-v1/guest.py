"""Explicit lab-only four-file transaction. Never performs HTTP/auth or alters log policy config."""
import hashlib,json,os,re,shlex,socket,stat,subprocess,sys,time
from pathlib import Path
ROOT=Path('/home/vagrant/privacy-application-overlay-v1');APP=Path('/opt/kaltura/app')
BACKUP=Path('/var/lib/kaltura-php83-lab/privacy-overlay-v1')
SYSTEM=Path('/etc/kaltura.d/system.ini')
TARGETS=('infra/log/KalturaLog.php','infra/log/KalturaSerializableStream.php','api_v3/lib/KalturaFrontController.php','api_v3/lib/KalturaDispatcher.php')
CONTROLS={'/etc/init.d/kaltura-batch':'a8eb09c22f10f222142d253123ec2ef807c3070a45500b6f6705334735b2ca86','/etc/init.d/kaltura-elastic-populate':'1dd32a9ce4124b1b02e7522ad4ef8d3ae9e681b675fafd23f3698e383cf8b10f'}
PHP='/usr/bin/php7.4';PHP_SHA='5ed671ea6fe1cfb9f6e7dde2b259ec5821d7e0eae95c31d103d5468f2e617c59'
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def need(test,code):
 if not test:raise RuntimeError(code)
def source_state(expected):
 rows={}
 for name,pin in expected.items():
  p=APP/name;s=p.lstat()
  need(stat.S_ISREG(s.st_mode) and s.st_nlink==1,'SOURCE_TYPE')
  need(digest(p)==pin,'SOURCE_DRIFT')
  rows[name]={'sha256':pin,'uid':s.st_uid,'gid':s.st_gid,'mode':stat.S_IMODE(s.st_mode)}
 return rows
def replace_file(name,data,meta):
 target=APP/name;temporary=target.with_name(target.name+'.privacy-overlay-v1-new')
 fd=os.open(temporary,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
 try:
  with os.fdopen(fd,'wb') as f:
   f.write(data);f.flush();os.fsync(f.fileno());os.fchown(f.fileno(),meta['uid'],meta['gid']);os.fchmod(f.fileno(),meta['mode'])
  os.replace(temporary,target)
 finally:
  if temporary.exists():temporary.unlink()
def app_processes():
 rows={}
 for proc in Path('/proc').iterdir():
  if not proc.name.isdigit():continue
  try:
   comm=(proc/'comm').read_text().strip()
   if comm not in ('apache2','php','php7.4'):continue
   args=(proc/'cmdline').read_bytes().split(b'\0');scripts=[]
   for a in args:
    if not a.endswith(b'.php'):continue
    p=Path(a.decode());p=p if p.is_absolute() else (proc/'cwd').resolve()/p
    if str(p.resolve()).startswith(str(APP)+'/'):scripts.append(str(p.resolve()))
   if comm=='apache2' or scripts:
    fields=(proc/'stat').read_text().rsplit(')',1)[1].split()
    rows[proc.name]={'starttime':fields[19],'comm':comm,'scripts':scripts}
  except FileNotFoundError:continue
 return rows
def wait_none(limit=30):
 until=time.monotonic()+limit
 while time.monotonic()<until:
  if not app_processes():return
  time.sleep(.2)
 raise RuntimeError('OLD_APPLICATION_PROCESSES_REMAIN')
def control_config():
 values={}
 for line in SYSTEM.read_text().splitlines():
  match=re.match(r'^\s*(?:export\s+)?([A-Z_]+)=(.*)$',line)
  if not match or match[1] not in ['BASE_DIR','APP_DIR','LOG_DIR','PHP_BIN','OS_KALTURA_USER']:continue
  tokens=shlex.split(match[2],comments=True);need(len(tokens)==1,'SYSTEM_ASSIGNMENT')
  value=tokens[0]
  for key,existing in values.items():value=value.replace('${'+key+'}',existing).replace('$'+key,existing)
  need(not any(c in value for c in ['$','`',';','\n']),'SYSTEM_EXPANSION')
  values[match[1]]=value
 need(values.get('BASE_DIR')=='/opt/kaltura' and values.get('APP_DIR')==str(APP) and values.get('LOG_DIR')=='/opt/kaltura/log','SYSTEM_PATHS')
 need(values.get('PHP_BIN') in ['/usr/bin/php','/usr/bin/php7.4'] and digest(values['PHP_BIN'])==PHP_SHA,'SYSTEM_PHP')
 need(re.fullmatch('[a-z_][a-z0-9_-]*',values.get('OS_KALTURA_USER','')) is not None,'SYSTEM_USER')
 return values

def audits():
 results={};private={}
 for label in ['logger','cache']:
  command=[PHP,'-n','-d','extension=/usr/lib/php/20190902/json.so','-d','extension=/usr/lib/php/20190902/memcache.so','-d','error_reporting=-1','-d','display_errors=stderr','-d','log_errors=0','-r',(ROOT/(label+'.php')).read_text()]
  p=subprocess.run(command,capture_output=True,timeout=20);need(p.returncode==0 and not p.stderr,'CONFIG_AUDIT_EXECUTION')
  result=json.loads(p.stdout);private[label]=result.pop('private_configuration_snapshot');results[label]=result
 disk=results['logger'];cache=results['cache']
 need(disk['known_disk_components'] and not disk['unsafe_message_extra'] and disk['writer_count']==3,'DISK_LOGGER')
 need(disk['extras_classes_reviewed'],'EXTRA_CLASSES')
 need(all(f['operator_known'] for w in disk['writers'] for f in w['filters']),'FILTER_OPERATOR')
 need(cache['post_worker_restart_disk_equivalence'] and cache['two_reads_stable'] and cache['configuration_stable_private_comparison'] and cache['diagnostic_count']==0,'CACHE_CONFIGURATION')
 return results,private

def final_state(expected,metadata,system_bytes):
 rows=source_state(expected)
 need(all(all(rows[n][k]==metadata[n][k] for k in ['uid','gid','mode']) for n in expected),'FINAL_SOURCE_METADATA')
 need(SYSTEM.read_bytes()==system_bytes,'FINAL_SYSTEM_CONFIG_DRIFT')
 return rows

PUBLIC_FAILURE_CODES=frozenset(['SOURCE_TYPE','SOURCE_DRIFT','FINAL_SOURCE_METADATA','FINAL_SYSTEM_CONFIG_DRIFT','CONTROL_CONFIG_DRIFT','OLD_APPLICATION_PROCESSES_REMAIN','SOURCE_METADATA','OLD_PID_SURVIVED','NEW_PROCESS_INVENTORY','RESTORED_PROCESS_INVENTORY','RESTORE_BACKUP_DRIFT','SYSTEM_CONFIG_DRIFT','PRIVATE_CONFIG_DRIFT','POST_CONFIG_DRIFT','POST_SUPPORT_SOURCE_DRIFT','POST_MODULE_DRIFT','SERVICE_COMMAND_FAILED','CONFIG_AUDIT_EXECUTION','DISK_LOGGER','EXTRA_CLASSES','FILTER_OPERATOR','CACHE_CONFIGURATION'])
def public_failure(error):
 value=str(error)
 return value if isinstance(error,RuntimeError) and value in PUBLIC_FAILURE_CODES else type(error).__name__

def transaction(report,apply,recover,private_errors=None):
 if private_errors is None:private_errors=[]
 try:
  apply();report['status']='OVERLAY_INSTALLED_NO_AUTH_ACCEPTANCE'
 except Exception as error:
  report['failure_code']=public_failure(error);private_errors.append({'phase':'apply','class':type(error).__name__,'detail':str(error)})
  try:
   recover();report['status']='FAILED_ROLLED_BACK_NO_AUTH'
  except Exception as rollback:
   report['rollback_failure_code']=public_failure(rollback);private_errors.append({'phase':'recovery','class':type(rollback).__name__,'detail':str(rollback)});report['status']='FAILED_RECOVERY_REQUIRED_NO_AUTH'

def write_private(path,data):
 fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_TRUNC|os.O_NOFOLLOW,0o600)
 with os.fdopen(fd,'wb') as f:f.write(data);f.flush();os.fsync(f.fileno());os.fchmod(f.fileno(),0o600)

def main(pin):
 need(os.geteuid()==0 and socket.gethostname()=='kaltura-php74-baseline','LAB_IDENTITY')
 a=json.loads(subprocess.check_output(['ip','-j','-4','addr'],timeout=10));ips={v.get('local') for link in a for v in link.get('addr_info',[])}
 need('192.168.56.74' in ips and not ips.intersection({'192.168.56.20','192.168.56.21','192.168.56.30','192.168.56.83'}),'LAB_ADDRESS')
 need(ROOT.is_dir() and not ROOT.is_symlink() and ROOT.stat().st_uid==0 and not ROOT.stat().st_mode&0o022,'STAGE_OWNER')
 need(digest(ROOT/'manifest.json')==pin,'MANIFEST_PIN');m=json.loads((ROOT/'manifest.json').read_text())
 need(tuple(m['before'])==TARGETS and set(m['after'])==set(TARGETS),'EXACT_FOUR_TARGETS')
 for name,h in m['files'].items():
  p=ROOT/name;s=p.lstat();need(stat.S_ISREG(s.st_mode) and s.st_uid==0 and not s.st_mode&0o222 and digest(p)==h,'STAGE_IMMUTABLE')
 need(digest(PHP)==PHP_SHA,'PHP_PIN')
 for p,h in CONTROLS.items():need(digest(p)==h,'INIT_SCRIPT_DRIFT')
 for name,pin in m['support_sources'].items():need(digest(APP/name)==pin,'SUPPORT_SOURCE_DRIFT')
 for path,pin in m['modules'].items():need(digest(path)==pin,'MODULE_DRIFT')
 config=control_config();config_bytes=SYSTEM.read_bytes()
 audit_before,private_before=audits()
 original=source_state(m['before']);old=app_processes()
 need(any(r['comm']=='apache2' for r in old.values()),'APACHE_NOT_RUNNING')
 known={str(APP/'batch/KGenericBatchMgr.class.php'),str(APP/'plugins/search/providers/elastic_search/scripts/populateElasticFromLog.php')}
 need({x for p in old.values() for x in p['scripts']}==known,'APPLICATION_PROCESS_INVENTORY')
 for file,script in [('/opt/kaltura/var/run/batch.pid',str(APP/'batch/KGenericBatchMgr.class.php')),('/opt/kaltura/log/populate_elastic.pid',str(APP/'plugins/search/providers/elastic_search/scripts/populateElasticFromLog.php'))]:
  pid=Path(file).read_text().strip();need(pid.isdigit() and pid in old and script in old[pid]['scripts'],'PIDFILE_BINDING')
 for unit in ['apache2','monit']:need(subprocess.run(['systemctl','is-active','--quiet',unit],timeout=10).returncode==0,'EXPECTED_ACTIVE_SERVICE')
 for name in TARGETS:
  p=subprocess.run([PHP,'-n','-l',str(ROOT/'candidate'/name)],capture_output=True,timeout=15)
  need(p.returncode==0,'CANDIDATE_LINT')
 need(not BACKUP.exists() and not BACKUP.is_symlink(),'BACKUP_EXISTS')
 for ancestor in BACKUP.parents:
  if ancestor.exists():need(not ancestor.is_symlink() and ancestor.stat().st_uid==0 and not ancestor.stat().st_mode&0o022,'BACKUP_PARENT')
 BACKUP.mkdir(parents=True,mode=0o700);os.chmod(BACKUP,0o700)
 for i,name in enumerate(TARGETS):
  p=BACKUP/str(i);fd=os.open(p,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
  with os.fdopen(fd,'wb') as f:f.write((APP/name).read_bytes());f.flush();os.fsync(f.fileno())
  need(digest(p)==m['before'][name],'BACKUP_JOIN')
 write_private(BACKUP/'metadata.json',json.dumps(original).encode())
 report={'status':'INCOMPLETE','baseline_label':'PUBLISHED_PHP74_WITH_APPROVED_PRIVACY_OVERLAY','before':original,'old_processes':old,'commands':[],'auth_executed':False,'benchmark_executed':False}
 def command(args):
  p=subprocess.run(args,capture_output=True,timeout=90);i=len(report['commands'])
  for ext,raw in [('stdout',p.stdout),('stderr',p.stderr)]:
   f=BACKUP/('command-'+str(i)+'.'+ext);write_private(f,raw)
  report['commands'].append({'argv':args,'exit':p.returncode,'stdout_bytes':len(p.stdout),'stderr_bytes':len(p.stderr)})
  need(p.returncode==0,'SERVICE_COMMAND_FAILED')
 def stop():
  need(SYSTEM.read_bytes()==config_bytes,'CONTROL_CONFIG_DRIFT')
  command(['systemctl','stop','monit.service'])
  current={x for r in app_processes().values() for x in r['scripts']}
  if str(APP/'batch/KGenericBatchMgr.class.php') in current:command(['/etc/init.d/kaltura-batch','stop'])
  if str(APP/'plugins/search/providers/elastic_search/scripts/populateElasticFromLog.php') in current:command(['/etc/init.d/kaltura-elastic-populate','stop'])
  command(['systemctl','stop','apache2.service']);wait_none()
 def start():
  need(SYSTEM.read_bytes()==config_bytes,'CONTROL_CONFIG_DRIFT')
  command(['systemctl','start','apache2.service'])
  command(['/etc/init.d/kaltura-elastic-populate','start']);command(['/etc/init.d/kaltura-batch','start'])
  command(['systemctl','start','monit.service'])
 touched=False
 def apply():
  nonlocal touched
  stop();source_state(m['before'])
  need(SYSTEM.read_bytes()==config_bytes,'SYSTEM_CONFIG_DRIFT')
  audit_stopped,private_stopped=audits();need(private_stopped==private_before,'PRIVATE_CONFIG_DRIFT')
  touched=True
  for name in TARGETS:replace_file(name,(ROOT/'candidate'/name).read_bytes(),original[name])
  report['after']=source_state(m['after'])
  need(all(all(report['after'][n][k]==original[n][k] for k in ['uid','gid','mode']) for n in TARGETS),'SOURCE_METADATA')
  start()
  new=app_processes();need(new and all(k not in new or new[k]['starttime']!=v['starttime'] for k,v in old.items()),'OLD_PID_SURVIVED')
  need(any(r['comm']=='apache2' for r in new.values()) and {x for p in new.values() for x in p['scripts']}==known,'NEW_PROCESS_INVENTORY')
  audit_after,private_after=audits();need(private_after==private_before,'POST_CONFIG_DRIFT')
  for name,pin in m['support_sources'].items():need(digest(APP/name)==pin,'POST_SUPPORT_SOURCE_DRIFT')
  for path,pin in m['modules'].items():need(digest(path)==pin,'POST_MODULE_DRIFT')
  report['configuration_audit_before']=audit_before;report['configuration_audit_after']=audit_after
  report['new_processes']=new
  report['after_final']=final_state(m['after'],original,config_bytes)
 def recover():
  stop()
  if touched:
   for i,name in reversed(list(enumerate(TARGETS))):
    need(digest(BACKUP/str(i))==m['before'][name],'RESTORE_BACKUP_DRIFT')
    replace_file(name,(BACKUP/str(i)).read_bytes(),original[name])
  report['restored_before_start']=source_state(m['before']);start()
  report['restored_final']=final_state(m['before'],original,config_bytes)
  restored_processes=app_processes()
  need(any(r['comm']=='apache2' for r in restored_processes.values()) and {x for p in restored_processes.values() for x in p['scripts']}==known,'RESTORED_PROCESS_INVENTORY')
 private_errors=[]
 transaction(report,apply,recover,private_errors)
 write_private(BACKUP/'private-errors.json',json.dumps(private_errors).encode())
 write_private(BACKUP/'result.json',json.dumps(report).encode())
 print(json.dumps(report,sort_keys=True))
 return 0 if report['status']=='OVERLAY_INSTALLED_NO_AUTH_ACCEPTANCE' else 2
if __name__=='__main__':sys.exit(main(sys.argv[1]))
