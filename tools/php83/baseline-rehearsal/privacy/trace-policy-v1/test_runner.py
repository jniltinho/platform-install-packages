import importlib.util,sys,unittest
from pathlib import Path
from unittest.mock import patch
HERE=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('runner_prepare',HERE/'prepare.py');prep=importlib.util.module_from_spec(s);s.loader.exec_module(prep)
s=importlib.util.spec_from_file_location('runner_validate',HERE/'validate.py');valid=importlib.util.module_from_spec(s);s.loader.exec_module(valid)
with patch.dict(sys.modules,{'prepare':prep,'validate':valid}):
 s=importlib.util.spec_from_file_location('trace_runner',HERE/'run.py');r=importlib.util.module_from_spec(s);s.loader.exec_module(r)
class Tests(unittest.TestCase):
 def test_repository_root(self):self.assertTrue((r.REPO/'AGENTS.md').is_file())
 def test_real_pinned_payload_without_ssh(self):
  with patch.object(r.subprocess,'run',side_effect=AssertionError('No execution during payload')):
   blobs,m=r.payload()
  self.assertEqual(len(m['files']),54)
  self.assertEqual({n.split('/')[0] for n in m['files'] if '/' in n},{'original74','policy74','original83','policy83'})
  self.assertTrue(all(r.sha(blobs[n])==pin for n,pin in m['files'].items()))
 def test_original_and_candidate_policy_preserve_sources(self):
  blobs,m=r.payload()
  for name in r.pipeline.PATHS:
   if name not in prep.TARGETS:
    self.assertEqual(blobs['original74/'+name],blobs['policy74/'+name]);self.assertEqual(blobs['original83/'+name],blobs['policy83/'+name])
 def test_runner_no_production_or_network_fixture(self):
  text=(HERE/'guest.py').read_text()
  self.assertNotIn('curl',text);self.assertNotIn('mysql',text.replace('php-mysql-probe','runtime'))
  self.assertEqual(set(r.PINS),{'/usr/bin/php7.4','/usr/lib/php/20190902/json.so','/home/vagrant/php-mysql-probe/runtime83/php8.3'})
if __name__=='__main__':unittest.main()
