import importlib.util,json,tempfile,unittest
from pathlib import Path
s=importlib.util.spec_from_file_location('pipeline_prepare',Path(__file__).with_name('prepare.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class Prepare(unittest.TestCase):
 def test_real_source_closure(self):
  with tempfile.TemporaryDirectory() as d:
   r=m.prepare(Path('/tmp/kaltura-php83-audit/Rigel-18.20.0.zip'),Path(d)/'fresh')
   self.assertEqual(r['source_files'],11);self.assertEqual(len(r['files']),12);self.assertEqual(r['product_changes'],0)
 def test_existing_directory(self):
  with tempfile.TemporaryDirectory() as d:
   with self.assertRaises(ValueError):m.prepare(Path('/does/not/exist'),Path(d))
 def test_wrong_archive(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'wrong.zip';p.write_bytes(b'wrong')
   with self.assertRaises(ValueError):m.prepare(p,Path(d)/'new')
 def test_no_product_repair(self):
  text=Path(__file__).with_name('probe.php').read_text()
  self.assertNotIn('REDACTED',text);self.assertNotIn('preg_replace',text)
  self.assertIn("'stream'=>'php://memory'",text)
  self.assertIn('return false;',text)
  self.assertIn('KalturaLogFactory::getLogger($config)',text)
if __name__=='__main__':unittest.main()
