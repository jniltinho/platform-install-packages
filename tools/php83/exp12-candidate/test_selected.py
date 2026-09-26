import importlib.util,json,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent));import selected as s
class SelectedTests(unittest.TestCase):
 def test_exact(self):self.assertEqual(len(s.validate(s.SELECTED.read_bytes())['patches']),65)
 def test_patch_drift(self):
  d=json.loads(s.SELECTED.read_text());d['patches'][0]['after_sha256']='0'*64
  with self.assertRaises(ValueError):s.validate(json.dumps(d).encode())
 def test_publication(self):
  d=json.loads(s.SELECTED.read_text());d['selection_authorization']['release_publication_approved']=True
  with self.assertRaises(ValueError):s.validate(json.dumps(d).encode())
 def test_cache_waiver(self):
  d=json.loads(s.SELECTED.read_text());d['selection_authorization']['strict_cross_engine_cache_layout']='PASS'
  with self.assertRaises(ValueError):s.validate(json.dumps(d).encode())
 def test_draft_drift(self):
  with self.assertRaises(ValueError):s.make_selected(s.DRAFT.read_bytes()+b' ')
 def test_fresh_stage(self):
  with tempfile.TemporaryDirectory() as d:
   out=Path(d)/'patches';r=s.stage('/tmp/kaltura-php83-audit/Rigel-18.20.0.zip',out);self.assertEqual(r['targets'],65);self.assertEqual(len(list(out.iterdir())),66)
   with self.assertRaises(ValueError):s.stage('/tmp/kaltura-php83-audit/Rigel-18.20.0.zip',out)
if __name__=='__main__':unittest.main()
