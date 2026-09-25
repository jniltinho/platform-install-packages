"""Synthetic, offline regressions for the standalone patch inventory auditor."""
import difflib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

SPEC = importlib.util.spec_from_file_location('patch_inventory', Path(__file__).with_name('audit-patch-inventory.py'))
AUDIT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(AUDIT)


class InventoryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.repo = self.root / 'repo'
        self.patches = self.repo / 'patches/php83'
        self.held = self.patches / 'held'
        self.held.mkdir(parents=True)
        self.source = self.root / 'source'
        self.source.mkdir()
        self.manifest = {'patches': []}
        self.write_manifest()

    def write_manifest(self):
        (self.patches / 'manifest.json').write_text(json.dumps(self.manifest))

    def add(self, name='example', scope='held', path='src/example.php', inferred=False,
            files=False, before='old\n', after='new\n'):
        source = self.source / path
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_text(before)
        patch_name = name + '.patch'
        parent = self.held if scope == 'held' else self.patches
        patch = ''.join(difflib.unified_diff(before.splitlines(True), after.splitlines(True),
                                           fromfile='a/' + path, tofile='b/' + path)).encode()
        (parent / patch_name).write_bytes(patch)
        entry = dict(path=path, before_sha256=AUDIT.digest(before.encode()),
                     after_sha256=AUDIT.digest(after.encode()))
        entry['patch_sha256' if inferred or files else 'sha256'] = AUDIT.digest(patch)
        if not inferred:
            entry['patch'] = ((parent / patch_name).relative_to(self.repo).as_posix()
                              if files else patch_name)
        if scope == 'active':
            self.manifest['patches'].append(entry)
            self.write_manifest()
        else:
            metadata = dict(status='held parent status', files=[entry]) if files else entry
            json_name = 'core_compile' if name == 'core_compile.yml' else name
            (parent / (json_name + '.json')).write_text(json.dumps(metadata))
        return entry

    def audit(self):
        return AUDIT.audit(self.repo, self.source)

    def test_empty_inventory_fails(self):
        self.assertEqual(self.audit()['result'], 'FAIL')

    def test_valid_isolated_application_and_original_unchanged(self):
        self.add(scope='active')
        report = self.audit()
        self.assertEqual(report['result'], 'PASS', report)
        self.assertEqual((self.source / 'src/example.php').read_text(), 'old\n')
        self.assertFalse(report['promotion'])
        self.assertFalse(report['stacking'])

    def test_metadata_formats_and_inferred_names(self):
        self.add(scope='active')
        for name in ('KalturaPDO-query', 'dateUtils-ternary', 'doc-comment-property', 'core_compile.yml'):
            self.add(name, inferred=True, path='src/' + name)
        self.add('symfony', files=True, path='src/symfony.php')
        report = self.audit()
        self.assertEqual(report['result'], 'PASS', report)
        self.assertEqual(report['counts'], {'active': 1, 'held': 5})
        self.assertEqual(report['entries'][-1]['status'], 'held parent status')
        unknown = [e for e in report['entries'] if e['status'] == 'unknown']
        self.assertEqual(len(unknown), 5)

    def test_alternatives_are_not_stacked(self):
        self.add('one', after='first\n')
        self.add('two', after='second\n')
        report = self.audit()
        self.assertEqual(report['result'], 'PASS', report)
        self.assertEqual(len(report['alternative_groups']), 1)
        self.assertFalse(report['alternative_groups'][0]['stacked'])

    def test_missing_patch(self):
        self.add()
        (self.held / 'example.patch').unlink()
        self.assertEqual(self.audit()['result'], 'FAIL')

    def test_uncovered_patch(self):
        (self.held / 'stray.patch').write_text('')
        self.assertIn('metadata count', ' '.join(self.audit()['errors']))

    def test_duplicate_metadata(self):
        self.add()
        (self.held / 'duplicate.json').write_bytes((self.held / 'example.json').read_bytes())
        self.assertIn('metadata count', ' '.join(self.audit()['errors']))

    def test_drift_source_patch_and_after(self):
        for kind in ('source', 'patch', 'after'):
            with self.subTest(kind=kind):
                self.add()
                if kind == 'source':
                    (self.source / 'src/example.php').write_text('changed\n')
                elif kind == 'patch':
                    (self.held / 'example.patch').write_text('changed\n')
                else:
                    file = self.held / 'example.json'
                    data = json.loads(file.read_text())
                    data['after_sha256'] = '0' * 64
                    file.write_text(json.dumps(data))
                self.assertIn('SHA256 drift', ' '.join(self.audit()['errors']))

    def test_path_traversal(self):
        for field in ('path', 'patch'):
            with self.subTest(field=field):
                self.add()
                file = self.held / 'example.json'
                data = json.loads(file.read_text())
                data[field] = '../outside'
                file.write_text(json.dumps(data))
                self.assertEqual(self.audit()['result'], 'FAIL')

    def test_source_symlink_escape(self):
        self.add()
        outside = self.root / 'outside'
        outside.write_text('old\n')
        target = self.source / 'src/example.php'
        target.unlink()
        target.symlink_to(outside)
        self.assertIn('symlink escape', ' '.join(self.audit()['errors']))

    def test_patch_header_escape(self):
        with self.assertRaisesRegex(ValueError, 'headers'):
            AUDIT.apply_isolated(b'old\n', b'--- a/../x\n+++ b/../x\n@@ -1 +1 @@\n-old\n+new\n', 'safe')

    def test_offset_and_reverse_rejected(self):
        patch = b'--- a/x\n+++ b/x\n@@ -1 +1 @@\n-old\n+new\n'
        with self.assertRaisesRegex(ValueError, 'non-exact'):
            AUDIT.apply_isolated(b'extra\nold\n', patch, 'x')
        with self.assertRaisesRegex(ValueError, 'non-exact'):
            AUDIT.apply_isolated(b'new\n', patch, 'x')


if __name__ == '__main__':
    unittest.main()
