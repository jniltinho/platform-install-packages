"""Adversarial offline record guards, not additional native execution."""
import copy,importlib.util,json,pathlib,unittest
HERE=pathlib.Path(__file__).resolve().parent;s=importlib.util.spec_from_file_location('r',HERE/'reconcile.py');r=importlib.util.module_from_spec(s);s.loader.exec_module(r)
E=r.E
P=json.loads((E/'primary.json').read_text());C=json.loads((E/'claude-chain-matrix.json').read_text());M=json.loads(pathlib.Path('/tmp/php-xml-lifecycle-fix-prep-r1/identities.json').read_text())
class Tests(unittest.TestCase):
 def runbad(self,mutate):
  p=copy.deepcopy(P);c=copy.deepcopy(C);m=copy.deepcopy(M);mutate(p,c,m)
  for row in p['records']:
   if 'body' in row:row['stdout']=json.dumps(row['body'])
  for row in c['records']:
   if 'body' in row:row['stdout']=json.dumps(row['body'])
  with self.assertRaises((ValueError,KeyError,TypeError)):r.reconcile(p,copy.deepcopy(p),c,m)
 def candidate(self,p):return next(x for x in p['records'] if x['kind']=='behavior' and x['variant']=='candidate' and x['case']=='construct-good')
 def test_actual38plus2_replay(self):self.assertEqual(r.reconcile(P,P,C,M)['status'],'PASS_BOUNDED_HELD_CONTRACT_R2')
 def test_missing_record(self):self.runbad(lambda p,c,m:p['records'].pop())
 def test_duplicate_case(self):self.runbad(lambda p,c,m:p['records'].__setitem__(1,copy.deepcopy(p['records'][0])))
 def test_boolean_exit(self):self.runbad(lambda p,c,m:p['records'][0].update(exit=False))
 def test_float_exit(self):self.runbad(lambda p,c,m:p['records'][0].update(exit=0.0))
 def test_independent_mismatch(self):
  q=copy.deepcopy(P);q['records'][0]['exit']=2
  with self.assertRaises(ValueError):r.reconcile(P,q,C,M)
 def test_drop_candidate_diagnostic(self):self.runbad(lambda p,c,m:self.candidate(p)['body']['diagnostics'].pop())
 def test_duplicate_candidate_diagnostic(self):self.runbad(lambda p,c,m:self.candidate(p)['body']['diagnostics'].append(copy.deepcopy(self.candidate(p)['body']['diagnostics'][0])))
 def test_unknown_native_warning(self):self.runbad(lambda p,c,m:self.candidate(p).update(stderr=self.candidate(p)['stderr']+'Warning: unexpected\n'))
 def test_drop_native_stderr(self):self.runbad(lambda p,c,m:self.candidate(p).update(stderr=''))
 def test_wrong_diagnostic_line(self):self.runbad(lambda p,c,m:self.candidate(p)['body']['diagnostics'][0].update(line=999))
 def test_bool_diagnostic_severity(self):self.runbad(lambda p,c,m:self.candidate(p)['body']['diagnostics'][0].update(severity=True))
 def test_stderr_list(self):self.runbad(lambda p,c,m:self.candidate(p).update(stderr=[]))
 def test_scope_marker_leak(self):
  def mutate(p,c,m):next(x for x in p['records'] if x['kind']=='scope')['body']['states'][-1]['marker']=True
  self.runbad(mutate)
 def test_baseline_diagnostic_drop(self):self.runbad(lambda p,c,m:p['records'][0]['body']['diagnostics'].pop())
 def test_product_source_drift(self):self.runbad(lambda p,c,m:self.candidate(p)['body']['loaded'].update({'alpha/config/kConf.php':'0'*64}))
 def test_causal_chain_invented(self):self.runbad(lambda p,c,m:c['records'][0]['body']['exception']['chain'].append({'class':'RuntimeException','message':'SYNTHETIC_LOADER_FAILURE'}))
 def test_causal_origin_missing(self):self.runbad(lambda p,c,m:c['records'][0]['body']['resolver_exceptions'].clear())
 def test_causal_truncated(self):self.runbad(lambda p,c,m:c['records'][0]['body']['exception'].update(chain_truncated=True))
 def test_causal_wrong_source(self):self.runbad(lambda p,c,m:c['records'][0]['body']['loaded'].update({'alpha/config/kConf.php':'0'*64}))
 def test_causal_float_exit(self):self.runbad(lambda p,c,m:c['records'][0].update(exit=0.0))
 def test_original_failure_erased(self):self.runbad(lambda p,c,m:p.update(failures=[]))
 def test_changed_helper_hash_manifest(self):self.runbad(lambda p,c,m:m['files'].update({'candidate/infra/general/kXmlEntityLoaderPolicy.php':'0'*64}))
if __name__=='__main__':unittest.main()
