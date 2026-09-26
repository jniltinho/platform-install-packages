"""Synthetic-only real GNU-patch tests; never reads original migration archives."""
import importlib.util
from pathlib import Path
import unittest
import zipfile

HERE = Path(__file__).resolve().parent

def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value

b = module('zip_builder_v2', HERE / 'build.py')
legacy = module('zip_builder_v2_legacy_controls', HERE.parent / 'test_experimental_zip.py')
legacy.builder = b

class BuilderV2Tests(legacy.ZipTests):
    def add_source(self, path='infra/helper.php'):
        body = b'<?php class SyntheticHelper {}\n'
        patch = b'--- /dev/null\n+++ b/' + path.encode() + b'\n@@ -0,0 +1 @@\n+' + body
        (self.patches / 'add.patch').write_bytes(patch)
        entry = {'operation': 'add', 'path': path, 'patch': 'add.patch',
                 'sha256': b.sha(patch), 'before_sha256': None, 'after_sha256': b.sha(body)}
        self.manifest['patches'].append(entry)
        self.save_manifest()
        return entry

    def test_added_source_twice_reproducible(self):
        self.add_source()
        original = self.archive.read_bytes()
        a = b.build(self.archive, self.patches, self.root / 'a')
        c = b.build(self.archive, self.patches, self.root / 'b')
        self.assertEqual(a.read_bytes(), c.read_bytes())
        self.assertEqual(original, self.archive.read_bytes())
        with zipfile.ZipFile(a) as z:
            info = z.getinfo('source/infra/helper.php')
            self.assertEqual(info.date_time, b.STAMP)
            self.assertEqual(info.external_attr >> 16, 0o100644)
            self.assertEqual(z.read(info), b'<?php class SyntheticHelper {}\n')
            self.assertEqual(z.read('source/file.php'), b'<?php echo 2;\n')

    def test_add_existing_source_rejected(self):
        self.add_member('source/infra/helper.php', 'existing')
        self.add_source()
        with self.assertRaisesRegex(ValueError, 'collides'):
            b.build(self.archive, self.patches, self.root / 'out')

    def test_add_existing_directory_rejected(self):
        self.add_member('source/infra/helper.php/', '', 0o40755)
        self.add_source()
        with self.assertRaisesRegex(ValueError, 'collides'):
            b.build(self.archive, self.patches, self.root / 'out')

    def test_add_implicit_directory_rejected(self):
        self.add_member('source/infra/helper.php/child', 'existing')
        self.add_source()
        with self.assertRaisesRegex(ValueError, 'collides'):
            b.build(self.archive, self.patches, self.root / 'out')

    def test_add_under_file_rejected(self):
        self.add_member('source/infra', 'existing regular')
        self.add_source()
        with self.assertRaisesRegex(ValueError, 'parent is an upstream file'):
            b.build(self.archive, self.patches, self.root / 'out')

    def test_add_requires_explicit_null(self):
        entry = self.add_source()
        del entry['before_sha256']
        self.save_manifest()
        with self.assertRaisesRegex(ValueError, 'before_sha256 null'):
            b.build(self.archive, self.patches, self.root / 'out')

    def test_replace_cannot_use_null(self):
        self.manifest['patches'][0]['before_sha256'] = None
        self.save_manifest()
        with self.assertRaisesRegex(ValueError, 'Replacement needs'):
            b.build(self.archive, self.patches, self.root / 'out')

    def test_unknown_operation_rejected(self):
        self.manifest['patches'][0]['operation'] = 'delete'
        self.save_manifest()
        with self.assertRaisesRegex(ValueError, 'Unsupported'):
            b.build(self.archive, self.patches, self.root / 'out')

    def test_add_reserved_target_rejected(self):
        self.add_source('.php83-experimental/evil.php')
        with self.assertRaisesRegex(ValueError, 'Reserved patch target'):
            b.build(self.archive, self.patches, self.root / 'out')

    def test_add_after_hash_enforced(self):
        self.add_source()['after_sha256'] = '0' * 64
        self.save_manifest()
        with self.assertRaisesRegex(ValueError, 'Patch output checksum'):
            b.build(self.archive, self.patches, self.root / 'out')

    def test_add_header_enforced(self):
        entry = self.add_source()
        path = self.patches / 'add.patch'
        path.write_bytes(path.read_bytes().replace(b'/dev/null', b'a/missing'))
        entry['sha256'] = b.sha(path.read_bytes())
        self.save_manifest()
        with self.assertRaisesRegex(ValueError, 'exact null/source headers'):
            b.build(self.archive, self.patches, self.root / 'out')

if __name__ == '__main__':
    unittest.main()
