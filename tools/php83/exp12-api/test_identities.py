import copy,importlib.util,unittest
from pathlib import Path
s=importlib.util.spec_from_file_location('ci',Path(__file__).with_name('compare-identities.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class IdentityTests(unittest.TestCase):
 def reports(self):
  r=[]
  for helper in ['runtime-identity.py','runtime-identity.py','runtime83-identity.py','runtime83-identity.py']:
   r.append({'exit':0,'collector_sha256':m.sha((m.HERE/helper).read_bytes()),'identity':{'files':{'php':'pin'}},'command':['ssh','same'],'artifact_pin':(m.HERE/'artifact-sha256.txt').read_text().strip()})
  return r
 def test_equal(self):self.assertEqual(len(m.compare(*self.reports())),2)
 def reject(self,index,key,value):
  r=self.reports();r[index][key]=value
  with self.assertRaises(ValueError):m.compare(*r)
 def test_identity(self):self.reject(1,'identity',{})
 def test_native_identity(self):self.reject(3,'identity',{})
 def test_bool_exit(self):self.reject(0,'exit',False)
 def test_collector(self):self.reject(2,'collector_sha256','wrong')
 def test_command(self):self.reject(3,'command',[])
 def test_artifact(self):self.reject(1,'artifact_pin','wrong')
 def test_distinct_paths(self):m.distinct_inputs([Path('/tmp/'+n) for n in ['a','b','c','d']])
 def test_duplicate_paths(self):
  with self.assertRaises(ValueError):m.distinct_inputs([Path('/tmp/a')]*4)
 def test_canonical_duplicate(self):
  with self.assertRaises(ValueError):m.distinct_inputs([Path('/tmp/a'),Path('/tmp/x/../a'),Path('/tmp/c'),Path('/tmp/d')])
if __name__=='__main__':unittest.main()

