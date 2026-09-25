import importlib.util, tempfile, unittest
from pathlib import Path
S=importlib.util.spec_from_file_location('prepare',Path(__file__).with_name('prepare.py')); m=importlib.util.module_from_spec(S); S.loader.exec_module(m)
class PreparationTests(unittest.TestCase):
    def test_three_patches(self): self.assertEqual(len(m.patches()),3)
    def test_patch_hashes(self):
        for row in m.patches(): self.assertEqual(m.sha(row['patch']),row['patch_sha256'])
    def test_bad_zip_refused_before_destination(self):
        with tempfile.TemporaryDirectory() as td:
            z=Path(td)/'wrong.zip'; z.write_bytes(b'bad'); d=Path(td)/'out'
            with self.assertRaisesRegex(ValueError,'identity'): m.prepare(z,d)
            self.assertFalse(d.exists())
    def test_native_diagnostics_not_suppressed(self): self.assertIn('return false; // Native diagnostics', (m.HERE/'probe.php').read_text())
    def test_sandbox_network_denied(self):
        s=(m.HERE/'run.sh').read_text(); self.assertIn('PrivateNetwork=yes',s); self.assertIn('SystemCallFilter=~socket socketpair',s); self.assertIn('SystemCallErrorNumber=EPERM',s)
    def test_distinct_full_entrypoints(self):
        s=(m.HERE/'probe.php').read_text()
        for label in ('fatal-hp','fatal-core','fatal-cli','cli-tasks'): self.assertIn(label,s)
    def test_no_source_function_extraction(self):
        s=(m.HERE/'probe.php').read_text(); self.assertNotIn('eval(',s); self.assertNotIn('preg_replace(',s)
if __name__=='__main__': unittest.main()
