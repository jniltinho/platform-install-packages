"""V3 root-coordinator-only host runner for versioned V2 observation. --check does not stage or authenticate API."""
import argparse,base64,hashlib,json,os,re,secrets,selectors,shlex,signal,stat,subprocess,time,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
UUID='9e954729-16f3-4eda-9db5-b94e5ada9e44'
CONFIG=Path('/tmp/php74-baseline-strict-r1.conf')
KEYS=Path('/tmp/php74-baseline-hostkey-r1')
PINS={'guest_untimed.py': '3f95f1ced7b530e42b90e1872b34add4f1ddea0c6da174a79bda8a324955d56c', 'observation_v2.py': 'ec32386df1c745f5754ece19f3127f6da85415e644c8556e6c07666b2ea1abc5', 'protocol_v2.py': '147d74b0a04779fd0819ebe210d8a1a6aea4af8fbc773683a278e540ce70d4b8', 'rehearsal.py': 'ccf78ba0b1d3c94f05f63fd2d87c351953022c149c0e75392b5c86be2c02bb70'}
STAGE='/var/lib/kaltura-baseline-untimed100-r1'
SSH=['ssh','-T','-o','BatchMode=yes','-o','ConnectTimeout=10','-F',str(CONFIG),'baseline74']
class Rejected(ValueError):pass
def need(ok):
 if not ok:raise Rejected('RUNNER_REJECTED')
def sha(b):return hashlib.sha256(b).hexdigest()
def bounded(argv,data=None,timeout=30,cap=4*1024*1024):
 # All pipes, including stdin, obey one deadline; no raw stderr persists.
 need(data is None or len(data)<=1024*1024)
 p=subprocess.Popen(argv,stdin=subprocess.PIPE if data is not None else subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE,start_new_session=True)
 sel=selectors.DefaultSelector();out=bytearray();err=0;sent=0;deadline=time.monotonic()+timeout;completed=False
 try:
  for stream,kind in ((p.stdout,'out'),(p.stderr,'err')):
   os.set_blocking(stream.fileno(),False);sel.register(stream,selectors.EVENT_READ,kind)
  if data is not None:
   os.set_blocking(p.stdin.fileno(),False);sel.register(p.stdin,selectors.EVENT_WRITE,'in')
  while sel.get_map():
   need(time.monotonic()<deadline)
   for key,_ in sel.select(min(.2,max(0,deadline-time.monotonic()))):
    if key.data=='in':
     if sent<len(data):sent+=os.write(key.fileobj.fileno(),data[sent:sent+4096])
     if sent==len(data):sel.unregister(key.fileobj);key.fileobj.close()
     continue
    raw=os.read(key.fileobj.fileno(),65536)
    if not raw:sel.unregister(key.fileobj);continue
    if key.data=='out':out.extend(raw)
    else:err+=len(raw)
    need(len(out)+err<=cap)
  rc=p.wait(timeout=max(.1,deadline-time.monotonic()));completed=True;return rc,bytes(out),err
 finally:
  if not completed:
   try:os.killpg(p.pid,signal.SIGKILL)
   except ProcessLookupError:pass
  if p.poll() is None:p.wait(timeout=10)
  sel.close();p.stdout.close();p.stderr.close()
  if p.stdin is not None and not p.stdin.closed:p.stdin.close()
def pinned(path,pin,private=False):
 s=path.lstat();need(stat.S_ISREG(s.st_mode) and s.st_nlink==1 and not path.is_symlink())
 if private:need(s.st_uid==os.getuid() and stat.S_IMODE(s.st_mode)==0o600)
 raw=path.read_bytes();need(sha(raw)==pin);return raw
def host_guard(text):
 rows={}
 for line in text.splitlines():
  k,sep,v=line.partition('=')
  if sep:
   need(k not in rows);rows[k.strip('"')]=v.strip('"')
 need(rows.get('UUID')==UUID and rows.get('name')=='kaltura-php74-noble-baseline' and rows.get('VMState')=='running' and rows.get('cpus')=='4' and rows.get('memory')=='8192')
 need(any(len(v.split(','))==6 and v.split(',')[1:]==['tcp','127.0.0.1','2201','','22'] for k,v in rows.items() if re.fullmatch(r'Forwarding\(\d+\)',k)))
 return {k:rows[k] for k in ('UUID','name','VMState','cpus','memory')}
