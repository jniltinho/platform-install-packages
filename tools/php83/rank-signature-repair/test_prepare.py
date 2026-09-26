import importlib.util
from pathlib import Path
import tempfile
import unittest

s = importlib.util.spec_from_file_location('rank_prepare',Path(__file__).with_name('prepare.py'))
m = importlib.util.module_from_spec(s);s.loader.exec_module(m)
ARCHIVE='/tmp/kaltura-php83-audit/Rigel-18.20.0.zip'

class RepairTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source=m.member(ARCHIVE,m.ORIGINAL_PIN)
        cls.candidate=m.repair(cls.source)
    def test_exact_delta(self):
        self.assertTrue(m.validate(self.source,self.candidate))
        self.assertEqual(len(self.source)-len(self.candidate),7)
    def test_body_unchanged(self):
        self.assertEqual(self.source.split(m.BEFORE)[1],self.candidate.split(m.AFTER)[1])
    def test_prefix_unchanged(self):
        self.assertEqual(self.source.split(m.BEFORE)[0],self.candidate.split(m.AFTER)[0])
    def test_wrong_original(self):
        with self.assertRaises(ValueError):m.repair(self.source+b' ')
    def test_comment_drift(self):
        with self.assertRaises(ValueError):m.validate(self.source,self.candidate+b'// changed')
    def test_argument_order_drift(self):
        with self.assertRaises(ValueError):m.validate(self.source,self.candidate.replace(m.AFTER,b'protected function anonymousRankEntry($entryId, $rank, $entryType)'))
    def test_unpatched_rejected(self):
        with self.assertRaises(ValueError):m.validate(self.source,self.source)
    def test_wrong_archive_pin(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'wrong.zip';p.write_bytes(b'not archive')
            with self.assertRaises(ValueError):m.member(p,m.ORIGINAL_PIN)

if __name__=='__main__':unittest.main()
