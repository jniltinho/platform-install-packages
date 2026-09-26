import importlib.util,json,unittest,copy
from pathlib import Path
s=importlib.util.spec_from_file_location('collect',Path(__file__).with_name('collect.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
TARGET='vendor/aws/Aws/Common/Credentials/Credentials.php'
class Guards(unittest.TestCase):
 def setUp(self):
  self.b={'kind':'plain','operation':'roundtrip','runtime':'8.3.6','probe_sha256':'a'*64,'loaded':{TARGET:'b'*64},'diagnostics':[]};self.manifest={'files':{'probe.php':'a'*64,'original/'+TARGET:'b'*64}}
 def runb(self,exit=0):return m.validate({'exit':exit,'stdout':json.dumps(self.b)},'original','plain','roundtrip',self.manifest)
 def test_valid(self):self.assertEqual(self.runb(),self.b)
 def test_bool_exit(self):
  with self.assertRaises(ValueError):self.runb(False)
 def test_float_exit(self):
  with self.assertRaises(ValueError):self.runb(0.0)
 def test_failed_exit(self):
  with self.assertRaises(ValueError):self.runb(255)
 def test_wrong_runtime(self):
  self.b['runtime']='8.4.0'
  with self.assertRaises(ValueError):self.runb()
 def test_empty_loaded(self):
  self.b['loaded']={}
  with self.assertRaises(ValueError):self.runb()
 def test_wrong_loaded(self):
  self.b['loaded'][TARGET]='c'*64
  with self.assertRaises(ValueError):self.runb()
 def test_missing_target(self):
  self.b['loaded']={'other':'a'*64};self.manifest['files']['original/other']='a'*64
  with self.assertRaises(ValueError):self.runb()
 def test_wrong_probe(self):
  self.b['probe_sha256']='d'*64
  with self.assertRaises(ValueError):self.runb()
 def test_wrong_operation(self):
  self.b['operation']='read'
  with self.assertRaises(ValueError):self.runb()
 def test_missing_diagnostics(self):
  self.b['diagnostics']=None
  with self.assertRaises(ValueError):self.runb()
if __name__=='__main__':unittest.main()
