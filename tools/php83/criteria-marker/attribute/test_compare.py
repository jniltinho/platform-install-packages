import base64,copy,hashlib,json,unittest
import compare
class CompareTests(unittest.TestCase):
    def setUp(self):
        self.ids={'files':{'original.php':'o','attribute.php':'a','criteriaFilter.php':'f'}}
        rep={'serialized_base64':'YQ==','serialized_bytes':1,'serialized_sha256':hashlib.sha256(b'a').hexdigest(),'roundtrip_bytes_identical':True}
        rows={c:None for c in compare.CASES}
        for c in ['fresh','mycriteria_hint','mycriteria_marker','kalturacriteria_marker']:rows[c]={'representation':copy.deepcopy(rep)}
        rows['once_twice']=[None,None,copy.deepcopy(rep)];rows['clone']=[None,None,copy.deepcopy(rep)];rows['serialize_attached']=[None,copy.deepcopy(rep)]
        self.payload=compare.legacy(rows);self.records=[]
        self.ids74=copy.deepcopy(self.ids);self.ids83=copy.deepcopy(self.ids)
        for ids,payload in [(self.ids74,{}),(self.ids83,self.payload)]:ids['files']['legacy.json']=hashlib.sha256((json.dumps(payload,sort_keys=True,indent=2)+'\n').encode()).hexdigest()
        for mode in compare.MODES:
            v=mode[:-2];version=mode[-2:];events=[]
            if version=='83':
                events=[{'message':'Creation of dynamic property UnrelatedMarkerControl::$fixtureMarker is deprecated','severity':8192,'file':'probe.php','line':1}]
            if mode=='original83':
                events += [{'message':'Creation of dynamic property '+name+' is deprecated','severity':8192,'file':'probe.php','line':2} for name in ['Criteria::$creteria_filter_attached','myCriteria::$hint','KalturaCriteria::$creteria_filter_attached']]
            body={'schema':2,'php':{'74':'7.4.33','83':'8.3.6'}[version],'variant':v,'rows':copy.deepcopy(rows),'imports':{} if version=='74' else {k:{'representation':copy.deepcopy(rep)} for k in self.payload},'source_sha256':{'criteria':self.ids['files'][v+'.php'],'filter':'f'},'events':events}
            self.records.append({'mode':mode,'exit':0,'stdout':json.dumps(body),'body':body,'stderr':'\n'.join(e['message'] for e in events)})
    def check(self):
        for r in self.records:r['stdout']=json.dumps(r['body'])
        return compare.validate(self.records,self.ids74,self.ids83,self.payload)
    def test_positive(self):self.assertFalse(self.check()['patch_selected'])
    def test_duplicate_mode(self):
        self.records[-1]=self.records[1]
        with self.assertRaises(ValueError):self.check()
    def test_layout_changed(self):
        self.records[1]['body']['rows']['fresh']['new_property']=None
        with self.assertRaises(ValueError):self.check()
    def test_unrelated_control_missing(self):
        self.records[3]['body']['events']=[]
        with self.assertRaises(ValueError):self.check()
    def test_import_changed(self):
        self.records[3]['body']['imports']['/fresh/representation']['representation']['serialized_base64']='Yg=='
        with self.assertRaises(ValueError):self.check()
    def test_payload_unbound(self):
        self.payload['/fresh/representation']='Yg=='
        with self.assertRaises(ValueError):self.check()
    def test_missing_hint_control(self):
        self.records[2]['body']['events']=[e for e in self.records[2]['body']['events'] if 'myCriteria::$hint' not in e['message']]
        with self.assertRaises(ValueError):self.check()
    def test_new_warning(self):
        self.records[3]['body']['events'].append({'message':'new warning','severity':2,'file':'probe.php','line':3})
        with self.assertRaises(ValueError):self.check()
    def test_source_drift(self):
        self.records[3]['body']['source_sha256']['criteria']='bad'
        with self.assertRaises(ValueError):self.check()
    def test_raw_body_binding(self):
        self.records[0]['stdout']='{}'
        with self.assertRaises(ValueError):compare.validate(self.records,self.ids74,self.ids83,self.payload)

    def test_legacy_hash_drift(self):
        self.ids83['files']['legacy.json']='bad'
        with self.assertRaises(ValueError):self.check()
    def test_74_fixture_not_empty(self):
        self.ids74['files']['legacy.json']=self.ids83['files']['legacy.json']
        with self.assertRaises(ValueError):self.check()
