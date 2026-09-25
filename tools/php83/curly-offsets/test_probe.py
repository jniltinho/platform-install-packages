import copy
import hashlib
import importlib.util
from pathlib import Path
import unittest
s=importlib.util.spec_from_file_location('curly_behavior',Path(__file__).with_name('collect.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class ProbeValidation(unittest.TestCase):
 def setUp(self):
  self.label='purifier';self.ids={self.label:{'candidate_sha256':'0'*64}}
  self.body={'case':self.label,'php':'8.3.6','source_path':m.PATHS[self.label],'source_sha256':'0'*64,'load_diagnostics':[], 'rows':[{'case':name,'value':value,'diagnostics':[]} for name,value in m.expected(self.label)]}
  self.body['rows'][-1]['diagnostics']=[{'phase':'native-string-overread','severity':2,'file':'probe.php','line':next(i for i,line in enumerate(Path(__file__).with_name('probe.php').read_text().splitlines(),1) if "recordCase('native-string-overread'" in line),'category':'uninitialized-string-offset','message_sha256':'2'*64}]
 def test_valid(self):m.validate(self.body,self.label,'83','candidate',self.ids)
 def test_drift(self):
  self.body['source_sha256']='1'*64
  with self.assertRaises(RuntimeError):m.validate(self.body,self.label,'83','candidate',self.ids)
 def test_bool_not_int(self):
  self.body['rows'][-3]['value'][1]=0
  with self.assertRaises(RuntimeError):m.validate(self.body,self.label,'83','candidate',self.ids)
 def test_extra_field(self):
  self.body['secret']='x'
  with self.assertRaises(RuntimeError):m.validate(self.body,self.label,'83','candidate',self.ids)
 def test_missing_case(self):
  self.body['rows'].pop()
  with self.assertRaises(RuntimeError):m.validate(self.body,self.label,'83','candidate',self.ids)
 def test_unexpected_diagnostic(self):
  self.body['rows'][0]['diagnostics']=[{}]
  with self.assertRaises(RuntimeError):m.validate(self.body,self.label,'83','candidate',self.ids)
 def test_expected_scope(self):
  self.assertEqual(len(m.expected('google-old')),20);self.assertEqual(len(m.expected('google-new')),20);self.assertEqual(len(m.expected('purifier')),28)
 def test_fixture_real_class_loading(self):
  source=Path(__file__).with_name('probe.php').read_text()
  self.assertIn("require '/audit/source/'.$paths[$label]",source)
  self.assertNotIn('class Google_Utils',source)
  self.assertNotIn('class HTMLPurifier_Encoder',source)
if __name__=='__main__':unittest.main()
