import sys,unittest,tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent));import stage
ROOT=Path(__file__).resolve().parents[4];ART=ROOT.parent/'platform-install-packages-php83-artifacts'
class StageTests(unittest.TestCase):
 def test_actual_archive_join(self):
  with tempfile.TemporaryDirectory() as d:
   m=stage.stage(Path('/tmp/kaltura-php83-audit/Rigel-18.20.0.zip'),ART/'exp11/Rigel-18.20.0-php83-experimental.exp11.zip',ART/'exp12/Rigel-18.20.0-php83-experimental.exp12.zip',Path(d)/'fresh');self.assertEqual(m['exp12_sha256'],stage.PIN);self.assertEqual(len(m['files']),11)
 def test_bad_artifact(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'bad.zip';p.write_bytes(b'bad')
   with self.assertRaisesRegex(ValueError,'pin'):stage.stage(p,p,p,Path(d)/'out')
if __name__=='__main__':unittest.main()
