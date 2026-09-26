import json,pathlib,tempfile,unittest
import verify
class VerifyTests(unittest.TestCase):
 def stage(self,d):
  root=pathlib.Path(d); variants={}
  for v in ['exp12','prerequisite','candidate']:
   variants[v]={}
   for i in range(7):
    p=root/v/str(i);p.parent.mkdir(exist_ok=True);p.write_bytes(b'x');variants[v][str(i)]=verify.sha(b'x')
  data={'variants':variants,'harness':{}};(root/'identities.json').write_text(json.dumps(data));return root,verify.sha((root/'identities.json').read_bytes())
 def test_positive(self):
  with tempfile.TemporaryDirectory() as d:r,h=self.stage(d);verify.verify(r,h)
 def test_extra_file(self):
  with tempfile.TemporaryDirectory() as d:
   r,h=self.stage(d);(r/'extra').write_bytes(b'x')
   with self.assertRaises(ValueError):verify.verify(r,h)
 def test_mutation(self):
  with tempfile.TemporaryDirectory() as d:
   r,h=self.stage(d);(r/'candidate/0').write_bytes(b'y')
   with self.assertRaises(ValueError):verify.verify(r,h)
 def test_symlink(self):
  with tempfile.TemporaryDirectory() as d:
   r,h=self.stage(d);(r/'candidate/0').unlink();(r/'candidate/0').symlink_to(r/'prerequisite/0')
   with self.assertRaises(ValueError):verify.verify(r,h)
 def test_manifest_pin(self):
  with tempfile.TemporaryDirectory() as d:
   r,h=self.stage(d)
   with self.assertRaises(ValueError):verify.verify(r,'0'*64)
if __name__=='__main__':unittest.main()
