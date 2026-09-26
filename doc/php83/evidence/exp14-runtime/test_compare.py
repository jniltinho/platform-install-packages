import copy, importlib.util, unittest
from pathlib import Path
s=importlib.util.spec_from_file_location('cmp',Path(__file__).with_name('compare-runtime.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class Comparator(unittest.TestCase):
 def api(self):
  return [m.load(m.RUN/x) for x in ['api-primary.json','claude-api.json']]+[m.load(m.BASE/'exp13-runtime/api-primary.json')]
 def cli(self):
  return {n:[m.load(m.RUN/f'cli{n}-primary.json'),m.load(m.RUN/f'claude-cli{n}.json')] for n in ['74','83']}
 def test_actual_reconcile(self):self.assertEqual(m.reconcile()['status'],'PASS_BOUNDED_API4_CLI48_ACTUAL_ARTIFACT_REPEAT')
 def test_unexpected_candidate_diagnostic(self):
  a=self.api()
  for r in a[:2]:r['records'][3]['diagnostics']=[{'severity':'ApplicationDiagnostic','path':'/audit/app/unexpected.php','line':1,'count':1}]
  with self.assertRaises(ValueError):m.api_comparison(*a)
 def test_duplicate_api_row(self):
  a=self.api();a[0]['records'][2]=copy.deepcopy(a[0]['records'][3])
  with self.assertRaises(ValueError):m.api_comparison(*a)
 def test_wrong_prior(self):
  a=self.api();a[0]['previous_artifact']['zip_sha256']='a'*64
  with self.assertRaises(ValueError):m.api_comparison(*a)
 def test_cleanup(self):
  a=self.api();a[0]['cleanup']['stopped']=False
  with self.assertRaises(ValueError):m.api_comparison(*a)
 def test_source_after(self):
  a=self.api();a[0]['post_source']['previous']['matches']=False
  with self.assertRaises(ValueError):m.api_comparison(*a)
 def test_native_cli_stderr(self):
  r=self.cli();r['83'][1]['rows'][0]['stderr']+='changed'
  with self.assertRaises(ValueError):m.cli_comparison(r)
 def test_duplicate_cli(self):
  r=self.cli();r['83'][0]['rows'][0]=copy.deepcopy(r['83'][0]['rows'][1])
  with self.assertRaises(ValueError):m.cli_comparison(r)
 def test_both_cli_same_bad_exit(self):
  r=self.cli()
  for v in r['83']:v['rows'][0]['exit']=True
  with self.assertRaises(ValueError):m.cli_comparison(r)
 def test_missing_api_row(self):
  a=self.api();a[0]['records'].pop()
  with self.assertRaises(ValueError):m.api_comparison(*a)
 def test_current_pin(self):
  a=self.api();a[0]['artifact']['zip_sha256']='a'*64
  with self.assertRaises(ValueError):m.api_comparison(*a)
 def ledger(self):
  import json
  return [json.loads(x) for x in (m.RUN/'primary74-execution-ledger.jsonl').read_text().splitlines()]
 def test_missing_ledger_phase(self):
  e=self.ledger();e=[x for x in e if x['phase']!='api-primary']
  with self.assertRaises(ValueError):m.ledger_validate(e,'74','primary')
 def test_orchestrator_drift(self):
  e=self.ledger();e[0]['orchestrator_sha256']='a'*64
  with self.assertRaises(ValueError):m.ledger_validate(e,'74','primary')
 def test_ledger_path_escape(self):
  e=self.ledger();next(x for x in e if 'command' in x)['stdout_path']='/etc/passwd'
  with self.assertRaises(ValueError):m.ledger_validate(e,'74','primary')
 def test_null_productive_hash_cannot_remove_link(self):
  e=self.ledger();r=next(x for x in e if x['phase']=='api-primary')
  r['output_sha256']=None;r['output']='/outside/not-a-report.json'
  with self.assertRaises(ValueError):m.ledger_validate(e,'74','primary')
 def test_missing_snapshot_output_hash(self):
  e=self.ledger();next(x for x in e if x['phase']=='primary74-runtime-before')['output_sha256']=None
  with self.assertRaises(ValueError):m.ledger_validate(e,'74','primary')
if __name__=='__main__':unittest.main()
