"""Local guard tests; duplicated fixtures are not independent execution proof."""
import copy
import importlib.util
import unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('exp11_runtime_compare',HERE/'compare-runtime.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

def read(name):return m.load(HERE/name)

class Guards(unittest.TestCase):
 def setUp(self):
  self.api=read('api-primary.json');self.api2=copy.deepcopy(self.api)
  token='f'*32
  if self.api['db']['unit'].endswith(token):token='e'*32
  self.api2['db']={'datadir':'/tmp/kaltura-pdo-mysql.'+token,'unit':'php83-exp11-api-'+token}
  self.api2['cleanup']['unit']=self.api2['db']['unit']
  self.prior=m.load(m.BASE/'exp10-runtime/api-primary.json')
 def check_api(self):return m.api_comparison(self.api,self.api2,self.prior)
 def test_api_fixture_positive(self):self.assertEqual(self.check_api()['diagnostic_events'],503)
 def test_api_bool_exit(self):
  self.api2['records'][0]['returncode']=False
  with self.assertRaises(ValueError):self.check_api()
 def test_api_missing_row(self):
  self.api2['records'].pop()
  with self.assertRaises(ValueError):self.check_api()
 def test_api_diagnostic_loss(self):
  self.api2['records'][3]['diagnostics']=[]
  with self.assertRaises(ValueError):self.check_api()
 def test_api_active_cleanup(self):
  self.api2['cleanup']['is_active_output']='active'
  with self.assertRaises(ValueError):self.check_api()
 def test_api_same_db(self):
  self.api2=copy.deepcopy(self.api)
  with self.assertRaises(ValueError):self.check_api()
 def test_api_response_drift(self):
  self.api2['records'][3]['stdout']+='unexpected'
  with self.assertRaises(ValueError):self.check_api()
 def test_api_control_removed(self):
  self.api2['records'][1]['signature_failure']=False
  with self.assertRaises(ValueError):self.check_api()
 def cli(self):
  a=read('cli74-primary.json');b=read('cli83-primary.json')
  return {'74':(a,copy.deepcopy(a)),'83':(b,copy.deepcopy(b))}
 def test_cli_fixture_positive(self):self.assertEqual(m.cli_comparison(self.cli())['positive_rows'],44)
 def test_cli_duplicate(self):
  r=self.cli();r['83'][1]['rows'][1]=copy.deepcopy(r['83'][1]['rows'][0])
  with self.assertRaises(ValueError):m.cli_comparison(r)
 def test_cli_bool_exit(self):
  r=self.cli();r['83'][1]['rows'][-1]['exit']=False
  with self.assertRaises(ValueError):m.cli_comparison(r)
 def test_cli_stderr_drift(self):
  r=self.cli();r['83'][1]['rows'][-1]['stderr']+='hidden'
  with self.assertRaises(ValueError):m.cli_comparison(r)
 def test_additions_fixture_positive(self):
  a=read('additions-primary.json');self.assertEqual(m.additions_comparison(a,copy.deepcopy(a))['processes'],17)
 def test_additions_missing(self):
  a=read('additions-primary.json');a['records'].pop()
  with self.assertRaises(ValueError):m.additions_comparison(a,copy.deepcopy(a))
 def test_additions_wrong_control(self):
  a=read('additions-primary.json');a['records'][-1]['exit']=0
  with self.assertRaises(ValueError):m.additions_comparison(a,copy.deepcopy(a))
 def test_additions_bad_summary(self):
  a=read('additions-primary.json');a['summary']['application_acceptance']=True
  with self.assertRaises(ValueError):m.additions_comparison(a,copy.deepcopy(a))
 def test_classes_fixture_positive(self):
  a=read('curly-primary.json');self.assertEqual(m.curly_comparison(a,copy.deepcopy(a),m.load(m.BASE/'curly-offsets/behavior-primary.json'))['logical_cases'],68)
 def test_runtime_drift(self):
  a=read('runtime-before.json');b=copy.deepcopy(a);b['identity']['uid']=0
  with self.assertRaises(ValueError):m.runtime_comparison([a,a,a,b])

if __name__=='__main__':unittest.main()
