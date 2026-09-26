import importlib.util,unittest,tempfile
from pathlib import Path
s=importlib.util.spec_from_file_location('gstage',Path(__file__).with_name('stage.py'));g=importlib.util.module_from_spec(s);s.loader.exec_module(g)
class StageTests(unittest.TestCase):
 def test_archive_join(self):
  artifact=g.ROOT.parent/'platform-install-packages-php83-artifacts/exp12/Rigel-18.20.0-php83-experimental.exp12.zip'
  with tempfile.TemporaryDirectory() as d:
   output=Path(d)/'new';g.stage(artifact,output);self.assertTrue((output/'artifact-provenance.json').exists())
 def test_bad_artifact(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'bad.zip';p.write_bytes(b'bad')
   with self.assertRaises(ValueError):g.stage(p,Path(d)/'out')
if __name__=='__main__':unittest.main()
