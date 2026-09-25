import copy, unittest
from collect import expected, validate
class CollectorTests(unittest.TestCase):
    def body(self,case='hp'):
        return {'case':case,'php':'7.4.33','loaded':{},'rows':[{'case':k,'value':v} for k,v in dict(expected(case,'74','candidate'),hits=[]).items()]}
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
        b={'case':'fatal-core','php':'8.3.30','loaded':{},'rows':[]}
        with self.assertRaisesRegex(ValueError,'fatal'):validate(b,'fatal-core','83','original',255,'',{})
    def test_expected_queue_delta(self):
        a=expected('cli-version-queue','74','original');b=expected('cli-version-queue','74','candidate')
        self.assertFalse(a['fallback-hit']);self.assertTrue(b['fallback-hit']);self.assertEqual(b['queue'],a['queue']+['Closure'])
if __name__=='__main__':unittest.main()
