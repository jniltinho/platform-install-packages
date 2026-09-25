"""Offline ledger tests. No SSH, network, PHP, package installation or source writes."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('ledger_builder', HERE / 'build.py')
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)
REPO = HERE.parents[2]

class LedgerTests(unittest.TestCase):
    def archive(self, names):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        path = Path(temporary.name) / 'source.zip'
        with zipfile.ZipFile(path, 'w') as archive:
            for name in names:
                archive.writestr(name, b'synthetic bytes')
        return path, builder.digest(path.read_bytes())

    def test_archive_content_identity(self):
        path, sha = self.archive([builder.ROOT + 'vendor/example.php'])
        self.assertEqual(builder.archive_hashes(path, sha), {'vendor/example.php': builder.digest(b'synthetic bytes')})

    def test_archive_hash_drift_rejected(self):
        path, _ = self.archive([builder.ROOT + 'x'])
        with self.assertRaisesRegex(ValueError, 'identity mismatch'):
            builder.archive_hashes(path, '0' * 64)

    def test_archive_traversal_rejected(self):
        path, sha = self.archive([builder.ROOT + '../x'])
        with self.assertRaisesRegex(ValueError, 'Unexpected archive path'):
            builder.archive_hashes(path, sha)

    def test_wrong_archive_root_rejected(self):
        path, sha = self.archive(['other/x'])
        with self.assertRaisesRegex(ValueError, 'Unexpected archive path'):
            builder.archive_hashes(path, sha)

    def test_duplicate_archive_path_rejected(self):
        path, sha = self.archive([builder.ROOT + 'x', builder.ROOT + 'x'])
        with self.assertRaisesRegex(ValueError, 'Duplicate archive path'):
            builder.archive_hashes(path, sha)

    def test_packaged_extra_not_guessed_as_upstream(self):
        self.assertIsNone(builder.source_path('opt/kaltura/apps/html5/x.php', 'packaged'))
        self.assertEqual(builder.source_path('opt/kaltura/app/vendor/x.php', 'packaged'), 'vendor/x.php')

    def test_unknown_identity_explicit(self):
        self.assertEqual(builder.identity('packaged:x', None), 'unresolved:packaged:x')
        self.assertNotEqual(builder.identity('raw:x', 'a' * 64), builder.identity('raw:x', 'b' * 64))

    def test_evidence_references_and_counts(self):
        evidence = REPO / 'doc/php83/evidence'
        ledger = json.loads((evidence / 'inventory-ledger/ledger.json').read_text())
        for name, metadata in ledger['inputs'].items():
            self.assertEqual(builder.digest((evidence / name).read_bytes()), metadata['sha256'])
        self.assertEqual(len(ledger['findings']), 4986)
        self.assertEqual(ledger['summary']['static_findings'], 4711)
        self.assertEqual(ledger['summary']['syntax_findings'], 275)
        self.assertEqual(len({r['id'] for r in ledger['findings']}), 4986)
        self.assertTrue(all(r['file_key'] in ledger['files'] for r in ledger['findings']))
        self.assertTrue(all(r['matching_upstream_file_key'] in ledger['files'] for r in ledger['runtime_diagnostics']))
        self.assertFalse(ledger['t0_04_complete'])
        self.assertEqual(ledger['summary']['semantic_findings_resolved_by_this_join'], 0)

if __name__ == '__main__':
    unittest.main()
