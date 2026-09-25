import hashlib,json,tempfile,unittest
from pathlib import Path
import verify
class IdentityTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.base=Path(self.temp.name)
        files={}
        for n in verify.EXPECTED:
            (self.base/n).write_bytes(b'test');files[n]=hashlib.sha256(b'test').hexdigest()
        raw=json.dumps({'files':files}).encode();(self.base/'identities.json').write_bytes(raw);self.pin=hashlib.sha256(raw).hexdigest()
    def test_verified(self):self.assertEqual(len(verify.verify(self.base,self.pin)['files']),6)
    def test_manifest_drift(self):
        with self.assertRaises(ValueError):verify.verify(self.base,'0'*64)
    def test_fixture_drift(self):
        (self.base/'probe.php').write_bytes(b'changed')
        with self.assertRaises(ValueError):verify.verify(self.base,self.pin)
    def test_symlink(self):
        p=self.base/'probe.php';p.unlink();p.symlink_to(self.base/'run.sh')
        with self.assertRaises(ValueError):verify.verify(self.base,self.pin)
    def test_invalid_pin(self):
        with self.assertRaises(ValueError):verify.verify(self.base,'oops')
