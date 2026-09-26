import json,unittest
from unittest.mock import patch,Mock
import run_untimed as r
class RunnerTests(unittest.TestCase):
    def test_only_fixed_guest(self):
        self.assertEqual(r.SSH[-1],'baseline74');self.assertNotIn('192.168.56.20',r.STAGE)
    def test_verify_rejects_nonzero(self):
        with patch.object(r,'remote',return_value=Mock(returncode=1,stdout=b'STAGE_PINNED')):
            with self.assertRaises(ValueError):r.verify({'a':'b'})
    def test_verify_requires_exact_output(self):
        with patch.object(r,'remote',return_value=Mock(returncode=0,stdout=b'not verified')):
            with self.assertRaises(ValueError):r.verify({'a':'b'})
    def test_verify_success_bound_to_manifest(self):
        with patch.object(r,'remote',return_value=Mock(returncode=0,stdout=b'STAGE_PINNED\n')) as remote:r.verify({'a':'b'})
        self.assertEqual(json.loads(remote.call_args.args[1]),{'a':'b'})
    def test_inventory_remote_fail(self):
        with patch.object(r,'remote',return_value=Mock(returncode=1)),patch.object(r.Path,'read_bytes',return_value=b'public program'):
            with self.assertRaisesRegex(ValueError,'inventory'):r.inventory()
    def test_existing_evidence_stops_before_ssh(self):
        with patch.object(r.Path,'exists',return_value=True),patch.object(r,'remote') as remote:
            with self.assertRaisesRegex(ValueError,'overwrite'):r.main()
            remote.assert_not_called()
if __name__=='__main__':unittest.main()
