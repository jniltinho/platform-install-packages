import copy,importlib.util,json
from pathlib import Path
import unittest
s=importlib.util.spec_from_file_location('collector',Path(__file__).with_name('collect.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class Adapter(unittest.TestCase):
 def setUp(self):
  self.rows=m.expected_rows();self.prep=json.loads((m.ROOT/'doc/php83/evidence/exp13-xml/preparation.json').read_bytes())
 def row(self):
  phase,kind,variant,case,ref=self.rows[0];r=copy.deepcopy(ref);r.update(kind=kind,variant=variant,case=case)
  manifest=json.loads((m.ROOT/self.prep['stages'][phase]['local']/'identities.json').read_bytes());return r,ref,manifest
 def test_non_utf8_retains_both(self):
  row={}
  with self.assertRaises(UnicodeDecodeError):m.retain_channels(row,b'\xff',b'native stderr')
  import base64
  self.assertEqual(base64.b64decode(row['stdout_base64']),b'\xff');self.assertEqual(base64.b64decode(row['stderr_base64']),b'native stderr')
 def test_inventory(self):self.assertEqual(len(self.rows),40);self.assertEqual(sum(x[0]=='chain' for x in self.rows),2)
 def test_historical40(self):
  for phase,kind,variant,case,ref in self.rows:
   r=dict(ref,kind=kind,variant=variant,case=case);manifest=json.loads((m.ROOT/self.prep['stages'][phase]['local']/'identities.json').read_bytes());m.validate(r,ref,manifest)
 def test_exit_bool(self):
  r,ref,manifest=self.row();r['exit']=False
  with self.assertRaises(ValueError):m.validate(r,ref,manifest)
 def test_stderr_loss(self):
  r,ref,manifest=self.row();r['stderr']='changed'
  with self.assertRaises(ValueError):m.validate(r,ref,manifest)
 def test_source_drift(self):
  r,ref,manifest=self.row();manifest['files']['baseline/alpha/config/kConf.php']='0'*64
  with self.assertRaises(ValueError):m.validate(r,ref,manifest)
if __name__=='__main__':unittest.main()
