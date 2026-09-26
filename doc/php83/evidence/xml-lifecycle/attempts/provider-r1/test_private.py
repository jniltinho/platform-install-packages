"""Reuse all observation contracts against private collector; pin wrapper isolation."""
import importlib.util,pathlib,unittest
HERE=pathlib.Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('base_tests',HERE/'test_prepare.py');base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)
base.collect=base.module('collect-private')
class PrivateGuards(unittest.TestCase):
 def test_explicit_module(self):
  s=(HERE/'run-private.sh').read_text();self.assertIn('-d extension=/audit/soap.so ',s);self.assertNotIn('-d extension=soap ',s)
 def test_runtime_library_hashes(self):
  s=(HERE/'run-private.sh').read_text();self.assertIn("provider['files'].items()",s);self.assertIn('Provider/runtime/library drift',s)
 def test_readonly_network(self):
  s=(HERE/'run-private.sh').read_text()
  for t in ['PrivateNetwork=yes','SystemCallFilter=~socket socketpair','ProtectSystem=strict','BindReadOnlyPaths=$base:/audit/probe $soap:/audit/soap.so']:self.assertIn(t,s)
 def test_phase_guard(self):
  s=(HERE/'collect-private.py').read_text();self.assertIn("m.get('phase')=='private-soap-provider-r1'",s);self.assertIn("'providers.json' in m['files']",s)
 def test_no_install(self):
  s=(HERE/'provider-inspect.py').read_text();self.assertNotIn("'install'",s);self.assertIn("'dpkg-deb','-x'",s);self.assertIn('AllowUnauthenticated "false"',s)
def load_tests(loader,tests,pattern):
 tests.addTests(loader.loadTestsFromModule(base));return tests
if __name__=='__main__':unittest.main()
