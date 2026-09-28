"""Immutable runtime binding for local native profile split. Root VM operator only."""
import hashlib,importlib.util,json,os,re,stat,sys,signal
from pathlib import Path
HERE=Path(__file__).resolve().parent
LOCAL_PINS={'observe_r2.py': '14c9a9c4b1238c452295fa00083962e090b8d7b12f32d75073413e17bfc1c221', 'install.py': '2822c11fe941f22f57323febebeb52066995f891b4d1ef7d5b097b1f38ffc138', 'privacy_logs.py': '24ea4beb525a9084e1a17667654a815cbdb1fc1d6a84188133454b4c5e0c19a0', 'credential_patterns.py': 'c83376180af7db43c2ac0992f3aaee4571891d1e3ed8f5cd3761b22981377e22', 'credential_read.py': '379b1f314d0d39f17ab3df1d13aaf39e61c3c358db0bcc3491cb99babe4c3ab9', 'profile_process.py': '5af1540b25c861611fe52f0a1b3cbe09d570c8c52f79a996678daed8ba7d6fbd', 'profile_envelope.py': 'cfd18005fed262d5eaa66c8a7b8861dd048a5ceceda9048ea933976703dd7bcd'}
SOURCE_PINS={'deployment/bootstrap.php': 'bb8d4275f73bb14b06441d40f589e988f3b062b6fe4f0aaedc0fb3c7d0ab36de', 'alpha/lib/model/DeliveryProfile.php': '2fa1974f9feb7479b00f3c60eb3c44b80039acb187c2e913d4e7bd4fee5c269f', 'alpha/lib/model/DeliveryProfilePeer.php': 'dbfd0df052c0f3a5246ac3300f1dab8862793163d395c6a0677976ce4817f84f', 'alpha/lib/model/om/BaseDeliveryProfile.php': '0bd05e4a212e2e914cb6bc476e3bd85f680b25dcc9e5aca6a908fb68a2e3150a', 'alpha/lib/model/om/BaseDeliveryProfilePeer.php': '9805a9bf1c4d0fe721ff90673ec848b9732722f8e5f6df8e3a4bf44d928f75e0', 'alpha/lib/model/map/DeliveryProfileTableMap.php': '75a6eb94c163600443111e405ba38fb666d81feb0cec35fea7cab6f31eaf2669', 'alpha/lib/model/DeliveryProfileVodPackagerHls.php': '664b7d41cc60728c329ae3eb38409c02e5d83a54a0be12d02416af8dfd2e6241', 'alpha/lib/model/Partner.php': '27dfd30c3f0190e29a86489c10f154b8098f8d2b2b4a8928799056ee4c3d6f07', 'vendor/propel/util/PropelPDO.php': '9e4f602f50bc24432107f34a2f3b4a995518fe28c46be9dc8f642dbb9ca74d22'}
PAYLOAD_PIN='682ec53750b050bf8d7ee9836f91776433442c1da0eb3ad78283ba33dc2e5f3b'
PHP_PIN='5ed671ea6fe1cfb9f6e7dde2b259ec5821d7e0eae95c31d103d5468f2e617c59'
SNAPSHOT_PIN='2484fa4ff88b4ac432a544ef1395455809ff28e37e96e56951b6fba56f2e14aa'
MANIFEST_PIN='cf16bc5c49acbe5863934ba737c72e2b65878c84048389354e79163afeca0cb8'
class Rejected(ValueError):pass
def need(ok,code):
 if not ok:raise Rejected(code)
def frozen(path,pin):
 s=path.lstat();need(stat.S_ISREG(s.st_mode) and s.st_uid==0 and not s.st_mode&0o222 and s.st_nlink==1 and s.st_size<=1048576,'FROZEN_METADATA')
 raw=path.read_bytes();need(hashlib.sha256(raw).hexdigest()==pin,'FROZEN_PIN');return raw
def load(name,path,pin):
 frozen(path,pin);spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