REMOTE_GUARD='''import hashlib,json,os,socket,stat,subprocess
from pathlib import Path
assert os.geteuid()==0 and socket.gethostname()=='kaltura-php74-baseline'
a=json.loads(subprocess.check_output(['ip','-j','-4','addr'],timeout=10))
ips={v.get('local') for row in a for v in row.get('addr_info',[])}
assert '192.168.56.74' in ips and not ips.intersection({'192.168.56.20','192.168.56.21','192.168.56.30','192.168.56.83'})
for name in ('/','/var','/var/lib'):
 p=Path(name);s=p.lstat();assert stat.S_ISDIR(s.st_mode) and s.st_uid==s.st_gid==0 and not s.st_mode&0o022 and not os.listxattr(p)
stage=Path('/var/lib/kaltura-baseline-untimed100-r1');assert not os.path.lexists(stage)
old=subprocess.run(['systemctl','is-active','baseline-freeze-9541487c.service'],capture_output=True,timeout=10)
assert old.returncode in (3,4) and old.stdout.strip() in (b'inactive',b'unknown')
p=Path('/root/kaltura-baseline-private');s=p.lstat();assert stat.S_ISDIR(s.st_mode) and s.st_uid==0 and not s.st_mode&0o077
'''
def remote(code,timeout=30):return bounded(SSH+['sudo -n python3 -B -'],code.encode(),timeout)
def check():
 pinned(CONFIG,'15f687f3db61c013654442404e916b1b2ad7f0d1835e1f30ef10ca80355ceef3',True)
 pinned(KEYS,'6b6a9652a16acd478a01b508962452556138ce3a3f0c2cc4584baab58f00c4c6',True)
 blobs={k:pinned(HERE/k,v) for k,v in PINS.items()}
 rc,raw,_=bounded(['VBoxManage','showvminfo',UUID,'--machinereadable']);need(rc==0);host=host_guard(raw.decode())
 rc,raw,_=remote(REMOTE_GUARD+'print("CHECKED")\n');need(rc==0 and raw==b'CHECKED\n')
 return blobs,host
def unit_command(unit):
 need(re.fullmatch('baseline-freeze-[a-f0-9]{8}',unit) is not None)
 return 'sudo -n systemd-run --quiet --wait --pipe --collect --unit '+unit+' -p IPAddressDeny=any -p IPAddressAllow=localhost -p IPAddressAllow=192.168.56.74/32 -p NoNewPrivileges=yes -p ProtectSystem=strict -p ProtectHome=read-only -p PrivateTmp=yes -p ReadWritePaths=/root/kaltura-baseline-private -p RuntimeMaxSec=1100 /usr/bin/python3 -B '+STAGE+'/guest_untimed.py '+unit

EXPECTED_SOURCES={'alpha/apps/kaltura/lib/db/KalturaStatement.php': {'gid': 0, 'mode': 436, 'sha256': 'bd8ab13a8fb745eb603b9c35633e24637adb5356a1792642d884c6f7e1d85bd2', 'uid': 0}, 'api_v3/lib/KalturaDispatcher.php': {'gid': 0, 'mode': 436, 'sha256': '9ce4b17a9fb1bef95fbbbbc6f08cb396a6cc944b055bac8413d740ce5d73c7b9', 'uid': 0}, 'api_v3/lib/KalturaFrontController.php': {'gid': 0, 'mode': 436, 'sha256': '79570bd2be507f0045281a903aa13bd2de4037c2e12df3370075c4445184a4ca', 'uid': 0}, 'infra/log/KalturaLog.php': {'gid': 0, 'mode': 436, 'sha256': '40e4db5733cfab59e0e873f94ee64166de380d86425625411dc716f6cb1003dd', 'uid': 0}, 'infra/log/KalturaSerializableStream.php': {'gid': 0, 'mode': 436, 'sha256': '8411013a6f2ac78b6d092594d088ba9a5fbe71ada9de00692a369388c40dc04c', 'uid': 0}}
def round_projection(row):
 sys.path.insert(0,str(HERE.parent/'baseline-api'))
 import rehearsal
 from assemble_v2 import privacy
 out={'untimed_round':rehearsal.validate_round(row['untimed_round'])}
 count=row.get('round_token_count');need(type(count) is int and 0<=count<=34)
 out['round_token_count']=count
 if out['untimed_round']['functional_round_pass']:need(count==34)
 if 'round_privacy' in row:
  v=row['round_privacy'];need(type(v) is dict and set(v)=={'common_end_verified','pattern_count','batches'} and v['common_end_verified'] is True and type(v['pattern_count']) is int and 2<=v['pattern_count']<=72)
  batches=v['batches'];need(type(batches) is list and 1<=len(batches)<=3)
  projected=[]
  for b in batches:
   privacy(b);need(2<=len(b['files']['counts'])<=32 and len(b['files']['counts'])==len(b['journal']['counts']))
   projected.append({'files':{k:b['files'][k] for k in ('counts','status','uncovered_tail_bytes')},'journal':{k:b['journal'][k] for k in ('counts','status','cutoff_covered','complete')},'scope':'FINITE_COMMON_END_ROUND_WINDOW'})
  need(sum(len(b['files']['counts']) for b in batches)==v['pattern_count'])
  out['round_privacy']={'common_end_verified':True,'pattern_count':v['pattern_count'],'batches':projected}
 return out

