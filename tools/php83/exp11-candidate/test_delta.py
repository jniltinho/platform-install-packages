import copy
import io
import json
import unittest
import zipfile
import delta
import selected

class DeltaTests(unittest.TestCase):
    def setUp(self):
        self.current = selected.make_selected(selected.stage.MANIFEST.read_bytes())
        self.prior = {'patches': copy.deepcopy(self.current['patches'][:59])}
        self.old = {}; self.new = {}
        self.meta = self.current['upstream_root'] + '/.php83-experimental/'
        for i, row in enumerate(self.current['patches']):
            before, after, patch = b'before', b'after', b'patch'
            row.update(before_sha256=delta.stage.digest(before), after_sha256=delta.stage.digest(after), sha256=delta.stage.digest(patch))
            path = self.current['upstream_root'] + '/' + row['path']
            self.old[path] = after if i < 59 else before
            self.new[path] = after
            self.new[self.meta + row['patch']] = patch
            if i < 59: self.old[self.meta + row['patch']] = patch
        self.prior['patches'] = copy.deepcopy(self.current['patches'][:59])
        self.old[self.meta+'manifest.json'] = b'{}'
        self.new[self.meta+'manifest.json'] = json.dumps(self.current).encode()
        self.old['unrelated'] = self.new['unrelated'] = b'unchanged'
    def zip(self, items):
        output = io.BytesIO()
        with zipfile.ZipFile(output, 'w') as z:
            for k,v in items.items(): z.writestr(k,v)
        return output.getvalue()
    def check(self):
        return delta.compare(self.zip(self.old), self.zip(self.new), self.prior, self.current)
    def test_exact_delta(self): self.assertEqual(self.check()['prior_targets_preserved'],59)
    def test_extra_change(self):
        self.new['unrelated'] = b'drift'
        with self.assertRaises(ValueError): self.check()
    def test_extra_member(self):
        self.new['unexpected'] = b'x'
        with self.assertRaises(ValueError): self.check()
    def test_missing_member(self):
        del self.new['unrelated']
        with self.assertRaises(ValueError): self.check()
    def test_prior_target_drift(self):
        p = self.current['upstream_root'] + '/' + self.current['patches'][0]['path']
        self.old[p] = self.new[p] = b'tampered-both'
        with self.assertRaises(ValueError): self.check()
    def test_new_target_wrong_hash(self):
        p = self.current['upstream_root'] + '/' + self.current['patches'][-1]['path']
        self.new[p] = b'wrong'
        with self.assertRaises(ValueError): self.check()
    def test_new_patch_wrong_hash(self):
        self.new[self.meta+self.current['patches'][-1]['patch']] = b'wrong'
        with self.assertRaises(ValueError): self.check()
    def test_embedded_metadata_drift(self):
        self.new[self.meta+'manifest.json'] = b'{}'
        with self.assertRaises(ValueError): self.check()
