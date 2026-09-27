import copy,json,pathlib,unittest
import observe74
class AdapterTests(unittest.TestCase):
 def test_upstream_stage_and_module_pins(self):
  blobs,m=observe74.payload();g=blobs['guest.py'].decode();compile(g,'guest74.py','exec')
  self.assertEqual(m['base_archive_sha256'],observe74.prepare.policy.old.UPSTREAM)
  self.assertEqual(m['after_sha256'],'40e4db5733cfab59e0e873f94ee64166de380d86425625411dc716f6cb1003dd')
  self.assertIn('kaltura-php74-baseline',g);self.assertNotIn('kaltura-php83-lab',g)
  self.assertIn(observe74.JSON_PIN,g);self.assertIn('extension='+observe74.JSON,g)
  self.assertEqual(blobs['probe.php'],(observe74.HERE/'probe.php').read_bytes())
 def test_different_runtime_rejected(self):
  _,m=observe74.payload()
  r={'source_before':m['files'],'source_after':m['files'],'runtime_before':observe74.PHP_PIN,'runtime_after':'bad','json_sha256_after':observe74.JSON_PIN,'processes':[]}
  with self.assertRaises(ValueError):observe74.reconcile(r,m)
 def test_original83_not_valid74(self):
  _,m=observe74.payload();r=json.loads((observe74.OUT/'primary.json').read_text())
  with self.assertRaises(ValueError):observe74.reconcile(r,m)
if __name__=='__main__':unittest.main()
