import copy,importlib.util,json,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent;s=importlib.util.spec_from_file_location('sql_compare',HERE/'compare.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
REPORT=HERE.parents[4]/'doc/php83/evidence/baseline-rehearsal/privacy/sql-display-v1/primary.json'
class Tests(unittest.TestCase):
 def setUp(self):self.r=json.loads(REPORT.read_text())
 def reject(self):
  with self.assertRaises(ValueError):m.validate(self.r)
 def test_actual(self):self.assertEqual(m.validate(self.r)['cohorts'],4)
 def test_exit_bool(self):self.r['records'][0]['execution']['exit']=False;self.reject()
 def test_duplicate_cohort(self):self.r['records'][1]['cohort']='original74';self.reject()
 def test_reused_db(self):self.r['records'][1]['db']=self.r['records'][0]['db'];self.reject()
 def test_source_drift(self):self.r['source_after']='DRIFT';self.reject()
 def test_runtime_drift(self):self.r['runtime_after']={};self.reject()
 def mutate_body(self,fn):
  row=self.r['records'][1];fn(row['body']);row['execution']['stdout']=json.dumps(row['body'])
 def test_body_not_bound(self):self.r['records'][1]['body']['inline_literal_visible']=False;self.reject()
 def test_source_body_pin(self):self.mutate_body(lambda b:b.update(source_sha256='0'*64));self.reject()
 def test_old_leak_required(self):
  row=self.r['records'][0];row['body']['rows'][0]['original_leak']=False;row['execution']['stdout']=json.dumps(row['body']);self.reject()
 def test_policy_return(self):self.mutate_body(lambda b:b.update(dry_run=['return',['boolean',True]]));self.reject()
 def test_monitor_change(self):self.mutate_body(lambda b:b['rows'][0].update(monitor=['changed']));self.reject()
 def test_inline_negative(self):self.mutate_body(lambda b:b.update(inline_literal_visible=False));self.reject()
 def test_missing_case(self):self.mutate_body(lambda b:b['rows'].pop());self.reject()
 def test_cleanup(self):self.r['records'][1]['cleanup']['stopped']=False;self.reject()
 def test_binding_boolean_not_integer(self):
  self.mutate_body(lambda b:b['rows'][0]['binding'][0].__setitem__(1,1));self.reject()
 def test_native_stderr(self):self.r['records'][1]['execution']['stderr']='NEW_DIAGNOSTIC';self.reject()
 def test_diagnostics_required_empty(self):self.mutate_body(lambda b:b.update(diagnostics=[{'severity':8192}]));self.reject()
 def test_cleanup_bool_not_int(self):self.r['records'][1]['cleanup']['stop_exit']=False;self.reject()
 def test_same_tamper_both83_expected_bool(self):
  for row in self.r['records'][2:]:
   row['body']['dry_run'][1][1]=1;row['body']['inline_outcome'][1][1]=1
   for case in row['body']['rows']:case['outcome'][1][1]=1
   row['execution']['stdout']=json.dumps(row['body'])
  self.reject()
if __name__=='__main__':unittest.main()
