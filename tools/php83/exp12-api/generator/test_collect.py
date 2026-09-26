import importlib.util,unittest,json
from pathlib import Path
s=importlib.util.spec_from_file_location('c',Path(__file__).with_name('collect.py'));c=importlib.util.module_from_spec(s);s.loader.exec_module(c)
class GuardTests(unittest.TestCase):
 def rows(self):return [{'runtime':rt,'variant':v,'mode':'generate','case':'module','exit':0} for rt,v in c.VARIANTS]
 def test_matrix(self):self.assertEqual(c.validate_matrix(self.rows(),{'generate':['module']}),4)
 def test_duplicate(self):
  rows=self.rows();rows[1]=rows[0]
  with self.assertRaises(ValueError):c.validate_matrix(rows,{'generate':['module']})
 def test_bool_exit(self):
  rows=self.rows();rows[0]['exit']=False
  with self.assertRaises(ValueError):c.validate_matrix(rows,{'generate':['module']})
 def test_missing(self):
  with self.assertRaises(ValueError):c.validate_matrix(self.rows()[:-1],{'generate':['module']})
 def test_unsafe_generated_path(self):
  with self.assertRaises(ValueError):c.decode_outputs({'outputs':{'../bad':{}}})
 def test_checksum_duplicate(self):
  with self.assertRaises(ValueError):c.parse_checksums(('a'*64+'  /x\n')*2)
 def test_checksum_malformed(self):
  with self.assertRaises(ValueError):c.parse_checksums('bad\n')
 def test_empty_outputs(self):self.assertEqual(c.decode_outputs({'outputs':[]}),{})
if __name__=='__main__':unittest.main()
