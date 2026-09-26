import copy,importlib.util,json,pathlib,unittest
HERE=pathlib.Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('native',HERE/'collect-native.py');native=importlib.util.module_from_spec(s);s.loader.exec_module(native)
M=json.loads(pathlib.Path('/tmp/php-xml-lifecycle-fix-prep-r1/identities.json').read_text())
E=HERE.parents[2]/'doc/php83/evidence/xml-lifecycle/private-primary83.json'
def body():
 r=next(x for x in json.loads(E.read_text())['records'] if x['variant']=='original' and x['case']=='explicit-ok')
 b=copy.deepcopy(r['body']);b['variant']='candidate';b['probe_sha256']=M['files']['behavior.php'];b['loaded']={p[10:]:h for p,h in M['files'].items() if p.startswith('candidate/')};return b
class Tests(unittest.TestCase):
 def test_inventory38(self):self.assertEqual(2*len(native.BEHAVIOR)+len(native.SCOPE),38)
 def test_synthetic_candidate_shape_not_runtime_proof(self):self.assertEqual(native.validate(body(),'behavior','candidate','explicit-ok',M)['functional_checks'],'PASS_BOUNDED')
 def bad(self,mutate):
  b=body();mutate(b)
  with self.assertRaises((ValueError,KeyError,TypeError)):native.validate(b,'behavior','candidate','explicit-ok',M)
 def test_missing_real_class(self):self.bad(lambda b:b['loaded'].pop('infra/general/kXmlEntityLoaderPolicy.php'))
 def test_leaked_marker(self):self.bad(lambda b:b['events'][-1].update(marker_seen=True))
 def test_leaked_http(self):self.bad(lambda b:b['events'][-1]['wrappers'].update(http=True))
 def test_false_response(self):self.bad(lambda b:b.update(result={'value':'wrong'}))
 def test_unknown_process(self):
  with self.assertRaises(ValueError):native.validate(body(),'unknown','candidate','explicit-ok',M)
 def test_float_runtime(self):self.bad(lambda b:b['runtime'].update(php_id=80306.0))
 def test_wrong_probe(self):self.bad(lambda b:b.update(probe_sha256='0'*64))
 def test_bool_severity(self):self.bad(lambda b:b['diagnostics'][0].update(severity=True))
 def test_scope_flag(self):self.bad(lambda b:b.update(application_patch_selected=True))
 def test_error_not_hidden(self):self.bad(lambda b:b.update(exception={'class':'RuntimeException','message':'bad'}))
if __name__=='__main__':unittest.main()
