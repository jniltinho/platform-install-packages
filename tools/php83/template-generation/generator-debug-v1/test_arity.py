import importlib.util,json,unittest
from pathlib import Path
s=importlib.util.spec_from_file_location('a',Path(__file__).with_name('collect_arity.py'));a=importlib.util.module_from_spec(s);s.loader.exec_module(a)
class ArityTests(unittest.TestCase):
 def row(self,constant=0):return {'runtime':'83','case':'zero','exit':0,'stderr':'','stdout':json.dumps({'runtime':'8.3.6','returned':True,'returned_type':'boolean','defined':True,'constant':constant,'diagnostics':[],'exception':None})}
 def test_numeric_contract(self):a.contract(self.row())
 def test_bool_not_integer(self):
  with self.assertRaises(ValueError):a.contract(self.row(False))
 def test_wrong_integer(self):
  with self.assertRaises(ValueError):a.contract(self.row(1))
 def test_exit_bool(self):
  r=self.row();r['exit']=False
  with self.assertRaises(ValueError):a.contract(r)
 def test_stderr(self):
  r=self.row();r['stderr']='warning'
  with self.assertRaises(ValueError):a.contract(r)
 def test_literal_zero(self):self.assertEqual(a.p.statement(b"define('SF_DEBUG', 0);"),b"define('SF_DEBUG', 0);")
 def test_literal_one(self):a.p.statement(b"define('SF_DEBUG', 1);")
 def test_literal_empty(self):
  with self.assertRaises(ValueError):a.p.statement(b"define('SF_DEBUG', );")
 def test_injection(self):
  with self.assertRaises(ValueError):a.p.statement(b"define('SF_DEBUG', 0); echo 1;")
 def test_expression(self):
  with self.assertRaises(ValueError):a.p.statement(b"define('SF_DEBUG', (0));")
 def test_duplicate(self):
  with self.assertRaises(ValueError):a.p.statement(b"define('SF_DEBUG', 0);\ndefine('SF_DEBUG', 1);")
 def synthetic(self):
  spec=importlib.util.spec_from_file_location('tv',Path(__file__).with_name('test_validate.py'));tv=importlib.util.module_from_spec(spec);spec.loader.exec_module(tv);tv.OutputTests.setUpClass();return tv.OutputTests().synthetic()
 def test_complete_extraction(self):
  files,provenance=a.p.extract(self.synthetic());self.assertEqual(set(files),{'zero.php','one.php'});self.assertEqual(len(provenance),7)
 def test_extraction_duplicate(self):
  r=self.synthetic();r['records'].append(next(x for x in r['records'] if x['runtime']=='83' and x['variant']=='debug' and x['case']=='default-false'))
  with self.assertRaises(ValueError):a.p.extract(r)
 def test_empty_output_rejected(self):
  r=self.synthetic();row=next(x for x in r['records'] if x['runtime']=='83' and x['variant']=='debug' and x['case']=='default-false');b=json.loads(row['stdout']);b['outputs']={};row['stdout']=json.dumps(b)
  with self.assertRaisesRegex(ValueError,'Output inventory'):a.p.extract(r)
 def test_verified_prepare(self):
  import tempfile
  with tempfile.TemporaryDirectory() as d:
   report=Path(d)/'r.json';report.write_text(json.dumps(self.synthetic()));out=Path(d)/'out';m=a.p.prepare(report,a.p.sha(report.read_bytes()),out)
   self.assertEqual(len(m['sources']),7);self.assertTrue((out/'zero.php').exists())
 def test_identity_both_stages_intended(self):
  import tempfile
  from unittest.mock import patch
  with tempfile.TemporaryDirectory() as d:
   report=Path(d)/'r.json';report.write_text(json.dumps(self.synthetic()));out=Path(d)/'out';m=a.p.prepare(report,a.p.sha(report.read_bytes()),out);files,_=a.p.verified(report,a.p.sha(report.read_bytes()))
   expected={a.STAGE+'/'+n:a.c.sha(b) for n,b in files.items()};expected[a.STAGE+'/arity-run.sh']=a.c.sha((a.HERE/'arity-run.sh').read_bytes());stdout=''.join(pin+'  '+name+'\n' for name,pin in expected.items())
   with patch.object(a.c,'remote',return_value={'exit':0,'stdout':stdout}),patch.object(a.c,'identities',return_value={'retained_generation_stage':'verified'}) as identities:
    result=a.identity(out,files,m);self.assertEqual(result['generation_source_and_runtime'],{'retained_generation_stage':'verified'});identities.assert_called_once()
if __name__=='__main__':unittest.main()