class Context:
 def __init__(self,unit):
  need(re.fullmatch('baseline-profile-[0-9a-f]{8}',unit) is not None,'UNIT');self.unit=unit
  self.modules={}
  for name,pin in LOCAL_PINS.items():self.modules[name]=load(name[:-3],HERE/name,pin)
  self.tls=self.modules['install.py'];self.extra=self.modules['privacy_logs.py'];self.reader=self.modules['credential_read.py'];self.credentials=self.modules['credential_patterns.py'];self.process=self.modules['profile_process.py']
  stage=Path('/home/vagrant/privacy-media-overlay-v3/tools/php83')
  # Frozen legacy transport imports must resolve only authenticated stage files.
  # Literal dependency identities match previously reviewed media guest.
  for name,pin in {'baseline-api/protocol.py':'4587eab6222c2cacc381b6ef100dc557f1afb814250dcc5ba92b3b2ee7eeca34','baseline-api/transport.py':'5a5896f22aeef0a8baf0ba3869b2cbfebcd655b94ab5671dc13580d1035edf20','baseline-protocol/deadline_transport.py':'330c7aedaa57c439af579b9fa9f262c1062bbd66014d3e4c0adbe9b8a6c1dbe2','baseline-protocol/guarded_http.py':'4cc44f15645ced42e1e156586a79a2795d38f929c6f812eb695e427ee7e47b59'}.items():frozen(stage/name,pin)
  sys.path.insert(0,str(stage/'baseline-api'))
  self.legacy=load('untimed_driver',stage/'baseline-rehearsal/untimed_driver.py','b461835902bde19d3ec3ca555a88dac640176aa7318315d9cb4bee3d29df14b5')
  self.apache=load('apache_tls_logs',HERE/'privacy_logs_r2.py','d67eb65900c3134c91efaf94b18ba482b59261c81b0084de0cea3bcd37d5246c')
  self.files=load('profile_files',stage/'baseline-rehearsal/privacy/append-window-v1/scan.py','43189edbe0cfb9f4a0654b7b8425f8f4a876bf270a309f96309142a0ec5b34fc')
  self.journal=load('profile_journal',stage/'baseline-rehearsal/privacy/journal-window-v1/scan.py','a390e2464c3df47b36ed0b2e19607887b908351d3e7245439e392646239ba5e8')
  self.settle=load('profile_settle',HERE/'settle.py','2b1382fc7ff4163240d9c6e3342738ce90ab8537df9ea9999497a44e24d84764')
  self.convergence=load('profile_convergence',HERE/'convergence.py','b7f8114c27a930c471d3640c76ad60f28e0c0133b63abb5a4d805fa7c01cceca')
  overlay=Path('/home/vagrant/privacy-application-overlay-v4');raw=frozen(overlay/'manifest.json',MANIFEST_PIN);self.manifest=json.loads(raw)
  for n,h in self.manifest['files'].items():frozen(overlay/n,h)
  self.overlay=load('profile_overlay',overlay/'guest.py',self.manifest['files']['guest.py'])
  self.before=None;self.audit_count=0
 def inventory(self):return self.extra.extend(lambda:self.apache.extend(self.legacy.logs))
 def guard(self):
  self.inventory();v=self.tls.observe_check(True)
  need(self.tls.obs.read(self.tls.SSL,1048576)==self.tls.config(),'INSTALLED_TLS_CONFIG')
  need(v['listeners']['8444']==['TARGET'],'INSTALLED_TLS_LISTENER');self.tls.handshake(8444,str(self.tls.CA))
  raw=frozen(HERE/'snapshot.json',SNAPSHOT_PIN);snap=json.loads(raw)
  need(snap['snapshot_uuid']=='357bc3f1-8477-45d3-9dee-57b5ec0f1daf' and snap['vm_uuid']=='9e954729-16f3-4eda-9db5-b94e5ada9e44' and snap['command_exit']==0,'SNAPSHOT_ATTESTATION')
  props=self.tls.obs.command(['/usr/bin/systemctl','show',self.unit+'.service','-p','IPAddressDeny','-p','IPAddressAllow','-p','NoNewPrivileges']).decode('ascii');v={}
  for line in props.splitlines():
   k,val=line.split('=',1);need(k not in v,'NETWORK_POLICY');v[k]=val
  need(v.get('NoNewPrivileges')=='yes' and set(v.get('IPAddressDeny','').split())=={'0.0.0.0/0','::/0'} and set(v.get('IPAddressAllow','').split())=={'127.0.0.0/8','::1/128','192.168.56.74/32'},'NETWORK_POLICY')
  for n,pin in SOURCE_PINS.items():
   p=Path('/opt/kaltura/app')/n;s=p.lstat();need(stat.S_ISREG(s.st_mode) and s.st_uid==0 and s.st_nlink==1 and s.st_size<=2097152 and hashlib.sha256(p.read_bytes()).hexdigest()==pin,'NATIVE_SOURCE_PIN')
  self.process.verified(self.process.PHP,PHP_PIN,32*1024*1024)
  state=(self.overlay.source_state(self.manifest['after']),self.legacy.logging_preflight(),self.overlay.audits()[1])
  for p,h in self.manifest['modules'].items():need(self.overlay.digest(p)==h,'RUNTIME_PIN')
  if self.before is None:self.before=state
  else:need(self.before==state,'SOURCE_CONFIG_DRIFT')
 def snapshot(self):return self.files.snapshot(self.inventory()),self.journal.snapshot()
 def patterns(self):return self.credentials.patterns(self.reader.read_fixed('/opt/kaltura/app/configurations/db.ini'),self.reader.read_fixed('/root/kaltura-baseline-private/mysql-password'))
 def invoke(self,phase):return self.process.invoke(HERE/'delivery_profile_split.php',phase,PAYLOAD_PIN,PHP_PIN)
 def audit(self,boundary,patterns):
  start,jstart=boundary
  def once():
   self.settle.wait_quiet(self.snapshot)
   cutoff=self.snapshot()
   f=self.files.scan_window(start,patterns,inventory=self.inventory)
   need(f['status']=='COMPLETE_FINITE_FILE_WINDOW' and f['uncovered_tail_bytes']==0 and len(f['counts'])==len(patterns) and all(type(v) is int and v==0 for v in f['counts']),'FILE_PRIVACY')
   j=self.journal.scan_window(jstart,patterns)
   need(j['status']=='COMPLETE_FINITE_JOURNAL_WINDOW' and j['cutoff_covered'] is True and len(j['counts'])==len(patterns) and all(type(v) is int and v==0 for v in j['counts']),'JOURNAL_PRIVACY')
   again=self.files.scan_window(start,patterns,inventory=self.inventory)
   need(again['status']=='COMPLETE_FINITE_FILE_WINDOW' and again['uncovered_tail_bytes']==0 and len(again['counts'])==len(patterns) and all(type(v) is int and v==0 for v in again['counts']),'FILE_PRIVACY')
   need(again['end_offsets']==f['end_offsets'],'FILE_TAIL_DURING_JOURNAL')
   need(self.snapshot()==cutoff and f['end_offsets']=={p:m.size for p,m in cutoff[0].items()},'COMMON_AUDIT_END_DRIFT');return True
  self.convergence.run(once,Rejected);self.audit_count+=1
if __name__=='__main__':
 try:
  def interrupted(*args):raise Rejected('INTERRUPTED')
  signal.signal(signal.SIGTERM,interrupted);signal.signal(signal.SIGINT,interrupted)
  need(len(sys.argv)==2,'UNIT');c=Context(sys.argv[1]);result=c.modules['profile_envelope.py'].execute(c);result['finite_audits_completed']=c.audit_count;print(json.dumps(result,sort_keys=True));raise SystemExit(0 if result['status']=='NATIVE_PROFILE_SPLIT_COMMITTED_FINITE_PRIVACY' else 2)
 except Exception:print(json.dumps({'status':'PROFILE_ENVELOPE_FAILED_CLOSED','full_acceptance':False}));raise SystemExit(2)
