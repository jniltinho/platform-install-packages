import copy, json, unittest
import build
class InventoryTests(unittest.TestCase):
    def setUp(self): self.spec=json.loads((build.HERE/'sources.json').read_text())
    def test_deterministic(self): self.assertEqual(build.build(),build.build())
    def test_no_completion(self):
        r=build.build(); self.assertFalse(r['runtime_activation_verified']); self.assertFalse(r['full_entrypoint_inventory_complete']); self.assertEqual(len(r['routes']),13)
    def test_drift(self):
        self.spec['source_pins'][next(iter(self.spec['source_pins']))]='0'*64
        with self.assertRaisesRegex(ValueError,'SOURCE_DRIFT'): build.build(contract=self.spec)
    def test_anchor(self):
        self.spec['routes'][0]['anchors'][0][1]='NOT_A_SOURCE_ANCHOR'
        with self.assertRaisesRegex(ValueError,'ANCHOR_MISSING'): build.build(contract=self.spec)
    def test_candidate(self):
        self.spec['archive_candidate_paths'].append('missing')
        with self.assertRaisesRegex(ValueError,'CANDIDATE_CARDINALITY'): build.build(contract=self.spec)
if __name__=='__main__': unittest.main()
