import importlib.util
from pathlib import Path
import tempfile
import unittest
s=importlib.util.spec_from_file_location('exp11_pin',Path(__file__).with_name('artifact.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class ArtifactPin(unittest.TestCase):
 def test_missing(self):
  with tempfile.TemporaryDirectory() as d:
   with self.assertRaises(FileNotFoundError):m.read_pin(Path(d)/'missing')
 def test_valid(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'pin';p.write_text('a'*64+'\n');self.assertEqual(m.read_pin(p),'a'*64)
 def test_pending(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'pin';p.write_text('PENDING')
   with self.assertRaises(RuntimeError):m.read_pin(p)
 def test_wrong_length(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'pin';p.write_text('a'*63)
   with self.assertRaises(RuntimeError):m.read_pin(p)
 def test_extra_data(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'pin';p.write_text('a'*64+' file.zip')
   with self.assertRaises(RuntimeError):m.read_pin(p)
if __name__=='__main__':unittest.main()
