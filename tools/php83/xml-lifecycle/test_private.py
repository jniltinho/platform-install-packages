"""Reuse all observation contracts against private collector; pin wrapper isolation."""
import importlib.util,pathlib,unittest
HERE=pathlib.Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('base_tests',HERE/'test_prepare.py');base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)
original_oserror=base.Tests.test_oserror_retained
def private_oserror(self):
 import tempfile,json,hashlib,sys
 from unittest.mock import patch
 with tempfile.TemporaryDirectory() as d:
  stage=pathlib.Path(d)/'stage';base.prepare.prepare(stage);out=pathlib.Path(d)/'out.json'
  (stage/'providers.json').write_text('{}')
  mp=stage/'identities.json';m=json.loads(mp.read_text());m['phase']='private-soap-provider-r1';m['files']['providers.json']=hashlib.sha256(b'{}').hexdigest();mp.write_text(json.dumps(m))
  with patch.object(sys,'argv',['collect','83',str(stage),str(out)]),patch.object(base.collect.subprocess,'run',side_effect=OSError('synthetic')):
   with self.assertRaises(SystemExit):base.collect.main()
  x=json.loads(out.read_text());self.assertEqual(len(x['records']),22);self.assertEqual(len(x['failures']),22)
base.Tests.test_oserror_retained=private_oserror
base.collect=base.module('collect-private')
class PrivateGuards(unittest.TestCase):
 def test_hash_schemas(self):
  m=base.module('prepare-private');h='a'*64
  self.assertEqual(m.file_hash(h),h)
  self.assertEqual(m.file_hash({'resolved_path':'/usr/bin/php7.4','sha256':h}),h)
  for bad in [True,{}, {'sha256':h},'G'*64,'a'*63]:
   with self.assertRaises(ValueError):m.file_hash(bad)

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
