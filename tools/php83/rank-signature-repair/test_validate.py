import copy
import json
from pathlib import Path
import unittest
import validate as m

class ContractTests(unittest.TestCase):
    def setUp(self):
        self.report=json.loads((m.observe.ROOT/'doc/php83/evidence/rank-signature-repair/primary-r2.json').read_text())
    def reject(self):
        with self.assertRaises(ValueError):m.validate(self.report)
    def test_actual_four(self):self.assertEqual(m.validate(self.report)['omission_calls'],16)
    def test_duplicate_mode(self):self.report['records'][3]=copy.deepcopy(self.report['records'][2]);self.reject()
    def test_missing_mode(self):self.report['records'].pop();self.reject()
    def test_boolean_exit(self):self.report['records'][0]['exit']=False;self.reject()
    def test_suppressed_diagnostic(self):self.report['records'][2]['stderr']='';self.reject()
    def test_wrong_all_required(self):
        for r in self.report['records']:r['body']['required']=2;r['stdout']=json.dumps(r['body'])
        self.reject()
    def test_hide74_metadata_delta(self):
        self.report['records'][0]['body']['parameters'][1]['default_available']=False;self.reject()
    def test_unexpected_body_access(self):self.report['records'][0]['body']['autoload_requests']=['entryPeer'];self.reject()
    def test_source_drift(self):self.report['source_after']['original.php']='0'*64;self.reject()
    def test_runtime_drift(self):self.report['runtime_after']['exit']=1;self.reject()
    def test_unknown_stderr(self):self.report['records'][3]['stderr']='new warning';self.reject()

if __name__=='__main__':unittest.main()
