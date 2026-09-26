"""Repository-local fake subprocess controls; not PHP/runtime evidence."""
import base64,importlib.util,json,subprocess,unittest
from pathlib import Path
from types import SimpleNamespace
s=importlib.util.spec_from_file_location('collector',Path(__file__).with_name('collect-r2.py'));c=importlib.util.module_from_spec(s);s.loader.exec_module(c)
class Retention(unittest.TestCase):
 def result(self,out,err=b'warning',rc=0):
  return c.observe_process(['synthetic-no-execution'],'',{'variant':'original','kind':'plain','operation':'roundtrip','writer':None},lambda *a,**k:SimpleNamespace(returncode=rc,stdout=out,stderr=err))
 def test_malformed_json_retained(self):
  row=self.result(b'not-json');self.assertEqual(base64.b64decode(row['stdout_base64']),b'not-json')
  with self.assertRaises(ValueError):c.validate(row,'74',{})
 def test_scalar_json_retained(self):
  for raw in [b'null',b'[]',b'false',b'1',b'"text"']:
   row=self.result(raw);self.assertEqual(row['stdout'],raw.decode())
   with self.assertRaises(ValueError):c.validate(row,'74',{})
 def test_malformed_runtime_shape(self):
  row=self.result(b'{"runtime":null,"result":{}}')
  with self.assertRaises(ValueError):c.validate(row,'74',{})
 def test_invalid_utf8_bytes_retained(self):
  row=self.result(b'\xff',b'\xfe');self.assertIs(row['invalid_utf8_output'],True);self.assertEqual(base64.b64decode(row['stdout_base64']),b'\xff');self.assertEqual(base64.b64decode(row['stderr_base64']),b'\xfe')
 def test_timeout_partial_channels_retained(self):
  def timeout(*a,**k):raise subprocess.TimeoutExpired(a[0],60,output=b'partial',stderr=b'timeout-stderr')
  row=c.observe_process(['synthetic'],'',{},timeout);self.assertIsNone(row['exit']);self.assertTrue(row['timeout']);self.assertEqual(row['stdout'],'partial');self.assertEqual(row['stderr'],'timeout-stderr')
 def test_launch_failure_retained(self):
  def fail(*a,**k):raise OSError('synthetic launch failure')
  row=c.observe_process(['synthetic'],'',{},fail);self.assertIsNone(row['exit']);self.assertEqual(row['launch_error'],'synthetic launch failure')
 def test_nonzero_exit_retained(self):
  row=self.result(b'failure',rc=255);self.assertEqual(row['exit'],255);self.assertEqual(row['stdout'],'failure')
 def test_wrong_wire_shape(self):
  for value in [None,[],False,{'base64':False,'sha256':'a','format':'C'}]:
   with self.assertRaises(ValueError):c.wiredata(value)
 def test_invalid_wire_never_inserted(self):
  wires={}
  with self.assertRaises(ValueError):c.remember_wire(wires,'original/plain',{'base64':'Tjs=','sha256':'wrong','format':'N'})
  self.assertEqual(wires,{})
if __name__=='__main__':unittest.main()
