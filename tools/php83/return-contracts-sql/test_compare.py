import copy,json,pathlib,unittest
import compare,prepare
P=prepare.ROOT/'doc/php83/evidence/return-contracts-sql'
class Compare(unittest.TestCase):
 def setUp(self):self.report=json.loads((P/'primary-r1.json').read_text());self.d=json.loads((P/'diagnostic-contract-r1.json').read_text())
 def bad(self):self.assertRaises(ValueError,compare.validate,self.report,self.d)
 def test_real_primary(self):self.assertTrue(compare.validate(self.report,self.d))
 def test_real_repeat(self):self.assertTrue(compare.validate(json.loads((P/'independent-r1.json').read_text()),self.d))
 def test_explicit91(self):self.assertEqual(len(compare.expected_rows()),91)
 def test_cohort_duplicate(self):self.report['records'][1]['cohort']='prerequisite';self.bad()
 def test_cohort_missing(self):self.report['records'].pop();self.bad()
 def test_exit_bool(self):self.report['records'][0]['execution']['exit']=False;self.bad()
 def test_exit_float(self):self.report['records'][0]['execution']['exit']=0.0;self.bad()
 def test_missing_row(self):self.report['records'][0]['body']['rows'].pop();self.bad()
 def test_typed_float(self):self.report['records'][0]['body']['rows'][0][-1][-1][-1]=0.0;self.bad()
 def test_typed_bool(self):self.report['records'][0]['body']['rows'][0][-1][-1][-1]=False;self.bad()
 def test_both_cohorts_same_wrong_value(self):
  for r in self.report['records']:r['body']['rows'][0][-1][-1][-1]=9
  self.bad()
 def test_extra_stderr(self):self.report['records'][0]['execution']['stderr']+='unsafe extra';self.bad()
 def test_dropped_diagnostic(self):self.report['records'][0]['body']['diagnostics'].pop();self.bad()
 def test_loaded_hash(self):self.report['records'][0]['body']['loaded']['vendor/propel/Propel.php']='0'*64;self.bad()
 def test_stop_false(self):self.report['records'][0]['cleanup']['stop_exit']=False;self.bad()
 def test_active_unit(self):self.report['records'][0]['cleanup']['state']='active';self.bad()
 def test_self_authorized_source(self):
  r=self.report['records'][0];r['body']['loaded']['vendor/propel/Propel.php']='0'*64;self.report['identities']['files']['prerequisite/vendor/propel/Propel.php']='0'*64;self.bad()
 def test_stage_pin_drift(self):self.report['stage_pin']='0'*64;self.bad()
 def test_source_drift(self):self.report['source_after']='different';self.bad()
 def test_runtime_drift(self):self.report['runtime_after']={};self.bad()
if __name__=='__main__':unittest.main()