def public_rows(raw):
 from assemble_v2 import assemble,ENV_KEYS
 rows=[json.loads(line) for line in raw.splitlines() if line.strip()]
 need(0<len(rows)<=256 and all(type(row) is dict for row in rows))
 out=[]
 for row in rows:
  status=row.get('status')
  need(status in ('INCOMPLETE','FAILED_OR_INCOMPLETE_MEDIA_OBSERVATION','EXISTING_MEDIA_FREEZE_OBSERVATION_COMPLETE'))
  if status!='EXISTING_MEDIA_FREEZE_OBSERVATION_COMPLETE':
   # Deliberately reduced projection: arbitrary nested diagnostics are never copied.
   partial={'status':status}
   if 'untimed_round' in row:partial.update(round_projection(row))
   out.append(partial);continue
  need(row.get('sources_before')==row.get('sources_after')==EXPECTED_SOURCES)
  env=dict.fromkeys(ENV_KEYS);env.update(vm_uuid=UUID,observed_readonly=True)
  validated=assemble(row,env)
  safe={k:row[k] for k in ('status','baseline_label','upload_attempted','wrong_secret_rejected','admin_escalation_rejected','source_sha256','stored_source_sha256','original_asset_id','file_sync_id','version_observations','entry_version_status','overlay_manifest_sha256','runtime_pins_verified','asset_version')}
  safe.update(fixture=validated['protocol_fixture'],profile=validated['profile'],sources_before=EXPECTED_SOURCES,sources_after=EXPECTED_SOURCES)
  for phase in ('invalid_nonce','user_privacy','media_privacy'):
   v=row[phase];safe[phase]={'files':{k:v['files'][k] for k in ('counts','status','uncovered_tail_bytes')},'journal':{k:v['journal'][k] for k in ('counts','status','cutoff_covered','complete')},'scope':'FINITE_OBSERVATION_WINDOW'}
  safe.update(round_projection(row));need('round_privacy' in safe and safe['untimed_round']['functional_round_pass'])
  out.append(safe)
 return out

def main(check_only,output):
 if not check_only:need(output is not None and not os.path.lexists(output))
 blobs,host=check()
 if check_only:return {'status':'READ_ONLY_PREFLIGHT_PASSED','guest_execution':False,'approved_freeze':False}
 unit='baseline-freeze-'+secrets.token_hex(4)
 # Exclusive local intent precedes any guest staging. A consumed path is never retried.
 dest=Path(output);dest.mkdir(mode=0o700)
 intent={'status':'STAGING_INTENT','unit':unit,'stage':STAGE,'files':PINS,'host':host}
 with (dest/'intent.json').open('x') as f:json.dump(intent,f,sort_keys=True)
 payload={k:base64.b64encode(v).decode() for k,v in blobs.items()}
 stage_code=REMOTE_GUARD+'''import base64
payload='''+repr(payload)+'''
pins='''+repr(PINS)+'''
assert set(payload)==set(pins)=={'guest_untimed.py','observation_v2.py','protocol_v2.py','rehearsal.py'}
values={k:base64.b64decode(v,validate=True) for k,v in payload.items()}
assert all(hashlib.sha256(v).hexdigest()==pins[k] for k,v in values.items())
stage.mkdir(mode=0o755)
for name,value in values.items():
 fd=os.open(stage/name,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o444)
 with os.fdopen(fd,'wb') as f:f.write(value);f.flush();os.fsync(f.fileno())
 os.chmod(stage/name,0o444)
print('STAGED')
'''
 rc,raw,_=remote(stage_code);need(rc==0 and raw==b'STAGED\n')
 result={'status':'INCOMPLETE','guest_exit':None,'approved_freeze':False,'unit':unit,'files':PINS}
 failure_stage='CAPTURE'
 try:
  rc,raw,err=bounded(SSH+[unit_command(unit)],timeout=1130)
  result.update(guest_exit=rc,stderr_bytes=err,stdout_bytes=len(raw))
  failure_stage='PUBLIC_PROJECTION'
  result['phase_receipts']=public_rows(raw)
  failure_stage='TERMINAL_STATUS'
  need(rc!=0 or result['phase_receipts'][-1]['status']=='EXISTING_MEDIA_FREEZE_OBSERVATION_COMPLETE')
  result['status']='OBSERVATION_CAPTURED_NOT_APPROVED' if rc==0 else 'FAILED_OBSERVATION'
 except Exception:result.update(status='FAILED_OR_INCOMPLETE_CAPTURE',failure_stage=failure_stage)
 finally:
  try:
   rc,_,_=bounded(SSH+['sudo -n systemctl stop '+unit+'.service'],timeout=30)
   q,state,_=bounded(SSH+['systemctl is-active '+unit+'.service'],timeout=10)
   result['unit_inactive']=state.strip() in (b'inactive',b'unknown') and q in (3,4)
  except Exception:result['unit_inactive']=False
  if not result['unit_inactive']:result['status']='FAILED_CLEANUP'
  with (dest/'result.json').open('x') as f:json.dump(result,f,sort_keys=True,indent=2);f.write('\n')
 return {'status':result['status'],'guest_exit':result['guest_exit'],'unit_inactive':result['unit_inactive'],'approved_freeze':False}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');p.add_argument('--output');a=p.parse_args()
 try:
  r=main(a.check,a.output);print(json.dumps(r));raise SystemExit(0 if r['status'] in ('READ_ONLY_PREFLIGHT_PASSED','OBSERVATION_CAPTURED_NOT_APPROVED') else 2)
 except Exception:print('{"status":"RUNNER_REJECTED","approved_freeze":false}');raise SystemExit(2)
