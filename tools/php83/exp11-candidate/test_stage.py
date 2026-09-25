"""Synthetic 59+4 selection/replay tests; no PHP, VM, original-tree writes or ZIP build."""
import copy
import difflib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile

SPEC = importlib.util.spec_from_file_location('exp11_stage', Path(__file__).with_name('stage.py'))
stage = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(stage)


class SelectionTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.repo = Path(temporary.name)
        self.archive = self.repo / 'original.zip'
        self.manifest_path = self.repo / 'manifest.json'
        self.paths = [f'src/file{i:02}.php' for i in range(59)] + stage.TARGETS
        self.entries = []
        with zipfile.ZipFile(self.archive, 'w') as archive:
            for index, path in enumerate(self.paths):
                original = f'<?php\n/* before {index} */\n'.encode()
                changed = original.replace(b'before', b'after')
                archive.writestr(stage.ROOT + '/' + path, original)
                if index == 59:
                    source_patch = 'patches/php83/held/base-object-ternary/base-object-ternary.patch'
                elif index in (60, 61):
                    source_patch = 'meta/patch' + str(index) + '.patch'
                else:
                    source_patch = f'patches/patch{index:02}.patch'
                data = ''.join(difflib.unified_diff(original.decode().splitlines(True), changed.decode().splitlines(True),
                                                  fromfile='a/' + path, tofile='b/' + path)).encode()
                target = self.repo / source_patch
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(data)
                self.entries.append({'patch': target.name, 'sha256': stage.digest(data), 'path': path,
                                     'before_sha256': stage.digest(original), 'after_sha256': stage.digest(changed),
                                     'source_patch': source_patch})
        self.docs = {'prior': {'revision': 'exp10', 'target_php': '8.3', 'upstream_root': stage.ROOT,
                              'upstream_sha256': stage.digest(self.archive.read_bytes()), 'patches': self.entries[:59]},
                     'ternary': {'files': [{k: self.entries[59][k] for k in ('path', 'before_sha256', 'after_sha256')}],
                                 'patch_sha256': self.entries[59]['sha256']},
                     'purifier': copy.deepcopy(self.entries[60]), 'cli': copy.deepcopy(self.entries[61]),
                     'core': {'files': [{'path': self.entries[62]['path'], 'patch': self.entries[62]['source_patch'],
                                        'patch_sha256': self.entries[62]['sha256'],
                                        'before_sha256': self.entries[62]['before_sha256'],
                                        'after_sha256': self.entries[62]['after_sha256']}]}}
        self.inputs = {}
        for name, value in [('REPO', self.repo), ('MANIFEST', self.manifest_path),
                            ('ORIGINAL', stage.digest(self.archive.read_bytes())), ('INPUTS', self.inputs)]:
            replacement = patch.object(stage, name, value)
            replacement.start(); self.addCleanup(replacement.stop)
        self.write_documents()
        self.manifest = {'status': 'PREPARED_NOT_SELECTED', 'revision': 'exp11', 'target_php': '8.3',
                         'upstream_root': stage.ROOT, 'upstream_sha256': stage.ORIGINAL,
                         'selection_provenance': stage.provenance(), 'patches': copy.deepcopy(self.entries)}
        self.write_manifest()

    def write_documents(self):
        for role, document in self.docs.items():
            name = 'meta/' + role + '.json'
            data = json.dumps(document).encode()
            path = self.repo / name; path.parent.mkdir(exist_ok=True); path.write_bytes(data)
            self.inputs[role] = (name, stage.digest(data))

    def write_manifest(self):
        self.manifest_path.write_text(json.dumps(self.manifest))

    def synchronize_manifest(self):
        self.write_documents()
        self.manifest['selection_provenance'] = stage.provenance()
        # Test fixtures can update their pinned documents; the real tool uses fixed anchors.
        self.manifest['patches'] = stage.expected_selection(self.docs)
        self.write_manifest()

    def validate(self):
        return stage.validate(self.archive)

    def test_exact_59_plus_4_and_private_replay(self):
        payload, patches, report = self.validate()
        self.assertEqual(json.loads(payload)['patches'][:59], self.docs['prior']['patches'])
        self.assertEqual(len(patches), 63)
        self.assertEqual(len(report['exact_private_copy_replays']), 63)
        self.assertFalse(report['zip_built']); self.assertFalse(report['selection_approved'])
        self.assertEqual(report['status'], 'PREPARED_NOT_SELECTED')

    def test_prior_order_drift(self):
        rows = self.manifest['patches']; rows[0], rows[1] = rows[1], rows[0]
        self.write_manifest()
        with self.assertRaisesRegex(ValueError, 'ordered 59\\+4'): self.validate()

    def test_addition_order_drift(self):
        rows = self.manifest['patches']; rows[59], rows[60] = rows[60], rows[59]
        self.write_manifest()
        with self.assertRaisesRegex(ValueError, 'ordered 59\\+4'): self.validate()

    def test_omission(self):
        self.manifest['patches'].pop(); self.write_manifest()
        with self.assertRaisesRegex(ValueError, 'ordered 59\\+4'): self.validate()

    def test_prior_field_changed(self):
        self.manifest['patches'][0]['extra'] = 'invented'; self.write_manifest()
        with self.assertRaisesRegex(ValueError, 'ordered 59\\+4'): self.validate()

    def test_target_collision(self):
        self.docs['prior']['patches'][0]['path'] = stage.TARGETS[0]
        with self.assertRaisesRegex(ValueError, 'collision'): self.synchronize_manifest()

    def test_leaf_collision(self):
        self.docs['prior']['patches'][0]['patch'] = self.entries[59]['patch']
        with self.assertRaisesRegex(ValueError, 'collision'): self.synchronize_manifest()

    def test_patch_drift(self):
        (self.repo / self.entries[0]['source_patch']).write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError, 'Patch byte drift'): self.validate()

    def test_original_target_hash_drift(self):
        self.docs['prior']['patches'][0]['before_sha256'] = '0' * 64; self.synchronize_manifest()
        with self.assertRaisesRegex(ValueError, 'Original target identity'): self.validate()

    def test_wrong_after_hash(self):
        self.docs['prior']['patches'][0]['after_sha256'] = '0' * 64; self.synchronize_manifest()
        with self.assertRaisesRegex(ValueError, 'Resulting source hash'): self.validate()

    def test_metadata_drift(self):
        (self.repo / self.inputs['core'][0]).write_text('{}')
        with self.assertRaisesRegex(ValueError, 'Pinned metadata drift'): self.validate()

    def test_provenance_declaration_drift(self):
        self.manifest['selection_provenance'][0]['sha256'] = '0' * 64; self.write_manifest()
        with self.assertRaisesRegex(ValueError, 'Provenance declaration'): self.validate()

    def test_archive_drift(self):
        self.archive.write_bytes(b'wrong')
        with self.assertRaisesRegex(ValueError, 'Original archive identity'): self.validate()

    def test_status_cannot_claim_selected(self):
        self.manifest['status'] = 'SELECTED'; self.write_manifest()
        with self.assertRaisesRegex(ValueError, 'identity/status'): self.validate()

    def test_path_traversal(self):
        self.docs['prior']['patches'][0]['source_patch'] = '../outside.patch'
        with self.assertRaisesRegex(ValueError, 'Unsafe input'): self.synchronize_manifest()

    def test_symlink_patch(self):
        path = self.repo / self.entries[0]['source_patch']; target = self.repo / 'copy.patch'
        target.write_bytes(path.read_bytes()); path.unlink(); path.symlink_to(target)
        with self.assertRaisesRegex(ValueError, 'Unsafe repository'): self.validate()

    def test_patch_headers_not_metadata_only(self):
        path = self.repo / self.entries[0]['source_patch']
        path.write_bytes(path.read_bytes().replace(b'+++ b/src/file00.php', b'+++ b/escape.php'))
        self.docs['prior']['patches'][0]['sha256'] = stage.digest(path.read_bytes()); self.synchronize_manifest()
        with self.assertRaisesRegex(ValueError, 'target headers'): self.validate()

    def test_offset_rejected(self):
        path = self.repo / self.entries[0]['source_patch']
        data = b'--- a/src/file00.php\n+++ b/src/file00.php\n@@ -5 +5 @@\n-/* before 0 */\n+/* after 0 */\n'
        path.write_bytes(data); self.docs['prior']['patches'][0]['sha256'] = stage.digest(data); self.synchronize_manifest()
        with self.assertRaisesRegex(ValueError, 'apply exactly'): self.validate()

    def test_missing_sfcore_record(self):
        self.docs['core']['files'] = []
        with self.assertRaisesRegex(ValueError, 'sfCore metadata'): self.synchronize_manifest()

    def test_duplicate_sfcore_record(self):
        self.docs['core']['files'] *= 2
        with self.assertRaisesRegex(ValueError, 'sfCore metadata'): self.synchronize_manifest()

    def test_unselected_ternary_helper_changed(self):
        self.docs['ternary']['files'].append({'path': 'helper.php', 'before_sha256': '1' * 64, 'after_sha256': '2' * 64})
        with self.assertRaisesRegex(ValueError, 'ternary changed set'): self.synchronize_manifest()

    def test_wrong_autoload_target(self):
        self.docs['cli']['path'] = 'other.php'
        with self.assertRaisesRegex(ValueError, 'autoload target'): self.synchronize_manifest()

    def test_malformed_hash(self):
        self.docs['prior']['patches'][0]['after_sha256'] = 'unknown'
        with self.assertRaisesRegex(ValueError, 'SHA256'): self.synchronize_manifest()


if __name__ == '__main__':
    unittest.main()
