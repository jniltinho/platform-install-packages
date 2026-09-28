import importlib.util,pathlib,unittest
p=pathlib.Path(__file__).with_name('control-policy.py');s=importlib.util.spec_from_file_location('control_policy',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class ControlTests(unittest.TestCase):
 def raw(self,p='kaltura-base',deps='php7.4-cli, libapache2-mod-php7.4, curl'):
  return f'Package: {p}\nVersion: 18.20.0-1\nDepends: {deps}\nDescription: unchanged\n continuation\n'.encode()
 def test_base(self):
  b,r=m.transform(self.raw(),'kaltura-base');self.assertIn(b'php8.3-soap (= 8.3.6-0ubuntu0.24.04.11)',b);self.assertIn(b'libapache2-mod-php8.3',b);self.assertIn(b'18.20.0-1+php83lab1',b);self.assertTrue(b.endswith(b'Description: unchanged\n continuation\n'))
 def test_other(self):
  b,r=m.transform(self.raw('kaltura-db','kaltura-base, mariadb-client'),'kaltura-db');self.assertEqual(r['php_dependency_substitutions'],0)
 def test_identity(self):
  with self.assertRaises(ValueError):m.transform(self.raw(),'kaltura-front')
 def test_double_version(self):
  with self.assertRaises(ValueError):m.transform(self.raw()+b'Version: 1-1\n','kaltura-base')
 def test_second_application(self):
  b,_=m.transform(self.raw(),'kaltura-base')
  with self.assertRaises(ValueError):m.transform(b,'kaltura-base')
 def test_unknown_runtime_edge(self):
  with self.assertRaises(ValueError):m.transform(self.raw('kaltura-db'),'kaltura-db')
 def test_missing_runtime_edge(self):
  with self.assertRaises(ValueError):m.transform(self.raw(deps='curl'),'kaltura-base')
 def test_folded_dependency(self):
  b,_=m.transform(self.raw(deps='curl,\n php7.4-cli'),'kaltura-base');self.assertIn(b'\n php8.3-cli',b)
if __name__=='__main__':unittest.main()
