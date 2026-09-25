import importlib.util,unittest
from pathlib import Path
s=importlib.util.spec_from_file_location('p',Path(__file__).with_name('prepare_arity.py'));p=importlib.util.module_from_spec(s);s.loader.exec_module(p)
class ExtractTests(unittest.TestCase):
 def test_empty(self):self.assertEqual(p.statement(b"define('SF_DEBUG',       );"),b"define('SF_DEBUG',       );")
 def test_true(self):self.assertEqual(p.statement(b"define('SF_DEBUG', 1);"),b"define('SF_DEBUG', 1);")
 def test_multiple(self):
  with self.assertRaises(ValueError):p.statement(b"define('SF_DEBUG', );\ndefine('SF_DEBUG', 1);")
 def test_injection(self):
  for v in [b"define('SF_DEBUG', system('id'));",b"define('SF_DEBUG', ); system('id');",b"define('SF_DEBUG', false);",b"define('SF_DEBUG', /*x*/ );",b" define('SF_DEBUG', );"]:
   with self.subTest(v=v):
    with self.assertRaises(ValueError):p.statement(v)
 def test_missing(self):
  with self.assertRaises(ValueError):p.statement(b'<?php echo 1;')
 def test_no_application_boot(self):
  code=p.HEADER+p.statement(b"define('SF_DEBUG', );")+p.FOOTER
  for token in [b'require ',b'include ',b'eval(',b'shell_exec(',b'system(']:self.assertNotIn(token,code)
 def fixture(self,duplicate=False,wrong=False):
  import json,base64,tempfile
  d=tempfile.TemporaryDirectory();self.addCleanup(d.cleanup);root=Path(d.name);rows=[]
  cases=['default-false','default-zero','rotate-false','rotate-zero','controller-false','controller-zero','default-true']
  if duplicate:cases[-2]=cases[0]
  for case in cases:
   data=b"define('SF_DEBUG', 1);" if case=='default-true' or wrong else b"define('SF_DEBUG', );"
   body={'outputs':{'fixture.php':{'sha256':p.sha(data),'base64':base64.b64encode(data).decode()}}}
   rows.append({'runtime':'83','variant':'candidate','case':case,'stdout':json.dumps(body)})
  report=root/'report.json';report.write_text(json.dumps({'records':rows}));return report,root/'output'
 def test_prepare_complete(self):
  from unittest.mock import patch
  report,out=self.fixture()
  with patch.object(p,'REPORT_PIN',p.sha(report.read_bytes())):self.assertEqual(len(p.prepare(report,out)['sources']),7)
 def test_prepare_duplicate(self):
  from unittest.mock import patch
  report,out=self.fixture(duplicate=True)
  with patch.object(p,'REPORT_PIN',p.sha(report.read_bytes())):
   with self.assertRaises(ValueError):p.prepare(report,out)
 def test_prepare_name_literal_mismatch(self):
  from unittest.mock import patch
  report,out=self.fixture(wrong=True)
  with patch.object(p,'REPORT_PIN',p.sha(report.read_bytes())):
   with self.assertRaises(ValueError):p.prepare(report,out)
 def test_prepare_pin(self):
  report,out=self.fixture()
  with self.assertRaises(ValueError):p.prepare(report,out)
 def test_prepare_existing_directory(self):
  from unittest.mock import patch
  report,out=self.fixture();out.mkdir()
  with patch.object(p,'REPORT_PIN',p.sha(report.read_bytes())):
   with self.assertRaises(FileExistsError):p.prepare(report,out)
if __name__=='__main__':unittest.main()
