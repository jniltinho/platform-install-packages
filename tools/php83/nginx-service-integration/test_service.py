import hashlib,os,pathlib,subprocess,tempfile,unittest
from unittest import mock
import service as s
import generate as g

class Tests(unittest.TestCase):
 def contract(self):
  return {'schema':1,'seconds':120,'socket_gid':7373,'files':{str(s.BINARY):s.BINARY_PIN,str(s.BASE/'lab_adapter.py'):s.ADAPTER_PIN,str(s.BASE/'sanitizer.py'):s.SANITIZER_PIN,str(s.CONFIG):'a'*64}}
 def test_contract(self):self.assertEqual(len(s.validate_contract(self.contract())),4)
 def test_fixed_lifetime(self):
  for value in (0,121,True,120.0):
   c=self.contract();c['seconds']=value
   with self.assertRaises(ValueError):s.validate_contract(c)
 def test_pins_and_closure_reject(self):
  for path,pin in (('/tmp/unreviewed','a'*64),(str(s.BINARY),'b'*64),(str(s.CONFIG),'not-a-pin')):
   c=self.contract();c['files'][path]=pin
   with self.assertRaises(ValueError):s.validate_contract(c)
 def test_arbitrary_group_rejected(self):
  for gid in (0,33,112,True):
   c=self.contract();c['socket_gid']=gid
   with self.assertRaises(ValueError):s.validate_contract(c)
 def test_identity_group_current_observation(self):
  import types
  user=types.SimpleNamespace(pw_uid=7373,pw_gid=7373,pw_name='kaltura')
  group=types.SimpleNamespace(gr_gid=7373,gr_mem=['www-data'])
  with mock.patch.object(s.os,'geteuid',return_value=0),mock.patch.object(s.os,'getegid',return_value=0),mock.patch.object(s.socket,'gethostname',return_value='kaltura-php83-lab'),mock.patch.object(s,'read'),mock.patch.object(s.subprocess,'run',return_value=types.SimpleNamespace(stdout=b'[{"addr_info":[{"local":"192.168.56.83"}]}]')),mock.patch.object(s.Path,'stat',return_value=types.SimpleNamespace(st_gid=0,st_mode=0o100644)),mock.patch.object(s.pwd,'getpwnam',return_value=user),mock.patch.object(s.grp,'getgrnam',return_value=group),mock.patch.object(s.pwd,'getpwall',return_value=[user]):
   s.lab_identity()
   group.gr_mem.append('unexpected')
   with self.assertRaises(ValueError):s.lab_identity()
 def test_unknown_contract_fields(self):
  c=self.contract();c['shell']='bad'
  with self.assertRaises(ValueError):s.validate_contract(c)
 def test_no_raw_exceptions(self):
  with mock.patch.object(s,'execute',side_effect=RuntimeError('PRIVATE_CANARY')):
   self.assertEqual(s.main(),1)
 def test_nonroot_rejection(self):
  with mock.patch.object(s.os,'geteuid',return_value=1000):
   self.assertEqual(s.main(),1)
 def test_unit_contract(self):
  unit=g.artifacts()['kaltura-nginx.service']
  for item in ('Type=simple','KillMode=control-group','Restart=no','RuntimeMaxSec=126','TimeoutStopSec=6','StandardError=null','-I -B'):
   self.assertIn(item,unit)
  self.assertNotIn('ExecStartPre=',unit);self.assertNotIn('nginx -t',unit)
 def test_init_syntax_no_unmanaged_paths(self):
  with tempfile.TemporaryDirectory() as tmp:
   p=pathlib.Path(tmp)/'init';p.write_text(g.INIT)
   self.assertEqual(subprocess.run(['sh','-n',str(p)],capture_output=True).returncode,0)
   r=subprocess.run(['sh',str(p),'configtest'],capture_output=True)
   self.assertEqual(r.returncode,2);self.assertEqual(r.stderr,b'LAB_ACTION_REQUIRES_REVIEW\n')
  self.assertNotIn('start-stop-daemon',g.INIT);self.assertNotIn('/opt/kaltura/nginx/sbin',g.INIT);self.assertNotIn('|| true',g.INIT)
 def test_pin_actual_dependencies(self):
  root=pathlib.Path(__file__).resolve().parents[1]
  self.assertEqual(hashlib.sha256((root/'nginx-log-privacy-supervisor/lab_adapter.py').read_bytes()).hexdigest(),s.ADAPTER_PIN)
  self.assertEqual(hashlib.sha256((root/'nginx-log-privacy/sanitizer.py').read_bytes()).hexdigest(),s.SANITIZER_PIN)
if __name__=='__main__':unittest.main()
