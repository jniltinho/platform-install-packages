import base64,copy,hashlib,json,unittest
import compare
class ComparatorTests(unittest.TestCase):
    def setUp(self):
        self.ids={'files':{'original.php':'o','declaration.php':'d','criteriaFilter.php':'f'}}
        self.records=[]
        for mode in compare.MODES:
            variant=mode[:-2];v=mode[-2:]
            body={'schema':1,'variant':variant,'php':{'74':'7.4.33','83':'8.3.6'}[v],'rows':{c:{'marker':None} for c in compare.CASES},'source_sha256':{'criteria':self.ids['files'][variant+'.php'],'filter':'f'},'events':[]}
            rep={'serialized_base64':'YQ==','serialized_bytes':1,'serialized_sha256':hashlib.sha256(b'a').hexdigest(),'roundtrip_bytes_identical':True,'property_exists':False}
            body['rows']['fresh']['representation']=copy.deepcopy(rep)
            body['rows']['once_twice']=[None,None,copy.deepcopy(rep)]
            body['rows']['clone']=[None,None,copy.deepcopy(rep)]
            body['rows']['serialize_attached']=[None,copy.deepcopy(rep)]
            err=''
            if mode=='original83':
                err='Creation of dynamic property Criteria::$creteria_filter_attached is deprecated'
                body['events']=[{'phase':'once_twice','severity':8192,'file':'criteriaFilter.php','line':51,'message':err}]
            self.records.append({'mode':mode,'exit':0,'stderr':err,'body':body})
    def check(self):
        for r in self.records:r['stdout']=json.dumps(r['body'])
        return compare.validate(self.records,self.ids)
    def test_stdout_body_binding(self):
        self.check(); self.records[0]['stdout']='{}'
        with self.assertRaises(ValueError):compare.validate(self.records,self.ids)
    def test_unrelated_warning_regression(self):
        self.records[3]['body']['events']=[{'phase':'fresh','severity':2,'file':'probe.php','line':1,'message':'new warning'}]
        with self.assertRaises(ValueError):self.check()
    def test_unrelated_exact_source_line_mapping(self):
        for i,name,line in [(2,'original.php',99),(3,'declaration.php',100)]:
            self.records[i]['body']['events'].append({'phase':'load','severity':8192,'file':name,'line':line,'message':'iterator return warning'})
        self.assertTrue(self.check()['unrelated_diagnostics']['83']['equal_after_exact_added_line_mapping'])
    def test_positive(self):self.assertFalse(self.check()['patch_selected'])
    def test_duplicate_mode(self):
        self.records[3]=self.records[1]
        with self.assertRaises(ValueError):self.check()
    def test_drift(self):
        self.records[3]['body']['source_sha256']['criteria']='wrong'
        with self.assertRaises(ValueError):self.check()
    def test_missing_control(self):
        self.records[2]['body']['events']=[]
        with self.assertRaises(ValueError):self.check()
    def test_missing_native_stderr(self):
        self.records[2]['stderr']=''
        with self.assertRaises(ValueError):self.check()
    def test_behavior_change(self):
        self.records[3]['body']['rows']['clear']['marker']=True
        with self.assertRaises(ValueError):self.check()
    def test_case_missing(self):
        del self.records[3]['body']['rows']['fresh']
        with self.assertRaises(ValueError):self.check()
    def test_bool_exit(self):
        self.records[0]['exit']=False
        with self.assertRaises(ValueError):self.check()
    def test_representation_delta_not_parity(self):
        for i,r in enumerate(self.records):
            data=b'a' if i%2==0 else b'ab'
            r['body']['rows']['fresh']['representation']={'serialized_base64':base64.b64encode(data).decode(),'serialized_bytes':len(data),'serialized_sha256':hashlib.sha256(data).hexdigest(),'roundtrip_bytes_identical':True,'property_exists':i%2==1}
        result=self.check();self.assertFalse(result['exact_representation_parity']);self.assertEqual(len(result['representation_changes']),2)
    def test_serialization_corruption(self):
        self.records[0]['body']['rows']['fresh']['representation']={'serialized_base64':'YQ==','serialized_bytes':2,'serialized_sha256':'wrong','roundtrip_bytes_identical':True}
        with self.assertRaises(ValueError):self.check()
