import copy,importlib.util,json,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent

def load(name):
 s=importlib.util.spec_from_file_location(name,HERE/(name+'.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
build=load('build');collect=load('collect')
class Proof(unittest.TestCase):
 def test_two_bytes_only(self):
  a=(build.SOURCE/build.TARGET).read_bytes();b=build.transform(a)
  old=b'$res .= $xml_element_name == NULL ? "" :\n\t\t\t$close_xml_element ?'
  off=a.index(old);left=off+len(b'$res .= ');right=off+len(old)-2
  self.assertEqual(b,a[:left]+b'('+a[left:right]+b')'+a[right:]);self.assertEqual(len(b),len(a)+2)
 def test_source_drift(self):
  with self.assertRaises(ValueError):build.transform((build.SOURCE/build.TARGET).read_bytes()+b' ')
 def records(self):return json.loads((collect.ROOT/'doc/php83/evidence/base-object-ternary/primary-r2.json').read_text())['records']
 def test_actual_record_validation(self):collect.validate(self.records())
 def test_timeout(self):
  a=self.records();a[0]['exit']=124
  with self.assertRaises(ValueError):collect.validate(a)
 def test_boolean_exit(self):
  a=self.records();a[0]['exit']=False
  with self.assertRaises(ValueError):collect.validate(a)
 def mutate(self,fn):
  a=self.records();b=json.loads(a[0]['stdout']);fn(b);a[0]['stdout']=json.dumps(b)
  with self.assertRaises(ValueError):collect.validate(a)
 def test_wrong_association(self):self.mutate(lambda b:b['rows'][0].update(value=''))
 def test_extra_diagnostic(self):self.mutate(lambda b:b['diagnostics'].append(b['diagnostics'][0]))
 def test_source_hash(self):self.mutate(lambda b:b['hashes'].update({build.TARGET:'0'*64}))
 def test_missing_case(self):self.mutate(lambda b:b['rows'].pop())
 def test_side_effect(self):self.mutate(lambda b:b['rows'][-1]['trace'].append(['unexpected']))
if __name__=='__main__':unittest.main()
