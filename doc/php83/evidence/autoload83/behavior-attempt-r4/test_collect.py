import copy, unittest
from collect import expected, validate as original_validate, required_loaded, TARGETS, family
HASHES={"candidate/"+TARGETS["hp"]:"1"*64}
for path in required_loaded("hp","candidate"):
    HASHES[("candidate/"+path[7:]) if path.startswith("source/") else path]="1"*64
def validate(*args):
    args=list(args);args[6]=HASHES;return original_validate(*args)
class CollectorTests(unittest.TestCase):
    def body(self,case='hp'):
        return {'case':case,'php':'7.4.33','diagnostics':[],'target':{'path':TARGETS['hp'],'sha256':'1'*64},'loaded':{path:'1'*64 for path in required_loaded(case,'candidate')},'rows':[{'case':k,'value':v} for k,v in expected(case,'74','candidate').items()]}
    def test_hp_expected(self): self.assertEqual(validate(self.body(),'hp','74','candidate',0,'',{}),'PASS')
    def test_wrong_runtime(self):
        with self.assertRaisesRegex(ValueError,'Runtime'): validate(self.body(),'hp','83','candidate',0,'',{})
    def test_nonzero_not_pass(self):
        with self.assertRaisesRegex(ValueError,'failed'): validate(self.body(),'hp','74','candidate',255,'',{})
    def test_source_mismatch(self):
        b=self.body();b['loaded']={'source/vendor/a.php':'0'*64}
        with self.assertRaisesRegex(ValueError,'source'):validate(b,'hp','74','candidate',0,'',{})
    def test_wrong_callback_order(self):
        b=self.body();next(r for r in b['rows'] if r['case']=='queue-after')['value'].reverse()
        with self.assertRaisesRegex(ValueError,'queue-after'):validate(b,'hp','74','candidate',0,'',{})
    def test_duplicate_row(self):
        b=self.body();b['rows'].append(copy.deepcopy(b['rows'][0]))
        with self.assertRaisesRegex(ValueError,'Duplicate'):validate(b,'hp','74','candidate',0,'',{})
    def test_original83_requires_real_fatal(self):
        b={'case':'fatal-core','php':'8.3.30','target':{'path':TARGETS['core'],'sha256':None},'loaded':{},'rows':[]}
        with self.assertRaisesRegex(ValueError,'fatal'):validate(b,'fatal-core','83','original',255,'',{})
    def test_empty_loaded_rejected(self):
        b=self.body();b['loaded']={}
        with self.assertRaisesRegex(ValueError,'not loaded'):validate(b,'hp','74','candidate',0,'',{})
    def test_extra_row_rejected(self):
        b=self.body();b['rows'].append({'case':'extra','value':True})
        with self.assertRaisesRegex(ValueError,'inventory'):validate(b,'hp','74','candidate',0,'',{})
    def test_wrong_hit_trace_rejected(self):
        b=self.body();next(r for r in b['rows'] if r['case']=='hits')['value']=[]
        with self.assertRaisesRegex(ValueError,'hits'):validate(b,'hp','74','candidate',0,'',{})
    def test_unexpected_warning_rejected(self):
        b=self.body();b['diagnostics']=[{'phase':'hit','severity':2,'file':'unexpected.php','line':1,'message_sha256':'0'*64}]
        with self.assertRaisesRegex(ValueError,'diagnostic'):validate(b,'hp','74','candidate',0,'',{})
    def test_known_location_wrong_message_rejected(self):
        from collect import validate_diagnostics
        b={'diagnostics':[{'phase':'load','severity':8192,'file':TARGETS['hp'],'line':17,'message_sha256':'0'*64}]}
        with self.assertRaisesRegex(ValueError,'message'):validate_diagnostics(b,'hp','74','original')
    def test_wrong_fatal_line_rejected(self):
        import hashlib
        b={'case':'fatal-core','php':'8.3.6','target':{'path':TARGETS['core'],'sha256':None},'loaded':{},'rows':[],'fatal':{'severity':64,'file':TARGETS['core'],'line':999,'message_sha256':hashlib.sha256(b'__autoload() is no longer supported, use spl_autoload_register() instead').hexdigest()}}
        with self.assertRaisesRegex(ValueError,'line'):validate(b,'fatal-core','83','original',255,'__autoload() is no longer supported',{})
    def test_expected_queue_delta(self):
        a=expected('cli-version-queue','74','original');b=expected('cli-version-queue','74','candidate')
        self.assertFalse(a['fallback-hit']);self.assertTrue(b['fallback-hit']);self.assertEqual(b['queue'],a['queue']+['Closure'])
if __name__=='__main__':unittest.main()
