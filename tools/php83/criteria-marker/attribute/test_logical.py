import base64,copy,hashlib,importlib.util,json
from pathlib import Path
import unittest
spec=importlib.util.spec_from_file_location('logical_compare',Path(__file__).with_name('logical-compare.py'));c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
class LogicalTests(unittest.TestCase):
    def setUp(self):
        self.payload={str(i):'YQ==' for i in range(7)};self.records=[];h=hashlib.sha256(b'a').hexdigest()
        for mode in c.MODES:
            b={'schema':1,'php':('7.4.33' if mode.endswith('74') else '8.3.6'),'variant':mode[:-2],'rows':{k:{'input_sha256':h,'reserialized_sha256':h,'logical':{'type':'integer','value':1}} for k in self.payload}}
            self.records.append({'mode':mode,'exit':0,'body':b,'stdout':json.dumps(b)})
    def check(self):
        for r in self.records:r['stdout']=json.dumps(r['body'])
        return c.validate(self.records,self.payload)
    def test_equal(self):self.assertFalse(self.check()['attribute_selected'])
    def test_value_changed(self):
        self.records[2]['body']['rows']['0']['logical']['value']=2
        with self.assertRaises(ValueError):self.check()
    def test_bool_int_not_equal(self):
        self.records[2]['body']['rows']['0']['logical']['value']=True
        with self.assertRaises(ValueError):self.check()
    def test_wrong_type(self):
        self.records[2]['body']['rows']['0']['logical']['type']='string'
        with self.assertRaises(ValueError):self.check()
    def test_payload_drift(self):
        self.payload['0']='Yg=='
        with self.assertRaises(ValueError):self.check()
    def test_missing_mode(self):
        self.records.pop()
        with self.assertRaises(ValueError):self.check()
    def test_raw_delta_not_waived(self):
        self.records[2]['body']['rows']['0']['reserialized_sha256']='different'
        result=self.check();self.assertFalse(result['representation']['attribute83']['0']['raw_bytes_equal']);self.assertIn('GATE_STILL_FAILED',result['status'])
