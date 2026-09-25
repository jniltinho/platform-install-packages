import importlib.util,json,unittest
from pathlib import Path
s=importlib.util.spec_from_file_location('a',Path(__file__).with_name('collect_arity.py'));a=importlib.util.module_from_spec(s);s.loader.exec_module(a)
class ArityTests(unittest.TestCase):
 def row(self,constant=0):return {'runtime':'83','case':'zero','exit':0,'stderr':'','stdout':json.dumps({'runtime':'8.3.6','returned':True,'returned_type':'boolean','defined':True,'constant':constant,'diagnostics':[],'exception':None})}
 def test_numeric_contract(self):a.contract(self.row())
 def test_bool_not_integer(self):
  with self.assertRaises(ValueError):a.contract(self.row(False))
 def test_wrong_integer(self):
  with self.assertRaises(ValueError):a.contract(self.row(1))
 def test_exit_bool(self):
  r=self.row();r['exit']=False
  with self.assertRaises(ValueError):a.contract(r)
 def test_stderr(self):
  r=self.row();r['stderr']='warning'
  with self.assertRaises(ValueError):a.contract(r)
 def test_literal_zero(self):self.assertEqual(a.p.statement(b"define('SF_DEBUG', 0);"),b"define('SF_DEBUG', 0);")
 def test_literal_one(self):a.p.statement(b"define('SF_DEBUG', 1);")
 def test_literal_empty(self):
  with self.assertRaises(ValueError):a.p.statement(b"define('SF_DEBUG', );")
 def test_injection(self):
  with self.assertRaises(ValueError):a.p.statement(b"define('SF_DEBUG', 0); echo 1;")
 def test_expression(self):
  with self.assertRaises(ValueError):a.p.statement(b"define('SF_DEBUG', (0));")
 def test_duplicate(self):
  with self.assertRaises(ValueError):a.p.statement(b"define('SF_DEBUG', 0);\ndefine('SF_DEBUG', 1);")
if __name__=='__main__':unittest.main()
