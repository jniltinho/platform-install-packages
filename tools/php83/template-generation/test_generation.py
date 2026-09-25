import importlib.util,json,unittest
from pathlib import Path
s=importlib.util.spec_from_file_location('v',Path(__file__).with_name('validate_generation.py'));v=importlib.util.module_from_spec(s);s.loader.exec_module(v)
class GenerationContractTests(unittest.TestCase):
 def report(self):return json.loads((v.c.ROOT/'doc/php83/evidence/template-generation/generation-primary-r4.json').read_text())
 def reject(self,fn):
  r=self.report();fn(r)
  with self.assertRaises(ValueError):v.validate(r)
 def body(self,r,fn,index=0):
  b=json.loads(r['records'][index]['stdout']);fn(b);r['records'][index]['stdout']=json.dumps(b)
 def test_actual_records(self):v.validate(self.report())
 def test_duplicate_case(self):self.reject(lambda r:r['records'].__setitem__(1,r['records'][0]))
 def test_missing_row(self):self.reject(lambda r:r['records'].pop())
 def test_false_exit(self):self.reject(lambda r:r['records'][0].update(exit=False))
 def test_unknown_status(self):self.reject(lambda r:r['records'][0].update(exit=124))
 def test_extra_native_stderr(self):self.reject(lambda r:r['records'][0].update(stderr='extra'))
 def test_missing_diagnostic(self):self.reject(lambda r:self.body(r,lambda b:b['diagnostics'].pop()))
 def test_altered_output(self):self.reject(lambda r:self.body(r,lambda b:b.update(outputs={})))
 def test_extra_output(self):self.reject(lambda r:self.body(r,lambda b:b['outputs'].update({'extra.php':next(iter(b['outputs'].values()))})))
 def test_missing_lint(self):self.reject(lambda r:r['records'][0]['lints'].pop())
 def test_false_lint_exit(self):self.reject(lambda r:r['records'][0]['lints'][0].update(exit=False))
 def test_command_drift(self):self.reject(lambda r:r['records'][0].update(command='different'))
 def test_pending_state(self):self.reject(lambda r:r.update(pending=['unfinished']))
 def test_program_hash(self):
  def change(r):
   for k in ['identity_before','identity_after']:r[k]['snapshot_program_sha256']='0'*64
  self.reject(change)
 def test_acceptance_flag(self):self.reject(lambda r:r.update(generated_syntax_acceptance=True))
if __name__=='__main__':unittest.main()
