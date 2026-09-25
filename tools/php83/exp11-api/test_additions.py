"""Local retained-corpus/guard tests only; no VM, PHP or SQL."""
import copy,importlib.util,unittest
from pathlib import Path
s=importlib.util.spec_from_file_location('exp11_additions',Path(__file__).with_name('collect-additions.py'))
m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class AdditionCorpus(unittest.TestCase):
 def setUp(self):
  self.contract,self.expected=m.reference_records()
  self.records=[dict(family=f,case=c,**self.expected[(f,c)]) for f,c in m.CASES]
 def test_reviewed17_processes(self):self.assertEqual(m.validate(self.records,self.expected)['positive_processes'],16)
 def test_duplicate(self):
  self.records[1]=copy.deepcopy(self.records[0])
  with self.assertRaises(ValueError):m.validate(self.records,self.expected)
 def test_missing(self):
  with self.assertRaises(ValueError):m.validate(self.records[:-1],self.expected)
 def test_extra(self):
  with self.assertRaises(ValueError):m.validate(self.records+self.records[:1],self.expected)
 def test_boolean_status(self):
  self.records[0]['exit']=False
  with self.assertRaises(ValueError):m.validate(self.records,self.expected)
 def test_float_status(self):
  self.records[0]['exit']=0.0
  with self.assertRaises(ValueError):m.validate(self.records,self.expected)
 def test_extra_stdout(self):
  self.records[0]['stdout']+='x'
  with self.assertRaises(ValueError):m.validate(self.records,self.expected)
 def test_missing_stderr(self):
  self.records[0]['stderr']=''
  with self.assertRaises(ValueError):m.validate(self.records,self.expected)
 def test_fatal_must_remain_fatal(self):
  self.records[-1]['exit']=0
  with self.assertRaises(ValueError):m.validate(self.records,self.expected)
 def test_actual_fixture_pins(self):self.assertGreater(len(m.fixtures()),10)
if __name__=='__main__':unittest.main()
