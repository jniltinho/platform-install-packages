import pathlib,tempfile,unittest
import compose
class CompositionTests(unittest.TestCase):
 def test_strict_success(self):
  self.assertEqual(compose.apply_patch(b'a\nb\nc\n','f',b'--- a/f\n+++ b/f\n@@ -1,3 +1,3 @@\n a\n-b\n+B\n c\n'),b'a\nB\nc\n')
 def test_offset_rejected(self):
  with self.assertRaises(ValueError):compose.apply_patch(b'x\na\nb\nc\n','f',b'--- a/f\n+++ b/f\n@@ -1,3 +1,3 @@\n a\n-b\n+B\n c\n')
 def test_failed_patch_rejected(self):
  with self.assertRaises(ValueError):compose.apply_patch(b'a\n','f',b'--- a/f\n+++ b/f\n@@ -1 +1 @@\n-b\n+B\n')
 def test_existing_output(self):
  with tempfile.TemporaryDirectory() as d:
   with self.assertRaises(ValueError):compose.compose('missing',d)
 def test_bad_archive(self):
  with tempfile.TemporaryDirectory() as d:
   p=pathlib.Path(d);(p/'bad').write_bytes(b'x')
   with self.assertRaises(ValueError):compose.compose(p/'bad',p/'out')
   self.assertFalse((p/'out').exists())
if __name__=='__main__':unittest.main()
