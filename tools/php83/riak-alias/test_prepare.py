import hashlib,importlib.util,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('riak_prepare',HERE/'prepare.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
ZIP=Path('/tmp/kaltura-php83-audit/Rigel-18.20.0.zip')
class Guards(unittest.TestCase):
 def test_exact_source_delta(self):
  with tempfile.TemporaryDirectory() as t:
   out=Path(t)/'stage';r=m.prepare(ZIP,out);self.assertEqual(r['files'],14)
   manifest=json.loads((out/'identities.json').read_text());self.assertEqual(r['manifest_sha256'],m.sha((out/'identities.json').read_bytes()))
   for n,h in manifest['files'].items():self.assertEqual(m.sha((out/n).read_bytes()),h)
   n='vendor/aws/Doctrine/Common/Cache/RiakCache.php';a=(out/'original'/n).read_text();b=(out/'candidate'/n).read_text()
   b=b.replace('use Riak\\Object as RiakObject;','use Riak\\Object;').replace('new RiakObject($id)','new Object($id)').replace('isExpired(RiakObject $object)','isExpired(Object $object)')
   self.assertEqual(a,b);self.assertIn('$winner = $objectList[count($objectList)];',b)
 def test_existing_rejected(self):
  with tempfile.TemporaryDirectory() as t:
   with self.assertRaises(ValueError):m.prepare(ZIP,Path(t))
 def test_zip_drift(self):
  with tempfile.TemporaryDirectory() as t:
   p=Path(t)/'bad.zip';p.write_bytes(b'bad')
   with self.assertRaises(ValueError):m.prepare(p,Path(t)/'stage')
 def test_patch_drift(self):
  with tempfile.TemporaryDirectory() as t,patch.dict(m.PINS,{'patch_sha256':'0'*64}):
   with self.assertRaises(ValueError):m.prepare(ZIP,Path(t)/'stage')
 def test_source_drift(self):
  with tempfile.TemporaryDirectory() as t,patch.dict(m.PINS,{'files':{'vendor/aws/Doctrine/Common/Cache/Cache.php':'0'*64}}):
   with self.assertRaises(ValueError):m.prepare(ZIP,Path(t)/'stage')
 def test_candidate_drift(self):
  with tempfile.TemporaryDirectory() as t,patch.dict(m.PINS,{'candidate_sha256':'0'*64}):
   with self.assertRaises(ValueError):m.prepare(ZIP,Path(t)/'stage')
if __name__=='__main__':unittest.main()
