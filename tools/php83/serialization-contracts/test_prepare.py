import importlib.util,unittest
from pathlib import Path
s=importlib.util.spec_from_file_location('prepare',Path(__file__).with_name('prepare.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class Guards(unittest.TestCase):
 def test_exact_three_targets(self):self.assertEqual(len(m.TARGETS),3)
 def test_bridge_retains_legacy(self):
  x=b'<?php class X {\n    public function serialize() {return "N;";}\n}'
  y=m.candidate(x);self.assertEqual(y.count(b'public function serialize()'),1);self.assertIn(b'$this->serialize()',y);self.assertIn(b'$this->unserialize(',y)
 def test_no_duplicate_bridge(self):
  with self.assertRaises(ValueError):m.candidate(b'function __serialize() {}')
 def test_missing_signature(self):
  with self.assertRaises(ValueError):m.candidate(b'<?php')
 def test_ambiguous_signature(self):
  with self.assertRaises(ValueError):m.candidate(b'    public function serialize()'*2)
 def test_real_pinned_targets(self):
  a=m.read_sources(m.ORIGINAL);b=m.read_sources(m.EXP12)
  for p in m.TARGETS:self.assertEqual(a[p],b[p]);self.assertNotEqual(m.candidate(b[p]),b[p])
 def test_no_warning_suppression(self):self.assertNotIn('error_reporting',m.BRIDGE);self.assertNotIn('@',m.BRIDGE)
 def test_strict_envelope(self):self.assertIn("array_keys($data) !== array('payload')",m.BRIDGE);self.assertIn("!is_string($data['payload'])",m.BRIDGE)
if __name__=='__main__':unittest.main()
