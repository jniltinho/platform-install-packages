import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).parent))
import observe as m

class ObservationPreparation(unittest.TestCase):
    def test_exact_stage_files(self):
        self.assertEqual(set(m.files()),{'original.php','candidate.php','KalturaBaseService.php','probe.php','run.sh'})
    def test_sources_validated(self):
        data=m.files();self.assertTrue(m.prepare.validate(data['original.php'],data['candidate.php']))
    def test_stage_name_bounded(self):
        self.assertRegex(m.STAGE,r'^/home/vagrant/php-rank-signature\.[a-f0-9]{32}$')
    def test_atomic_json_and_cleanup(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'result.json';m.atomic(p,{'phase':1});m.atomic(p,{'phase':2})
            self.assertEqual(json.loads(p.read_text()),{'phase':2});self.assertEqual(list(Path(tmp).iterdir()),[p])
    def test_atomic_failure_cleanup(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'result.json'
            with patch.object(m.os,'replace',side_effect=OSError('test')):
                with self.assertRaises(OSError):m.atomic(p,{'phase':1})
            self.assertEqual(list(Path(tmp).iterdir()),[])
    def test_existing_report_refused_before_ssh(self):
        with tempfile.TemporaryDirectory() as tmp,patch.object(m,'remote') as remote:
            p=Path(tmp)/'result.json';p.write_text('preserve')
            with self.assertRaises(FileExistsError):m.observe(p)
            remote.assert_not_called();self.assertEqual(p.read_text(),'preserve')

if __name__=='__main__':unittest.main()
