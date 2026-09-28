import ast,hashlib,json,os,stat,tempfile,unittest,subprocess,signal,sys
from pathlib import Path
from unittest.mock import patch
import guest,run
N='1'*32
def response():return {'nonce':N,'version':'7.4.33','sapi':'apache2handler','modules':['Core','date'],'ini_file':'/etc/php/7.4/apache2/php.ini'}
class Tests(unittest.TestCase):
 def test_projection(self):self.assertNotIn('nonce',guest.project(response(),N))
 def test_rejected_responses(self):
  for k,v in [('nonce','x'),('sapi','fpm-fcgi'),('version','8.3.6'),('modules',['Core','Core']),('modules',['bad\nmodule']),('ini_file','/unexpected')]:
   r=response();r[k]=v
   with self.assertRaises(guest.Rejected):guest.project(r,N)
  r=response();r['password']='synthetic'
  with self.assertRaises(guest.Rejected):guest.project(r,N)
 def test_bad_nonce_before_open(self):
  with patch.object(guest,'web_fd') as opened:
   with self.assertRaises(guest.Rejected):guest.owned_probe('../escape',lambda n:response())
   opened.assert_not_called()
 def test_trust_modes(self):
  def s(uid=0,gid=0,mode=0o755):return type('S',(),{'st_uid':uid,'st_gid':gid,'st_mode':stat.S_IFDIR|mode})()
  self.assertTrue(guest.trusted(s(),[],False));self.assertTrue(guest.trusted(s(mode=0o775),[],True))
  for info,attrs,exclusive in [(s(mode=0o775),[],False),(s(mode=0o777),[],True),(s(gid=33),[],True),(s(uid=1),[],True),(s(),['acl'],True)]:self.assertFalse(guest.trusted(info,attrs,exclusive))
 def test_group(self):
  g=type('G',(),{'gr_mem':['intruder']})();u=type('U',(),{'pw_uid':1,'pw_gid':0})()
  with patch.object(guest.grp,'getgrgid',return_value=g),patch.object(guest.pwd,'getpwall',return_value=[]):self.assertFalse(guest.root_group_exclusive())
  g.gr_mem=[]
  with patch.object(guest.grp,'getgrgid',return_value=g),patch.object(guest.pwd,'getpwall',return_value=[u]):self.assertFalse(guest.root_group_exclusive())
 def test_php_exact_legacy_expression(self):
  p=run.ROOT/'tools/php83/baseline-rehearsal/untimed_driver.py';tree=ast.parse(p.read_text());f=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='probe')
  assign=next(x for x in f.body if isinstance(x,ast.Assign) and x.targets[0].id=='code')
  expr=ast.Expression(assign.value);self.assertEqual(eval(compile(expr,'legacy','eval'),{'nonce':N}),guest.php_code(N))
 def test_pin(self):
  self.assertEqual(len(run.blobs()),6);self.assertEqual(run.sha((run.ROOT/run.RUNTIME).read_bytes()),run.RUNTIME_PIN)
 def test_unit(self):
  c=run.unit_command('baseline-web-'+8*'a');self.assertIn('ReadWritePaths=/opt/kaltura/app/api_v3/web',c);self.assertNotIn('/root/kaltura-baseline-private',c)
  with self.assertRaises(ValueError):run.unit_command('wrong;echo')
 def test_host_projection_closed(self):
  r=response();r.pop('nonce');r.update(nonce_verified=True,probe_removed=True,probe_code_sha256='a'*64,status='CURRENT_APACHE_PHP74_OBSERVED_OWN_PROBE_REMOVED',baseline_acceptance=False,app_credentials_read=False,sql_executed=False)
  self.assertTrue(run.project(json.dumps(r))['probe_removed'])
  r['raw_body']='synthetic'
  with self.assertRaises(ValueError):run.project(json.dumps(r))
 def test_owned_cleanup(self):
  # Isolated temporary fd; simulate root metadata only at the cleanup predicate.
  with tempfile.TemporaryDirectory() as d:
   real=guest.os.fstat
   def rootstat(fd):
    s=real(fd)
    return type('S',(),{'st_mode':s.st_mode,'st_uid':0,'st_nlink':s.st_nlink,'st_ino':s.st_ino,'st_dev':s.st_dev})()
   with patch.object(guest,'web_fd',side_effect=lambda:os.open(d,os.O_RDONLY|os.O_DIRECTORY)),patch.object(guest.os,'fstat',side_effect=rootstat):
    self.assertTrue(guest.owned_probe(N,lambda n:response())['probe_removed']);self.assertEqual(list(Path(d).iterdir()),[])
    def timeout(n):raise TimeoutError()
    with self.assertRaises(TimeoutError):guest.owned_probe(N,timeout)
    self.assertEqual(list(Path(d).iterdir()),[])
 def test_occupied_and_symlink(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/('baseline_provider_'+N+'.php');p.write_text('existing')
   with patch.object(guest,'web_fd',side_effect=lambda:os.open(d,os.O_RDONLY|os.O_DIRECTORY)):
    with self.assertRaises(FileExistsError):guest.owned_probe(N,lambda n:response())
    self.assertEqual(p.read_text(),'existing');p.unlink();p.symlink_to('/missing')
    with self.assertRaises(FileExistsError):guest.owned_probe(N,lambda n:response())
    self.assertTrue(p.is_symlink())
 def test_drift_preserved(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/('baseline_provider_'+N+'.php')
   def request(n):p.write_bytes(b'changed');return response()
   real=guest.os.fstat
   def rootstat(fd):
    s=real(fd);return type('S',(),{'st_mode':s.st_mode,'st_uid':0,'st_nlink':s.st_nlink,'st_ino':s.st_ino,'st_dev':s.st_dev})()
   with patch.object(guest,'web_fd',side_effect=lambda:os.open(d,os.O_RDONLY|os.O_DIRECTORY)),patch.object(guest.os,'fstat',side_effect=rootstat):
    with self.assertRaisesRegex(guest.Rejected,'PROBE_DRIFT'):guest.owned_probe(N,request)
   self.assertEqual(p.read_bytes(),b'changed')
 def test_actual_sigterm_cleanup(self):
  with tempfile.TemporaryDirectory() as d:
   code="""import sys,os,time
sys.path.insert(0,sys.argv[1]);import guest
real=guest.os.fstat
def rootstat(fd):
 s=real(fd);return type('S',(),{'st_mode':s.st_mode,'st_uid':0,'st_nlink':s.st_nlink,'st_ino':s.st_ino,'st_dev':s.st_dev})()
guest.os.fstat=rootstat
guest.web_fd=lambda:os.open(sys.argv[2],os.O_RDONLY|os.O_DIRECTORY)
def request(n):
 print('READY',flush=True);time.sleep(30)
guest.install_signal_cleanup()
try:guest.owned_probe('1'*32,request)
except guest.Rejected as e:
 assert str(e)=='INTERRUPTED';print('INTERRUPTED',flush=True)
"""
   p=subprocess.Popen([sys.executable,'-B','-c',code,str(Path(guest.__file__).parent),d],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
   try:
    import selectors
    sel=selectors.DefaultSelector();sel.register(p.stdout,selectors.EVENT_READ)
    try:self.assertTrue(sel.select(5));self.assertEqual(p.stdout.readline(),b'READY\n')
    finally:sel.close()
    p.send_signal(signal.SIGTERM);out,err=p.communicate(timeout=5)
    self.assertEqual((p.returncode,out,err),(0,b'INTERRUPTED\n',b''));self.assertEqual(list(Path(d).iterdir()),[])
   finally:
    if p.poll() is None:p.kill();p.communicate()
if __name__=='__main__':unittest.main()
