import importlib.util,json,pathlib,tempfile,unittest
HERE=pathlib.Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('pilot_compose',HERE/'compose-payload.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class PayloadGuards(unittest.TestCase):
 def test_selection_actual(self):
  d=json.loads(m.pinned(m.ROOT/'doc/php83/evidence/exp14-candidate/selected-r1/manifest.json',m.MANIFEST_PIN));self.assertEqual(len(m.validate_selection(d)),76)
 def test_collision(self):
  with self.assertRaises(ValueError):m.validate_selection({'patches':[{'path':'same'}]*76})
 def test_count(self):
  with self.assertRaises(ValueError):m.validate_selection({'patches':[]})
 def test_paths(self):
  for p in ['/outside','a/../b','../b','a//b','a/./b']:
   with self.subTest(p=p),self.assertRaises(ValueError):m.safe_path(p)
 def test_hash_drift(self):
  with tempfile.TemporaryDirectory() as t:
   p=pathlib.Path(t)/'x';p.write_bytes(b'a')
   with self.assertRaises(ValueError):m.pinned(p,m.sha(b'b'))
 def test_fresh_only(self):
  with tempfile.TemporaryDirectory() as t:
   with self.assertRaises(ValueError):m.compose(pathlib.Path(t))
 def test_no_newline_patch(self):
  a=b'first\nreturn false;';b=b'first\nreturn true;'
  p=m.patch_bytes('x.php',a,b);self.assertIn(b'No newline',p);m.policy.old.strict_replay('x.php',a,p,b)
 def test_added_source_patch(self):
  a=b'';b=b'<?php\nclass Added {}\n';p=m.patch_bytes('x.php',a,b);m.policy.old.strict_replay('x.php',a,p,b)
 def test_no_change_not_patch(self):
  with self.assertRaises(ValueError):m.patch_bytes('x.php',b'a',b'a')
 def test_privacy_five_unique(self):self.assertEqual(len(set(m.policy.TARGETS+[m.sql.TARGET])),5)
 def test_added_rejects_all_kinds(self):
  for regular in (False,True):
   with self.assertRaises(ValueError):m.check_target_member('a.php',{'a.php'},regular)
 def test_nonregular_target(self):
  with self.assertRaises(ValueError):m.check_target_member('a.php',set(),False)
 def test_privacy_contract_pinned(self):self.assertEqual(len(m.verify_privacy_inputs()['expected_privacy_after']),5)
 def test_privacy_output_rejects_drift(self):
  changed={p:b'bad' for p in m.CONTRACT['expected_privacy_after']}
  with self.assertRaises(ValueError):m.validate_privacy_outputs(changed)
if __name__=='__main__':unittest.main()
