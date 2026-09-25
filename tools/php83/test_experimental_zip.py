import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

spec = importlib.util.spec_from_file_location(
    'experimental_zip', Path(__file__).with_name('build-experimental-zip.py'))
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


class ZipTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.archive = self.root / 'original.zip'
        with zipfile.ZipFile(self.archive, 'w') as archive:
            archive.writestr('source/file.php', '<?php echo 1;\n')
        self.patches = self.root / 'patches'
        self.patches.mkdir()
        patch = b'--- a/file.php\n+++ b/file.php\n@@ -1 +1 @@\n-<?php echo 1;\n+<?php echo 2;\n'
        (self.patches / 'one.patch').write_bytes(patch)
        self.manifest = {'upstream_sha256': builder.sha(self.archive.read_bytes()),
                         'upstream_root': 'source', 'revision': 'test', 'patches': [{
                             'path': 'file.php', 'patch': 'one.patch', 'sha256': builder.sha(patch),
                             'before_sha256': builder.sha(b'<?php echo 1;\n'),
                             'after_sha256': builder.sha(b'<?php echo 2;\n')}]}
        self.save_manifest()

    def save_manifest(self):
        (self.patches / 'manifest.json').write_text(json.dumps(self.manifest))

    def test_reproducible_and_original_unchanged(self):
        before = self.archive.read_bytes()
        a = builder.build(self.archive, self.patches, self.root / 'a')
        b = builder.build(self.archive, self.patches, self.root / 'b')
        self.assertEqual(a.read_bytes(), b.read_bytes())
        self.assertEqual(self.archive.read_bytes(), before)
        with zipfile.ZipFile(a) as output:
            self.assertEqual(output.read('source/file.php'), b'<?php echo 2;\n')
            self.assertIn('source/.php83-experimental/manifest.json', output.namelist())

    def test_source_drift_rejected(self):
        self.archive.write_bytes(self.archive.read_bytes() + b'drift')
        with self.assertRaisesRegex(ValueError, 'Upstream checksum'):
            builder.build(self.archive, self.patches, self.root / 'out')

    def test_patch_drift_rejected(self):
        (self.patches / 'one.patch').write_text('wrong')
        with self.assertRaisesRegex(ValueError, 'Patch checksum'):
            builder.build(self.archive, self.patches, self.root / 'out')

    def test_output_hash_mismatch_rejected(self):
        self.manifest['patches'][0]['after_sha256'] = 'wrong'
        self.save_manifest()
        with self.assertRaisesRegex(ValueError, 'Patch output checksum'):
            builder.build(self.archive, self.patches, self.root / 'out')

    def test_existing_output_preserved(self):
        output = self.root / 'out'
        output.mkdir()
        (output / 'keep').write_text('keep')
        with self.assertRaises(FileExistsError):
            builder.build(self.archive, self.patches, output)
        self.assertEqual((output / 'keep').read_text(), 'keep')

    def test_unsafe_paths(self):
        for path in ['../escape', '/absolute', 'root/../escape', 'root//file', 'root//', 'root\\file', 'root/\nfile']:
            with self.subTest(path=path), self.assertRaises(ValueError):
                builder.safe_path(path)

    def test_archive_traversal_rejected_even_with_matching_hash(self):
        with zipfile.ZipFile(self.archive, 'a') as archive:
            archive.writestr('source/../escape', 'bad')
        self.manifest['upstream_sha256'] = builder.sha(self.archive.read_bytes())
        self.save_manifest()
        with self.assertRaisesRegex(ValueError, 'Unsafe archive path'):
            builder.build(self.archive, self.patches, self.root / 'out')

    def add_member(self, name, data, mode=0o100644):
        with zipfile.ZipFile(self.archive, 'a') as archive:
            item = zipfile.ZipInfo(name)
            item.external_attr = mode << 16
            item.comment = b'entry provenance'
            archive.writestr(item, data)
            archive.comment = b'upstream revision'
        self.manifest['upstream_sha256'] = builder.sha(self.archive.read_bytes())
        self.save_manifest()

    def test_rejects_symlink(self):
        self.add_member('source/link', 'file.php', 0o120777)
        with self.assertRaisesRegex(ValueError, 'symlink'):
            builder.build(self.archive, self.patches, self.root / 'out')

    def test_rejects_reserved_source_metadata(self):
        self.add_member('source/.php83-experimental/manifest.json', '{}')
        with self.assertRaisesRegex(ValueError, 'Reserved'):
            builder.build(self.archive, self.patches, self.root / 'out')

    def test_patch_cannot_collide_with_metadata(self):
        entry = self.manifest['patches'][0]
        (self.patches / 'README.txt').write_bytes((self.patches / 'one.patch').read_bytes())
        entry['patch'] = 'README.txt'
        self.save_manifest()
        with self.assertRaises(ValueError):
            builder.build(self.archive, self.patches, self.root / 'out')

    def test_preserves_comments_and_executable_bit(self):
        self.add_member('source/bin/', '', 0o40775)
        self.add_member('source/bin/run.sh', '#!/bin/sh\n', 0o100775)
        result = builder.build(self.archive, self.patches, self.root / 'out')
        with zipfile.ZipFile(result) as archive:
            self.assertEqual(archive.comment, b'upstream revision')
            self.assertEqual(archive.getinfo('source/bin/run.sh').comment, b'entry provenance')
            self.assertEqual(archive.getinfo('source/bin/run.sh').external_attr >> 16, 0o100755)
            self.assertEqual(archive.getinfo('source/bin/').external_attr & 0x10, 0x10)

    def test_offset_rejected(self):
        patch = (self.patches / 'one.patch').read_bytes().replace(b'@@ -1 +1 @@', b'@@ -2 +2 @@')
        (self.patches / 'one.patch').write_bytes(patch)
        self.manifest['patches'][0]['sha256'] = builder.sha(patch)
        self.save_manifest()
        with self.assertRaisesRegex(ValueError, 'exactly'):
            builder.build(self.archive, self.patches, self.root / 'out')

    def test_later_patch_cannot_mutate_earlier_verified_output(self):
        self.add_member('source/other.php', '<?php echo 1;\n')
        patch = (b'--- a/other.php\n+++ b/other.php\n@@ -1 +1 @@\n'
                 b'-<?php echo 1;\n+<?php echo 2;\n'
                 b'--- a/file.php\n+++ b/file.php\n@@ -1 +1 @@\n'
                 b'-<?php echo 2;\n+<?php echo 3;\n')
        (self.patches / 'two.patch').write_bytes(patch)
        entry = dict(self.manifest['patches'][0], path='other.php', patch='two.patch', sha256=builder.sha(patch))
        self.manifest['patches'].append(entry)
        self.save_manifest()
        with self.assertRaisesRegex(ValueError, 'Patch output checksum'):
            builder.build(self.archive, self.patches, self.root / 'out')
