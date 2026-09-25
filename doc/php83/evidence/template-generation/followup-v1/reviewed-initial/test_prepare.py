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
if __name__=='__main__':unittest.main()
