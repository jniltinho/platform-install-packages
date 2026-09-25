import importlib.util, unittest
from pathlib import Path
S=importlib.util.spec_from_file_location('composition',Path(__file__).with_name('collect.py'));m=importlib.util.module_from_spec(S);S.loader.exec_module(m)
class CompositionTests(unittest.TestCase):
    def test_thirty_process_matrix(self):self.assertEqual(len(m.CASES)*3,30)
    def test_cli_append_native74_delta(self):
        self.assertEqual(m.expected('cli-append','original')['winner'],'/audit/composition-fixtures/cli-shadow.php')
        self.assertEqual(m.expected('cli-append','candidate')['winner'],'/audit/fixtures/project/lib/model/FixtureFallback.php')
    def test_prepend_wins_both(self):
        for v in ['original','candidate']:self.assertEqual(m.expected('cli-prepend',v)['winner'],'/audit/composition-fixtures/cli-shadow.php')
    def test_throw_front_no_later_handler(self):
        for v in ['original','candidate']:
            r=m.expected('cli-throw-front',v);self.assertIsNone(r['winner']);self.assertTrue(all(x[0]=='later' for x in r['events']))
    def test_throw_tail_candidate_hit_then_exception(self):
        r=m.expected('cli-throw-tail','candidate');self.assertTrue(r['hit']['loaded']);self.assertEqual(r['miss']['exception']['class'],'RuntimeException')
    def test_core_internal_duplicates_not_idempotence(self):
        r=m.expected('core-repeat','candidate');self.assertEqual(len(r['internal-callables']),2);self.assertEqual(r['queue-after'].count('sfCore::splAutoload'),1)
    def test_all_cases_have_exact_event_contract(self):
        for c in m.CASES:
            for v in ['original','candidate']:self.assertIn('events',m.expected(c,v))
    def valid_body(self):
        c='cli-append';rows=m.expected(c,'candidate');target=m.TARGETS['cli'];winner=rows['winner']
        hashes={'/audit/source/'+target:'1'*64,'/audit/probe.php':'2'*64,winner:'3'*64}
        b={'case':c,'php':'8.3.6','target':{'path':target,'sha256':'1'*64},'loaded':dict(hashes),'rows':[{'case':k,'value':v} for k,v in rows.items()],'diagnostics':[]}
        return b,hashes
    def test_validator_positive(self):
        b,h=self.valid_body();self.assertEqual(m.validate(b,'cli-append','83','candidate',0,'',h),'PASS')
    def test_wrong_winner_rejected(self):
        b,h=self.valid_body();next(r for r in b['rows'] if r['case']=='winner')['value']='wrong'
        with self.assertRaisesRegex(ValueError,'rows'):m.validate(b,'cli-append','83','candidate',0,'',h)
    def test_missing_loaded_rejected(self):
        b,h=self.valid_body();b['loaded']={}
        with self.assertRaisesRegex(ValueError,'loader'):m.validate(b,'cli-append','83','candidate',0,'',h)
    def test_unexpected_native_stderr(self):
        b,h=self.valid_body()
        with self.assertRaisesRegex(ValueError,'stderr'):m.validate(b,'cli-append','83','candidate',0,'Warning: new warning',h)
    def test_fatal_exact_line_contract(self):
        d,s=m.diagnostic_contract('cli-repeat','83','candidate');self.assertIn('on line 36',s);self.assertIn('Cannot declare class simpleAutoloader',s)
    def test_no_source_extraction(self):
        s=(m.HERE/'probe.php').read_text();self.assertNotIn('eval(',s);self.assertNotIn('preg_replace(',s);self.assertIn('return false;',s)
if __name__=='__main__':unittest.main()
