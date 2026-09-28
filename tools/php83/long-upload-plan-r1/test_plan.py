import unittest
from dataclasses import FrozenInstanceError, replace
import plan as p


class PlanTests(unittest.TestCase):
    def setUp(self):
        self.parts = p.plan(p.SIZE, p.SHA256)

    def test_exact_contiguous_coverage(self):
        self.assertEqual(len(self.parts), 112)
        self.assertEqual(sum(x.length for x in self.parts), p.SIZE)
        offset = 0
        for x in self.parts:
            self.assertEqual(x.offset, offset)
            self.assertTrue(0 < x.length <= 1048576)
            offset += x.length
        self.assertEqual(offset, p.SIZE)

    def test_first_and_last_semantics(self):
        self.assertEqual(self.parts[0], p.Part(1, 0, p.CHUNK, False, False, -1))
        self.assertEqual(sum(x.final_chunk for x in self.parts), 1)
        self.assertTrue(self.parts[-1].final_chunk)
        for x in self.parts[1:]:
            self.assertTrue(x.resume)
            self.assertEqual(x.resume_at, x.offset)

    def test_no_identity_coercion(self):
        for value in (True, str(p.SIZE), float(p.SIZE), p.SIZE - 1, p.SIZE + 1):
            with self.assertRaises(ValueError):
                p.plan(value, p.SHA256)
        for value in (None, p.SHA256.upper(), '0' * 64):
            with self.assertRaises(ValueError):
                p.plan(p.SIZE, value)

    def test_only_next_part(self):
        for n in range(len(self.parts)):
            self.assertEqual(p.require_next(self.parts, n, n + 1), self.parts[n])

    def test_replay_skip_and_completion_rejected(self):
        for ack, number in ((0, 2), (1, 1), (2, 2), (112, 113), (-1, 0), (True, 2), (0, True)):
            with self.assertRaises(ValueError):
                p.require_next(self.parts, ack, number)

    def test_numeric_aliases_rejected(self):
        for field, value in (('number', True), ('offset', False),
                             ('length', float(p.CHUNK)), ('resume', 0),
                             ('final_chunk', 0), ('resume_at', -1.0)):
            changed = (replace(self.parts[0], **{field: value}),) + self.parts[1:]
            with self.subTest(field=field), self.assertRaises(ValueError):
                p.require_next(changed, 0, 1)

    def test_mutated_plan_rejected(self):
        changed = (replace(self.parts[0], final_chunk=True),) + self.parts[1:]
        with self.assertRaises(ValueError):
            p.require_next(changed, 0, 1)
        with self.assertRaises(FrozenInstanceError):
            self.parts[0].length = 1


if __name__ == '__main__':
    unittest.main()
