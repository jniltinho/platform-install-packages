import importlib.util,pathlib,unittest,tempfile
P=pathlib.Path(__file__).with_name('build.py');s=importlib.util.spec_from_file_location('builder',P);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class Tests(unittest.TestCase):
 def fixture(self,p):return ('<?php\n'+ '\n'.join(x[0] for x in m.RULES[p])+'\n/* unchanged */\n').encode()
 def test_all_exact_edits(self):
  for p,rules in m.RULES.items():
   b=self.fixture(p);a=m.transform(p,b,m.sha(b))
   self.assertIn(b'/* unchanged */',a)
   self.assertEqual(a.count(b'function '),b.count(b'function '))
   for old,new in rules:self.assertIn((new+'\n').encode(),a)
 def test_hash_drift(self):
  p=next(iter(m.RULES));b=self.fixture(p)
  with self.assertRaises(ValueError):m.transform(p,b+b' ',m.sha(b))
 def test_missing_declaration(self):
  p=next(iter(m.RULES));b=b'<?php\n'
  with self.assertRaises(ValueError):m.transform(p,b,m.sha(b))
 def test_duplicate_declaration(self):
  p=next(iter(m.RULES));b=self.fixture(p)*2
  with self.assertRaises(ValueError):m.transform(p,b,m.sha(b))
 def test_unapproved_target(self):
  with self.assertRaises(ValueError):m.transform('x',b'',m.sha(b''))
 def test_candidate_collision(self):
  p=next(iter(m.RULES));b=self.fixture(p)+(m.RULES[p][0][1]+'\n').encode()
  with self.assertRaises(ValueError):m.transform(p,b,m.sha(b))
 def test_three_narrow_attributes(self):
  attrs=[(p,o,n) for p,v in m.RULES.items() for o,n in v if '#[' in n]
  self.assertEqual(len(attrs),3);self.assertTrue(all(p.endswith('/PropelPDO.php') for p,o,n in attrs))
 def test_no_transaction_native_bool(self):
  for p,v in m.RULES.items():
   for old,new in v:
    if any(x in old for x in ['beginTransaction','commit()','rollBack()']):self.assertNotIn(': bool',new)
 def test_existing_output_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   with self.assertRaises(ValueError):m.build('nonexistent',d)
 def test_wrong_zip_refused_before_output(self):
  with tempfile.TemporaryDirectory() as d:
   p=pathlib.Path(d);(p/'bad').write_bytes(b'bad')
   with self.assertRaises(ValueError):m.build(p/'bad',p/'out')
   self.assertFalse((p/'out').exists())
if __name__=='__main__':unittest.main()
