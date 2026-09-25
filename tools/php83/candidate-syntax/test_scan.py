import hashlib
import importlib.util
from pathlib import Path
import tempfile
import unittest
import zipfile

spec = importlib.util.spec_from_file_location('syntax_scan', Path(__file__).with_name('scan.py'))
scan = importlib.util.module_from_spec(spec); spec.loader.exec_module(scan)

class ScanTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name); self.source = self.root/'source'; self.source.mkdir()
        self.archive = self.root/'input.zip'
        self.data = b'<?php echo 1;'
        (self.source/'test.php').write_bytes(self.data)
        self.write_zip([('server-Rigel-18.20.0/test.php', self.data)])
    def write_zip(self, entries):
        with zipfile.ZipFile(self.archive, 'w') as z:
            for name, data in entries: z.writestr(name, data)
        self.pin = scan.sha(self.archive)
    def verify(self): return scan.archive_inventory(self.archive, self.source, self.pin)
    def test_valid(self):
        self.assertEqual(self.verify(), {'test.php': hashlib.sha256(self.data).hexdigest()})
    def test_wrong_hash(self):
        self.pin = '0'*64
        with self.assertRaises(RuntimeError): self.verify()
    def test_source_drift(self):
        (self.source/'test.php').write_bytes(b'changed')
        with self.assertRaises(RuntimeError): self.verify()
    def test_extra_source(self):
        (self.source/'extra.php').write_text('extra')
        with self.assertRaises(RuntimeError): self.verify()
    def test_traversal(self):
        self.write_zip([('server-Rigel-18.20.0/../escape.php', b'bad')])
        with self.assertRaises(RuntimeError): self.verify()
    def test_wrong_root(self):
        self.write_zip([('other/test.php', self.data)])
        with self.assertRaises(RuntimeError): self.verify()
    def test_symlink(self):
        (self.source/'link.php').symlink_to('test.php')
        with self.assertRaises(RuntimeError): self.verify()
    def test_duplicate_entry(self):
        with self.assertWarns(UserWarning):
            self.write_zip([('server-Rigel-18.20.0/test.php', self.data)]*2)
        with self.assertRaises(RuntimeError): self.verify()
    def test_diagnostics_are_not_rejections(self):
        summary = scan.summarize([{'exit': 0, 'diagnostics': 'Deprecated'}, {'exit': 255, 'diagnostics': 'Parse error'}, {'exit': 124, 'diagnostics': 'Timeout'}])
        self.assertEqual(summary, {'files_scanned': 3, 'compiler_rejected': 1, 'compiler_accepted': 1, 'incomplete': 1, 'diagnostic_files': 3, 'accepted_with_diagnostics': 1})
    def test_explicit_syntax_only_flags(self):
        self.assertEqual(scan.FLAGS, ['-n', '-d', 'short_open_tag=1', '-d', 'error_reporting=32767', '-d', 'display_errors=stderr', '-d', 'log_errors=0', '-l'])
    def test_extension_selection(self):
        self.assertEqual(scan.SUFFIXES, {'.php', '.phtml', '.inc', '.php5'})

if __name__ == '__main__': unittest.main()
