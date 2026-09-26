import copy,json,unittest
import observe,build
class ObservationGuards(unittest.TestCase):
 def fixture(self):
  ids=json.loads(observe.COMPOSITION.read_text());ids['harness']={p:build.sha((build.HERE/p).read_bytes()) for p in ['probe.php','run.sh','verify.py']};return ids
 def test_source_binding(self):observe.validate_ids(self.fixture())
 def test_rehashed_malicious_variant(self):
  d=self.fixture();p=next(iter(d['variants']['candidate']));d['variants']['candidate'][p]='0'*64
  with self.assertRaises(ValueError):observe.validate_ids(d)
 def test_wrong_prerequisite(self):
  d=self.fixture();d['prerequisite_patch_sha256']='0'*64
  with self.assertRaises(ValueError):observe.validate_ids(d)
 def test_extra_harness(self):
  d=self.fixture();d['harness']['evil.php']='0'*64
  with self.assertRaises(ValueError):observe.validate_ids(d)
 def test_wrong_harness(self):
  d=self.fixture();d['harness']['probe.php']='0'*64
  with self.assertRaises(ValueError):observe.validate_ids(d)
 def test_runner_quiet_identity_stdout(self):
  text=(build.HERE/'run.sh').read_text()
  self.assertIn('python3 verify.py "$base" "$3" >/dev/null',text)
  self.assertIn('"$pin" >/dev/null || exit 70',text)
if __name__=='__main__':unittest.main()
