import hashlib,importlib.util,json,pathlib,sys,tempfile,unittest
from unittest import mock
import run as r
class Tests(unittest.TestCase):
 def host(self):return '\n'.join(k+'="'+v+'"' for k,v in {'UUID':r.UUID,'name':'kaltura-php74-noble-baseline','VMState':'running','cpus':'4','memory':'8192','Forwarding(0)':'ssh,tcp,127.0.0.1,2201,,22'}.items())
 def test_target_nat(self):
  self.assertEqual(r.host_guard(self.host())['UUID'],r.UUID)
  for old,new in [('2201','2200'),('127.0.0.1','0.0.0.0'),('running','paused'),(r.UUID,'0'*36)]:self.assertRaises(r.Rejected,r.host_guard,self.host().replace(old,new))
 def test_network_no_web_write(self):
  cmd=r.unit_command('baseline-freeze-12345678');self.assertIn('ProtectSystem=strict',cmd);self.assertIn('IPAddressAllow=192.168.56.74/32',cmd);self.assertNotIn('api_v3/web',cmd)
  self.assertRaises(r.Rejected,r.unit_command,'bad;command')
 def test_exact_pins(self):
  for name,pin in r.PINS.items():self.assertEqual(hashlib.sha256((r.HERE/name).read_bytes()).hexdigest(),pin)
 def test_bounded_child_output_and_error_redaction(self):
  rc,raw,n=r.bounded([sys.executable,'-c',"import sys;print('SAFE');sys.stderr.write('SYNTHETIC_SECRET')"],timeout=5)
  self.assertEqual((rc,raw,n),(0,b'SAFE\n',16))
  self.assertRaises(r.Rejected,r.bounded,[sys.executable,'-c',"print('x'*1024)"],timeout=5,cap=64)
 def test_check_no_mutation(self):
  with mock.patch.object(r,'check',return_value=({},{})),mock.patch.object(r,'remote') as remote:
   self.assertEqual(r.main(True,None)['status'],'READ_ONLY_PREFLIGHT_PASSED');remote.assert_not_called()
 def test_existing_output_rejected_before_ssh(self):
  with tempfile.TemporaryDirectory() as d,mock.patch.object(r,'check') as check:
   self.assertRaises(r.Rejected,r.main,False,d);check.assert_not_called()
 def test_public_reduced_projection(self):
  self.assertRaises(Exception,r.public_rows,b'{"unexpected":"SYNTHETIC_SECRET"}\n')
  value=r.public_rows(b'{"status":"INCOMPLETE","error":{"body":"SYNTHETIC_SECRET"}}\n')
  self.assertEqual(value,[{'status':'INCOMPLETE'}]);self.assertNotIn('SYNTHETIC',json.dumps(value))
 def test_stdin_deadline(self):
  import time
  start=time.monotonic()
  self.assertRaises(r.Rejected,r.bounded,[sys.executable,'-c','import time;time.sleep(5)'],data=b'x'*500000,timeout=.1)
  self.assertLess(time.monotonic()-start,2)
 def test_exited_leader_descendant_pipe_deadline(self):
  import time
  start=time.monotonic()
  self.assertRaises(r.Rejected,r.bounded,[sys.executable,'-c','import os,time; p=os.fork(); time.sleep(5) if p==0 else None'],timeout=.1)
  self.assertLess(time.monotonic()-start,2)
if __name__=='__main__':unittest.main()
